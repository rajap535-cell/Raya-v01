"""
RAYA Phase-2 — Track-1 Negative Validation Tests
Tests behavior when inputs are missing, invalid, or unsupported.

Goal:
- System must fail LOUDLY and CLEARLY.
- No silent fallback.
- No guessing or inference.
"""

from farmer_search_engine import farmer_search, format_for_farmer


print("\n=== NEGATIVE VALIDATION TESTS ===")


# --------------------------------------------------
# 1️⃣ Invalid Crop Name
# --------------------------------------------------
print("\n-- Invalid Crop Test --")
bad_crop = farmer_search(
    state="Karnataka",
    district="Mandya",
    crop="UNKNOWNCROP",
    stage="flowering"
)
print("Result:", bad_crop)


# --------------------------------------------------
# 2️⃣ Invalid Stage Name
# --------------------------------------------------
print("\n-- Invalid Stage Test --")
bad_stage = farmer_search(
    state="Karnataka",
    district="Mandya",
    crop="rice",
    stage="UNKNOWNSTAGE"
)
print("Result:", bad_stage)


# --------------------------------------------------
# 3️⃣ Missing Market Data
# --------------------------------------------------
print("\n-- Missing Market Data Test --")
missing_market = farmer_search(
    state="UnknownState",
    district="UnknownDistrict",
    crop="rice",
    stage="flowering"
)
print("Result:", missing_market["market"])


# --------------------------------------------------
# 4️⃣ Unsupported Weather Event
# --------------------------------------------------
print("\n-- Unsupported Weather Test --")
unsupported_weather = farmer_search(
    state="Karnataka",
    district="Mandya",
    crop="rice",
    stage="flowering",
    weather_event="hailstorm"  # not defined in Track-1
)
print("Result:", unsupported_weather["weather"])


# --------------------------------------------------
# 5️⃣ Missing Stage (incomplete input)
# --------------------------------------------------
print("\n-- Missing Stage Test --")
try:
    no_stage = farmer_search(
        state="Karnataka",
        district="Mandya",
        crop="rice",
        stage=None
    )
    print("Result:", no_stage)
except Exception as e:
    print("Exception thrown (acceptable):", e)


# --------------------------------------------------
# 6️⃣ Formatting layer should NOT hallucinate
# --------------------------------------------------
print("\n-- Format Validation (no hallucination) --")
formatted = format_for_farmer(missing_market)
print("Formatted Output:")
print(formatted)
