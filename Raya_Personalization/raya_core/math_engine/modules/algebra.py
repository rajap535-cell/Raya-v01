from sympy import symbols, Eq, solve
import re
from .base_module import BaseMathModule


class AlgebraModule(BaseMathModule):

    name = "algebra"

    def supports(self, query: str) -> bool:
        q = query.lower()
        return "solve" in q or "=" in q and any(c.isalpha() for c in q)

    def solve(self, query: str):

        try:
            expr = query.lower().replace("solve", "").strip()

            if "=" in expr:
                left, right = expr.split("=")
                x = symbols("x")

                equation = Eq(eval(left), eval(right))
                result = solve(equation)

            else:
                x = symbols("x")
                result = solve(expr)

            return {"result": result}

        except Exception as e:
            print("[AlgebraModule Error]", e)
            return None