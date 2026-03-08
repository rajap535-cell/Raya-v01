from sympy import symbols, diff, integrate, limit, sympify
from .base_module import BaseMathModule


class CalculusModule(BaseMathModule):

    name = "calculus"

    def supports(self, query: str) -> bool:
        q = query.lower()
        return any(k in q for k in ["integrate", "differentiate", "limit"])

    def solve(self, query: str):

        x = symbols("x")

        try:

            if "integrate" in query:
                expr = query.replace("integrate", "").strip()
                result = integrate(sympify(expr), x)

            elif "differentiate" in query:
                expr = query.replace("differentiate", "").strip()
                result = diff(sympify(expr), x)

            elif "limit" in query:
                expr = query.replace("limit", "").strip()
                result = limit(sympify(expr), x, 0)

            else:
                return None

            return {"result": result}

        except Exception as e:
            print("[CalculusModule Error]", e)
            return None