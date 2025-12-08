# raya_core/base.py

class EngineResult:
    def __init__(self, text: str, sources=None, confidence: float = 0.8, meta=None):
        """
        A unified result object returned by Raya's brain engine.
        :param text: The main response text
        :param sources: Dict or string representing the data source(s)
        :param confidence: Confidence score (0.0–1.0)
        :param meta: Additional metadata or context
        """
        self.text = text
        self.sources = sources or {}
        self.confidence = confidence
        self.meta = meta or {}

    def __repr__(self):
        return f"EngineResult(text={self.text[:40]!r}..., confidence={self.confidence}, source={self.sources})"
