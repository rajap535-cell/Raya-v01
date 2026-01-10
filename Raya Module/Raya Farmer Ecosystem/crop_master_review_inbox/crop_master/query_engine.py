import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CROPS_DIR = BASE_DIR / "crops"


def load_crop(crop_name):
    crop_file = CROPS_DIR / f"{crop_name.lower()}.crop_master.json"
    if not crop_file.exists():
        raise FileNotFoundError(f"Crop Master not found for crop: {crop_name}")

    with open(crop_file, "r", encoding="utf-8") as f:
        return json.load(f)


# 1️⃣ WEATHER IMPACT BY STAGE
def rain_risk(crop_name, stage):
    crop = load_crop(crop_name)

    stage_data = crop["growth_lifecycle"]["stages"].get(stage)
    climate_data = crop["climate_interactions"].get(stage, {})
    rain_data = climate_data.get("excess_rainfall")

    if not stage_data:
        return f"Stage '{stage}' is not defined for {crop_name}."

    if not rain_data:
        return f"No specific rainfall risk defined for {crop_name} during {stage}."

    summary = crop["stage_risk_summary"].get(stage, "No summary available.")

    return {
        "stage_sensitivity": stage_data["sensitivity"],
        "rain_risk_level": rain_data["risk_level"],
        "effects": rain_data["effects"],
        "explanation": summary
    }


# 2️⃣ DISEASE RELEVANCE BY STAGE
def diseases_at_stage(crop_name, stage):
    crop = load_crop(crop_name)
    relevant = []

    for disease in crop["diseases"]:
        if stage in disease["affected_stages"]:
            relevant.append({
                "disease": disease["name"],
                "severity": disease["severity_by_stage"].get(stage),
                "symptoms": disease["visible_symptoms"]
            })

    if not relevant:
        return f"No diseases are relevant for {crop_name} during {stage}."

    return relevant


# 3️⃣ HARVEST TIMING CONSEQUENCES
def harvest_risk(crop_name, timing):
    crop = load_crop(crop_name)

    if timing not in ["early", "late"]:
        return "Harvest timing must be 'early' or 'late'."

    harvest_logic = crop["harvest_logic"].get(f"{timing}_harvest")
    market_impact = crop["market_impact"].get(f"{timing}_harvest")

    if not harvest_logic:
        return f"No {timing} harvest logic defined for {crop_name}."

    return {
        "risks": harvest_logic.get("risks", []),
        "quality_impact": harvest_logic.get("quality_impact"),
        "market_impact": market_impact
    }

# 4️⃣ TEMPERATURE RISK (Phase-1: basic rule-based)

def temperature_risk(temp_c):
    """
    Phase-1 temperature intelligence.
    Simple thresholds, no crop-specific tuning yet.
    """
    if temp_c >= 40:
        return {
            "risk_level": "high",
            "impact": "Heat stress, crop damage likely"
        }
    elif temp_c >= 30:
        return {
            "risk_level": "moderate",
            "impact": "Reduced growth efficiency"
        }
    else:
        return {
            "risk_level": "low",
            "impact": "Temperature within safe range"
        }

# 5️⃣ HUMIDITY RISK (Phase-1: basic rule-based)

def humidity_risk(humidity_percent):
    """
    Phase-1 humidity intelligence.
    Simple thresholds, crop-agnostic.
    """
    if humidity_percent >= 85:
        return {
            "risk_level": "high",
            "impact": "High fungal and disease risk"
        }
    elif humidity_percent >= 65:
        return {
            "risk_level": "moderate",
            "impact": "Conditions may favor disease spread"
        }
    else:
        return {
            "risk_level": "low",
            "impact": "Humidity within safe range"
        }

# 6️⃣ WIND RISK (Phase-1: basic rule-based)

def wind_risk(wind_speed_kmph):
    """
    Phase-1 wind intelligence.
    Simple thresholds, crop-agnostic.
    """
    if wind_speed_kmph >= 40:
        return {
            "risk_level": "high",
            "impact": "Crop lodging, physical damage likely"
        }
    elif wind_speed_kmph >= 20:
        return {
            "risk_level": "moderate",
            "impact": "Potential stress and minor damage"
        }
    else:
        return {
            "risk_level": "low",
            "impact": "Wind conditions safe"
        }
