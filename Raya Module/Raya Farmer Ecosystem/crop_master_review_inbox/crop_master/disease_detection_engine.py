"""
RAYA Phase-2 — Track-3: Disease Detection Engine (FINAL LOCKED)

Purpose:
Image → Disease Name → Crop Master → Structured Output

STRICT RULES:
- ML layer ONLY returns disease name
- ALL knowledge from Crop Knowledge Engine (Track-2)
- No bypass / no duplicate logic
- No advisory / no inference
- Deterministic & test-compliant
"""

from copy import deepcopy
from crop_knowledge_engine import get_relevant_diseases


# ----------------------------------------------------------
# DUMMY ML PREDICTOR (MVP)
# ----------------------------------------------------------
def predict_disease(image_path: str) -> dict:
    """
    Simulated ML model
    ONLY returns disease name + confidence
    """
    if not image_path:
        return {
            "status": "error",
            "error": "invalid_input",
            "message": "Image input is required"
        }

    # Replace with real ML model later
    return {
        "status": "success",
        "disease_name": "Blast Disease",
        "confidence": 0.85
    }


# ----------------------------------------------------------
# MATCH DISEASE (NO LOGIC, ONLY MATCH)
# ----------------------------------------------------------
def _match_disease(detected_name: str, disease_list: list):
    """
    Matches predicted disease name with Crop Knowledge Engine output
    """
    for disease in disease_list:
        if disease.get("name", "").lower() == detected_name.lower():
            return disease
    return None


# ----------------------------------------------------------
# MAIN ENGINE
# ----------------------------------------------------------
def detect_disease(snapshot: dict) -> dict:

    # ---------------- INPUT VALIDATION ----------------
    if not isinstance(snapshot, dict):
        return {
            "status": "error",
            "error": "invalid_input",
            "message": "Invalid input format"
        }

    crop = snapshot.get("crop")
    stage = snapshot.get("stage")
    image_path = snapshot.get("image")

    if not crop:
        return {
            "status": "error",
            "error": "missing_crop",
            "message": "Crop is required"
        }

    if not stage:
        return {
            "status": "error",
            "error": "missing_stage",
            "message": "Stage is required for disease validation"
        }

    if not image_path:
        return {
            "status": "error",
            "error": "invalid_input",
            "message": "Image input is required"
        }

    # ---------------- ML PREDICTION ----------------
    prediction = predict_disease(image_path)

    if prediction.get("status") == "error":
        return prediction

    detected_name = prediction.get("disease_name")
    confidence = prediction.get("confidence")

    # ------------------------------------------------------
    # STRICT TRACK-2 USAGE (NO BYPASS)
    # ------------------------------------------------------
    disease_block = get_relevant_diseases(crop, stage)

    if not isinstance(disease_block, dict):
        return {
            "status": "error",
            "error": "invalid_knowledge_response",
            "message": "Invalid response from Crop Knowledge Engine"
        }

    if disease_block.get("status") == "error":
        return deepcopy(disease_block)

    disease_list = disease_block.get("diseases", [])

    # ------------------------------------------------------
    # MATCH DISEASE (STAGE-RELEVANT ONLY)
    # ------------------------------------------------------
    matched = _match_disease(detected_name, disease_list)

    # ------------------------------------------------------
    # CASE 1: MATCH FOUND → ACTIVE
    # ------------------------------------------------------
    if matched:
        return {
            "status": "success",
            "crop": crop,
            "stage": stage,
            "disease_detection": {
                "name": matched.get("name"),
                "confidence": confidence,
                "stage_relevance": "active",
                "symptoms": matched.get("symptoms") or [],
                "prevention": matched.get("prevention") or []
            }
        }

    # ------------------------------------------------------
    # CASE 2: UNKNOWN DISEASE → SUCCESS (NOT ERROR)
    # ------------------------------------------------------
    return {
        "status": "success",
        "crop": crop,
        "stage": stage,
        "disease_detection": {
            "name": "unknown_disease",
            "confidence": confidence,
            "stage_relevance": "unknown",
            "message": "Detected disease not found in Crop Master for this crop/stage"
        }
    }


# ----------------------------------------------------------
# TEST HARNESS
# ----------------------------------------------------------
if __name__ == "__main__":

    test_cases = [
        # 1️⃣ Valid Active Case
        {"crop": "rice", "stage": "Flowering", "image": "leaf.jpg"},

        # 2️⃣ Different Stage (will return unknown or active based on Track-2)
        {"crop": "rice", "stage": "Maturity", "image": "leaf.jpg"},

        # 3️⃣ Unknown Disease (simulate by changing predictor)
        {"crop": "rice", "stage": "Flowering", "image": "unknown.jpg"},

        # 4️⃣ Invalid Crop Mapping
        {"crop": "wheat", "stage": "Flowering", "image": "leaf.jpg"},

        # 5️⃣ Missing Stage
        {"crop": "rice", "stage": None, "image": "leaf.jpg"},

        # 6️⃣ Missing Crop
        {"crop": None, "stage": "Flowering", "image": "leaf.jpg"},

        # 7️⃣ Invalid Image
        {"crop": "rice", "stage": "Flowering", "image": None},
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n--- TEST CASE {i} ---")
        print(detect_disease(test))