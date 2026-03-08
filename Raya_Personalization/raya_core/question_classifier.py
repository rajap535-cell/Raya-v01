# raya_core/question_classifier.py

from enum import Enum, auto
import re


class QuestionType(Enum):
    MATH = auto()
    FACT_DEFINITION = auto()
    HISTORICAL = auto()
    EXPLANATION = auto()
    OPEN_ENDED = auto()
    OPINION = auto()
    NEWS = auto()
    CONVERSATIONAL = auto()
    UNKNOWN = auto()


# --- Math detection ---
MATH_PATTERN = re.compile(
    r"""
    \d+[\d,]*\s*[\+\-\*/\^=]        |  # arithmetic like 2+2
    \b(equal to|percentage|percent|growth|rate)\b |
    \b(calculate|how much|solve)\b  |
    \b(square root|root of)\b       |
    \b(sin|cos|tan|sqrt|log|ln)\s*\( |
    \d+\s*\(                        |  # implicit multiplication 2(3+4)
    \([0-9\+\-\*/\^\s]+\)           # parenthesis math
    """,
    re.VERBOSE,
)

FACT_PREFIXES = (
    "what is", "what are", "define", "meaning of"
)

HISTORICAL_PREFIXES = (
    "who invented", "who discovered", "when did",
    "who was", "when was"
)

EXPLANATION_PREFIXES = (
    "explain", "how does", "how do", "why does", "why is"
)

NEWS_PREFIXES = (
    "news", "latest news", "headlines", "current news"
)

OPINION_PREFIXES = (
    "best", "better", "should i", "which is better",
    "which is best"
)

CONVERSATIONAL_PREFIXES = (
    "hi", "hello", "who are you", "how are you"
)


def classify_question(query: str) -> QuestionType:
    q = query.lower().strip()

    # 🔥 MATH FIRST (highest priority)
    if MATH_PATTERN.search(q):
        return QuestionType.MATH

    # Conversational
    if any(q.startswith(p) for p in CONVERSATIONAL_PREFIXES):
        return QuestionType.CONVERSATIONAL

    # News
    if any(p in q for p in NEWS_PREFIXES):
        return QuestionType.NEWS

    # Historical
    if any(q.startswith(p) for p in HISTORICAL_PREFIXES):
        return QuestionType.HISTORICAL

    # Fact definition
    if any(q.startswith(p) for p in FACT_PREFIXES):
        return QuestionType.FACT_DEFINITION

    # Explanation
    if (
        any(q.startswith(p) for p in EXPLANATION_PREFIXES)
        or q.startswith("why")
        or q.startswith("how")
    ):
        return QuestionType.EXPLANATION

    # Opinion
    if any(q.startswith(p) for p in OPINION_PREFIXES):
        return QuestionType.OPINION

     

    if re.search(symbolic_pattern, query.replace(" ", "")):
        return QuestionType.MATH
    
    symbolic_pattern = r"[a-zA-Z]+\s*[\+\-\*/\^=]|\d+[a-zA-Z]"
   
    if "%" in query or "percent" in query.lower():
        return QuestionType.MATH

    if re.search(r"\d+\s+to\s+\d+", query.lower()):
        return QuestionType.MATH

    return QuestionType.UNKNOWN