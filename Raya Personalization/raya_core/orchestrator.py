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

DEBUG = True  # Turn off in production

# Load persistent cache
_CACHE = load_cache()

def _cache_key(q: str) -> str:
    q = q.strip().lower()
    q = re.sub(r"[^a-z0-9\s]", "", q)
    return " ".join(q.split())

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
    key = _cache_key(query)
    if DEBUG:
        print(f"\n[Orchestrator] 🧠 Query: '{query}'")

    # 1️⃣ Check cache
    if key in _CACHE:
        cached = _CACHE[key]
        if DEBUG:
            print("[Orchestrator] 💾 Using cached result")
        return EngineResult(
            sources={cached.get("source", "cache"): True},  # dictionary
            text=cached.get("text", ""),
            confidence=cached.get("confidence", 0.8),
            meta={**cached.get("meta", {}), "cache": True},
        )

    final_text = None
    best_source = None
    metadata = {}

    # 2️⃣ Wikipedia
    final_text = _try_wikipedia(query)
    if final_text:
        best_source = "Wikipedia"

    # 3️⃣ Web Search
    if not final_text:
        final_text = _try_web_search(query)
        if final_text:
            best_source = "Web Search"

    # 4️⃣ Pipeline
    if not final_text:
        try:
            if DEBUG:
                print("[Stage: Pipeline] ⚙️ Running local pipeline...")
            final_text, metadata = run_pipeline(query, db_file, intents)
            if final_text:
                best_source = metadata.get("best_source", "pipeline")
                if DEBUG:
                    print("[Stage: Pipeline] ✅ Returned from pipeline")
            else:
                if DEBUG:
                    print("[Stage: Pipeline] ❌ Empty pipeline output.")
        except Exception as e:
            if DEBUG:
                print(f"[Stage: Pipeline] ⚠️ Error: {e}")

    # 5️⃣ Fallback
    if not final_text:
        final_text = "Sorry, I don't know the answer to that."
        best_source = "Fallback"
        if DEBUG:
            print("[Stage: Fallback] ❗ Using fallback response.")

    # 6️⃣ Cache result
    confidence = 0.9 if best_source != "Fallback" else 0.2
    _CACHE[key] = {
        "source": best_source,
        "text": final_text,
        "confidence": confidence,
        "meta": metadata,
        "sources": {best_source: True},  # store as dictionary
    }
    save_cache(_CACHE)

    if DEBUG:
        print(f"[Orchestrator] ✅ Final Source: {best_source}")
        print(f"[Orchestrator] ✅ Confidence: {confidence}")
        print(f"[Orchestrator] ✅ Preview: {final_text[:100]}")

    return EngineResult(
        sources={best_source: True},  # ✅ dictionary
        text=final_text,
        confidence=confidence,
        meta=metadata,
    )
