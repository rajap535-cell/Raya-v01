"""
RAYA — Crop Master Query Layer
(PRODUCTION READY — ENRICHED INTELLIGENCE VERSION)

Purpose
-------
Query and resolve structured crop intelligence
from Crop Master datasets.

Upgrades
--------
✔ Stage-aware intelligence extraction
✔ Water management integration
✔ Yield risk integration
✔ Critical operation support
✔ Robust schema compatibility
✔ Defensive lifecycle resolution
✔ Deterministic structured outputs
"""

import json
from pathlib import Path
from datetime import datetime, timezone


# -------------------------------------------------------
# Paths
# -------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

CROPS_DIR = BASE_DIR / "crops"


# -------------------------------------------------------
# Timezone-Aware UTC Timestamp
# -------------------------------------------------------
def utc_timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()


# -------------------------------------------------------
# Loader
# -------------------------------------------------------
def load_crop(crop_name: str) -> dict:

    crop_file = (
        CROPS_DIR /
        f"{crop_name.lower()}.crop_master.json"
    )

    if not crop_file.exists():

        return {
            "status": "error",
            "error": "crop_not_found",
            "message": (
                f"Crop Master not found "
                f"for '{crop_name}'"
            ),
            "meta": {
                "generated_at": utc_timestamp()
            }
        }

    with open(
        crop_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# -------------------------------------------------------
# Stage Alias Resolver
# -------------------------------------------------------
def _resolve_alias(
    alias: str,
    crop: dict,
    stages: dict
) -> str | None:
    """
    Resolve backward-compatible stage aliases
    (e.g. nursery -> Germination/Seedling).
    When an alias maps to multiple canonical stages,
    the first existing stage is used as default.
    """
    aliases = crop.get("stage_aliases", {}) or {}

    target_norm = (
        alias.lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    for key, targets in aliases.items():

        key_norm = (
            key.lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        if key_norm != target_norm:
            continue

        for target in targets:

            canonical = _resolve_stage(
                target,
                stages
            )

            if canonical:

                return canonical

    return None


# -------------------------------------------------------
# Stage Resolver
# -------------------------------------------------------
def _resolve_stage(
    stage_input: str,
    stages: dict,
    crop: dict | None = None
) -> str | None:

    normalized = (
        stage_input
        .lower()
        .replace(" ", "_")
    )

    for canonical in stages.keys():

        key = (
            canonical
            .lower()
            .replace(" ", "_")
        )

        if key == normalized:

            return canonical

    # ---------------------------------------------------
    # Backward-compatibility alias resolution
    # ---------------------------------------------------
    if crop:

        alias_resolved = _resolve_alias(
            normalized,
            crop,
            stages
        )

        if alias_resolved:

            return alias_resolved

    return None


# -------------------------------------------------------
# Lifecycle Resolver
# -------------------------------------------------------
def _get_stages(crop: dict) -> dict:

    lifecycle = (

        crop.get("lifecycle")

        or crop.get("growth_lifecycle")

        or {}
    )

    return lifecycle.get("stages", {})


# -------------------------------------------------------
# Stage Intelligence Resolver
# -------------------------------------------------------
def _get_stage_data(
    crop_name: str,
    stage: str
):

    crop = load_crop(crop_name)

    if crop.get("status") == "error":

        return crop, None, None

    stages = _get_stages(crop)

    if not stages:

        return {
            "status": "error",
            "error": "no_stage_data",
            "message": (
                "No lifecycle data found "
                "in Crop Master"
            )
        }, None, None

    resolved_stage = _resolve_stage(
        stage,
        stages,
        crop
    )

    if not resolved_stage:

        return {
            "status": "error",
            "error": "invalid_stage",
            "message": (
                f"Invalid stage '{stage}'"
            ),
            "valid_stages": list(
                stages.keys()
            )
        }, None, None

    stage_data = stages.get(
        resolved_stage,
        {}
    )

    return crop, resolved_stage, stage_data


# =======================================================
# 1️⃣ Stage Snapshot
# =======================================================
def get_stage_snapshot(
    crop_name: str,
    stage: str
) -> dict:

    crop, resolved_stage, stage_data = (
        _get_stage_data(
            crop_name,
            stage
        )
    )

    if (
        isinstance(crop, dict)
        and crop.get("status") == "error"
    ):
        return crop

    # -----------------------------------------------
    # Stage Risk Summary
    # -----------------------------------------------

    stage_risk_summary = (
        crop.get("stage_risk_summary", {})
        .get(resolved_stage)
    )

    # -----------------------------------------------
    # Risk Impact Map
    # -----------------------------------------------

    risk_impact_map = (
        crop.get("risk_impact_map", {})
        .get(resolved_stage, {})
    )

    return {

        "status": "success",

        "stage": resolved_stage,

        "duration_days": stage_data.get(
            "duration_days"
        ),

        "sensitivity": stage_data.get(
            "sensitivity"
        ),

        # NEW
        "yield_risk_level": stage_data.get(
            "yield_risk_level"
        ),

        # NEW
        "critical_operations": stage_data.get(
            "critical_operations",
            []
        ),

        # NEW
        "water_management": stage_data.get(
            "water_management"
        ),

        "risk_summary": stage_risk_summary,

        "risk_impact_map": risk_impact_map,

        "meta": {
            "generated_at": utc_timestamp(),
            "engine": "RAYA Query Engine"
        }
    }


# =======================================================
# 2️⃣ Water Requirement
# =======================================================
def get_water_requirement(
    crop_name: str,
    stage: str
) -> dict:

    crop, resolved_stage, stage_data = (
        _get_stage_data(
            crop_name,
            stage
        )
    )

    if (
        isinstance(crop, dict)
        and crop.get("status") == "error"
    ):
        return crop

    return {

        "status": "success",

        "stage": resolved_stage,

        # UPDATED
        "water_management": stage_data.get(
            "water_management"
        ),

        # OPTIONAL BACKWARD COMPATIBILITY
        "water_requirement": stage_data.get(
            "water_requirement"
        ),

        "meta": {
            "generated_at": utc_timestamp(),
            "engine": "RAYA Query Engine"
        }
    }


# =======================================================
# 3️⃣ Critical Operations
# =======================================================
def get_critical_operations(
    crop_name: str,
    stage: str
) -> dict:

    crop, resolved_stage, stage_data = (
        _get_stage_data(
            crop_name,
            stage
        )
    )

    if (
        isinstance(crop, dict)
        and crop.get("status") == "error"
    ):
        return crop

    return {

        "status": "success",

        "stage": resolved_stage,

        "critical_operations": stage_data.get(
            "critical_operations",
            []
        ),

        "meta": {
            "generated_at": utc_timestamp(),
            "engine": "RAYA Query Engine"
        }
    }


# =======================================================
# 4️⃣ Yield Risk Intelligence
# =======================================================
def get_yield_risk(
    crop_name: str,
    stage: str
) -> dict:

    crop, resolved_stage, stage_data = (
        _get_stage_data(
            crop_name,
            stage
        )
    )

    if (
        isinstance(crop, dict)
        and crop.get("status") == "error"
    ):
        return crop

    return {

        "status": "success",

        "stage": resolved_stage,

        "yield_risk_level": stage_data.get(
            "yield_risk_level"
        ),

        "meta": {
            "generated_at": utc_timestamp(),
            "engine": "RAYA Query Engine"
        }
    }


# =======================================================
# INTERNAL — Disease Resolver
# =======================================================
def _diseases_at_stage(
    crop_name: str,
    stage: str
):

    crop = load_crop(crop_name)

    if crop.get("status") == "error":

        return []

    resolved_stage = stage

    diseases = crop.get(
        "diseases",
        []
    )

    relevant = []

    for disease in diseases:

        if resolved_stage in disease.get(
            "affected_stages",
            []
        ):

            relevant.append({

                "disease": disease.get(
                    "name"
                ),

                "severity": (
                    disease.get(
                        "severity_by_stage",
                        {}
                    ).get(resolved_stage)
                ),

                "symptoms": disease.get(
                    "visible_symptoms",
                    []
                ),

                "prevention": disease.get(
                    "prevention_logic",
                    []
                )
            })

    return relevant


# -------------------------------------------------------
# Developer Test Harness
# -------------------------------------------------------
if __name__ == "__main__":

    print("\n================================================")
    print("🚀 RAYA QUERY ENGINE TEST")
    print("================================================")

    print("\n--- Stage Snapshot ---\n")

    print(
        json.dumps(
            get_stage_snapshot(
                "rice",
                "flowering"
            ),
            indent=2
        )
    )

    print("\n--- Water Requirement ---\n")

    print(
        json.dumps(
            get_water_requirement(
                "rice",
                "flowering"
            ),
            indent=2
        )
    )

    print("\n--- Critical Operations ---\n")

    print(
        json.dumps(
            get_critical_operations(
                "rice",
                "flowering"
            ),
            indent=2
        )
    )

    print("\n--- Yield Risk ---\n")

    print(
        json.dumps(
            get_yield_risk(
                "rice",
                "flowering"
            ),
            indent=2
        )
    )

    print("\n--- Internal Disease Resolver ---\n")

    print(
        json.dumps(
            _diseases_at_stage(
                "rice",
                "Flowering"
            ),
            indent=2
        )
    )

    print("\n================================================")
    print("✅ QUERY ENGINE TEST COMPLETE")
    print("================================================\n")