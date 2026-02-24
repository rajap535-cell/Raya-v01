import re

def solve_percentage_growth(query: str):
    try:
        # Remove commas
        clean = query.replace(",", "")

        # Extract numbers
        numbers = re.findall(r"\d+\.?\d*", clean)

        if len(numbers) != 2:
            return None

        initial = float(numbers[0])
        final = float(numbers[1])

        if initial == 0:
            return None

        growth = ((final - initial) / initial) * 100

        return (
            f"Initial value: {initial:,.0f}\n"
            f"Final value: {final:,.0f}\n"
            f"Percentage growth: {growth:.2f}%"
        )

    except Exception:
        return None