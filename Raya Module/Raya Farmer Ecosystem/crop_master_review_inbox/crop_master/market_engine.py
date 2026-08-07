"""
RAYA — Market Intelligence Layer
(PRODUCTION READY — FINAL LOCKED VERSION)

Purpose:
Provide structured market snapshot for crops
based on state and district.

Design Principles
-----------------
• Deterministic
• Read-only
• Structured responses only
• No ML
• No prediction
"""

# -------------------------------------------------
# Imports
# -------------------------------------------------

import json

from pathlib import Path
from datetime import datetime, timezone


# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MARKET_DIR = BASE_DIR / "data" / "market_data"


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _normalize(text: str) -> str:

    return text.strip().lower()


# -------------------------------------------------
# Timezone-Aware Timestamp (UPDATED)
# -------------------------------------------------

def _timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()


# -------------------------------------------------
# Market Loader
# -------------------------------------------------

def load_market_file(
    state: str,
    district: str
):

    filename = (
        f"{_normalize(state)}_"
        f"{_normalize(district)}_prices.json"
    )

    file_path = MARKET_DIR / filename

    if not file_path.exists():

        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# -------------------------------------------------
# Public API
# -------------------------------------------------

def get_market_price(
    crop: str,
    state: str,
    district: str
):
    """
    Return structured market snapshot.
    """

    data = load_market_file(
        state,
        district
    )

    # -------------------------------------------------
    # Missing Market File
    # -------------------------------------------------

    if not data:

        return {

            "status": "no_price_data",

            "message": (
                f"No market data for "
                f"{district}, {state}"
            ),

            "location": {
                "state": state.title(),
                "district": district.title()
            },

            "meta": {
                "source": "market_engine",
                "last_updated": _timestamp()
            }
        }

    crop_key = _normalize(crop)

    crop_data = data.get(crop_key)

    # -------------------------------------------------
    # Missing Crop Data
    # -------------------------------------------------

    if not crop_data:

        return {

            "status": "crop_not_listed",

            "message": (
                f"No data available "
                f"for crop '{crop}'"
            ),

            "location": {
                "state": state.title(),
                "district": district.title()
            },

            "crop": crop_key,

            "meta": {
                "source": "market_engine",
                "last_updated": _timestamp()
            }
        }

    # -------------------------------------------------
    # Final Structured Response
    # -------------------------------------------------

    return {

        "status": "success",

        "location": {

            "state": state.title(),

            "district": district.title(),

            "mandi": crop_data.get("mandi")
        },

        "crop": crop_key,

        # ---------------------------------------------
        # Price
        # ---------------------------------------------

        "price": {

            "modal": crop_data.get(
                "modal_price"
            ),

            "min": crop_data.get(
                "min_price"
            ),

            "max": crop_data.get(
                "max_price"
            ),

            "currency": "INR/quintal"
        },

        # ---------------------------------------------
        # Arrival
        # ---------------------------------------------

        "arrival": {

            "quantity": crop_data.get(
                "arrival_qty"
            ),

            "unit": "quintal"
        },

        # ---------------------------------------------
        # Trend
        # ---------------------------------------------

        "trend": {

            "direction": crop_data.get(
                "trend_direction"
            ),

            "change_percent": crop_data.get(
                "trend_change_percent"
            ),

            "window": "7d"
        },

        # ---------------------------------------------
        # Forecast
        # ---------------------------------------------

        "forecast": {

            "next_7_days": crop_data.get(
                "forecast"
            ),

            "confidence": crop_data.get(
                "forecast_confidence"
            )
        },

        # ---------------------------------------------
        # Metadata
        # ---------------------------------------------

        "meta": {

            "source": crop_data.get(
                "source",
                "mock"
            ),

            "last_updated": crop_data.get(
                "last_updated",
                _timestamp()
            )
        }
    }


# -------------------------------------------------
# Backward Compatibility Wrapper
# -------------------------------------------------

def get_market_price_legacy(
    crop: str,
    state: str,
    district: str
):
    """
    Legacy compatibility wrapper.
    """

    result = get_market_price(
        crop,
        state,
        district
    )

    if result.get("status") != "success":

        return result

    return {

        "status": "success",

        "crop": result["crop"],

        "mandi": result["location"]["mandi"],

        "min_price": result["price"]["min"],

        "max_price": result["price"]["max"],

        "modal_price": result["price"]["modal"]
    }


# -------------------------------------------------
# Test Harness (ONLY TEST BLOCK KEPT)
# -------------------------------------------------

if __name__ == "__main__":

    print("\n🚀 Running Market Engine Test...\n")

    result = get_market_price(
        crop="rice",
        state="Karnataka",
        district="Mandya"
    )

    print("\n--- MARKET OUTPUT ---\n")

    print(
        json.dumps(
            result,
            indent=2
        )
    )