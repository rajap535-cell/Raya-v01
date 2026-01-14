# orchestrator.py - unified entry for all queries (with deep debug)
import re
import wikipedia
import requests
from bs4 import BeautifulSoup
from typing import Optional
from config import ENGINE_ORDER, WIKI_SENTENCES
from raya_core.cache import load_cache, save_cache
from raya_core.pipeline import run_pipeline
from aggregator import aggregate
from raya_core.base import EngineResult
from raya_core.cache import cache_get, cache_put
from raya_core.router import ask_via_router
from raya_core.local_model import ask_local
from raya_core.backend_cloud import ask_cloud

DEBUG = True  # Turn off in production

# Load persistent cache
_CACHE = load_cache() or {}

def _cache_key(q: str) -> str:
    q = q.strip().lower()
    q = re.sub(r"[^a-z0-9\s]", "", q)
    return " ".join(q.split())

def _wiki_safe_query(q: str)-> str:
    q = q.lower ()
    q = re.sub(r"(latest|recent|current|new|research on)", "", q)
    q = q.strip()
    return q
    
def _try_wikipedia(query: str) -> Optional[str]:
    if DEBUG: print(f"[Stage: Wikipedia] 🔍 Searching for: {query}")
    try:
        result = wikipedia.summary(query, sentences=WIKI_SENTENCES)

        # ---- Wikipedia Relevance Filter ----
        irrelevant_keywords = [
            "film", "album", "song", "television", "episode", "novel",
            "character", "fictional", "video game", "band", "music", "movie", "drama"
        ]
        if result and any(word in result.lower() for word in irrelevant_keywords):
            if DEBUG: print("[Stage: Wikipedia] ⚠️ Irrelevant Wikipedia result detected — skipping.")
            result = None
        # ------------------------------------

        if result:
            if DEBUG: print(f"[Stage: Wikipedia] ✅ Relevant summary accepted ({len(result)} chars)")
            return result
        else:
            if DEBUG: print("[Stage: Wikipedia] 🚫 No valid Wikipedia summary, moving to next stage...")

    except Exception as e:
        if DEBUG: print(f"[Stage: Wikipedia] ⚠️ Error: {e}")
    return None


def _try_web_search(query: str) -> Optional[str]:
    if DEBUG: print(f"[Stage: WebSearch] 🌐 Searching web for: {query}")
    try:
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            if DEBUG: print(f"[Stage: WebSearch] ❌ HTTP {response.status_code}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        snippet = soup.find("div", class_="BNeawe").text if soup.find("div", class_="BNeawe") else None
        if snippet:
            if DEBUG: print(f"[Stage: WebSearch] ✅ Got snippet: {snippet[:80]}...")
            return snippet
        else:
            if DEBUG: print("[Stage: WebSearch] ❌ No snippet found.")
    except Exception as e:
        if DEBUG: print(f"[Stage: WebSearch] ⚠️ Error: {e}")
    return None

def ask_raya(query: str, db_file: str = "custom_db.sqlite", intents: list = []) -> EngineResult:
    if DEBUG:
        print(f"\n[Orchestrator] 🧠 Query: '{query}'")

    # ---------- HARD INITIALIZATION (NON-NEGOTIABLE) ----------
    key = _cache_key(query)
    cached = None
    final_text = None
    metadata = {}
    best_source = "Unknown"

    from raya_core.cache import CACHE_ENABLED

    # ---------- CACHE ----------
    if CACHE_ENABLED:
        try:
            cached = _CACHE.get(key)
        except Exception:
            cached = None

    if cached:
        if cached.get("text", "").startswith("[cloud disabled]"):
            if DEBUG:
                print("[Orchestrator] 🚫 Skipping stale cloud-disabled cache")
        else:
            if DEBUG:
                print("[Orchestrator] 💾 Using cached result")
            return EngineResult(
                sources={cached.get("source", "cache"): True},
                text=cached.get("text", ""),
                confidence=cached.get("confidence", 0.8),
                meta={**cached.get("meta", {}), "cache": True},
            )

    # ---------- ROUTER ----------
    route_decision = ask_via_router(query)
    route = route_decision.get("model", "local")

    if DEBUG:
        print(f"[Router] 🧭 Route selected: {route}")

    # ---------- LOCAL LLM ----------
    final_text = None
    best_source= None
    
    if route in ("local", "hybrid"):
        if DEBUG:
            print("[Stage: Local LLM] 🧠 Generating")
        final_text = ask_local(query)

    # ❌ Local failed → Wikipedia fallback
    if final_text.startswith("[local error]"):
        if DEBUG:
            print("[Stage: Wikipedia] 🔄 Local failed, trying Wikipedia")
        wiki_text = _try_wikipedia(query)
        if wiki_text:
            final_text = wiki_text
            best_source = "Wikipedia"
        else:
            final_text = None
    else:
        best_source = "Local LLM"

    # ---------- PIPELINE ----------
    if route == "hybrid" or not final_text:
        try:
            if DEBUG:
                print("[Stage: Pipeline] ⚙️ Running pipeline")
            pipeline_text, metadata = run_pipeline(query, db_file, intents)
            if pipeline_text:
                final_text = aggregate([final_text, pipeline_text])
                best_source = "Pipeline"
        except Exception as e:
            if DEBUG:
                print(f"[Stage: Pipeline] ⚠️ Error: {e}")

    # ---------- CLOUD ----------
    if not final_text or route == "cloud":
        try:
            if DEBUG:
                print("[Stage: Cloud LLM] ☁️ Escalating")
            final_text = ask_cloud(query)
            best_source = "Cloud LLM"
        except Exception as e:
            if DEBUG:
                print(f"[Stage: Cloud LLM] ❌ Error: {e}")

    # ---------- FINAL FALLBACK ----------
    if not final_text:
        final_text = "Sorry, I don't have enough verified information to answer that yet."
        best_source = "Fallback"

    confidence = 0.9 if best_source != "Fallback" else 0.2

    # ---------- SAVE CACHE ----------
    _CACHE[key] = {
        "source": best_source,
        "text": final_text,
        "confidence": confidence,
        "meta": metadata,
    }
    save_cache(_CACHE)

    if DEBUG:
        print(f"[Orchestrator] ✅ Final Source: {best_source}")
        print(f"[Orchestrator] ✅ Confidence: {confidence}")

    return EngineResult(
        sources={best_source: True},
        text=final_text,
        confidence=confidence,
        meta=metadata,
    )
