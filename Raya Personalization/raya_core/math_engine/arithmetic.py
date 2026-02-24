from sympy import sympify
from sympy.core.sympify import SympifyError


from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from sympy import simplify

transformations = standard_transformations + (
    implicit_multiplication_application,
)

def solve_arithmetic(query: str):
    try:
        expression = normalize_expression(query)
        result = parse_expr(expression, transformations=transformations)
        result = simplify(result)
        return f"Result: {result}"
    except Exception:
        return None


def normalize_expression(text: str) -> str:
    text = text.lower()

    replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiplied by": "*",
        "divided by": "/",
        "^": "**",
    }

    for word, symbol in replacements.items():
        text = text.replace(word, symbol)

    return text