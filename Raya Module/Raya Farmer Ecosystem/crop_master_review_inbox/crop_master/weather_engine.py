import sys
from pathlib import Path

# Add crop_master root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from query_engine import rain_risk


SUPPORTED_EVENTS = ["rain"]


def assess_weather_event(crop, stage, event_type, intensity):
    """
    Converts a weather event into crop-stage impact
    using Crop Master truth only.
    """

    if event_type not in SUPPORTED_EVENTS:
        return f"Weather event '{event_type}' is not supported in Phase-1."

    if event_type == "rain" and intensity in ["heavy", "excess"]:
        return rain_risk(crop, stage)

    return f"No significant {event_type} impact defined for {crop} during {stage}."
