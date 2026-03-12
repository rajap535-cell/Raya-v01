"""
RAYA — Market Intelligence Layer
Phase-1 (LOCKED)

Purpose:
Provide market price snapshot for crops
based on state and district.

Design Principles:
• Deterministic
• Read-only
• Structured responses only
• No ML / No prediction
"""

import json
from pathlib import Path


# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MARKET_DIR = BASE_DIR / "market_data"


# -------------------------------------------------
# Market Loader
# -------------------------------------------------
def load_market_file(state: str, district: str):

    filename = f"{state.lower()}_{district.lower()}_prices.json"

    file_path = MARKET_DIR / filename

    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------------------------
# Public API
# -------------------------------------------------
def get_market_price(crop: str, state: str, district: str):
    """
    Return market snapshot for crop.
    """

    data = load_market_file(state, district)

    if not data:
        return {
            "status": "no_price_data",
            "message": f"No market price data for {district}, {state}"
        }

    crop_data = data.get(crop.lower())

    if not crop_data:
        return {
            "status": "crop_not_listed",
            "message": f"No price data for {crop} in {district}"
        }

    return {
        "status": "success",
        "crop": crop,
        "mandi": crop_data.get("mandi"),
        "min_price": crop_data.get("min_price"),
        "max_price": crop_data.get("max_price"),
        "modal_price": crop_data.get("modal_price")
    }


# -------------------------------------------------
# Developer Test Harness
# -------------------------------------------------
if __name__ == "__main__":

    result = get_market_price(
        crop="rice",
        state="Karnataka",
        district="Mandya"
    )

    print("\n--- MARKET SNAPSHOT ---")
    print(result)