# intent.py
import re
from typing import Set

# ---------- Keywords ----------
QUESTION_WORDS = {
    "who", "what", "when", "where", "why", "how", "which", "whom", "whose"
}

RECENCY_HINTS = {
    "latest", "today", "tonight", "this week", "this month", "breaking",
    "update", "updates", "yesterday", "recent", "new", "newest", "current", "now",
    "2024", "2025", "2026"
}

MONTHS = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
}

RESEARCH_HINTS = {
    "paper", "preprint", "arxiv", "study", "studies", "research",
    "doi", "journal", "conference", "proceedings", "benchmark"
}

FACT_QUESTION_PATTERNS = [
    r"^who\b", r"^what\b", r"^when\b", r"^where\b", r"^why\b", r"^how\b",
    r"\bdefine\b", r"\bmeaning of\b", r"\bhistory of\b", r"\bsummary of\b"
]

YESNO_PREFIXES = (
    "is ", "are ", "was ", "were ", "did ", "do ", "does ",
    "can ", "could ", "will ", "would ", "has ", "have ", "had "
)


# ---------- Main Functions ----------
def is_factual_question(text: str) -> bool:
    """Lightweight classifier: check if a query looks like a factual Q."""
    if not text:
        return False

    t = text.strip().lower()

    # ignore simple system commands
    if t in {"date", "time", "news"}:
        return False

    return (
        "?" in t
        or t.split()[0] in QUESTION_WORDS
        or t.startswith(YESNO_PREFIXES)
    )


def detect_intents(text: str) -> Set[str]:
    """
    Detect query intent(s).
    Returns a set like {"fact", "news", "research"}.
    Ensures at least {"fact"} is always present.
    """
    if not text:
        return {"fact"}

    q = text.strip().lower()
    intents: Set[str] = set()

    # special-case UI command
    if q == "news":
        return {"news_section"}

    # --- Research ---
    if any(h in q for h in RESEARCH_HINTS):
        intents.add("research")

    # --- News ---
    year_hit = bool(re.search(r"\b20\d{2}\b", q))
    month_hit = any(m in q for m in MONTHS)
    recency_hit = any(h in q for h in RECENCY_HINTS)
    if "news" in q or year_hit or month_hit or recency_hit:
        intents.add("news")

    # --- Fact ---
    if any(re.search(p, q) for p in FACT_QUESTION_PATTERNS) or is_factual_question(q):
        intents.add("fact")

    # --- Fallback ---
    if not intents:
        intents.add("fact")

    return intents
