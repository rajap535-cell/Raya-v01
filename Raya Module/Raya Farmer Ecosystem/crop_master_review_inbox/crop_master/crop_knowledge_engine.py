"""
RAYA — Crop Knowledge Rule Engine
Phase-2 Track-2

Purpose
-------
Deterministic rule engine that extracts agronomic knowledge
from Crop Master files.

Design Principles
-----------------
• No ML / No inference
• Deterministic rule matching
• Read-only Crop Master access
• Defensive schema handling
• Always returns structured dicts
"""

import json
from pathlib import Path


# -------------------------------------------------------
# Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CROPS_DIR = BASE_DIR / "crops"


# -------------------------------------------------------
# Crop Loader
# -------------------------------------------------------

def load_crop(crop_name: str) -> dict:

    crop_file = CROPS_DIR / f"{crop_name.lower()}.crop_master.json"

    if not crop_file.exists():
        return {
            "status": "error",
            "error": "crop_not_found",
            "message": f"Crop Master not found for '{crop_name}'"
        }

    with open(crop_file, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------------------------------
# Lifecycle Resolver
# Supports:
# lifecycle
# growth_lifecycle
# -------------------------------------------------------

def _get_stages(crop: dict) -> dict:

    lifecycle = (
        crop.get("lifecycle")
        or crop.get("growth_lifecycle")
        or {}
    )

    return lifecycle.get("stages", {})


# -------------------------------------------------------
# Stage Normalization
# -------------------------------------------------------

def _resolve_stage(stage_input: str, stages: dict) -> str | None:

    normalized = stage_input.lower().replace(" ", "_")

    for canonical in stages.keys():

        key = canonical.lower().replace(" ", "_")

        if key == normalized:
            return canonical

    return None


# =======================================================
# 1️⃣ Stage Advice Extraction
# =======================================================

def get_stage_advice(crop_name: str, stage: str) -> dict:

    crop = load_crop(crop_name)

    if crop.get("status") == "error":
        return crop

    stages = _get_stages(crop)

    if not stages:
        return {
            "status": "error",
            "error": "no_stage_data",
            "message": "No lifecycle data found in Crop Master"
        }

    canonical_stage = _resolve_stage(stage, stages)

    if not canonical_stage:
        return {
            "status": "error",
            "error": "invalid_stage",
            "message": f"Invalid stage '{stage}'",
            "valid_stages": list(stages.keys())
        }

    stage_data = stages[canonical_stage]

    return {
        "status": "success",
        "stage": canonical_stage,
        "advice": {
            "sowing_guidance": stage_data.get("sowing_guidance"),
            "water_principles": stage_data.get("water_principles"),
            "fertilizer_principles": stage_data.get("fertilizer_principles"),
            "preventive_care": stage_data.get("stage_risk_summary", [])
        }
    }


# =======================================================
# 2️⃣ Relevant Diseases Extraction
# =======================================================

def get_relevant_diseases(crop_name: str, stage: str) -> dict:

    crop = load_crop(crop_name)

    if crop.get("status") == "error":
        return crop

    stages = _get_stages(crop)

    canonical_stage = _resolve_stage(stage, stages)

    if not canonical_stage:
        return {
            "status": "error",
            "error": "invalid_stage",
            "message": f"Invalid stage '{stage}'",
            "valid_stages": list(stages.keys())
        }

    diseases = crop.get("diseases", [])

    canonical_norm = canonical_stage.lower().replace(" ", "_")

    relevant = []

    for disease in diseases:

        affected = disease.get("affected_stages", [])

        for s in affected:

            stage_norm = s.lower().replace(" ", "_")

            if stage_norm == canonical_norm:

                relevant.append({
                    "name": disease.get("name"),
                    "severity": disease.get("severity_by_stage", {}).get(canonical_stage),
                    "symptoms": disease.get("visible_symptoms", []),
                    "prevention": disease.get("prevention_logic")
                })

                break

    return {
        "status": "success",
        "stage": canonical_stage,
        "diseases": relevant
    }


# =======================================================
# 3️⃣ Fertilizer Logic Extraction
# =======================================================

def get_fertilizer_logic(crop_name: str, stage: str) -> dict:

    crop = load_crop(crop_name)

    if crop.get("status") == "error":
        return crop

    stages = _get_stages(crop)

    if not stages:
        return {
            "status": "error",
            "error": "no_stage_data",
            "message": "No lifecycle data found in Crop Master"
        }

    canonical_stage = _resolve_stage(stage, stages)

    if not canonical_stage:
        return {
            "status": "error",
            "error": "invalid_stage",
            "message": f"Invalid stage '{stage}'",
            "valid_stages": list(stages.keys())
        }

    stage_data = stages[canonical_stage]

    return {
        "status": "success",
        "stage": canonical_stage,
        "fertilizer": {
            "nutrient_principles": stage_data.get("nutrient_principles"),
            "timing_guidance": stage_data.get("fertilizer_timing"),
            "notes": stage_data.get("fertilizer_notes")
        }
    }


# =======================================================
# Developer Test Harness
# =======================================================

if __name__ == "__main__":

    print("\nTEST 1 — Valid crop + valid stage")
    print(get_stage_advice("rice", "Flowering"))

    print("\nTEST 2 — Valid crop + invalid stage")
    print(get_stage_advice("rice", "moon_stage"))

    print("\nTEST 3 — Unknown crop")
    print(get_stage_advice("dragonfruit", "flowering"))

    print("\nTEST 4 — Stage case mismatch")
    print(get_stage_advice("rice", "flowering"))

    print("\nTEST 5 — Disease match")
    print(get_relevant_diseases("rice", "flowering"))

    print("\nTEST 6 — Fertilizer logic")
    print(get_fertilizer_logic("rice", "flowering"))