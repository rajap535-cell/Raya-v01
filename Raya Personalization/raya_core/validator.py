import re

def is_future_query(query: str) -> bool:
    return bool(re.search(r"\b20(2[4-9]|3\d)\b", query))


def requires_number(query: str) -> bool:
    keywords = [
        "how many", "distance", "gdp", "population",
        "year", "when", "rate", "percentage"
    ]
    q = query.lower()
    return any(k in q for k in keywords)


def has_number(text: str) -> bool:
    return bool(re.search(r"\d", text))


def is_generic_wikipedia_answer(text: str) -> bool:
    # Wikipedia articles that explain topic instead of answering
    bad_starts = [
        "the economy of",
        "the human brain is",
        "there is evidence that",
        "is an astronomical",
    ]
    t = text.lower().strip()
    return any(t.startswith(b) for b in bad_starts)


def validate_answer(query: str, source: str, text: str) -> bool:
    """
    Returns True if answer is acceptable, False if it should be rejected
    """

    if not text or len(text.strip()) < 30:
        return False

    # Wikipedia should never answer future questions
    if source == "wikipedia" and is_future_query(query):
        return False

    # Numeric question but no numbers
    if requires_number(query) and not has_number(text):
        return False

    # Generic wiki dump instead of direct answer
    if source == "wikipedia" and is_generic_wikipedia_answer(text):
        return False

    # Local LLM timeout or error
    if text.startswith("[local error]"):
        return False

    return True
