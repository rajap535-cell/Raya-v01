"""
RAYA Phase-2 — Track-1: Farmer Search Engine
Deterministic, Truth-based, Non-ML, Non-UI

This file is orchestration only.
No domain logic lives here.

Dependencies:
✓ weather_engine.py
✓ query_engine.py
✓ Crop Master JSON
✓ Market snapshot loader
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
# Market loader (deterministic snapshot)
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
    crop: str | None,
    stage: str | None,
    weather_event: str | None = None,
    weather_intensity: str | None = None
):
    # ---------------- INPUT VALIDATION ----------------
    if not crop:
        return {
            "status": "incomplete",
            "message": "Please specify the crop name."
        }

    if not stage:
        return {
            "status": "incomplete",
            "message": "Please specify crop growth stage."
        }

    packet = {
        "location": {"state": state, "district": district},
        "crop": crop,
        "stage": stage
    }

    # ---------------- WEATHER ----------------
    if weather_event:
        packet["weather"] = assess_weather_event(
            crop=crop,
            stage=stage,
            event=weather_event,
            intensity=weather_intensity
        )
    else:
        packet["weather"] = {
            "status": "no_weather_alert",
            "message": "No weather alerts reported for this stage."
        }

    # ---------------- STAGE SNAPSHOT ----------------
    stage_info = get_stage_snapshot(crop, stage)
    if isinstance(stage_info, str):
        return {
            "status": "invalid_stage",
            "message": stage_info
        }
    packet["stage_snapshot"] = stage_info

    # ---------------- DISEASES ----------------
    diseases = diseases_at_stage(crop, stage)
    packet["diseases"] = diseases if isinstance(diseases, list) else []

    # ---------------- WATER ----------------
    packet["water"] = get_water_requirement(crop, stage)

    # ---------------- MARKET ----------------
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
            "message": f"No market price data available for {district}, {state}."
        }

    return packet


# ----------------------------------------------------------
# Farmer-readable formatter (truth-only)
# ----------------------------------------------------------
def format_for_farmer(packet: dict) -> str:
    out = []

    if packet.get("status") in {"incomplete", "invalid_stage"}:
        return packet.get("message", "Input error")

    out.append(f"Crop: {packet['crop']}")
    out.append(f"Stage: {packet['stage']}")
    out.append(f"Location: {packet['location']['district']}, {packet['location']['state']}")

    # Weather
    w = packet["weather"]
    if w:
        out.append(f"Weather: {w.get('message', w)}")

    # Stage snapshot
    s = packet["stage_snapshot"]
    if s.get("sensitivity"):
        out.append(f"Sensitivity: {s['sensitivity']}")
    if s.get("risks"):
        out.append(f"Risks: {', '.join(s['risks'])}")

    # Diseases
    if packet["diseases"]:
        out.append(
            "Diseases this stage: " +
            ", ".join(d["disease"] for d in packet["diseases"])
        )
    else:
        out.append("Diseases this stage: None detected")

    # Water
    if packet["water"]:
        out.append(f"Water Requirement: {packet['water']}")
    else:
        out.append("Water Requirement: Not defined")

    # Market
    mp = packet["market"]
    if mp.get("status") == "no_price_data":
        out.append(mp["message"])
    else:
        out.append(
            f"Market Price (Modal): {mp['modal']} "
            f"({mp['min']}–{mp['max']}) at {mp['mandi']}"
        )

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
