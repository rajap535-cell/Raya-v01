from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

transformations = standard_transformations + (
    implicit_multiplication_application,
)

from sympy import Eq, solve
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

transformations = standard_transformations + (
    implicit_multiplication_application,
)

def solve_equation(query: str):
    try:
        if "=" not in query:
            return None

        left_str, right_str = query.split("=", 1)

        left_str = left_str.strip().replace("^", "**")
        right_str = right_str.strip().replace("^", "**")

        if not left_str or not right_str:
            return None  # incomplete equation

        left = parse_expr(left_str, transformations=transformations)
        right = parse_expr(right_str, transformations=transformations)

        variables = list(left.free_symbols.union(right.free_symbols))

        if not variables:
            return None

        solution = solve(Eq(left, right), variables[0])

        return f"Solution for {variables[0]}: {solution}"

    except Exception as e:
        print(f"[Equation Solver Error]: {e}")  # debug visibility
        return None

def detect_variable(expr: str):
    match = re.search(r"[a-zA-Z]", expr)
    return match.group(0) if match else None


def normalize_expression(text: str):
    text = text.replace("^", "**")
    return text