# raya_core/router.py
import re
from raya_core.local_model import ask_local
from raya_core.backend_cloud import ask_cloud


# DAY-3 HARD LOCK
ENABLE_CLOUD = False


# Router rules (as approved)
CLOUD_KEYWORDS = {
    "code", "generate", "analysis", "research", "legal", "finance",
    "explain", "compare", "reason", "design"
}

LOCAL_KEYWORDS = {
    "personal", "remember", "recall", "my", "profile", "preference",
    "news", "search", "summarize", "embed", "summary"
}

CLOUD_MIN_LENGTH = 350


def choose_model(user_query: str) -> str:
    q = (user_query or "").lower().strip()
    if not q:
        return "local"
    
    # Block local LLM for future factual questions
    if re.search(r"\b20(2[4-9]|3\d)\b", q):
        return "pipeline"

    # 🔴 HARD RULE: Future years → NEVER local
    if re.search(r"\b20(2[4-9]|3\d)\b", q):
        return "pipeline_first"

    # Cloud disabled (Day-3 lock)
    if not ENABLE_CLOUD:
        return "local"

    for k in CLOUD_KEYWORDS:
        if k in q:
            return "cloud"

    for k in LOCAL_KEYWORDS:
        if k in q:
            return "local"

    if len(q) > CLOUD_MIN_LENGTH:
        return "cloud"

    return "local"

def _local_confidence(text: str) -> float:
    """
    Heuristic confidence for local LLM output.
    No ML. Deterministic.
    """
    if not text:
        return 0.0
    if text.startswith("[local error]"):
        return 0.0
    if len(text.strip()) < 40:
        return 0.2
    if "i don't know" in text.lower():
        return 0.3
    return 0.75


def ask_via_router(prompt: str, fallback_to_cloud: bool = True) -> dict:
    route = choose_model(prompt)

    # Pipeline-first (future years, statistics, projections)
    if route == "pipeline_first":
        return {
            "model": "pipeline",
            "reason": "future_year_forced"
        }

    # Local-only mode
    if route == "local":
        local_text = ask_local(prompt)
        confidence = _local_confidence(local_text)

        return {
            "text": local_text,
            "model": "local",
            "confidence": confidence,
            "reason": "router_local"
        }

    # Cloud (disabled currently)
    if route == "cloud" and ENABLE_CLOUD:
        cloud_text = ask_cloud(prompt)
        return {
            "text": cloud_text,
            "model": "cloud",
            "confidence": 0.9,
            "reason": "router_cloud"
        }

    # Fallback
    return {
        "model": "local",
        "reason": "router_fallback"
    }
print("[Router] 🔒 Local-only mode active")
