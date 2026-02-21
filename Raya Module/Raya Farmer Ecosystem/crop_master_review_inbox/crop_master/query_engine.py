"""
RAYA — Crop Master Query Layer
Phase-1 LOCKED → Phase-2 Track-1 Compatible

Public Contract (Track-1):
✔ get_stage_snapshot(crop, stage)
✔ get_water_requirement(crop, stage)

Internal Utilities (NOT Track-1):
• _diseases_at_stage()

Design Principles:
- Deterministic
- Read-only access to Crop Master
- No ML / No inference
- Always returns dict (no None / no strings)
- Schema defensive: supports lifecycle OR growth_lifecycle
"""

import json
from pathlib import Path

# -------------------------------------------------------
# Paths
# -------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CROPS_DIR = BASE_DIR / "crops"


# -------------------------------------------------------
# Loader
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

def _resolve_stage(stage_input: str, stages: dict) -> str | None:
    """
    Case-insensitive stage resolver.
    Returns canonical stage name or None.
    """
    normalized = stage_input.lower().replace(" ", "_")

    for canonical in stages.keys():
        key = canonical.lower().replace(" ", "_")
        if key == normalized:
            return canonical

    return None


# -------------------------------------------------------
# Internal: lifecycle resolver
# Supports:
#   lifecycle
#   growth_lifecycle
# -------------------------------------------------------
def _get_stages(crop: dict) -> dict:
    lifecycle = (
        crop.get("lifecycle")
        or crop.get("growth_lifecycle")
        or {}
    )
    return lifecycle.get("stages", {})


# =======================================================
# 1️⃣ Stage Snapshot (Track-1 Core API)
# =======================================================
def get_stage_snapshot(crop_name: str, stage: str) -> dict:
    crop = load_crop(crop_name)

    if "error" in crop:
        return crop

    stages = _get_stages(crop)

    if not stages:
        return {
            "status": "error",
            "error": "no_stage_data",
            "message": "No lifecycle data found in Crop Master"
        }

    resolved_stage = _resolve_stage(stage, stages)

    if not resolved_stage:
        return {
            "status": "error",
            "error": "invalid_stage",
            "message": f"Invalid stage '{stage}'",
            "valid_stages": list(stages.keys())
        }

    stage_data = stages[resolved_stage]

    return {
        "status": "success",
        "stage": resolved_stage,
        "sensitivity": stage_data.get("sensitivity"),
        "risks": stage_data.get("stage_risk_summary", []),
        "description": stage_data.get("description"),
        "harvest_risk": stage_data.get("harvest_risk")
    }


# =======================================================
# 2️⃣ Water Requirement (Track-1 Core API)
# =======================================================
def get_water_requirement(crop_name: str, stage: str) -> dict:
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
    resolved_stage = _resolve_stage(stage, stages)

    if not resolved_stage:
        return {
            "status": "error",
            "error": "invalid_stage",
            "message": f"Invalid stage '{stage}'",
            "valid_stages": list(stages.keys())
        }

    stage_data = stages[resolved_stage]

    return {
        "status": "success",
        "stage": resolved_stage,
        "water_requirement": stage_data.get("water_requirement")
    }

# =======================================================
# INTERNAL — Phase-2 Utility (NOT Track-1 Contract)
# =======================================================
def _diseases_at_stage(crop_name: str, stage: str):
    """
    Internal helper for future Phase-2 disease intelligence.
    Do NOT use in Farmer Search Engine (Track-1).
    """
    crop = load_crop(crop_name)

    if "error" in crop:
        return []

    diseases = crop.get("diseases", [])
    relevant = []

    for disease in diseases:
        if stage in disease.get("affected_stages", []):
            relevant.append({
                "disease": disease.get("name"),
                "severity": disease.get("severity_by_stage", {}).get(stage),
                "symptoms": disease.get("visible_symptoms", [])
            })

    return relevant


# -------------------------------------------------------
# Developer Test Harness
# -------------------------------------------------------
if __name__ == "__main__":
    print("\n-- Stage Snapshot --")
    print(get_stage_snapshot("rice", "flowering"))

    print("\n-- Water Requirement --")
    print(get_water_requirement("rice", "flowering"))

    print("\n-- Internal Disease Helper (Phase-2 only) --")
    print(_diseases_at_stage("rice", "flowering"))
