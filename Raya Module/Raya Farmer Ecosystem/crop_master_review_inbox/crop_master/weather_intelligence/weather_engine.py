"""
RAYA — Weather Intelligence Layer
Phase-1 (LOCKED)

Purpose:
Map weather events to stage-specific impacts
using ONLY Crop Master truth.

NO inference
NO ML
NO disease selection
"""

import json
from pathlib import Path


# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CROPS_DIR = BASE_DIR / "crops"


# -------------------------------------------------
# Loader
# -------------------------------------------------
def load_crop(crop_name: str):
    crop_file = CROPS_DIR / f"{crop_name.lower()}.crop_master.json"
    if not crop_file.exists():
        return None
    with open(crop_file, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------------------------
# Rain (Phase-1: excess rainfall only)
# -------------------------------------------------
def rain_risk(crop: str, stage: str, _intensity=None):
    data = load_crop(crop)
    if not data:
        return {"status": "crop_not_found", "crop": crop}

    climate = data.get("climate_interactions", {}).get(stage)
    if not climate:
        return {"status": "no_climate_data", "stage": stage}

    rain = climate.get("excess_rainfall")
    if not rain:
        return {"status": "no_rain_risk"}

    return {
        "event": "rain",
        "type": "excess_rainfall",
        "risk_level": rain.get("risk_level"),
        "effects": rain.get("effects"),
        "explanation": rain.get("explanation")
    }


# -------------------------------------------------
# Temperature (High / Low)
# -------------------------------------------------
def temperature_risk(crop: str, stage: str, intensity: str):
    data = load_crop(crop)
    if not data:
        return {"status": "crop_not_found", "crop": crop}

    climate = data.get("climate_interactions", {}).get(stage)
    if not climate:
        return {"status": "no_climate_data", "stage": stage}

    if intensity == "high":
        temp = climate.get("high_temperature")
    elif intensity == "low":
        temp = climate.get("low_temperature")
    else:
        return {"status": "invalid_temperature_type", "value": intensity}

    if not temp:
        return {"status": "no_temperature_risk"}

    return {
        "event": "temperature",
        "type": intensity,
        "risk_level": temp.get("risk_level"),
        "effects": temp.get("effects"),
        "explanation": temp.get("explanation")
    }


# -------------------------------------------------
# Humidity (Phase-1: generic risk only)
# -------------------------------------------------
def humidity_risk(crop: str, stage: str, _unused=None):
    data = load_crop(crop)
    if not data:
        return {"status": "crop_not_found", "crop": crop}

    climate = data.get("climate_interactions", {}).get(stage)
    if not climate:
        return {"status": "no_climate_data", "stage": stage}

    humidity = climate.get("high_humidity")
    if not humidity:
        return {"status": "no_humidity_risk"}

    return {
        "event": "humidity",
        "risk_level": humidity.get("risk_level"),
        "effects": humidity.get("effects"),
        "explanation": humidity.get(
            "explanation",
            "High humidity increases disease pressure"
        )
    }


# -------------------------------------------------
# Wind
# -------------------------------------------------
def wind_risk(crop: str, stage: str, _intensity=None):
    data = load_crop(crop)
    if not data:
        return {"status": "crop_not_found", "crop": crop}

    climate = data.get("climate_interactions", {}).get(stage)
    if not climate:
        return {"status": "no_climate_data", "stage": stage}

    wind = climate.get("strong_winds")
    if not wind:
        return {"status": "no_wind_risk"}

    return {
        "event": "wind",
        "risk_level": wind.get("risk_level"),
        "effects": wind.get("effects"),
        "explanation": wind.get("explanation")
    }


# -------------------------------------------------
# Router (single entry point)
# -------------------------------------------------
SUPPORTED_EVENTS = {"rain", "temperature", "humidity", "wind"}


def assess_weather_event(
    crop: str,
    stage: str,
    event: str,
    intensity: str | None = None
):
    event = (event or "").lower()

    if event not in SUPPORTED_EVENTS:
        return {
            "status": "unsupported_event",
            "event": event,
            "supported": list(SUPPORTED_EVENTS)
        }

    if event == "rain":
        return rain_risk(crop, stage, intensity)
    if event == "temperature":
        return temperature_risk(crop, stage, intensity)
    if event == "humidity":
        return humidity_risk(crop, stage)
    if event == "wind":
        return wind_risk(crop, stage)

    return {"status": "unknown_error"}
