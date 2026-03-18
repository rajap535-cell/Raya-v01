# raya_math_engine/modules/symbolic.py

import re
from sympy import (
    symbols,
    diff,
    integrate,
    solve,
    simplify,
    expand,
    factor,
    limit,
    sin,
    cos,
    tan,
    log,
    sqrt,
)
from sympy.parsing.sympy_parser import parse_expr
from .base_module import BaseMathModule
from ..utils.normalizer import normalize_math_input


x = symbols("x")

# Allowed math symbols for parser
allowed_symbols = {
    "x": x,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "log": log,
    "sqrt": sqrt,
}


class SymbolicMathModule(BaseMathModule):

    name = "symbolic_math"

    def supports(self, query: str) -> bool:

        pattern = r"[a-zA-Z]|\^|\(|\)|sin|cos|tan|sqrt|=|integrate|differentiate|solve|factor|expand|limit|simplify"

        return bool(re.search(pattern, query))

    def solve(self, query: str):

        try:

            query = normalize_math_input(query)

            # DIFFERENTIATION
            if query.startswith("differentiate"):
                expr = query.replace("differentiate", "").strip()
                expr = parse_expr(expr, local_dict=allowed_symbols)
                return diff(expr, x)

            # INTEGRATION
            if query.startswith("integrate"):
                expr = query.replace("integrate", "").strip()
                expr = parse_expr(expr, local_dict=allowed_symbols)
                return integrate(expr, x)

            # EXPAND
            if query.startswith("expand"):
                expr = query.replace("expand", "").strip()
                expr = parse_expr(expr, local_dict=allowed_symbols)
                return expand(expr)

            # FACTOR
            if query.startswith("factor"):
                expr = query.replace("factor", "").strip()
                expr = parse_expr(expr, local_dict=allowed_symbols)
                return factor(expr)

            # LIMIT
            if query.startswith("limit"):
                expr = query.replace("limit", "").strip()
                expr = parse_expr(expr, local_dict=allowed_symbols)
                return limit(expr, x, 0)

            # SIMPLIFY
            if query.startswith("simplify"):
                expr = query.replace("simplify", "").strip()
                expr = parse_expr(expr, local_dict=allowed_symbols)
                return simplify(expr)

            # EQUATION SOLVING
            if query.startswith("solve") or "=" in query:

                equation = query.replace("solve", "").strip()

                left, right = equation.split("=")

                left_expr = parse_expr(left, local_dict=allowed_symbols)
                right_expr = parse_expr(right, local_dict=allowed_symbols)

                eq = left_expr - right_expr

                solution = solve(eq, x)

                return solution if solution else None

            # DEFAULT: simplify expression
            expr = parse_expr(query, local_dict=allowed_symbols)

            result = simplify(expr)

            # evaluate numeric expressions
            if result.is_number:
                return result.evalf()

            return result

        except Exception as e:

            print("[Symbolic Solver Error]", e)

            return "Invalid mathematical expression"