from .results import MathResult

class BaseMathModule:
    def supports(self, query: str) -> bool:
        raise NotImplementedError

    def solve(self, query: str) -> MathResult:
        raise NotImplementedError