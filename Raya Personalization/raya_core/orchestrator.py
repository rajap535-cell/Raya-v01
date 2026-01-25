# orchestrator.py - unified entry for all queries (STABLE & SAFE)
import re
import wikipedia
import requests
from bs4 import BeautifulSoup
from typing import Optional

from config import WIKI_SENTENCES
from raya_core.cache import load_cache, save_cache, CACHE_ENABLED
from raya_core.pipeline import run_pipeline
from aggregator import aggregate
from raya_core.base import EngineResult
from raya_core.router import ask_via_router
from raya_core.local_model import ask_local
from raya_core.backend_cloud import ask_cloud
from intent import detect_intents
from raya_core.validator import validate_answer, is_future_query


DEBUG = True  # turn off in production

# --------------------------------------------------
# Persistent Cache
# --------------------------------------------------
_CACHE = load_cache() or {}

# --------------------------------------------------
# Helpers
COMMON_TYPOS = {
    " os ": " is ",
    " teh ": " the ",
    " wht ": " what ",
}

def _normalize_query(q: str) -> str:
    q = f" {q.lower()} "
    for k, v in COMMON_TYPOS.items():
        q = q.replace(k, v)
    return q.strip()

def _should_use_wikipedia(query: str) -> bool:
    q = query.lower()
    BLOCK = {
        "latest", "news", "research", "study",
        "paper", "arxiv", "current", "recent" "how can", "how to",
        "ways to", "tips to"
    }
    return not any(w in q for w in BLOCK)
# --------------------------------------------------
def _cache_key(q: str) -> str:
    q = q.strip().lower()
    q = re.sub(r"[^a-z0-9\s]", "", q)
    return " ".join(q.split())

NEWS_WORDS = {
    "latest", "news", "current", "recent", "today",
    "update", "research", "study", "paper", "arxiv"
}

def _is_news_or_research(q: str) -> bool:
    q = q.lower()
    return any(w in q for w in NEWS_WORDS)

def is_future_query(q: str) -> bool:
    return bool(re.search(r"\b20(2[4-9]|3\d)\b", q))

def requires_number(q: str) -> bool:
    q = q.lower()
    return any(word in q for word in [
        "how many", "distance", "gdp", "population", "year"
    ])

def has_number(text: str) -> bool:
    return bool(re.search(r"\d", text))


def requires_number(q: str) -> bool:
    q = q.lower()
    return any(word in q for word in [
        "how many", "distance", "gdp", "population", "year"
    ])

def has_number(text: str) -> bool:
    return bool(re.search(r"\d", text))


def _wiki_safe_query(q: str) -> str:
    q = q.lower()
    q = re.sub(r"\bwhat is\b|\bwho is\b|\bdefine\b", "", q)
    q = re.sub(r"(latest|recent|current|new|research on)", "", q)
    q = q.strip()

    # uppercase acronyms
    if len(q) <= 5:
        q = q.upper()

    return q

def _try_wikipedia(query: str) -> Optional[str]:
    if DEBUG:
        print(f"[Stage: Wikipedia] 🔍 Searching for: {query}")

    try:
        result = wikipedia.summary(query, sentences=WIKI_SENTENCES)

        # filter entertainment junk
        irrelevant = [
            "film", "album", "song", "television", "episode",
            "novel", "fictional", "video game", "band", "movie"
        ]
        if any(k in result.lower() for k in irrelevant):
            if DEBUG:
                print("[Stage: Wikipedia] ⚠️ Irrelevant result rejected")
            return None

        if DEBUG:
            print(f"[Stage: Wikipedia] ✅ Accepted ({len(result)} chars)")
        return result

    except Exception as e:
        if DEBUG:
            print(f"[Stage: Wikipedia] ❌ Error: {e}")
        return None


# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------
def ask_raya(query: str, db_file: str = "custom_db.sqlite", intents: list = []) -> EngineResult:
    intents = list(detect_intents(query))
    if DEBUG:
        print(f"\n[Orchestrator] 🧠 Query: '{query}'")

    key = _cache_key(query)
    final_text = None
    best_source = "Unknown"
    metadata = {}

    # --------------------------------------------------
    # CACHE
    # --------------------------------------------------
    if CACHE_ENABLED:
        cached = _CACHE.get(key)
        if cached and not cached["text"].startswith("[cloud disabled]"):
            if DEBUG:
                print("[Orchestrator] 💾 Using cache")
            return EngineResult(
                sources={cached["source"]: True},
                text=cached["text"],
                confidence=cached["confidence"],
                meta={**cached.get("meta", {}), "cache": True},
                   
               )

    # --------------------------------------------------
    # ROUTER
    # --------------------------------------------------
    router_result = ask_via_router(query)
    route = router_result.get("model", "local")
    final_text = router_result.get("text")

    if DEBUG:
        print(f"[Router] 🧭 Route: {route}")

    # --------------------------------------------------

    if "fact" in intents:
        route = "wiki_first"

    if route == "wiki_first":
        wiki_text = _try_wikipedia(_wiki_safe_query(query))
        if wiki_text:
            return EngineResult(
                sources={"Wikipedia": True},
                text=wiki_text,
                confidence=0.95,
                meta={}
            )
    # LOCAL LLM
    # --------------------------------------------------
    if route in ("local", "hybrid"):
        if DEBUG:
            print("[Stage: Local LLM] 🧠 Generating")
        final_text = ask_local(query)

        if isinstance(final_text, str) and not final_text.startswith("[local error]"):
            best_source = "Local LLM"
    def _is_failed(text: Optional[str]) -> bool:
        if not text:
            return True
        if not isinstance(text, str):
            return True
        t = text.lower()
        return (
            t.startswith("[local error]")
            or "timeout" in t
            or "not running" in t
            or "i don't know" in t
        )

    # --------------------------------------------------
    # WIKIPEDIA FALLBACK (SAFE)
    # --------------------------------------------------
    wiki_text = _try_wikipedia(safe_query)

    if wiki_text:
        if is_future_query(query):
            if DEBUG:
                print("[Wikipedia] ❌ Rejected: future data")
            wiki_text=None
        elif requires_number(query) and not has_number(wiki_text):
            if DEBUG:
                print("[Wikipedia] ❌ Rejected: numeric answer required")
            wiki_text = None

        else:
            final_text = wiki_text
            best_source = "Wikipedia"


    if _is_failed(final_text) and _should_use_wikipedia(query):
        if DEBUG:
            print("[Stage: Wikipedia] 🔄 Trying fallback")
        safe_query = _wiki_safe_query(query)
        wiki_text = _try_wikipedia(safe_query)
        if wiki_text and validate_answer(query, "wikipedia", wiki_text):
            final_text = wiki_text
            best_source = "Wikipedia"
        else:
            final_text = None
    # --------------------------------------------------
    # PIPELINE (NO WIKI LOOP)
    # --------------------------------------------------
    if (route == "hybrid" or not final_text) and best_source != "Wikipedia":
        try:
            if DEBUG:
                print("[Stage: Pipeline] ⚙️ Running")
            pipe_text, metadata = run_pipeline(query, db_file, intents)

            if pipe_text:
                final_text = aggregate([final_text, pipe_text], extras={})
                best_source = "Pipeline"

        except Exception as e:
            if DEBUG:
                print(f"[Stage: Pipeline] ❌ Error: {e}")

    # --------------------------------------------------
    # CLOUD (HARD GUARDED)
    # --------------------------------------------------
    if _is_failed(final_text) and best_source != "Wikipedia":
        cloud_text = ask_cloud(query)

        if not cloud_text.startswith("[cloud disabled]"):
            final_text = cloud_text
            best_source = "Cloud LLM"

    # --------------------------------------------------
    # FINAL GUARANTEE (NEVER EMPTY)
    # --------------------------------------------------
    if _is_failed(final_text) and best_source=="Unknown":
        final_text = (
            "This topic is evolving and requires up-to-date sources. "
            "Here is a reliable overview based on established knowledge."
    )
    best_source = "Safe Fallback"
    # --------------------------------------------------
    # SAVE CACHE
    # --------------------------------------------------
    _CACHE[key] = {
        "source": best_source,
        "text": final_text,
        #"confidence": confidence,
        "meta": metadata,
    }
    save_cache(_CACHE)

    if DEBUG:
        print(f"[Orchestrator] ✅ Final Source: {best_source}")
        print(f"[Orchestrator]")

    return EngineResult(
        sources={best_source: True},
        text=final_text,
        #confidence=confidence,
        meta=metadata,
    )
