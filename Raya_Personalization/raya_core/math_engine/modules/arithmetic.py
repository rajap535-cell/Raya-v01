# modules/arithmetic.py

import re
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from sympy import simplify
from .base_module import BaseMathModule

transformations = standard_transformations + (
    implicit_multiplication_application,
)


class ArithmeticModule(BaseMathModule):

    name = "arithmetic"

    def supports(self, query: str) -> bool:
        pattern = r"^[0-9a-z\.\+\-\*/\^\(\)\s]+$"
        return bool(re.match(pattern, query))
    
    def solve(self, query: str):

        # call the real solver
        result = solve_arithmetic(query)

        if result is None:
            return None

        return {"result": result}


def solve_arithmetic(query: str):

    try:
        expression = normalize_expression(query)

        result = parse_expr(
            expression,
            transformations=transformations
        )

        result = simplify(result)

        return float(result)

    except Exception as e:
        print("[Arithmetic Solver Error]", e)
        return None


def normalize_expression(text: str):

    text = text.lower()

    replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiplied by": "*",
        "divided by": "/",
        "^": "**",
        "sqrt": "sqrt",
        "sin": "sin",
        "cos": "cos",
        "tan": "tan",
    }

    for word, symbol in replacements.items():
        text = text.replace(word, symbol)

    return text