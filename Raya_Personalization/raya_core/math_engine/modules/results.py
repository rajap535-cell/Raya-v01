class MathResult:
    def __init__(self, value=None, expression=None, explanation=None, metadata=None):
        self.value = value
        self.expression = expression
        self.explanation = explanation
        self.metadata = metadata or {}

    def __str__(self):
        if self.explanation:
            return self.explanation
        if self.expression:
            return f"Result: {self.expression}"
        return str(self.value)