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
    pi
)
from sympy.parsing.sympy_parser import parse_expr
from .base_module import BaseMathModule
from ..utils.normalizer import normalize_math_input


# =========================
# VARIABLES
# =========================
x, y, z = symbols("x y z")

allowed_symbols = {
    "x": x,
    "y": y,
    "z": z,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "log": log,
    "sqrt": sqrt,
    "pi": pi,
}


class SymbolicMathModule(BaseMathModule):

    name = "symbolic_math"

    def supports(self, query: str) -> bool:
        pattern = r"[a-zA-Z]|\^|\(|\)|=|sin|cos|tan|sqrt|log|integrate|differentiate|solve|factor|expand|limit|simplify"
        return bool(re.search(pattern, query))

    def solve(self, query: str):

        try:
            # =========================
            # STEP 0: NORMALIZATION
            # =========================
            query = normalize_math_input(query)

            # =========================
            # STEP 1: DEGREE HANDLING
            # =========================
            def convert_degrees(q):
                # sin(90) OR sin(90°)
                def repl(match):
                    func = match.group(1)
                    val = match.group(2)
                    return f"{func}(({val})*pi/180)"
                return re.sub(r"(sin|cos|tan)\((\d+)(°?)\)", repl, q)

            query = convert_degrees(query)

            # =========================
            # STEP 2: OPERATIONS
            # =========================

            # DIFFERENTIATE
            if query.startswith("differentiate"):
                expr = query.replace("differentiate", "").strip()
                expr = parse_expr(expr, local_dict=allowed_symbols)
                return simplify(diff(expr))

            # INTEGRATE
            if query.startswith("integrate"):
                expr = query.replace("integrate", "").strip()
                expr = parse_expr(expr, local_dict=allowed_symbols)
                return simplify(integrate(expr))

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

            # =========================
            # STEP 3: EQUATIONS (ROBUST)
            # =========================
            if query.startswith("solve") or "=" in query:

                equation = query.replace("solve", "").strip()

                if "=" not in equation:
                    return "Invalid equation"

                left, right = equation.split("=")

                left_expr = parse_expr(left, local_dict=allowed_symbols)
                right_expr = parse_expr(right, local_dict=allowed_symbols)

                eq = left_expr - right_expr

                variables = list(eq.free_symbols)

                if not variables:
                    return "No variable found"

                var = variables[0]

                solution = solve(eq, var)

                return solution if solution else None

            # =========================
            # STEP 4: DEFAULT EXPRESSION
            # =========================
            expr = parse_expr(query, local_dict=allowed_symbols)

            result = simplify(expr)

            if result.is_number:
                return result.evalf()

            return result

        except Exception as e:
            print("[Symbolic Solver Error]", e)
            return "Invalid mathematical expression"