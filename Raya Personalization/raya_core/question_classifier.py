# raya_core/question_classifier.py

from enum import Enum, auto


class QuestionType(Enum):
    FACT_DEFINITION = auto()
    HISTORICAL = auto()
    EXPLANATION = auto()
    OPEN_ENDED = auto()
    OPINION = auto()
    NEWS = auto()
    CONVERSATIONAL = auto()
    UNKNOWN = auto()


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

    # Explanation (VERY IMPORTANT)
    if (
        any(q.startswith(p) for p in EXPLANATION_PREFIXES)
        or q.startswith("why")
        or q.startswith("how")
    ):
        return QuestionType.EXPLANATION

    # Opinion
    if any(q.startswith(p) for p in OPINION_PREFIXES):
        return QuestionType.OPINION

    return QuestionType.UNKNOWN