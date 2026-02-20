# orchestrator.py - unified entry for all queries (STABLE & SAFE)

import re
import wikipedia
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
from raya_core.question_classifier import classify_question, QuestionType

DEBUG = True  # turn off in production

# --------------------------------------------------
# Persistent Cache
# --------------------------------------------------
_CACHE = load_cache() or {}

# --------------------------------------------------
# Helpers
# --------------------------------------------------
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

def _wiki_safe_query(q: str) -> str:
    q = q.lower()
    q = re.sub(r"\bwhat is\b|\bwho is\b|\bdefine\b", "", q)
    q = re.sub(r"(latest|recent|current|new|research on)", "", q)
    q = q.strip()
    if len(q) <= 5:
        q = q.upper()
    return q

def wiki_allowed(question_type: QuestionType) -> bool:
    return question_type in (
        QuestionType.FACT_DEFINITION,
        QuestionType.HISTORICAL
    )

def _try_wikipedia(query: str) -> Optional[str]:
    if DEBUG:
        print(f"[Stage: Wikipedia] 🔍 Searching for: {query}")
    try:
        result = wikipedia.summary(query, sentences=WIKI_SENTENCES)
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

def _is_failed(text: Optional[str]) -> bool:
    if not text or not isinstance(text, str):
        return True
    t = text.lower()
    return (
        t.startswith("[local error]")
        or "timeout" in t
        or "not running" in t
        or "i don't know" in t
    )

# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------

def ask_raya(query: str, db_file: str = "custom_db.sqlite", intents: list = []) -> EngineResult:
    intents = list(detect_intents(query))
    if DEBUG:
        print(f"\n[Orchestrator] 🧠 Query: '{query}'")

    question_type = classify_question(query)
    if DEBUG:
        print(f"[Orchestrator] 🏷️ Question Type: {question_type.name}")

    normalized = _normalize_query(query)
    key = _cache_key(normalized)

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
                confidence=cached.get("confidence", 0.9),
                meta={**cached.get("meta", {}), "cache": True},
            )

    # --------------------------------------------------
    # ROUTER
    # --------------------------------------------------
    router_result = ask_via_router(query)
    router_result["question_type"] = question_type
    route = router_result.get("model", "local")
    final_text = router_result.get("text")

    if DEBUG:
        print(f"[Router] 🧭 Route: {route}")

    # --------------------------------------------------
    wiki_candidate = None
    if route == "wiki_first" and wiki_allowed(question_type):
        wiki_candidate = _try_wikipedia(_wiki_safe_query(query))

    # --------------------------------------------------
    # LOCAL LLM
    # --------------------------------------------------
    if route in ("local", "hybrid"):
        if DEBUG:
            print("[Stage: Local LLM] 🧠 Generating")
        local_text = ask_local(query)
        if isinstance(local_text, str) and not local_text.startswith("[local error]"):
            final_text = local_text
            best_source = "Local LLM"
        if DEBUG:
            print("[Local Output]:", repr(local_text))
    # --------------------------------------------------
    # PIPELINE
    # --------------------------------------------------
    if (route == "hybrid" or _is_failed(final_text)) and best_source != "Wikipedia":
        try:
            if DEBUG:
                print("[Stage: Pipeline] ⚙️ Running")
            pipe_text, metadata = run_pipeline(query, db_file, intents)
            if pipe_text:
                final_text = pipe_text
                best_source = "Pipeline"
        except Exception as e:
            if DEBUG:
                print(f"[Stage: Pipeline] ❌ Error: {e}")

    # --------------------------------------------------
    # WIKIPEDIA FALLBACK (SAFE)
    # --------------------------------------------------
    if (
        _is_failed(final_text)
        and wiki_allowed(question_type)
        and not _is_news_or_research(query)
    ):
        if DEBUG:
            print("[Stage: Wikipedia] 🔄 Trying fallback")
        wiki_text = _try_wikipedia(_wiki_safe_query(query))
        if wiki_text and validate_answer(query, "wikipedia", wiki_text):
            final_text = wiki_text
            best_source = "Wikipedia"

    # --------------------------------------------------
    # CLOUD (LAST RESORT)
    # --------------------------------------------------
    if _is_failed(final_text) and best_source != "Wikipedia":
        cloud_text = ask_cloud(query)
        if not cloud_text.startswith("[cloud disabled]"):
            final_text = cloud_text
            best_source = "Cloud LLM"

    # --------------------------------------------------
    # FINAL GUARANTEE
    # --------------------------------------------------
    if _is_failed(final_text) and best_source == "Unknown":
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
        "meta": metadata,
    }
    save_cache(_CACHE)

    if DEBUG:
        print(f"[Orchestrator] ✅ Final Source: {best_source}")

    return EngineResult(
        sources={best_source: True},
        text=final_text,
        meta=metadata,
    )
