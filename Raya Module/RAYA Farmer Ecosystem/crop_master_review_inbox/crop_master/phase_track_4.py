"""
RAYA Phase-2 — Track-3: Disease Detection Engine (LOCKED)

Purpose:
Rule-based disease detection using:
• Farmer Snapshot (Track-1)
• Crop Knowledge Engine (Track-2)

STRICT RULES:
- No ML / No inference
- Deterministic only
- No modification to Track-1 / Track-2
"""

from copy import deepcopy
from crop_knowledge_engine import get_relevant_diseases


# ----------------------------------------------------------
# SAFE GET
# ----------------------------------------------------------
def _safe_get(data, key, default=None):
    if isinstance(data, dict):
        return data.get(key, default)
    return default


# ----------------------------------------------------------
# RULE ENGINE (CORE LOGIC)
# ----------------------------------------------------------
def evaluate_disease_risk(snapshot: dict, disease_list: list) -> list:

    results = []

    weather = _safe_get(snapshot, "weather", {})
    humidity = _safe_get(weather, "humidity", 0)
    temperature = _safe_get(weather, "temperature", 0)

    stage = _safe_get(snapshot, "stage", "unknown")

    for disease in disease_list:

        name = disease.get("name")

        # --------------------------------------------------
        # RULE SET (DETERMINISTIC)
        # --------------------------------------------------
        risk = "Low"
        reason = []

        # Example rules (expandable)
        if humidity >= 80:
            risk = "High"
            reason.append("High humidity")

        if 60 <= humidity < 80:
            risk = "Medium"
            reason.append("Moderate humidity")

        if stage.lower() == "flowering":
            reason.append("Sensitive growth stage")

        if temperature > 32:
            reason.append("High temperature stress")

        # --------------------------------------------------
        # FINALIZE ONLY IF SIGNAL EXISTS
        # --------------------------------------------------
        if reason:
            results.append({
                "disease": name,
                "risk": risk,
                "reason": " + ".join(reason)
            })

    return results


# ----------------------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------------------
def detect_diseases(snapshot_packet: dict) -> dict:

    if not isinstance(snapshot_packet, dict):
        return {"status": "error", "message": "Invalid snapshot"}

    if snapshot_packet.get("error"):
        return deepcopy(snapshot_packet)

    crop = snapshot_packet.get("crop")
    stage = snapshot_packet.get("stage")

    if not crop or not stage:
        return {"status": "error", "message": "Missing crop/stage"}

    # ------------------------------------------------------
    # FETCH DISEASE KNOWLEDGE (Track-2)
    # ------------------------------------------------------
    disease_block = get_relevant_diseases(crop, stage)

    if disease_block.get("status") == "error":
        return deepcopy(disease_block)

    disease_list = disease_block.get("diseases", [])

    # ------------------------------------------------------
    # RULE EVALUATION
    # ------------------------------------------------------
    risk_output = evaluate_disease_risk(snapshot_packet, disease_list)

    # ------------------------------------------------------
    # FINAL OUTPUT (IMMUTABLE SAFE)
    # ------------------------------------------------------
    return {
        "status": "success",
        "crop": crop,
        "stage": stage,
        "disease_risk": tuple(risk_output)  # 🔒 immutable
    }


# ----------------------------------------------------------
# TEST HARNESS
# ----------------------------------------------------------
if __name__ == "__main__":

    test_snapshot = {
        "crop": "rice",
        "stage": "Flowering",
        "weather": {
            "temperature": 30,
            "humidity": 85,
            "risk_level": "High"
        }
    }

    result = detect_diseases(test_snapshot)

    print("\n--- DISEASE DETECTION OUTPUT ---")
    print(result)