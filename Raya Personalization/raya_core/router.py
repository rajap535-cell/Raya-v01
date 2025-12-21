# raya_core/router.py
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

    # DAY-3 OVERRIDE: cloud disabled
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
    user_query = prompt

    # Force local while cloud is disabled
    local_text = ask_local(prompt)
    confidence = _local_confidence(local_text)

    # Never escalate to cloud in Day-3
    return {
        "text": local_text,
        "model": "local",
        "confidence": confidence,
        "reason": "router_local_locked"
    }

    # Cloud chosen explicitly
    cloud_text = ask_cloud(prompt)
    return {
        "text": cloud_text,
        "model": "cloud",
        "confidence": 0.9,
        "reason": "router_cloud"
    }
print("[Router] 🔒 Local-only mode active")
