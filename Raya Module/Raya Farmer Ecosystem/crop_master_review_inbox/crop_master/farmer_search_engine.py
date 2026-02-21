"""
RAYA Phase-2 — Track-1: Farmer Search Engine
LOCKED VERSION

Purpose:
Deterministic orchestration layer.

Inputs:
- state
- district
- crop
- stage
- optional weather_event
- optional weather_intensity

Outputs:
- Weather impact
- Stage sensitivity & risks
- Water requirement
- Market snapshot

Contract:
Uses ONLY public Query Engine APIs:
✔ get_stage_snapshot()
✔ get_water_requirement()

No disease logic exposed in Track-1.
"""

import json
from pathlib import Path

from weather_intelligence.weather_engine import assess_weather_event
from query_engine import (
    get_stage_snapshot,
    get_water_requirement
)

# ----------------------------------------------------------
# Paths
# ----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MARKET_DIR = BASE_DIR / "market"


# ----------------------------------------------------------
# Market Loader (Snapshot Only)
# ----------------------------------------------------------
def load_market_price(state: str, district: str):
    f = MARKET_DIR / f"{state.lower()}_{district.lower()}_prices.json"
    if not f.exists():
        return None

    with open(f, "r", encoding="utf-8") as mf:
        return json.load(mf)


# ----------------------------------------------------------
# Core Orchestration (Track-1)
# ----------------------------------------------------------
def farmer_search(
    state: str,
    district: str,
    crop: str,
    stage: str | None,
    weather_event: str | None = None,
    weather_intensity: str | None = None
):
    packet = {
        "location": {"state": state, "district": district},
        "crop": crop,
        "stage": stage
    }

    # ------------------------------------------------------
    # Stage validation via Query Engine
    # ------------------------------------------------------
    if not stage:
        return {
            "error": "missing_stage",
            "message": "Please specify crop growth stage"
        }

    stage_snapshot = get_stage_snapshot(crop, stage)
    stage = stage_snapshot["stage"]  # canonical stage
    packet["stage"] = stage

    # Propagate crop/stage errors directly
    if stage_snapshot["status"]=="error":
        return stage_snapshot

    packet["stage_snapshot"] = stage_snapshot

    # ------------------------------------------------------
    # Weather Section
    # ------------------------------------------------------
    if weather_event:
        packet["weather"] = assess_weather_event(
            crop,
            packet["stage"], #canonical
            weather_event,
            weather_intensity
        )
    else:
        packet["weather"] = {
            "status": "no_alert",
            "message": f"No weather alerts reported for {stage} stage"
        }

    # ------------------------------------------------------
    # Water Requirement
    # ------------------------------------------------------
    water_info = get_water_requirement(crop, stage)

    if water_info.get("error"):
        packet["water"] = {
            "status": "not_available"
        }
    else:
        packet["water"] = (water_info.get("water_requirement")
                           or {"status": "not_defined"})

    # ------------------------------------------------------
    # Market Section
    # ------------------------------------------------------
    price_data = load_market_price(state, district)

    if price_data:
        packet["market"] = {
            "mandi": price_data.get("mandi"),
            "modal": price_data.get("modal_price"),
            "min": price_data.get("min_price"),
            "max": price_data.get("max_price")
        }
    else:
        packet["market"] = {
            "status": "no_price_data",
            "message": f"No market price data for {district}, {state}"
        }

    return packet


# ----------------------------------------------------------
# Farmer-Readable Formatter
# ----------------------------------------------------------
def format_for_farmer(packet: dict) -> str:
    out = []

    if packet.get("error"):
        return packet.get("message")

    out.append(f"Crop: {packet['crop']}")
    out.append(f"Stage: {packet['stage']}")
    out.append(
        f"Location: {packet['location']['district']}, {packet['location']['state']}"
    )

    # Weather
    
    w = packet.get("weather")

    if w:
        if w.get("status") == "no_alert":
            out.append(w["message"])

        elif w.get("status") == "no_climate_data":
            out.append("No climate impact data available")

        else:
            effects = ", ".join(w.get("effects", [])) or "No major effects"

        out.append(
            f"Weather Risk: {w.get('risk_level', 'Unknown')} "
            f"due to {w.get('type', 'weather event')}. "
            f"Possible effects: {effects}"
        )

    
    # Stage sensitivity & risks
    s = packet.get("stage_snapshot", {})
    if s.get("sensitivity"):
        out.append(f"Sensitivity: {s['sensitivity']}")

    if s.get("risks"):
        out.append(f"Key Risks: {', '.join(s['risks'])}")

    # Water
    water = packet.get("water")

    if isinstance(water, dict):
        status = water.get("status")

        if status == "not_defined":
            out.append("Water Need: Not defined for this stage")

        elif status == "not_available":
            out.append("Water Need data not available")

        else:
            out.append(f"Water Need: {water}")
        
    elif water:
        out.append(f"Water Need: {water}")

    else:
        out.append("Water Need: Not defined")


    # Market
    mp = packet.get("market")
    if mp.get("status") == "no_price_data":
        out.append(mp["message"])
    else:
        out.append(
            f"Market Modal: {mp['modal']} ({mp['min']} - {mp['max']}) at {mp['mandi']}"
        )

    return "\n".join(out)


# ----------------------------------------------------------
# Developer Test Harness
# ----------------------------------------------------------
if __name__ == "__main__":
    pkt = farmer_search(
        state="Karnataka",
        district="Mandya",
        crop="rice",
        stage="flowering",
        weather_event="rain",
        weather_intensity="heavy"
    )

    print("\n--- STRUCTURED PACKET ---")
    print(pkt)

    print("\n--- FARMER VIEW ---")
    print(format_for_farmer(pkt))
