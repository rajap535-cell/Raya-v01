"""
RAYA — Weather Intelligence Layer
Phase-1 → Phase-2 Track-1 Compatible
Deterministic, Rule-based, Truth-only

Handles:
✔ Rain
✔ Temperature (high/low)
✔ Humidity
✔ Wind
"""

import json
from pathlib import Path
from query_engine import (
    diseases_at_stage,
    humidity_amplified_disease,
    get_stage_snapshot,
    get_water_requirement
)


# -------------------------------
# Helpers
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CROPS_DIR = BASE_DIR / "crops"


def load_crop(crop_name: str):
    crop_file = CROPS_DIR / f"{crop_name.lower()}.crop_master.json"
    if not crop_file.exists():
        raise FileNotFoundError(f"Crop Master not found for crop: {crop_name}")
    with open(crop_file, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================================================
# WEATHER EVENT FUNCTIONS (truth-based, no inference)
# =========================================================

def rain_risk(crop: str, stage: str, intensity: str | None):
    """
    Handles: light / moderate / heavy rain
    """
    data = load_crop(crop)

    stage_data = get_stage_snapshot(crop, stage)
    if isinstance(stage_data, str):
        return {"status": "invalid_stage", "message": stage_data}

    climate = data.get("climate_interactions", {}).get(stage, {})
    rain_data = climate.get("rainfall")

    if not rain_data:
        return {"status": "no_rain_data"}

    # Return deterministic packet
    return {
        "event": "rain",
        "intensity": intensity,
        "stage_impact": rain_data.get(intensity) or rain_data.get("general"),
        "stage_sensitive": stage_data.get("sensitivity", {}).get("rainfall"),
        "explanation": rain_data.get("explanation")
    }


def temperature_risk(crop: str, stage: str, intensity: str | None):
    """
    intensity ∈ {"high", "low"}
    """
    data = load_crop(crop)

    stage_data = get_stage_snapshot(crop, stage)
    if isinstance(stage_data, str):
        return {"status": "invalid_stage", "message": stage_data}

    climate = data.get("climate_interactions", {}).get(stage, {})
    key = "high_temperature" if intensity == "high" else "low_temperature"
    temp_data = climate.get(key)

    if not temp_data:
        return {"status": "no_temperature_data"}

    return {
        "event": "temperature",
        "intensity": intensity,
        "risk_level": temp_data.get("risk_level"),
        "effects": temp_data.get("effects"),
        "explanation": temp_data.get("explanation")
    }


def humidity_risk(crop: str, stage: str, _unused=None):
    """
    Focus: fungal amplification & leaf wetness logic
    """
    amplified = humidity_amplified_disease(crop, stage)
    if amplified:
        return {
            "event": "humidity",
            "amplified_diseases": amplified,
            "explanation": "High humidity favors fungal disease development"
        }
    return {"status": "no_humidity_effect"}


def wind_risk(crop: str, stage: str, intensity: str | None):
    data = load_crop(crop)

    stage_data = get_stage_snapshot(crop, stage)
    if isinstance(stage_data, str):
        return {"status": "invalid_stage", "message": stage_data}

    climate = data.get("climate_interactions", {}).get(stage, {})
    wind_data = climate.get("strong_wind")

    if not wind_data:
        return {"status": "no_wind_data"}

    return {
        "event": "wind",
        "risk_level": wind_data.get("risk_level"),
        "effects": wind_data.get("effects"),
        "explanation": wind_data.get("explanation")
    }


# =========================================================
# WEATHER ROUTER / GATEWAY
# =========================================================

SUPPORTED_EVENTS = {"rain", "temperature", "humidity", "wind"}


def assess_weather_event(crop: str, stage: str, event: str, intensity: str | None):
    e = (event or "").lower()
    if e not in SUPPORTED_EVENTS:
        return {
            "status": "unsupported_event",
            "event": event,
            "supported": list(SUPPORTED_EVENTS)
        }

    if e == "rain":
        return rain_risk(crop, stage, intensity)
    if e == "temperature":
        return temperature_risk(crop, stage, intensity)
    if e == "humidity":
        return humidity_risk(crop, stage, intensity)
    if e == "wind":
        return wind_risk(crop, stage, intensity)

    return {"status": "unknown_error"}


# Developer test harness
if __name__ == "__main__":
    print("\n-- TEST: Rain during Flowering --")
    print(assess_weather_event("rice", "flowering", "rain", "heavy"))

    print("\n-- TEST: High Temp during Vegetative --")
    print(assess_weather_event("rice", "vegetative", "temperature", "high"))

    print("\n-- TEST: Humidity Amplification --")
    print(assess_weather_event("rice", "flowering", "humidity", None))

    print("\n-- TEST: Wind --")
    print(assess_weather_event("rice", "flowering", "wind", None))
