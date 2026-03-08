import re
from .base_module import BaseMathModule
from .results import MathResult

def solve_percentage_growth(query: str):
    try:
        # Remove commas
        clean = query.replace(",", "")

        # Extract numbers
        numbers = re.findall(r"\d+\.?\d*", clean)

        if len(numbers) != 2:
            return None

        initial = float(numbers[0])
        final = float(numbers[1])

        if initial == 0:
            return None

        growth = ((final - initial) / initial) * 100

        return (
            f"Initial value: {initial:,.0f}\n"
            f"Final value: {final:,.0f}\n"
            f"Percentage growth: {growth:.2f}%"
        )

    except Exception:
        return None
    
# 🔥 NEW WRAPPER CLASS
class PercentageModule(BaseMathModule):

    def supports(self, query: str) -> bool:
        keywords = ["percent", "%", "increase", "decrease", "growth"]
        return any(k in query.lower() for k in keywords)

    def solve(self, query: str) -> MathResult:
        result = solve_percentage_growth(query)

        if result is None:
            return None

        return MathResult(
            value=None,
            explanation=result,
            metadata={"type": "percentage"}
        )