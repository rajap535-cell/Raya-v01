# raya_math_engine/utils/normalizer.py

import re


def normalize_math_input(text: str) -> str:
    """
    Convert human-style math into SymPy-compatible expressions.
    """

    q = text.lower().strip()

    # convert ^ to **
    q = q.replace("^", "**")

    # sqrt16 → sqrt(16)
    q = re.sub(r"\bsqrt\s*([0-9]+)", r"sqrt(\1)", q)

    # remove extra spaces
    q = re.sub(r"\s+", " ", q)

    # implicit multiplication: x2 → x*2
    q = re.sub(r"([a-z])(\d)", r"\1*\2", q)

    # implicit multiplication: 5x → 5*x
    q = re.sub(r"(\d)([a-z])", r"\1*\2", q)

    # implicit multiplication: 2(x+1) → 2*(x+1)
    q = re.sub(r"(\d)\(", r"\1*(", q)

    # sinx → sin(x)
    q = re.sub(r"(sin|cos|tan|log|ln)\s*([a-z])", r"\1(\2)", q)

    # remove spaces inside function calls
    q = re.sub(r"(sin|cos|tan|sqrt|log|ln)\s+\(", r"\1(", q)

    return q