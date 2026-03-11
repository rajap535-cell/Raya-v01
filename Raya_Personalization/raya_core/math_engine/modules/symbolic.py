# raya_math_engine/modules/symbolic.py

import re
from sympy import symbols, integrate, diff, limit, simplify
from sympy.parsing.sympy_parser import parse_expr
from .base_module import BaseMathModule
from ..utils.normalizer import normalize_math_input

x = symbols("x")


class SymbolicMathModule(BaseMathModule):

    name = "symbolic_math"

    import re

    def supports(self, query: str) -> bool:

        pattern = r"[a-zA-Z]|[\^]|\(|\)|sin|cos|tan|sqrt|=|integrate|differentiate|solve|factor|expand"

        return bool(re.search(pattern, query))

    from sympy import symbols, diff, integrate, solve, simplify
    from sympy.parsing.sympy_parser import parse_expr

    def solve(self, query: str):

        try:

            query = normalize_math_input(query)

            x = symbols("x")

            # DIFFERENTIATION
            if query.startswith("differentiate"):
                expr = query.replace("differentiate", "").strip()
                expr = parse_expr(expr)
                return diff(expr, x)

            # INTEGRATION
            if query.startswith("integrate"):
                expr = query.replace("integrate", "").strip()
                expr = parse_expr(expr)
                return integrate(expr, x)

            # SOLVE EQUATION
            if "=" in query:

                left, right = query.split("=")

                eq = parse_expr(left) - parse_expr(right)

                solution = solve(eq, x)

                return solution

            # DEFAULT: simplify expression
            expr = parse_expr(query)

            return simplify(expr)

        except Exception as e:

            print("[Symbolic Solver Error]", e)

            return None