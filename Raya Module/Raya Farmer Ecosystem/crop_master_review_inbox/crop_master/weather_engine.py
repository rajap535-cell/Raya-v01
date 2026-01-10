import sys
from pathlib import Path

# -------------------------------------------------
# Ensure crop_master root is in Python path
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from query_engine import (
    rain_risk,
    temperature_risk,
    humidity_risk,
    wind_risk
)

# -------------------------------------------------
# Supported weather signals (Phase-1)
# -------------------------------------------------
SUPPORTED_EVENTS = ["rain", "temperature", "humidity", "wind"]


def assess_weather_event(crop, stage, event_type, intensity):
    """
    Routes a weather event to Crop Master truth.

    Parameters:
        crop (str): crop name (e.g., 'rice')
        stage (str): growth stage (e.g., 'Flowering')
        event_type (str): rain / temperature / humidity / wind
        intensity (str): signal strength (e.g., heavy, high, low, strong)

    Returns:
        Deterministic, explainable impact derived from Crop Master
    """

    event_type = event_type.lower()
    intensity = intensity.lower()

    # -----------------------------
    # Rainfall
    # -----------------------------
    if event_type == "rain" and intensity in ["heavy", "excess"]:
        return rain_risk(crop, stage)

    # -----------------------------
    # Temperature (heat / cold)
    # -----------------------------
    if event_type == "temperature":
        temp_map = {
            "low": 20,
            "cold": 18,
            "moderate": 30,
            "high": 40,
            "heat": 42
        }
        temp_value = temp_map.get(intensity)
        if temp_value:
            return temperature_risk(temp_value)

    # -----------------------------
    # Humidity (disease amplification)
    # -----------------------------
    if event_type == "humidity":
        humidity_map = {
            "low": 50,
            "moderate": 70,
            "high": 90
        }
        humidity_value = humidity_map.get(intensity)
        if humidity_value:
            return humidity_risk(humidity_value)

    # -----------------------------
    # Wind (physical damage)
    # -----------------------------
    if event_type == "wind":
        wind_map = {
            "low": 10,
            "moderate": 25,
            "strong": 45,
            "high": 50
        }
        wind_value = wind_map.get(intensity)
        if wind_value:
            return wind_risk(wind_value)

    # -----------------------------
    # Default fallback (Phase-1 safe)
    # -----------------------------
    if event_type not in SUPPORTED_EVENTS:
        return f"Weather event '{event_type}' is not supported in Phase-1."

    return f"No significant {event_type} impact defined for {crop} during {stage}."
