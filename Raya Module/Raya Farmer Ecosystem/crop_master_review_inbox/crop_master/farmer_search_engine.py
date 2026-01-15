"""
RAYA Phase-2 — Track-1: Farmer Search Engine
Deterministic, Truth-based, Non-ML, Non-UI

Inputs:
- state
- district
- crop
- stage
- optional weather event/intensity

Outputs:
- weather impact
- stage sensitivity + risks
- disease relevance
- water requirement (rule-based)
- market price (latest snapshot)

This file is orchestration only.
Domain logic lives in:
✓ weather_engine.py
✓ query_engine.py
✓ crop_master JSON
✓ market layer
"""

import json
from pathlib import Path

from weather_intelligence.weather_engine import assess_weather_event
from query_engine import (
    get_stage_snapshot,
    diseases_at_stage,
    get_water_requirement
)


# ----------------------------------------------------------
# Market loader (deterministic / snapshot)
# ----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MARKET_DIR = BASE_DIR / "market"


def load_market_price(state: str, district: str):
    f = MARKET_DIR / f"{state.lower()}_{district.lower()}_prices.json"
    if not f.exists():
        return None
    with open(f, "r", encoding="utf-8") as mf:
        return json.load(mf)


# ----------------------------------------------------------
# Track-1 Main Orchestration
# ----------------------------------------------------------
def farmer_search(
    state: str,
    district: str,
    crop: str,
    stage: str,
    weather_event: str | None = None,
    weather_intensity: str | None = None
):
    packet = {
        "location": {"state": state, "district": district},
        "crop": crop,
        "stage": stage
    }

    # ---- WEATHER LAYER ----
    if weather_event:
        packet["weather"] = assess_weather_event(
            crop,
            stage,
            weather_event,
            weather_intensity
        )
    else:
        packet["weather"] = None

    # ---- STAGE SNAPSHOT ----
    stage_info = get_stage_snapshot(crop, stage)
    packet["stage_snapshot"] = stage_info

    # ---- DISEASES ----
    diseases = diseases_at_stage(crop, stage)
    packet["diseases"] = diseases or []

    # ---- WATER ----
    water = get_water_requirement(crop, stage)
    packet["water"] = water

    # ---- MARKET ----
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
            "state": state,
            "district": district
        }

    return packet


# ----------------------------------------------------------
# Farmer-Readable Formatter (Truth-only)
# ----------------------------------------------------------
def format_for_farmer(packet: dict) -> str:
    out = []

    out.append(f"Crop: {packet['crop']}")
    out.append(f"Stage: {packet['stage']}")
    out.append(f"Location: {packet['location']['district']}, {packet['location']['state']}")

    # WEATHER
    if packet["weather"]:
        w = packet["weather"]
        if w.get("status") == "unsupported_event":
            out.append(f"Weather: Unsupported event ({w['event']})")
        else:
            out.append(f"Weather Impact: {w}")

    # STAGE SNAPSHOT
    s = packet["stage_snapshot"]
    if isinstance(s, dict):
        sens = s.get("sensitivity") or {}
        if sens:
            sens_keys = [k for k,v in sens.items() if v]
            if sens_keys:
                out.append(f"Sensitivity: {', '.join(sens_keys)}")

        risks = s.get("risks")
        if risks:
            out.append(f"Risks: {', '.join(risks)}")

    # DISEASES
    if packet["diseases"]:
        dis = [d['disease'] for d in packet["diseases"]]
        out.append(f"Diseases this stage: {', '.join(dis)}")
    else:
        out.append("Diseases this stage: None detected")

    # WATER
    if packet["water"]:
        out.append(f"Water Need: {packet['water']}")
    else:
        out.append("Water Need: Not defined")

    # MARKET
    mp = packet["market"]
    if mp.get("status") == "no_price_data":
        out.append("Market: No price data available")
    else:
        out.append(f"Market Modal: {mp['modal']} ({mp['min']} - {mp['max']}) at {mp['mandi']}")

    return "\n".join(out)


# ----------------------------------------------------------
# Developer CLI Test Harness
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

    print("\n--- FARMER FORMAT ---")
    print(format_for_farmer(pkt))
