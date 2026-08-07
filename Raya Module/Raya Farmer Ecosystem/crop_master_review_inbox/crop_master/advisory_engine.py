"""
RAYA Phase-2 — Track-3: Advisory Aggregation Engine (LOCKED)

Purpose:
Bridge between:
• Farmer Search Engine (snapshot layer)
• Crop Knowledge Engine (rule-based intelligence)

STRICT RULES:
- No modification to Track-1
- No modification to Track-2
- No inference / no ML
- Deterministic only
- Immutable output
"""

from copy import deepcopy

from crop_knowledge_engine import (
    get_stage_advice,
    get_relevant_diseases,
    get_fertilizer_logic
)


# ----------------------------------------------------------
# SAFE GET (Prevents None errors globally)
# ----------------------------------------------------------
def _safe_get(data, key, default=None):
    if isinstance(data, dict):
        return data.get(key, default)
    return default


# ----------------------------------------------------------
# ALERT GENERATOR (LOCKED)
# ----------------------------------------------------------
def generate_alerts(snapshot: dict, knowledge: dict) -> list:
    alerts = []

    stage = _safe_get(snapshot, "stage", "unknown")

    # Weather Alert
    weather = _safe_get(snapshot, "weather", {})
    risk = _safe_get(weather, "risk_level")

    if risk in ("High", "Medium"):
        alerts.append(f"{risk} weather risk during {stage} stage")

    # Stage Sensitivity Alert
    stage_snapshot = _safe_get(snapshot, "stage_snapshot", {})
    sensitivity = _safe_get(stage_snapshot, "sensitivity")

    if sensitivity in ("High", "Medium"):
        alerts.append(f"Crop is {sensitivity.lower()}ly sensitive at {stage} stage")

    # Disease Alert
    disease_block = _safe_get(knowledge, "diseases", {})
    diseases = _safe_get(disease_block, "diseases", [])

    if isinstance(diseases, list) and len(diseases) > 0:
        alerts.append(f"Disease risk present during {stage} stage")

    return alerts


# ----------------------------------------------------------
# SCHEDULER (LOCKED)
# ----------------------------------------------------------
def generate_schedule(stage: str, knowledge: dict) -> list:
    schedule = []

    advice_block = _safe_get(knowledge, "advice", {})
    advice = _safe_get(advice_block, "advice", {})

    if _safe_get(advice, "water_principles"):
        schedule.append("Monitor irrigation based on stage water needs")

    if _safe_get(advice, "fertilizer_principles"):
        schedule.append("Apply fertilizers as per stage nutrient guidance")

    disease_block = _safe_get(knowledge, "diseases", {})
    if _safe_get(disease_block, "diseases"):
        schedule.append("Inspect crop regularly for disease symptoms")

    return schedule


# ----------------------------------------------------------
# MAIN ENGINE (LOCKED CORE)
# ----------------------------------------------------------
def build_advisory(snapshot_packet: dict) -> dict:

    # ------------------------------------------------------
    # HARD GUARD: Invalid input
    # ------------------------------------------------------
    if not isinstance(snapshot_packet, dict):
        return {"status": "error", "message": "Invalid snapshot packet"}

    # Pass-through errors (Track-1 safety)
    if snapshot_packet.get("error"):
        return deepcopy(snapshot_packet)

    crop = snapshot_packet.get("crop")
    stage = snapshot_packet.get("stage")

    if not crop or not stage:
        return {"status": "error", "message": "Missing crop or stage"}

    # ------------------------------------------------------
    # KNOWLEDGE ENGINE CALLS (Track-2)
    # ------------------------------------------------------
    stage_advice = get_stage_advice(crop, stage)
    diseases = get_relevant_diseases(crop, stage)
    fertilizer = get_fertilizer_logic(crop, stage)

    # ------------------------------------------------------
    # DEFENSIVE ERROR HANDLING (STRICT)
    # ------------------------------------------------------
    for block in (stage_advice, diseases, fertilizer):
        if not isinstance(block, dict):
            return {"status": "error", "message": "Invalid knowledge response"}
        if block.get("status") == "error":
            return deepcopy(block)

    # ------------------------------------------------------
    # KNOWLEDGE COMPOSITION (IMMUTABLE BASE)
    # ------------------------------------------------------
    knowledge = {
        "advice": deepcopy(stage_advice),
        "diseases": deepcopy(diseases),
        "fertilizer": deepcopy(fertilizer)
    }

    # ------------------------------------------------------
    # ALERTS & SCHEDULE
    # ------------------------------------------------------
    alerts = generate_alerts(snapshot_packet, knowledge)
    schedule = generate_schedule(stage, knowledge)

    # ------------------------------------------------------
    # FINAL PACKET (LOCKED STRUCTURE)
    # ------------------------------------------------------
    advisory_packet = {
        "status": "success",
        "crop": crop,
        "stage": stage,
        "location": deepcopy(snapshot_packet.get("location")),

        # Snapshot Layer (Track-1)
        "snapshot": {
            "weather": deepcopy(snapshot_packet.get("weather")),
            "water": deepcopy(snapshot_packet.get("water")),
            "market": deepcopy(snapshot_packet.get("market")),
            "stage_snapshot": deepcopy(snapshot_packet.get("stage_snapshot"))
        },

        # Knowledge Layer (Track-2)
        "advisory": {
            "stage_advice": stage_advice.get("advice"),
            "diseases": diseases.get("diseases"),
            "fertilizer": fertilizer.get("fertilizer")
        },

        # Aggregation Layer
        "alerts": tuple(alerts),      # 🔒 immutable
        "schedule": tuple(schedule)   # 🔒 immutable
    }

    return advisory_packet


# ----------------------------------------------------------
# SAFE IMPORT (LOCKED)
# ----------------------------------------------------------
def _load_farmer_search():
    try:
        from farmer_search_engine import build_farmer_packet
        return build_farmer_packet
    except ImportError:
        print("❌ ERROR: 'build_farmer_packet' not found in farmer_search_engine.py")
        return None


# ----------------------------------------------------------
# TEST HARNESS (SAFE EXECUTION)
# ----------------------------------------------------------
if __name__ == "__main__":

    farmer_search = _load_farmer_search()

    if not farmer_search:
        exit()

    snapshot = farmer_search(
        crop="rice",
        stage="Flowering",
        state="Karnataka",
        district="Mandya"
    )

    advisory = build_advisory(snapshot)

    print("\n--- FINAL ADVISORY PACKET ---")
    print(advisory)