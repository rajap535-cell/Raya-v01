"""
RAYA — Crop Knowledge Rule Engine
(PRODUCTION READY — ENRICHED INTELLIGENCE VERSION)

Purpose
-------
Deterministic agronomic intelligence engine
powered entirely by Crop Master datasets.

Capabilities
------------
✔ Structured advisory extraction
✔ Preventive action intelligence
✔ Avoid-action intelligence
✔ Fertilizer intelligence
✔ Disease-stage-weather relationships
✔ Climate-aware disease pressure mapping
✔ Deterministic rule matching
✔ Defensive schema handling
✔ Read-only Crop Master access
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
# UTC Timestamp
# -------------------------------------------------------

def utc_timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()
# -------------------------------------------------------
# Formatting Helpers
# -------------------------------------------------------

def _stage_label(
    stage: str
) -> str:

    return (
        stage or "current stage"
    ).replace("_", " ")


def _format_items(
    values
):

    values = values or []

    if isinstance(values, str):

        return values

    return ", ".join(
        str(value)
        for value in values
        if value
    )


def _infer_primary_nutrients(
    crop: dict,
    stage: str
):

    stage_norm = (
        stage or ""
    ).lower()

    crop_type = (
        crop.get(
            "crop_identity",
            {}
        ).get(
            "crop_type",
            ""
        ).lower()
    )

    if "maturity" in stage_norm:

        return []

    if any(
        key in stage_norm
        for key in [
            "flower",
            "grain_filling",
            "fruit_development",
            "fruit_set"
        ]
    ):

        if crop_type in [
            "fruit",
            "vegetable"
        ]:

            return [
                "Potassium",
                "Calcium"
            ]

        return [
            "Potassium",
            "Nitrogen"
        ]

    if any(
        key in stage_norm
        for key in [
            "vegetative",
            "tillering",
            "stem_elongation"
        ]
    ):

        return [
            "Nitrogen",
            "Phosphorus"
        ]

    if any(
        key in stage_norm
        for key in [
            "nursery",
            "seedling",
            "germination",
            "planting_establishment"
        ]
    ):

        return [
            "Nitrogen",
            "Phosphorus"
        ]

    return [
        "Nitrogen",
        "Phosphorus",
        "Potassium"
    ]


# -------------------------------------------------------
# Crop Loader
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
# Stage Intelligence Resolver
# -------------------------------------------------------

def _resolve_stage_data(
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

    canonical_stage = _resolve_stage(
        stage,
        stages,
        crop
    )

    if not canonical_stage:

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
        canonical_stage,
        {}
    )

    return crop, canonical_stage, stage_data


# =======================================================
# 1️⃣ Stage Advice Extraction
# =======================================================

def get_stage_advice(
    crop_name: str,
    stage: str
) -> dict:

    crop, canonical_stage, stage_data = (
        _resolve_stage_data(
            crop_name,
            stage
        )
    )

    if (
        isinstance(crop, dict)
        and crop.get("status") == "error"
    ):
        return crop

    risk_summary = (
        crop.get(
            "stage_risk_summary",
            {}
        ).get(canonical_stage)
    )

    return {

        "status": "success",

        "stage": canonical_stage,

        "advice": {

            # ------------------------------------------------
            # Structured Advisories
            # ------------------------------------------------

            "sowing_guidance": stage_data.get(
                "sowing_guidance"
            ),

            "water_principles": stage_data.get(
                "water_principles"
            ),

            "fertilizer_principles": stage_data.get(
                "fertilizer_principles"
            ),

            "critical_operations": stage_data.get(
                "critical_operations",
                []
            ),

            "water_management": stage_data.get(
                "water_management"
            ),

            # ------------------------------------------------
            # Preventive Actions
            # ------------------------------------------------

            "preventive_actions": stage_data.get(
                "preventive_actions",
                []
            ),

            # ------------------------------------------------
            # Avoid Actions
            # ------------------------------------------------

            "avoid_actions": stage_data.get(
                "avoid_actions",
                []
            ),

            # ------------------------------------------------
            # Stage Risk Intelligence
            # ------------------------------------------------

            "risk_summary": risk_summary,

            "yield_risk_level": stage_data.get(
                "yield_risk_level"
            )
        },

        "meta": {

            "generated_at": utc_timestamp(),

            "engine": "RAYA Crop Knowledge Engine"
        }
    }


# =======================================================
# 2️⃣ Disease Intelligence
# =======================================================

def get_relevant_diseases(
    crop_name: str,
    stage: str
) -> dict:

    crop, canonical_stage, stage_data = (
        _resolve_stage_data(
            crop_name,
            stage
        )
    )

    if (
        isinstance(crop, dict)
        and crop.get("status") == "error"
    ):
        return crop

    diseases = crop.get(
        "diseases",
        []
    )

    relevant = []

    canonical_norm = (
        canonical_stage
        .lower()
        .replace(" ", "_")
    )

    # ---------------------------------------------------
    # Climate Interactions
    # ---------------------------------------------------

    climate = (
        crop.get(
            "climate_interactions",
            {}
        ).get(canonical_stage, {})
    )

    climate_risks = list(
        climate.keys()
    )

    # ---------------------------------------------------
    # Disease Matching
    # ---------------------------------------------------

    for disease in diseases:

        affected_stages = disease.get(
            "affected_stages",
            []
        )

        for affected_stage in affected_stages:

            stage_norm = (
                affected_stage
                .lower()
                .replace(" ", "_")
            )

            if stage_norm == canonical_norm:

                weather_links = []

                # ----------------------------------------
                # Disease-Weather Relationships
                # ----------------------------------------
                # DEDUPLICATION: Use a set to prevent
                # repeated advisory messages
                # ----------------------------------------

                weather_link_set = set()

                # Check moisture conditions
                if any(
                    risk in [
                        "high_humidity",
                        "excess_rainfall"
                    ]
                    for risk in climate_risks
                ):

                    weather_link_set.add(
                        "High moisture may "
                        "increase disease pressure"
                    )

                # Check temperature conditions
                if any(
                    risk == "high_temperature"
                    for risk in climate_risks
                ):

                    weather_link_set.add(
                        "Heat stress may weaken crop immunity"
                    )

                # Convert set back to list for consistent output
                weather_links = sorted(weather_link_set)
                relevant.append({

                    "name": disease.get(
                        "name"
                    ),

                    "severity": (
                        disease.get(
                            "severity_by_stage",
                            {}
                        ).get(canonical_stage)
                    ),

                    "symptoms": disease.get(
                        "visible_symptoms",
                        []
                    ),

                    "prevention": disease.get(
                        "prevention_logic",
                        []
                    ),

                    # NEW
                    "weather_risk_links": weather_links,

                    # NEW
                    "climate_triggers": climate_risks
                })

                break

    return {

        "status": "success",

        "stage": canonical_stage,

        "diseases": relevant,

        "meta": {

            "generated_at": utc_timestamp(),

            "engine": "RAYA Crop Knowledge Engine"
        }
    }


# =======================================================
# 3️⃣ Fertilizer Intelligence
# =======================================================

def get_fertilizer_logic(
    crop_name: str,
    stage: str
) -> dict:

    crop, canonical_stage, stage_data = (
        _resolve_stage_data(
            crop_name,
            stage
        )
    )

    if (
        isinstance(crop, dict)
        and crop.get("status") == "error"
    ):
        return crop

    fertilizer_logic = stage_data.get(
        "fertilizer_logic"
    ) or {}

    primary_nutrients = (
        fertilizer_logic.get(
            "primary_nutrients"
        )
        or stage_data.get(
            "primary_nutrients"
        )
        or _infer_primary_nutrients(
            crop,
            canonical_stage
        )
    )

    stage_label = _stage_label(
        canonical_stage
    )

    nutrient_text = _format_items(
        primary_nutrients
    )

    if nutrient_text:

        default_nutrient_principles = (
            f"Focus on {nutrient_text} support "
            f"during {stage_label}"
        )

    else:

        default_nutrient_principles = (
            f"No major fertilizer application is required "
            f"during {stage_label} unless deficiency symptoms appear"
        )

    application_stage = (
        fertilizer_logic.get(
            "application_stage"
        )
        or stage_label
    )

    application_method = (
        stage_data.get(
            "fertilizer_application_method"
        )
        or fertilizer_logic.get(
            "application_method"
        )
        or "Split application with adequate soil moisture"
    )

    risk_if_skipped = fertilizer_logic.get(
        "risk_if_skipped"
    )

    if (
        not primary_nutrients
        or "no major" in str(application_stage).lower()
    ):

        default_timing_guidance = (
            f"No routine fertilizer timing is needed "
            f"during {stage_label}"
        )

    else:

        default_timing_guidance = (
            f"Apply during {application_stage} "
            f"when field moisture is stable"
        )

    timing_guidance = (
        stage_data.get(
            "fertilizer_timing"
        )
        or default_timing_guidance
    )
    notes = (
        stage_data.get(
            "fertilizer_notes"
        )
        or (
            f"If skipped: {risk_if_skipped}"
            if risk_if_skipped
            else "Use soil-test based dosing and adjust for local package of practices"
        )
    )

    return {

        "status": "success",

        "stage": canonical_stage,

        "fertilizer": {

            # ------------------------------------------------
            # Nutrient Intelligence
            # ------------------------------------------------

            "nutrient_principles": (
                stage_data.get(
                    "nutrient_principles"
                )
                or default_nutrient_principles
            ),

            "primary_nutrients": primary_nutrients,

            "timing_guidance": timing_guidance,

            "application_stage": application_stage,

            "notes": notes,

            "risk_if_skipped": (
                risk_if_skipped
                or "Reduced crop vigor or yield potential if nutrient demand is not met"
            ),

            # ------------------------------------------------
            # Advanced Fertilizer Intelligence
            # ------------------------------------------------

            "application_method": application_method,

            "soil_type_adjustment": (
                stage_data.get(
                    "soil_type_adjustment"
                )
                or "Adjust dosage based on soil testing and local soil fertility"
            ),

            "deficiency_symptoms": (
                stage_data.get(
                    "deficiency_symptoms"
                )
                or "Monitor leaf color changes, stunted growth, or poor grain development"
            ),

            "avoid_overuse": (
                stage_data.get(
                    "fertilizer_avoidance"
                )
                or "Avoid excess nitrogen and avoid fertilizer application before heavy rainfall"
            ),

            "weather_precautions": (
                stage_data.get(
                    "fertilizer_weather_precautions"
                )
                or "Do not apply fertilizer during heavy rain, flooding, or severe moisture stress"
            ),

            "recommended_focus": (
                stage_data.get(
                    "fertilizer_focus"
                )
                or default_nutrient_principles
            ),

            "organic_alternatives": (
                stage_data.get(
                    "organic_fertilizer_options"
                )
                or "Compost, farmyard manure, or organic certified fertilizers can supplement chemical applications"
            ),

            "cost_efficiency_tip": (
                stage_data.get(
                    "cost_efficiency_guidance"
                )
                or "Use soil testing to avoid unnecessary applications and optimize dosage for maximum efficiency"
            )
        },

        "meta": {

            "generated_at": utc_timestamp(),

            "engine": "RAYA Crop Knowledge Engine"
        }
    }

# =======================================================
# 4️⃣ Weather-Stage Advisory Intelligence
# =======================================================

def get_stage_weather_actions(
    crop_name: str,
    stage: str
) -> dict:

    crop, canonical_stage, stage_data = (
        _resolve_stage_data(
            crop_name,
            stage
        )
    )

    if (
        isinstance(crop, dict)
        and crop.get("status") == "error"
    ):
        return crop

    climate = (

        crop.get(
            "climate_interactions",
            {}
        ).get(canonical_stage, {})
    )

    actions = []

    for climate_event, details in climate.items():

        risk_level = details.get(
            "risk_level"
        )

        effects = details.get(
            "effects",
            []
        )

        actions.append({

            "event": climate_event,

            "risk_level": risk_level,

            "effects": effects,

            "recommended_action": (
                f"Monitor crop carefully during "
                f"{climate_event.replace('_', ' ')} conditions"
            )
        })

    return {

        "status": "success",

        "stage": canonical_stage,

        "weather_actions": actions,

        "meta": {

            "generated_at": utc_timestamp(),

            "engine": "RAYA Crop Knowledge Engine"
        }
    }


# =======================================================
# Developer Test Harness
# =======================================================

if __name__ == "__main__":

    print("\n================================================")
    print("🚀 RAYA CROP KNOWLEDGE ENGINE TEST")
    print("================================================")

    print("\n--- Stage Advice ---\n")

    print(
        json.dumps(
            get_stage_advice(
                "rice",
                "Flowering"
            ),
            indent=2
        )
    )

    print("\n--- Disease Intelligence ---\n")

    print(
        json.dumps(
            get_relevant_diseases(
                "rice",
                "Flowering"
            ),
            indent=2
        )
    )

    print("\n--- Fertilizer Intelligence ---\n")

    print(
        json.dumps(
            get_fertilizer_logic(
                "rice",
                "Flowering"
            ),
            indent=2
        )
    )

    print("\n--- Weather-Stage Intelligence ---\n")

    print(
        json.dumps(
            get_stage_weather_actions(
                "rice",
                "Flowering"
            ),
            indent=2
        )
    )

    print("\n================================================")
    print("✅ KNOWLEDGE ENGINE TEST COMPLETE")
    print("================================================\n")
