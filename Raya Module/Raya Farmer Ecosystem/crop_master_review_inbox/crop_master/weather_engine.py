"""
RAYA Weather Engine
Track-1 Compatible
(UPDATED SCHEMA — FLATTENED FIELDS)
"""

def get_weather_risk(crop, stage, state, district):

    return {
        "status": "success",
        "current": {
            "temperature_avg": 28,
            "temperature_min": 22,
            "temperature_max": 34,
            "humidity_percent": 75,
            "rainfall_mm": 5,
            "condition": "Partly Cloudy"
        },
        "risk": {
            "risk_level": "High",
            "risk_type": "Excess Rainfall",
            "impact": [
                "Poor pollination",
                "Spikelet sterility"
            ]
        },
        "forecast": {
            "expected_event": "Heavy Rain",
            "forecast_probability": "70%"
        }
    }