import re
from .percentage import solve_percentage_growth
from .arithmetic import solve_arithmetic
from .equations import solve_equation
from .symbolic import solve_symbolic
from .units import solve_units


def solve_math(query: str):
    q = query.lower().strip()

    # 1️⃣ Percentage Growth
    percent_result = solve_percentage_growth(query)
    if percent_result:
        print("[Stage: Math Engine] 📊 Percentage calculation")
        return percent_result
    
    # --- Unit conversion ---
    if detect_unit_conversion(q):
        return solve_units(query)

    # --- Equation solving ---
    if detect_equation(q):
        return solve_equation(query)

    # --- Symbolic manipulation ---
    if detect_symbolic(q):
        return solve_symbolic(query)

    # --- Arithmetic ---
    return solve_arithmetic(query)


# -----------------------------
# Detection Helpers
# -----------------------------

def detect_equation(q: str) -> bool:
    return "=" in q


def detect_symbolic(q: str) -> bool:
    keywords = ["expand", "factor", "simplify", "derive", "differentiate"]
    return any(k in q for k in keywords)


def detect_unit_conversion(q: str) -> bool:
    return " to " in q and any(unit in q for unit in [
        "km", "meter", "mile", "kg", "gram", "celsius",
        "fahrenheit", "hour", "minute", "second"
    ])