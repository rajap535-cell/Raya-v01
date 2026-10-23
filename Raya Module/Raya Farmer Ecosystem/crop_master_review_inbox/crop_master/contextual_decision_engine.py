"""
RAYA — Contextual Decision Intelligence Layer
==============================================

PHASE 3B — FARMER CONTEXT + PERSONALIZATION

Purpose
-------
Convert agricultural intelligence signals AND farmer context
into actionable, prioritized, explainable recommendations.

This layer consumes:
    • Weather Intelligence
    • Market Intelligence
    • Crop Knowledge
    • Stage Snapshot
    • Water Intelligence
    • Disease Intelligence
    • Farmer Context
    • Farm Constraints
    • Soil Conditions

Phase 3B Flow
-------------
Farmer
    ↓
Farm
    ↓
Field
    ↓
Soil
    ↓
Crop
    ↓
Stage
    ↓
Location
    ↓
Weather
    ↓
Water
    ↓
Disease
    ↓
Fertilizer
    ↓
Market
    ↓
Farmer Context
    ↓
Personalization
    ↓
Contextual Decision Engine
    ↓
RAYA Recommendation

Design Principles
-----------------
• Deterministic
• Rule-based
• No ML
• Explainable
• No duplicated Crop Master logic
• No duplicated Weather logic
• No duplicated Market logic
• Farmer Context enriches existing intelligence
• Context only affects relevant decisions
• Backward compatible with Phase 3 calls
• Missing farmer context must not break the engine
"""

# ============================================================
# Imports
# ============================================================

import json

from datetime import datetime, timezone

from farmer_search_engine import farmer_search

try:
    from farmer_context import (
        FARMER_CONTEXT_SCHEMA_VERSION,
        build_farmer_context,
        validate_farmer_context as validate_canonical_farmer_context,
    )
except ImportError:
    FARMER_CONTEXT_SCHEMA_VERSION = "3B.1"
    build_farmer_context = None
    validate_canonical_farmer_context = None


# ============================================================
# Constants
# ============================================================

PRIORITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


VALID_PRIORITIES = {
    "Critical",
    "High",
    "Medium",
    "Low",
}


# ============================================================
# Timestamp
# ============================================================

def utc_timestamp():
    """
    Return an ISO-8601 UTC timestamp.
    """
    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# Generic Helpers
# ============================================================

def _safe_dict(value):
    """
    Return a dictionary or an empty dictionary.
    """
    return value if isinstance(value, dict) else {}


def _safe_list(value):
    """
    Return a list or an empty list.
    """
    if isinstance(value, list):
        return value

    if value is None:
        return []

    return [value]


def _normalize_text(value):
    """
    Normalize text for deterministic comparisons.
    """
    if value is None:
        return ""

    return str(value).strip().lower()


def _normalize_crop(crop):
    """
    Normalize crop name.
    """
    return _normalize_text(crop)


def _normalize_stage(stage):
    """
    Normalize stage names for comparisons.

    Examples
    --------
    Flowering -> flowering
    Grain Filling -> grain filling
    Panicle_Initiation -> panicle initiation
    """
    return (
        _normalize_text(stage)
        .replace("_", " ")
        .replace("-", " ")
    )


def _priority_score(level):
    """
    Convert priority level to numeric score.
    """
    return PRIORITY_ORDER.get(
        level,
        PRIORITY_ORDER["Low"]
    )


def _score_to_priority(score):
    """
    Convert numeric score back to priority level.
    """
    if score >= 4:
        return "Critical"

    if score >= 3:
        return "High"

    if score >= 2:
        return "Medium"

    return "Low"


def _increase_priority(level, steps=1):
    """
    Increase recommendation priority.
    """
    score = _priority_score(level)

    score = min(
        score + steps,
        PRIORITY_ORDER["Critical"]
    )

    return _score_to_priority(score)


def _decrease_priority(level, steps=1):
    """
    Decrease recommendation priority.

    Never goes below Low.
    """
    score = _priority_score(level)

    score = max(
        score - steps,
        PRIORITY_ORDER["Low"]
    )

    return _score_to_priority(score)


def _is_priority_at_least(level, minimum):
    """
    Compare priority levels.
    """
    return (
        _priority_score(level)
        >= _priority_score(minimum)
    )


# ============================================================
# Farmer Context Validation
# ============================================================

def validate_farmer_context(farmer_context):
    """
    Validate the canonical Farmer Context contract produced by
    build_farmer_context().

    Phase 3B intentionally does NOT support the old aliases:
        farmer.labor
        farmer.budget
        farmer.guidance_pref
        farmer.input_preference

    The canonical contract is owned by farmer_context.py.
    """
    if farmer_context is None:
        return {
            "valid": False,
            "status": "missing",
            "missing": ["farmer_context"],
            "errors": [],
            "warnings": [],
            "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
        }

    if not isinstance(farmer_context, dict):
        return {
            "valid": False,
            "status": "invalid",
            "missing": ["farmer_context must be a dict"],
            "errors": ["Farmer context must be a dictionary."],
            "warnings": [],
            "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
        }

    if validate_canonical_farmer_context is not None:
        canonical = validate_canonical_farmer_context(
            farmer_context,
            strict=False,
        )
        valid = bool(canonical.get("valid"))
        status = "valid" if valid else "partial"
        return {
            "valid": valid,
            "status": status,
            "missing": canonical.get("errors", []),
            "errors": canonical.get("errors", []),
            "warnings": canonical.get("warnings", []),
            "schema_version": canonical.get(
                "schema_version",
                FARMER_CONTEXT_SCHEMA_VERSION,
            ),
        }

    # Defensive fallback if the context module is unavailable.
    required_sections = (
        "farmer",
        "farm",
        "soil",
        "personalization",
        "meta",
    )
    missing = [
        section
        for section in required_sections
        if section not in farmer_context
    ]

    farmer = _safe_dict(farmer_context.get("farmer"))
    canonical_fields = (
        "labor_availability",
        "budget_constraint",
        "guidance_preference",
        "preferred_input_type",
    )

    for field in canonical_fields:
        if field not in farmer:
            missing.append(f"farmer.{field}")

    legacy_fields = (
        "labor",
        "budget",
        "guidance_pref",
        "input_preference",
    )
    for field in legacy_fields:
        if field in farmer:
            missing.append(
                f"legacy field farmer.{field} is not allowed"
            )

    if missing:
        return {
            "valid": False,
            "status": "partial",
            "missing": missing,
            "errors": missing,
            "warnings": [],
            "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
        }

    return {
        "valid": True,
        "status": "valid",
        "missing": [],
        "errors": [],
        "warnings": [],
        "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
    }


# ============================================================
# Context Extraction
# ============================================================

def _extract_context_parts(
    farmer_context
):
    """
    Extract farmer, farm, soil and personalization
    sections safely.

    This keeps the decision engine independent from the
    internal implementation of farmer_context.py.
    """

    context = _safe_dict(
        farmer_context
    )

    farmer = _safe_dict(
        context.get("farmer")
    )

    farm = _safe_dict(
        context.get("farm")
    )

    soil = _safe_dict(
        context.get("soil")
    )

    personalization = _safe_dict(
        context.get("personalization")
    )

    return (
        farmer,
        farm,
        soil,
        personalization,
    )


# ============================================================
# Dynamic Base Priority
# ============================================================

def calculate_priority(
    weather_risk,
    crop_stage,
    disease_count
):
    """
    Calculate the generic agricultural priority.

    This preserves the original Phase 3 logic.

    Inputs
    ------
    weather_risk:
        Low / Medium / High

    crop_stage:
        Current crop stage

    disease_count:
        Number of disease signals
    """

    crop_stage = _normalize_stage(
        crop_stage
    )

    weather_risk = (
        _normalize_text(
            weather_risk
        )
    )

    disease_count = disease_count or 0

    # --------------------------------------------------------
    # Critical
    # --------------------------------------------------------

    if (
        crop_stage == "flowering"
        and weather_risk == "high"
    ):

        return "Critical"

    if (
        disease_count >= 2
        and weather_risk == "high"
    ):

        return "Critical"

    # --------------------------------------------------------
    # High
    # --------------------------------------------------------

    if weather_risk == "high":

        return "High"

    # --------------------------------------------------------
    # Medium
    # --------------------------------------------------------

    if weather_risk == "medium":

        return "Medium"

    return "Low"


# ============================================================
# Weather → Action Intelligence
# ============================================================

def generate_weather_actions(
    weather_packet
):
    """
    Convert weather signals into recommendations.

    Existing weather intelligence remains authoritative.
    """

    recommendations = []

    weather_packet = _safe_dict(
        weather_packet
    )

    if weather_packet.get(
        "status"
    ) != "success":

        return recommendations

    risk = _safe_dict(
        weather_packet.get("risk")
    )

    signals = _safe_dict(
        weather_packet.get("signals")
    )

    risk_level = risk.get(
        "risk_level"
    )

    risk_type = _normalize_text(
        risk.get("risk_type")
    )

    impacts = _safe_list(
        risk.get("impact")
    )

    # --------------------------------------------------------
    # Flood / Rain
    # --------------------------------------------------------

    if risk_type == "flood":

        recommendations.append({

            "type": "weather_management",

            "priority": "High",

            "action":
                "Improve field drainage immediately",

            "reason":
                "Weather intelligence indicates flood or excess-rain risk.",

            "source":
                "weather"
        })

        recommendations.append({

            "type": "crop_protection",

            "priority": "High",

            "action":
                "Avoid standing water around root zone",

            "reason":
                "Excess water can increase crop stress.",

            "source":
                "weather"
        })

    # --------------------------------------------------------
    # Drought
    # --------------------------------------------------------

    elif risk_type == "drought":

        recommendations.append({

            "type": "irrigation_management",

            "priority": "High",

            "action":
                "Increase irrigation scheduling frequency",

            "reason":
                "Weather intelligence indicates drought risk.",

            "source":
                "weather"
        })

        recommendations.append({

            "type": "soil_management",

            "priority": "Medium",

            "action":
                "Reduce soil moisture loss using mulching",

            "reason":
                "Reducing moisture loss supports water management during dry conditions.",

            "source":
                "weather"
        })

    # --------------------------------------------------------
    # Heat Stress
    # --------------------------------------------------------

    elif risk_type == "heat_stress":

        recommendations.append({

            "type": "heat_management",

            "priority": "High",

            "action":
                "Maintain adequate soil moisture during heat stress",

            "reason":
                "Weather intelligence indicates heat-stress risk.",

            "source":
                "weather"
        })

        recommendations.append({

            "type": "crop_monitoring",

            "priority": "Medium",

            "action":
                "Monitor leaf rolling and flower stress symptoms",

            "reason":
                "Heat conditions can increase crop stress.",

            "source":
                "weather"
        })

    # --------------------------------------------------------
    # High Humidity
    # --------------------------------------------------------

    elif risk_type == "humidity":

        recommendations.append({

            "type": "disease_prevention",

            "priority": "High",

            "action":
                "Increase disease scouting frequency",

            "reason":
                "Weather intelligence indicates elevated humidity-related risk.",

            "source":
                "weather"
        })

        recommendations.append({

            "type": "field_management",

            "priority": "Medium",

            "action":
                "Improve field aeration and drainage",

            "reason":
                "Field conditions can influence disease pressure.",

            "source":
                "weather"
        })

    # --------------------------------------------------------
    # Signal-Based Intelligence
    # --------------------------------------------------------

    if signals.get(
        "spraying_safe"
    ) is False:

        recommendations.append({

            "type": "spraying_advisory",

            "priority": "Medium",

            "action":
                "Avoid pesticide spraying during expected rainfall",

            "reason":
                "Weather operational signal indicates spraying is unsafe.",

            "source":
                "weather"
        })

    if signals.get(
        "irrigation_needed"
    ):

        recommendations.append({

            "type": "irrigation_alert",

            "priority": "High",

            "action":
                "Immediate irrigation planning recommended",

            "reason":
                "Weather intelligence indicates irrigation is needed.",

            "source":
                "weather"
        })

    # --------------------------------------------------------
    # Impact Intelligence
    # --------------------------------------------------------

    for impact in impacts:

        recommendations.append({

            "type": "risk_impact",

            "priority":
                risk_level or "Medium",

            "action":
                f"Monitor crop impact: {impact}",

            "reason":
                "Weather intelligence identified a crop-impact signal.",

            "source":
                "weather"
        })

    return recommendations


# ============================================================
# Stage-Aware Intervention Logic
# ============================================================

def generate_stage_actions(
    crop_stage,
    stage_packet
):
    """
    Generate recommendations from Crop Master stage
    intelligence.

    Crop Master remains the source of agricultural truth.
    """

    recommendations = []

    stage_packet = _safe_dict(
        stage_packet
    )

    if stage_packet.get(
        "status"
    ) != "success":

        return recommendations

    normalized_stage = _normalize_stage(
        crop_stage
    )

    sensitivity = stage_packet.get(
        "sensitivity"
    )

    critical_operations = _safe_list(
        stage_packet.get(
            "critical_operations"
        )
    )

    avoid_actions = _safe_list(
        stage_packet.get(
            "avoid_actions"
        )
    )

    # --------------------------------------------------------
    # Flowering
    # --------------------------------------------------------

    if normalized_stage == "flowering":

        recommendations.append({

            "type": "flowering_protection",

            "priority": "Critical",

            "action":
                "Avoid moisture stress during flowering",

            "reason":
                "The crop is currently at the flowering stage.",

            "source":
                "crop_stage"
        })

        recommendations.append({

            "type": "pollination_protection",

            "priority": "High",

            "action":
                "Maintain stable field conditions during pollination",

            "reason":
                "The crop is currently at the flowering stage.",

            "source":
                "crop_stage"
        })

    # --------------------------------------------------------
    # Sensitivity
    # --------------------------------------------------------

    if _normalize_text(
        sensitivity
    ) == "high":

        recommendations.append({

            "type": "sensitivity_management",

            "priority": "High",

            "action":
                "High sensitivity stage requires continuous monitoring",

            "reason":
                "Crop Master marks the current stage as highly sensitive.",

            "source":
                "crop_stage"
        })

    # --------------------------------------------------------
    # Critical Operations
    # --------------------------------------------------------

    for operation in critical_operations:

        recommendations.append({

            "type": "critical_operation",

            "priority": "Medium",

            "action":
                str(operation),

            "reason":
                "This operation is listed as important for the current crop stage.",

            "source":
                "crop_stage"
        })

    # --------------------------------------------------------
    # Avoid Actions
    # --------------------------------------------------------

    for item in avoid_actions:

        recommendations.append({

            "type": "avoid_action",

            "priority": "High",

            "action":
                f"Avoid: {str(item)}",

            "reason":
                "Crop Master identifies this as an action to avoid at the current stage.",

            "source":
                "crop_stage"
        })

    return recommendations


# ============================================================
# Market Intelligence
# ============================================================

def generate_market_actions(
    market_packet
):
    """
    Convert market intelligence into advisory actions.

    Static/demo market data is treated only as the supplied
    market snapshot. It is not represented as live data.
    """

    recommendations = []

    market_packet = _safe_dict(
        market_packet
    )

    if market_packet.get(
        "status"
    ) != "success":

        return recommendations

    trend = _safe_dict(
        market_packet.get("trend")
    )

    signals = _safe_dict(
        market_packet.get("signals")
    )

    direction = _normalize_text(
        trend.get("direction")
    )

    # --------------------------------------------------------
    # Increasing
    # --------------------------------------------------------

    if direction == "increasing":

        recommendations.append({

            "type": "market_strategy",

            "priority": "Low",

            "action":
                "Consider delayed selling if storage is available",

            "reason":
                "The supplied market snapshot shows an increasing price trend.",

            "source":
                "market"
        })

    # --------------------------------------------------------
    # Decreasing
    # --------------------------------------------------------

    elif direction == "decreasing":

        recommendations.append({

            "type": "market_strategy",

            "priority": "Medium",

            "action":
                "Monitor mandi prices closely for selling opportunity",

            "reason":
                "The supplied market snapshot shows a decreasing price trend.",

            "source":
                "market"
        })

    # --------------------------------------------------------
    # Market Signals
    # --------------------------------------------------------

    if signals.get(
        "sell"
    ):

        recommendations.append({

            "type": "market_signal",

            "priority": "Medium",

            "action":
                "Current market conditions support selling",

            "reason":
                "The market engine supplied a selling signal.",

            "source":
                "market"
        })

    if signals.get(
        "hold"
    ):

        recommendations.append({

            "type": "market_signal",

            "priority": "Low",

            "action":
                "Holding crop may improve future returns",

            "reason":
                "The market engine supplied a holding signal.",

            "source":
                "market"
        })

    return recommendations


# ============================================================
# Water Management Formatter
# ============================================================

def _format_water_management(
    water_management
):
    """
    Convert water-management packet into readable text.
    """

    if not water_management:

        return None

    if isinstance(
        water_management,
        dict
    ):

        parts = []

        requirement = water_management.get(
            "requirement"
        )

        irrigation_frequency = water_management.get(
            "irrigation_frequency"
        )

        drainage_required = water_management.get(
            "drainage_required"
        )

        critical_condition = water_management.get(
            "critical_condition"
        )

        soil_moisture = water_management.get(
            "soil_moisture"
        )

        if requirement:

            parts.append(
                f"Maintain {str(requirement).lower()} water availability"
            )

        if soil_moisture:

            parts.append(
                f"Keep soil moisture {str(soil_moisture).lower()}"
            )

        if irrigation_frequency:

            freq_text = str(
                irrigation_frequency
            ).strip()

            freq_lower = freq_text.lower()

            if freq_lower.startswith((
                "irrigate",
                "maintain",
                "keep",
                "avoid",
                "stop"
            )):

                parts.append(
                    freq_text
                )

            elif "continuous moisture" in freq_lower:

                parts.append(
                    "Maintain continuous soil moisture"
                )

            else:

                parts.append(
                    f"Irrigation schedule: {freq_text}"
                )

        if drainage_required is True:

            parts.append(
                "Keep drainage ready to prevent waterlogging"
            )

        elif drainage_required is False:

            parts.append(
                "Drainage intervention is only needed if waterlogging appears"
            )

        if critical_condition:

            parts.append(
                str(critical_condition)
            )

        if parts:

            return (
                ". ".join(parts)
                + "."
            )

    if isinstance(
        water_management,
        list
    ):

        return "; ".join(
            str(item)
            for item in water_management
        )

    return str(
        water_management
    )


# ============================================================
# Water Intelligence
# ============================================================

def generate_water_actions(
    water_packet
):
    """
    Convert standard water intelligence into recommendations.
    """

    recommendations = []

    water_packet = _safe_dict(
        water_packet
    )

    if water_packet.get(
        "status"
    ) != "success":

        return recommendations

    water_management = water_packet.get(
        "water_management"
    )

    water_advisory = _format_water_management(
        water_management
    )

    if water_advisory:

        recommendations.append({

            "type": "water_management",

            "priority": "Medium",

            "action":
                water_advisory,

            "reason":
                "Water intelligence supplied the current irrigation and moisture guidance.",

            "source":
                "water"
        })

    return recommendations


# ============================================================
# Disease Intelligence
# ============================================================

def generate_disease_actions(
    disease_packet
):
    """
    Preserve disease engine output while converting disease
    information into decision-layer recommendations.

    No disease facts are invented here.
    """

    recommendations = []

    disease_packet = _safe_dict(
        disease_packet
    )

    if disease_packet.get(
        "status"
    ) != "success":

        return recommendations

    diseases = _safe_list(
        disease_packet.get(
            "diseases"
        )
    )

    for disease in diseases:

        disease = _safe_dict(
            disease
        )

        disease_name = disease.get(
            "name"
        )

        severity = disease.get(
            "severity"
        )

        prevention = _safe_list(
            disease.get(
                "prevention"
            )
        )

        if not disease_name:

            continue

        prevention_text = (
            "; ".join(
                str(item)
                for item in prevention
            )
            if prevention
            else
            "Increase monitoring according to the existing disease guidance."
        )

        recommendations.append({

            "type": "disease_prevention",

            "priority":
                (
                    "High"
                    if _normalize_text(
                        severity
                    ) in (
                        "high",
                        "severe",
                        "critical",
                    )
                    else "Medium"
                ),

            "action":
                f"Monitor and manage {disease_name}: {prevention_text}",

            "reason":
                f"{disease_name} is present in the existing disease intelligence for this crop stage.",

            "source":
                "disease",

            "disease_name":
                disease_name,

            "disease_severity":
                severity,
        })

    return recommendations


# ============================================================
# Farmer Context → Relevant Signals
# ============================================================

def _build_context_signals(
    farmer,
    farm,
    soil,
    personalization,
    crop,
    stage
):
    """
    Build normalized Phase 3B decision signals from the
    canonical Farmer Context.

    IMPORTANT:
    This function consumes ONLY the canonical schema emitted by
    build_farmer_context(). No legacy naming aliases are supported.
    """
    farmer = _safe_dict(farmer)
    farm = _safe_dict(farm)
    soil = _safe_dict(soil)
    personalization = _safe_dict(personalization)

    normalized_crop = _normalize_crop(crop)
    normalized_stage = _normalize_stage(stage)

    # Canonical Farmer Context fields.
    labor_availability = _normalize_text(
        farmer.get("labor_availability")
    )
    budget_constraint = _normalize_text(
        farmer.get("budget_constraint")
    )
    guidance_preference = _normalize_text(
        farmer.get("guidance_preference")
    )
    preferred_input_type = _normalize_text(
        farmer.get("preferred_input_type")
    )
    primary_objective = _normalize_text(
        farmer.get("primary_objective")
    )
    market_access = _normalize_text(
        farmer.get("market_access")
    )

    # Canonical Farm Context fields.
    irrigation_reliability = _normalize_text(
        farm.get("irrigation_reliability")
    )

    # Canonical Soil Context fields.
    nitrogen_status = _normalize_text(
        soil.get("nitrogen_status")
    )
    phosphorus_status = _normalize_text(
        soil.get("phosphorus_status")
    )
    potassium_status = _normalize_text(
        soil.get("potassium_status")
    )
    fertility_level = _normalize_text(
        soil.get("fertility_level")
    )
    drainage = _normalize_text(
        soil.get("drainage_characteristics")
    )
    waterlogging = _normalize_text(
        soil.get("waterlogging_risk")
    )
    organic_carbon = soil.get("organic_carbon_percent")

    signals = {
        # Farmer constraints/preferences.
        "budget_limited": (
            bool(personalization.get("budget_limited"))
            or budget_constraint == "low"
        ),
        "labor_limited": (
            bool(personalization.get("labor_limited"))
            or labor_availability == "limited"
        ),
        "preventive_guidance": (
            guidance_preference == "preventive"
        ),
        "reactive_guidance": (
            guidance_preference == "reactive"
        ),
        "organic_preference": (
            preferred_input_type == "organic"
        ),
        "integrated_preference": (
            preferred_input_type == "integrated"
        ),
        "chemical_preference": (
            preferred_input_type == "chemical"
        ),
        "income_objective": (
            primary_objective in {
                "income",
                "market",
                "export",
            }
        ),
        "single_market": (
            bool(personalization.get("single_market"))
            or market_access == "local mandi only"
        ),

        # Water.
        "unreliable_irrigation": (
            bool(personalization.get("unreliable_irrigation"))
            or irrigation_reliability == "unreliable"
        ),
        "seasonal_irrigation": (
            bool(personalization.get("seasonal_irrigation"))
            or irrigation_reliability == "seasonal"
        ),

        # Soil.
        "nitrogen_deficient": (
            bool(personalization.get("nitrogen_deficient"))
            or nitrogen_status == "deficient"
        ),
        "phosphorus_deficient": (
            phosphorus_status == "deficient"
        ),
        "potassium_deficient": (
            potassium_status == "deficient"
        ),
        "waterlogging_risk": (
            bool(personalization.get("elevated_waterlogging_risk"))
            or waterlogging in {"medium", "high"}
        ),
        "poor_drainage": (
            "poor" in drainage
        ),
        "low_soil_fertility": (
            bool(personalization.get("low_soil_fertility"))
            or fertility_level == "low"
        ),
        "low_organic_carbon": (
            bool(personalization.get("low_organic_carbon"))
            or (
                organic_carbon is not None
                and organic_carbon < 0.5
            )
        ),

        # History.
        "blast_disease_history": bool(
            personalization.get("blast_disease_history")
        ),
        "irregular_rainfall_history": bool(
            personalization.get("irregular_rainfall_history")
        ),
        "soil_fertility_concern": bool(
            personalization.get("soil_fertility_concern")
        ),

        # Context identity.
        "farmer_id": farmer.get("farmer_id"),
        "farm_id": farm.get("farm_id"),
        "crop": normalized_crop,
        "stage": normalized_stage,
        "labor_availability": farmer.get("labor_availability"),
        "budget_constraint": farmer.get("budget_constraint"),
        "guidance_preference": farmer.get("guidance_preference"),
        "preferred_input_type": farmer.get("preferred_input_type"),
    }

    return signals


# ============================================================
# Personalization — Soil
# ============================================================

def generate_soil_personalization_actions(
    context_signals,
    crop,
    stage
):
    """
    Personalize fertilizer, water and field-risk priorities
    from soil conditions.

    Soil does not modify generic Crop Master facts.
    It only changes the priority of relevant decisions.
    """

    recommendations = []

    signals = _safe_dict(
        context_signals
    )

    crop_normalized = _normalize_crop(
        crop
    )

    # --------------------------------------------------------
    # Nitrogen deficiency
    # --------------------------------------------------------

    if signals.get(
        "nitrogen_deficient"
    ):

        recommendations.append({

            "type": "soil_nutrient_priority",

            "priority": "High",

            "action":
                "Prioritize the existing nitrogen-management guidance for this field",

            "reason":
                "The soil profile reports nitrogen deficiency.",

            "source":
                "farmer_context",

            "context_factor":
                "nitrogen_deficient",
        })

    # --------------------------------------------------------
    # Phosphorus deficiency
    # --------------------------------------------------------

    if signals.get(
        "phosphorus_deficient"
    ):

        recommendations.append({

            "type": "soil_nutrient_priority",

            "priority": "High",

            "action":
                "Prioritize the existing phosphorus-management guidance for this field",

            "reason":
                "The soil profile reports phosphorus deficiency.",

            "source":
                "farmer_context",

            "context_factor":
                "phosphorus_deficient",
        })

    # --------------------------------------------------------
    # Potassium deficiency
    # --------------------------------------------------------

    if signals.get(
        "potassium_deficient"
    ):

        recommendations.append({

            "type": "soil_nutrient_priority",

            "priority": "High",

            "action":
                "Prioritize the existing potassium-management guidance for this field",

            "reason":
                "The soil profile reports potassium deficiency.",

            "source":
                "farmer_context",

            "context_factor":
                "potassium_deficient",
        })

    # --------------------------------------------------------
    # Waterlogging
    # --------------------------------------------------------

    if signals.get(
        "waterlogging_risk"
    ):

        recommendations.append({

            "type": "soil_water_management",

            "priority": "High",

            "action":
                "Prioritize drainage and waterlogging prevention for this field",

            "reason":
                "The soil profile indicates elevated waterlogging risk.",

            "source":
                "farmer_context",

            "context_factor":
                "waterlogging_risk",
        })

    # --------------------------------------------------------
    # Low fertility
    # --------------------------------------------------------

    if signals.get(
        "low_soil_fertility"
    ):

        recommendations.append({

            "type": "soil_fertility",

            "priority": "Medium",

            "action":
                "Prioritize the existing soil-fertility management guidance",

            "reason":
                "The soil profile reports low fertility.",

            "source":
                "farmer_context",

            "context_factor":
                "low_soil_fertility",
        })

    # --------------------------------------------------------
    # Low organic carbon
    # --------------------------------------------------------

    if signals.get(
        "low_organic_carbon"
    ):

        recommendations.append({

            "type": "soil_health",

            "priority": "Medium",

            "action":
                "Prioritize the existing soil-health guidance for low organic carbon",

            "reason":
                "The soil profile reports organic carbon below the Phase 3 threshold.",

            "source":
                "farmer_context",

            "context_factor":
                "low_organic_carbon",
        })

    return recommendations


# ============================================================
# Personalization — Water Constraints
# ============================================================

def generate_water_constraint_actions(
    context_signals
):
    """
    Personalize water-related recommendations using only
    irrigation-relevant context.
    """

    recommendations = []

    signals = _safe_dict(
        context_signals
    )

    # --------------------------------------------------------
    # Unreliable irrigation
    # --------------------------------------------------------

    if signals.get(
        "unreliable_irrigation"
    ):

        recommendations.append({

            "type": "water_constraint",

            "priority": "High",

            "action":
                "Prioritize water-efficient and time-critical irrigation decisions",

            "reason":
                "The farm reports unreliable irrigation availability.",

            "source":
                "farmer_context",

            "context_factor":
                "unreliable_irrigation",
        })

    # --------------------------------------------------------
    # Seasonal irrigation
    # --------------------------------------------------------

    elif signals.get(
        "seasonal_irrigation"
    ):

        recommendations.append({

            "type": "water_constraint",

            "priority": "Medium",

            "action":
                "Plan irrigation-dependent operations around reliable water-supply windows",

            "reason":
                "The farm reports seasonal irrigation availability.",

            "source":
                "farmer_context",

            "context_factor":
                "seasonal_irrigation",
        })

    return recommendations


# ============================================================
# Personalization — Disease History
# ============================================================

def generate_disease_history_actions(
    context_signals,
    crop
):
    """
    Elevate disease-prevention priority only when farmer
    history is relevant to the selected crop.
    """

    recommendations = []

    signals = _safe_dict(
        context_signals
    )

    crop_normalized = _normalize_crop(
        crop
    )

    # --------------------------------------------------------
    # Rice Blast History
    # --------------------------------------------------------

    if (
        signals.get(
            "blast_disease_history"
        )
        and crop_normalized == "rice"
    ):

        recommendations.append({

            "type": "historical_disease_risk",

            "priority": "High",

            "action":
                "Elevate the existing rice disease-prevention guidance because Blast Disease is a recurring farm problem",

            "reason":
                "The farmer context records recurring Blast Disease on this farm and the selected crop is rice.",

            "source":
                "farmer_context",

            "context_factor":
                "blast_disease_history",
        })

    return recommendations


# ============================================================
# Personalization — Budget
# ============================================================

def generate_budget_actions(
    context_signals
):
    """
    Apply budget constraints to operational prioritization.

    Important:
    Budget does not change agricultural facts.
    It changes feasibility and prioritization.
    """

    recommendations = []

    signals = _safe_dict(
        context_signals
    )

    if signals.get(
        "budget_limited"
    ):

        recommendations.append({

            "type": "budget_constraint",

            "priority": "High",

            "action":
                "Prioritize essential interventions first and avoid non-essential expenditure",

            "reason":
                "The farmer profile reports a low budget constraint.",

            "source":
                "farmer_context",

            "context_factor":
                "budget_limited",
        })

    return recommendations


# ============================================================
# Personalization — Labour
# ============================================================

def generate_labor_actions(
    context_signals
):
    """
    Apply labour constraints to operational feasibility.

    Labour does not modify Crop Master facts.
    It changes which actions should be prioritized first.
    """

    recommendations = []

    signals = _safe_dict(
        context_signals
    )

    if signals.get(
        "labor_limited"
    ):

        recommendations.append({

            "type": "labor_constraint",

            "priority": "High",

            "action":
                "Prioritize time-critical and lower-effort operations before non-essential activities",

            "reason":
                "The farmer profile reports limited labour availability.",

            "source":
                "farmer_context",

            "context_factor":
                "labor_limited",
        })

    return recommendations


# ============================================================
# Personalization — Market Access
# ============================================================

def generate_market_context_actions(
    context_signals,
    market_packet
):
    """
    Personalize market decisions using market access.

    The market engine remains responsible for market facts.
    """

    recommendations = []

    signals = _safe_dict(
        context_signals
    )

    market_packet = _safe_dict(
        market_packet
    )

    if not signals.get(
        "single_market"
    ):

        return recommendations

    if market_packet.get(
        "status"
    ) != "success":

        return recommendations

    recommendations.append({

        "type": "market_access_constraint",

        "priority": "Medium",

        "action":
            "Use the available local mandi information carefully when planning the selling decision",

        "reason":
            "The farmer reports access to the local mandi only.",

        "source":
            "farmer_context",

        "context_factor":
            "single_market",
    })

    return recommendations


# ============================================================
# Personalization — Guidance Preference
# ============================================================

def generate_guidance_preference_actions(
    context_signals
):
    """
    Record the farmer's guidance preference as a presentation
    and prioritization signal.

    It does NOT modify agricultural facts.
    """

    recommendations = []

    signals = _safe_dict(
        context_signals
    )

    if signals.get(
        "preventive_guidance"
    ):

        recommendations.append({

            "type": "guidance_preference",

            "priority": "Medium",

            "action":
                "Prefer preventive actions when multiple relevant actions have similar priority",

            "reason":
                "The farmer prefers preventive guidance.",

            "source":
                "farmer_context",

            "context_factor":
                "guidance_preference",
        })

    return recommendations


# ============================================================
# Apply Farmer Context to Existing Recommendations
# ============================================================

def apply_context_to_recommendations(
    recommendations,
    context_signals,
    crop,
    stage
):
    """
    Adjust existing engine recommendation priorities based
    on relevant farmer context.

    This is the key Phase 3B personalization step.

    The function does NOT rewrite agricultural knowledge.
    It only adjusts decision priority where the relationship
    is explicitly defined.
    """

    recommendations = list(
        recommendations or []
    )

    signals = _safe_dict(
        context_signals
    )

    crop_normalized = _normalize_crop(
        crop
    )

    stage_normalized = _normalize_stage(
        stage
    )

    adjusted = []

    for item in recommendations:

        item = dict(
            item
        )

        recommendation_type = _normalize_text(
            item.get("type")
        )

        action = _normalize_text(
            item.get("action")
        )

        original_priority = (
            item.get("priority")
            if item.get("priority")
            in VALID_PRIORITIES
            else "Medium"
        )

        priority = original_priority

        reasons = []

        # ----------------------------------------------------
        # WATER CONSTRAINT
        # ----------------------------------------------------

        if (
            signals.get(
                "unreliable_irrigation"
            )
            or signals.get(
                "seasonal_irrigation"
            )
        ):

            if (
                "irrigation" in recommendation_type
                or "water" in recommendation_type
                or "irrigation" in action
                or "water" in action
            ):

                priority = _increase_priority(
                    priority
                )

                reasons.append(
                    "Irrigation availability is constrained on this farm."
                )

        # ----------------------------------------------------
        # WATERLOGGING / DRAINAGE
        # ----------------------------------------------------

        if signals.get(
            "waterlogging_risk"
        ):

            if (
                "drainage" in recommendation_type
                or "waterlogging" in action
                or "drainage" in action
                or "flood" in action
            ):

                priority = _increase_priority(
                    priority
                )

                reasons.append(
                    "The soil profile indicates elevated waterlogging risk."
                )

        # ----------------------------------------------------
        # NUTRIENT DEFICIENCY
        # ----------------------------------------------------

        if (
            signals.get(
                "nitrogen_deficient"
            )
            and (
                "fertilizer" in recommendation_type
                or "nutrient" in recommendation_type
                or "nitrogen" in action
                or "fertilizer" in action
                or "nutrient" in action
            )
        ):

            priority = _increase_priority(
                priority
            )

            reasons.append(
                "The soil profile reports nitrogen deficiency."
            )

        if (
            signals.get(
                "phosphorus_deficient"
            )
            and (
                "fertilizer" in recommendation_type
                or "nutrient" in recommendation_type
                or "phosphorus" in action
                or "fertilizer" in action
                or "nutrient" in action
            )
        ):

            priority = _increase_priority(
                priority
            )

            reasons.append(
                "The soil profile reports phosphorus deficiency."
            )

        if (
            signals.get(
                "potassium_deficient"
            )
            and (
                "fertilizer" in recommendation_type
                or "nutrient" in recommendation_type
                or "potassium" in action
                or "fertilizer" in action
                or "nutrient" in action
            )
        ):

            priority = _increase_priority(
                priority
            )

            reasons.append(
                "The soil profile reports potassium deficiency."
            )

        # ----------------------------------------------------
        # DISEASE HISTORY
        # ----------------------------------------------------

        if (
            signals.get(
                "blast_disease_history"
            )
            and crop_normalized == "rice"
            and (
                "disease" in recommendation_type
                or "disease" in action
                or "blast" in action
            )
        ):

            priority = _increase_priority(
                priority
            )

            reasons.append(
                "Blast Disease is recorded as a recurring problem on this farm."
            )

        # ----------------------------------------------------
        # LOW ORGANIC CARBON / SOIL HEALTH
        # ----------------------------------------------------

        if (
            signals.get(
                "low_organic_carbon"
            )
            and (
                "soil" in recommendation_type
                or "organic" in action
                or "soil health" in action
            )
        ):

            priority = _increase_priority(
                priority
            )

            reasons.append(
                "The soil profile reports low organic carbon."
            )

        # ----------------------------------------------------
        # BUDGET CONSTRAINT
        # ----------------------------------------------------

        if signals.get(
            "budget_limited"
        ):

            # Market strategy is not automatically made more
            # important by low budget.
            #
            # Essential nutrient/water/disease operations
            # retain their importance.
            if recommendation_type in (
                "market_strategy",
                "market_signal",
            ):

                if not _is_priority_at_least(
                    priority,
                    "High"
                ):

                    priority = _decrease_priority(
                        priority
                    )

                    reasons.append(
                        "Low budget means essential farm interventions take precedence over optional market actions."
                    )

        # ----------------------------------------------------
        # LABOUR CONSTRAINT
        # ----------------------------------------------------

        if signals.get(
            "labor_limited"
        ):

            # Only deprioritize generic, non-critical
            # operational actions.
            #
            # Safety/risk actions remain important.
            if (
                recommendation_type
                in (
                    "critical_operation",
                    "field_management",
                    "crop_monitoring",
                )
                and not _is_priority_at_least(
                    priority,
                    "Critical"
                )
            ):

                priority = _decrease_priority(
                    priority
                )

                reasons.append(
                    "Limited labour requires time-critical and essential operations to be prioritized."
                )

        # ----------------------------------------------------
        # FLOWERING + CONSTRAINTS
        # ----------------------------------------------------

        if stage_normalized == "flowering":

            if (
                signals.get(
                    "unreliable_irrigation"
                )
                or signals.get(
                    "seasonal_irrigation"
                )
            ):

                if (
                    "flowering" in recommendation_type
                    or "irrigation" in recommendation_type
                    or "water" in recommendation_type
                ):

                    priority = _increase_priority(
                        priority
                    )

                    reasons.append(
                        "Water constraints are especially relevant while the crop is at flowering."
                    )

        # ----------------------------------------------------
        # Store context influence
        # ----------------------------------------------------

        if reasons:

            item["base_priority"] = (
                original_priority
            )

            item["priority"] = (
                priority
            )

            item["personalization_applied"] = True

            existing_reasons = _safe_list(
                item.get("personalization_reasons")
            )

            item["personalization_reasons"] = (
                existing_reasons
                + reasons
            )

        else:

            item.setdefault(
                "base_priority",
                original_priority
            )

            item.setdefault(
                "personalization_applied",
                False
            )

        adjusted.append(
            item
        )

    return adjusted


# ============================================================
# Priority Adjustment from Context
# ============================================================

def calculate_personalized_priority(
    base_priority,
    context_signals,
    recommendations
):
    """
    Calculate the overall farmer-specific priority.

    Context affects overall priority only when it creates a
    relevant decision constraint or risk.
    """

    priority = (
        base_priority
        if base_priority in VALID_PRIORITIES
        else "Low"
    )

    signals = _safe_dict(
        context_signals
    )

    # --------------------------------------------------------
    # High-impact context constraints
    # --------------------------------------------------------

    high_impact = 0

    if signals.get(
        "unreliable_irrigation"
    ):

        high_impact += 1

    if signals.get(
        "waterlogging_risk"
    ):

        high_impact += 1

    if signals.get(
        "nitrogen_deficient"
    ):

        high_impact += 1

    if signals.get(
        "blast_disease_history"
    ):

        high_impact += 1

    # --------------------------------------------------------
    # Only escalate the overall priority when the context
    # actually creates relevant decision pressure.
    # --------------------------------------------------------

    if high_impact >= 2:

        priority = _increase_priority(
            priority
        )

    elif high_impact == 1:

        # Do not automatically turn Low into Critical.
        # One relevant context signal can raise the priority
        # by one level.
        priority = _increase_priority(
            priority
        )

    # --------------------------------------------------------
    # Check personalized recommendations
    # --------------------------------------------------------

    personalized_priorities = [

        item.get("priority")
        for item in recommendations
        if item.get(
            "personalization_applied"
        )
    ]

    if personalized_priorities:

        strongest = max(
            personalized_priorities,
            key=_priority_score
        )

        if (
            _priority_score(strongest)
            > _priority_score(priority)
        ):

            priority = strongest

    return priority


# ============================================================
# Personalization Summary
# ============================================================

def build_personalization_summary(
    context_signals,
    recommendations
):
    """
    Produce a compact, explainable summary of why the
    recommendation changed for this farmer.
    """

    signals = _safe_dict(
        context_signals
    )

    active_factors = []

    factor_labels = {

        "nitrogen_deficient":
            "Nitrogen-deficient soil",

        "phosphorus_deficient":
            "Phosphorus-deficient soil",

        "potassium_deficient":
            "Potassium-deficient soil",

        "waterlogging_risk":
            "Elevated waterlogging risk",

        "unreliable_irrigation":
            "Unreliable irrigation",

        "seasonal_irrigation":
            "Seasonal irrigation",

        "budget_limited":
            "Low budget constraint",

        "labor_limited":
            "Limited labour",

        "blast_disease_history":
            "Recurring Blast Disease history",

        "low_soil_fertility":
            "Low soil fertility",

        "low_organic_carbon":
            "Low organic carbon",

        "single_market":
            "Local mandi-only market access",
    }

    for key, label in factor_labels.items():

        if signals.get(key):

            active_factors.append(
                label
            )

    # --------------------------------------------------------
    # Reasons from recommendations
    # --------------------------------------------------------

    reasons = []

    for item in recommendations:

        if not item.get(
            "personalization_applied"
        ):

            continue

        for reason in _safe_list(
            item.get(
                "personalization_reasons"
            )
        ):

            if reason not in reasons:

                reasons.append(
                    reason
                )

    return {

        "active_factors":
            active_factors,

        "reasons":
            reasons,

        "personalized_recommendation_count":
            sum(
                1
                for item in recommendations
                if item.get(
                    "personalization_applied"
                )
            ),
    }


# ============================================================
# Recommendation Deduplication
# ============================================================

def synthesize_advisories(
    recommendations
):
    """
    Remove duplicates and sort recommendations.

    Personalized recommendations retain their explanations.
    """

    unique = []

    seen = set()

    for item in recommendations:

        item = dict(
            item
        )

        action = item.get(
            "action"
        )

        # ----------------------------------------------------
        # Normalize action safely
        # ----------------------------------------------------

        if isinstance(
            action,
            dict
        ):

            key = json.dumps(
                action,
                sort_keys=True
            )

        elif isinstance(
            action,
            list
        ):

            key = json.dumps(
                action,
                sort_keys=True
            )

        else:

            key = str(
                action
            ).strip().lower()

        # ----------------------------------------------------
        # Include recommendation type
        # so two different recommendation categories with
        # identical text are still distinguishable.
        # ----------------------------------------------------

        unique_key = (
            str(
                item.get(
                    "type"
                )
            )
            + "|"
            + key
        )

        if unique_key in seen:

            continue

        seen.add(
            unique_key
        )

        unique.append(
            item
        )

    # --------------------------------------------------------
    # Priority sorting
    # --------------------------------------------------------

    unique.sort(

        key=lambda x:
        _priority_score(
            x.get(
                "priority"
            )
        ),

        reverse=True
    )

    return unique


# ============================================================
# Final Recommendation Summary
# ============================================================

def build_final_recommendation(
    recommendations,
    priority,
    personalization_summary
):
    """
    Create a farmer-readable decision summary.

    This is intentionally deterministic.
    """

    if not recommendations:

        return {

            "headline":
                "No immediate recommendation generated.",

            "top_action":
                None,

            "why":
                [],

            "what_to_do":
                [],

            "what_to_avoid":
                [],
        }

    top = recommendations[0]

    top_action = top.get(
        "action"
    )

    why = []

    # --------------------------------------------------------
    # Top recommendation reason
    # --------------------------------------------------------

    if top.get(
        "reason"
    ):

        why.append(
            top.get(
                "reason"
            )
        )

    # --------------------------------------------------------
    # Personalization reason
    # --------------------------------------------------------

    for reason in _safe_list(
        top.get(
            "personalization_reasons"
        )
    ):

        if reason not in why:

            why.append(
                reason
            )

    # --------------------------------------------------------
    # Additional context reasons
    # --------------------------------------------------------

    for reason in _safe_list(
        personalization_summary.get(
            "reasons"
        )
    ):

        if reason not in why:

            why.append(
                reason
            )

    # --------------------------------------------------------
    # What to do
    # --------------------------------------------------------

    what_to_do = [

        item.get(
            "action"
        )
        for item in recommendations[:5]
        if item.get(
            "action"
        )
    ]

    # --------------------------------------------------------
    # What to avoid
    # --------------------------------------------------------

    what_to_avoid = [

        item.get(
            "action"
        )
        for item in recommendations
        if item.get(
            "type"
        ) == "avoid_action"
    ]

    return {

        "headline":
            f"Prioritize: {top_action}",

        "top_action":
            top_action,

        "why":
            why,

        "what_to_do":
            what_to_do,

        "what_to_avoid":
            what_to_avoid,
    }


# ============================================================
# Main Contextual Decision Engine
# ============================================================

def generate_contextual_advisory(
    crop,
    stage,
    state,
    district,
    farmer_context=None,
    agricultural_packet=None,
    timeline_context=None,
):
    """
    Generate the complete RAYA contextual advisory.

    Parameters
    ----------
    crop : str
        Crop name.

    stage : str
        Crop growth stage.

    state : str
        State.

    district : str
        District.

    farmer_context : dict, optional
        Canonical output of build_farmer_context().

        Expected structure:

        {
            "status": "active",
            "farmer": {...},
            "farm": {...},
            "soil": {...},
            "personalization": {...},
            "meta": {...}
        }

    Backward Compatibility
    ----------------------
    farmer_context is optional.

    Therefore this remains valid:

        generate_contextual_advisory(
            crop="rice",
            stage="Flowering",
            state="Karnataka",
            district="Mandya"
        )

    Phase 3B usage:

        agricultural_packet = farmer_search(
            crop="rice",
            stage="Flowering",
            state="Karnataka",
            district="Mandya",
        )

        generate_contextual_advisory(
            crop="rice",
            stage="Flowering",
            state="Karnataka",
            district="Mandya",
            farmer_context=context,
            agricultural_packet=agricultural_packet,
        )
    """

    # ========================================================
    # Validate basic inputs
    # ========================================================

    if not crop:

        return {

            "status":
                "error",

            "message":
                "Crop is required.",
        }

    if not stage:

        return {

            "status":
                "error",

            "message":
                "Crop stage is required.",
        }

    if not state:

        return {

            "status":
                "error",

            "message":
                "State is required.",
        }

    if not district:

        return {

            "status":
                "error",

            "message":
                "District is required.",
        }

    # ========================================================
    # Validate Farmer Context
    # ========================================================

    context_validation = validate_farmer_context(
        farmer_context
    )

    context_active = (
        context_validation.get(
            "valid"
        )
    )

    if context_active:

        (
            farmer,
            farm,
            soil,
            personalization
        ) = _extract_context_parts(
            farmer_context
        )

    else:

        farmer = {}
        farm = {}
        soil = {}
        personalization = {}

    # The selected decision must stay aligned with the farmer context.
    # This does not silently rewrite inputs; it reports mismatches.
    context_alignment_warnings = []

    if context_active:
        farm_location = {
            "state": farm.get("state"),
            "district": farm.get("district"),
        }

        if (
            farm_location["state"]
            and _normalize_text(farm_location["state"])
            != _normalize_text(state)
        ):
            context_alignment_warnings.append(
                "Farm context state differs from advisory state."
            )

        if (
            farm_location["district"]
            and _normalize_text(farm_location["district"])
            != _normalize_text(district)
        ):
            context_alignment_warnings.append(
                "Farm context district differs from advisory district."
            )

        selected_field = next(
            (
                field
                for field in _safe_list(farm.get("fields"))
                if (
                    _normalize_crop(field.get("current_crop"))
                    == _normalize_crop(crop)
                    and _normalize_stage(field.get("current_stage"))
                    == _normalize_stage(stage)
                )
            ),
            None,
        )

        if farm.get("fields") and selected_field is None:
            context_alignment_warnings.append(
                "No farm field exactly matches the selected crop and stage."
            )

    # ========================================================
    # Consume Unified Agricultural Packet
    # ========================================================
    #
    # Phase 3B integration rule:
    #   farmer_search() is executed by the orchestration layer
    #   exactly once. The decision engine consumes that packet.
    #
    # Backward compatibility:
    #   If agricultural_packet is not supplied, this function
    #   performs one search itself for direct/legacy callers.
    #   The Streamlit/backend production flow should always
    #   supply the already-generated packet.
    # ========================================================

    if agricultural_packet is None:
        packet = farmer_search(
            crop=crop,
            stage=stage,
            state=state,
            district=district,
        )
        search_executed_here = True
    else:
        packet = _safe_dict(agricultural_packet)
        search_executed_here = False

    if packet.get("status") != "success":
        return packet

    # ========================================================
    # Extract Intelligence
    # ========================================================

    weather_packet = _safe_dict(
        packet.get(
            "weather"
        )
    )

    market_packet = _safe_dict(
        packet.get(
            "market"
        )
    )

    water_packet = _safe_dict(
        packet.get(
            "water"
        )
    )

    stage_packet = _safe_dict(
        packet.get(
            "stage_snapshot"
        )
    )

    disease_packet = _safe_dict(
        packet.get(
            "diseases"
        )
    )

    fertilizer_packet = _safe_dict(
        packet.get(
            "fertilizer"
        )
    )

    diseases = _safe_list(
        disease_packet.get(
            "diseases"
        )
    )

    weather_risk = _safe_dict(
        weather_packet.get(
            "risk"
        )
    )

    weather_level = weather_risk.get(
        "risk_level"
    )

    # ========================================================
    # Generic Base Priority
    # ========================================================

    base_priority = calculate_priority(

        weather_level,

        stage,

        len(
            diseases
        )
    )

    # ========================================================
    # Generate Standard Intelligence Recommendations
    # ========================================================

    recommendations = []

    recommendations.extend(

        generate_weather_actions(
            weather_packet
        )
    )

    timeline_context = _safe_dict(timeline_context)
    timeline_recommendations = []
    for recommendation in _safe_list(
        timeline_context.get("recommendations")
    ):
        if not isinstance(recommendation, dict):
            continue
        action = recommendation.get("action")
        if not isinstance(action, str) or not action.strip():
            continue
        timeline_recommendations.append(
            {
                "type": "field_timeline",
                "action": action.strip(),
                "priority": recommendation.get(
                    "priority", "Medium"
                ),
                "personalization_applied": True,
                "personalization_reasons": _safe_list(
                    recommendation.get("personalization_reasons")
                ),
            }
        )
    recommendations.extend(timeline_recommendations)

    recommendations.extend(

        generate_stage_actions(
            stage,
            stage_packet
        )
    )

    recommendations.extend(

        generate_market_actions(
            market_packet
        )
    )

    recommendations.extend(

        generate_water_actions(
            water_packet
        )
    )

    recommendations.extend(

        generate_disease_actions(
            disease_packet
        )
    )

    # ========================================================
    # Contextual Personalization
    # ========================================================

    if context_active:

        context_signals = _build_context_signals(

            farmer,

            farm,

            soil,

            personalization,

            crop,

            stage
        )

        # ----------------------------------------------------
        # Soil-driven actions
        # ----------------------------------------------------

        recommendations.extend(

            generate_soil_personalization_actions(

                context_signals,

                crop,

                stage
            )
        )

        # ----------------------------------------------------
        # Water constraint
        # ----------------------------------------------------

        recommendations.extend(

            generate_water_constraint_actions(

                context_signals
            )
        )

        # ----------------------------------------------------
        # Disease history
        # ----------------------------------------------------

        recommendations.extend(

            generate_disease_history_actions(

                context_signals,

                crop
            )
        )

        # ----------------------------------------------------
        # Budget
        # ----------------------------------------------------

        recommendations.extend(

            generate_budget_actions(

                context_signals
            )
        )

        # ----------------------------------------------------
        # Labour
        # ----------------------------------------------------

        recommendations.extend(

            generate_labor_actions(

                context_signals
            )
        )

        # ----------------------------------------------------
        # Market access
        # ----------------------------------------------------

        recommendations.extend(

            generate_market_context_actions(

                context_signals,

                market_packet
            )
        )

        # ----------------------------------------------------
        # Guidance preference
        # ----------------------------------------------------

        recommendations.extend(

            generate_guidance_preference_actions(

                context_signals
            )
        )

        # ----------------------------------------------------
        # Apply context to existing recommendations
        # ----------------------------------------------------

        recommendations = apply_context_to_recommendations(

            recommendations,

            context_signals,

            crop,

            stage
        )

    else:

        context_signals = {}

    # ========================================================
    # Synthesize
    # ========================================================

    synthesized = synthesize_advisories(
        recommendations
    )

    # ========================================================
    # Personalized Overall Priority
    # ========================================================

    if context_active:

        priority = calculate_personalized_priority(

            base_priority,

            context_signals,

            synthesized
        )

    else:

        priority = base_priority

    # ========================================================
    # Personalization Summary
    # ========================================================

    personalization_summary = (
        build_personalization_summary(
            context_signals,
            synthesized
        )
        if context_active
        else
        {
            "active_factors": [],
            "reasons": [],
            "personalized_recommendation_count": 0,
        }
    )
    timeline_reasons = _safe_list(
        timeline_context.get("personalization_reasons")
    )
    for reason in timeline_reasons:
        if reason not in personalization_summary["reasons"]:
            personalization_summary["reasons"].append(reason)
    if timeline_reasons:
        if "Field history" not in personalization_summary["active_factors"]:
            personalization_summary["active_factors"].append(
                "Field history"
            )
        personalization_summary[
            "personalized_recommendation_count"
        ] += len(timeline_recommendations)

    # ========================================================
    # Final Recommendation
    # ========================================================

    final_recommendation = build_final_recommendation(

        synthesized,

        priority,

        personalization_summary
    )

    # ========================================================
    # Structured Decision Context
    # ========================================================

    decision_context = {

        "crop": crop,

        "stage": stage,

        "location": {

            "state":
                state,

            "district":
                district,
        },

        "farmer_context": {

            "available":
                context_active,

            "schema_version":
                context_validation.get(
                    "schema_version",
                    FARMER_CONTEXT_SCHEMA_VERSION,
                ),

            "alignment_warnings":
                context_alignment_warnings,

            "status":
                context_validation.get(
                    "status"
                ),

            "active_factors":
                personalization_summary.get(
                    "active_factors"
                ),
        },

        "intelligence": {

            "weather":
                weather_packet,

            "water":
                water_packet,

            "disease":
                disease_packet,

            "fertilizer":
                fertilizer_packet,

            "market":
                market_packet,

            "stage":
                stage_packet,
        },

        "personalization": {

            "signals":
                context_signals,

            "summary":
                personalization_summary,
        },

        "decision": {

            "base_priority":
                base_priority,

            "final_priority":
                priority,

            "recommendation_count":
                len(
                    synthesized
                ),
            "timeline_signals": _safe_list(
                timeline_context.get("signals")
            ),
        },
    }

    # ========================================================
    # Final Structured Advisory
    # ========================================================

    return {

        "status":
            "success",

        "meta": {

            "generated_at":
                utc_timestamp(),

            "engine":
                "RAYA Contextual Decision Engine",

            "version":
                "Phase 3B.1",

            "farmer_context_schema_version":
                context_validation.get(
                    "schema_version",
                    FARMER_CONTEXT_SCHEMA_VERSION,
                ),

            "personalization_active":
                context_active,

            "agricultural_packet_supplied":
                agricultural_packet is not None,

            "farmer_search_executed_here":
                search_executed_here,

            "context_validation":
                context_validation,
        },

        "location":
            packet.get(
                "location"
            ),

        "crop":
            packet.get(
                "crop"
            ),

        "stage":
            packet.get(
                "stage"
            ),

        "priority":
            priority,

        "signals": {

            "weather_risk":
                weather_level,

            "weather_type":
                weather_risk.get(
                    "risk_type"
                ),

            "market_trend":
                _safe_dict(
                    market_packet.get(
                        "trend"
                    )
                ).get(
                    "direction"
                ),

            "disease_count":
                len(
                    diseases
                ),

            "crop_stage":
                stage,

            "farmer_context_active":
                context_active,
        },

        # ----------------------------------------------------
        # Phase 3B context
        # ----------------------------------------------------

        "farmer_context": {

            "available":
                context_active,

            "farmer":
                farmer if context_active else {},

            "farm":
                farm if context_active else {},

            "soil":
                soil if context_active else {},

            "personalization_signals":
                context_signals,

            "active_factors":
                personalization_summary.get(
                    "active_factors"
                ),
        },

        # ----------------------------------------------------
        # Decision context
        # ----------------------------------------------------

        "decision_context":
            decision_context,

        # ----------------------------------------------------
        # Final recommendation
        # ----------------------------------------------------

        "final_recommendation":
            final_recommendation,

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        "recommendations":
            synthesized,

        "personalization_reasons":
            personalization_summary["reasons"],

        "timeline_context":
            timeline_context,
    }


# ============================================================
# Farmer-Friendly Advisory Viewer
# ============================================================

def show_contextual_advisory(
    packet
):
    """
    Print the contextual advisory in a farmer-readable
    terminal format.
    """

    if packet.get(
        "status"
    ) != "success":

        print(
            "\n❌ ERROR"
        )

        print(
            packet.get(
                "message"
            )
        )

        return

    print(
        "\n================================================"
    )

    print(
        "🧠 RAYA CONTEXTUAL DECISION REPORT"
    )

    print(
        "================================================\n"
    )

    print(
        f"Crop      : "
        f"{packet.get('crop')}"
    )

    print(
        f"Stage     : "
        f"{packet.get('stage')}"
    )

    location = _safe_dict(
        packet.get(
            "location"
        )
    )

    print(
        f"Location  : "
        f"{location.get('district')}, "
        f"{location.get('state')}"
    )

    print(
        f"Priority  : "
        f"{packet.get('priority')}"
    )

    # ========================================================
    # Farmer Context
    # ========================================================

    farmer_context = _safe_dict(
        packet.get(
            "farmer_context"
        )
    )

    if farmer_context.get(
        "available"
    ):

        farmer = _safe_dict(
            farmer_context.get(
                "farmer"
            )
        )

        print(
            "\n👨‍🌾 FARMER CONTEXT"
        )

        print(
            f"• Farmer: "
            f"{farmer.get('name')}"
        )

        print(
            f"• Objective: "
            f"{farmer.get('primary_objective')}"
        )

        print(
            f"• Budget: "
            f"{farmer.get('budget_constraint')}"
        )

        print(
            f"• Labour: "
            f"{farmer.get('labor_availability')}"
        )

        print(
            f"• Guidance: "
            f"{farmer.get('guidance_preference')}"
        )

        print(
            f"• Input type: "
            f"{farmer.get('preferred_input_type')}"
        )

        print(
            f"• Experience: "
            f"{farmer.get('farming_experience_years')} years"
        )

        active_factors = (
            farmer_context.get(
                "active_factors"
            )
            or []
        )

        if active_factors:

            print(
                "\n🎯 ACTIVE PERSONALIZATION FACTORS"
            )

            for factor in active_factors:

                print(
                    f"• {factor}"
                )

    # ========================================================
    # Signals
    # ========================================================

    print(
        "\n📌 SIGNALS"
    )

    signals = _safe_dict(
        packet.get(
            "signals"
        )
    )

    for key, value in signals.items():

        print(
            f"• {key}: {value}"
        )

    # ========================================================
    # Why
    # ========================================================

    final_recommendation = _safe_dict(
        packet.get(
            "final_recommendation"
        )
    )

    print(
        "\n🧠 WHY RAYA PRIORITIZED THIS"
    )

    why = _safe_list(
        final_recommendation.get(
            "why"
        )
    )

    if not why:

        print(
            "• Standard agricultural intelligence determined the priority."
        )

    else:

        for reason in why:

            print(
                f"• {reason}"
            )

    # ========================================================
    # Recommendations
    # ========================================================

    print(
        "\n✅ RECOMMENDATIONS"
    )

    recommendations = _safe_list(
        packet.get(
            "recommendations"
        )
    )

    if not recommendations:

        print(
            "No recommendations generated"
        )

    for item in recommendations:

        print(
            f"\n[{item.get('priority')}] "
            f"{item.get('type')}"
        )

        print(
            f"→ {item.get('action')}"
        )

        if item.get(
            "personalization_applied"
        ):

            print(
                "🎯 Personalized because:"
            )

            for reason in _safe_list(
                item.get(
                    "personalization_reasons"
                )
            ):

                print(
                    f"   • {reason}"
                )

    print(
        "\n================================================"
    )

    print(
        "✅ ADVISORY COMPLETE"
    )

    print(
        "================================================\n"
    )


# ============================================================
# Personalization Comparison Helper
# ============================================================

def compare_farmer_contexts(
    crop,
    stage,
    state,
    district,
    farmer_context_a,
    farmer_context_b,
    label_a="Farmer A",
    label_b="Farmer B",
    agricultural_packet=None,
    agricultural_packet_a=None,
    agricultural_packet_b=None,
):
    """
    Compare two real Farmer Contexts against the same agricultural
    situation.

    Production/E2E validation should provide agricultural_packet_a and
    agricultural_packet_b. Each packet must already have been generated
    exactly once by farmer_search().

    The decision engine then consumes those packets without performing
    another search.
    """
    if agricultural_packet_a is None:
        agricultural_packet_a = agricultural_packet

    if agricultural_packet_b is None:
        agricultural_packet_b = agricultural_packet

    advisory_a = generate_contextual_advisory(
        crop=crop,
        stage=stage,
        state=state,
        district=district,
        farmer_context=farmer_context_a,
        agricultural_packet=agricultural_packet_a,
    )

    advisory_b = generate_contextual_advisory(
        crop=crop,
        stage=stage,
        state=state,
        district=district,
        farmer_context=farmer_context_b,
        agricultural_packet=agricultural_packet_b,
    )

    if (
        advisory_a.get("status") != "success"
        or advisory_b.get("status") != "success"
    ):
        return {
            "status": "error",
            "message": "Unable to generate both farmer advisories.",
            "farmer_a": advisory_a,
            "farmer_b": advisory_b,
        }

    def _summary(advisory):
        recommendations = _safe_list(
            advisory.get("recommendations")
        )
        final_recommendation = _safe_dict(
            advisory.get("final_recommendation")
        )
        farmer_context = _safe_dict(
            advisory.get("farmer_context")
        )
        personalization = _safe_dict(
            advisory.get("personalization")
        )

        return {
            "priority": advisory.get("priority"),
            "top_recommendation": (
                recommendations[0].get("action")
                if recommendations
                else None
            ),
            "top_recommendation_type": (
                recommendations[0].get("type")
                if recommendations
                else None
            ),
            "top_recommendation_priority": (
                recommendations[0].get("priority")
                if recommendations
                else None
            ),
            "active_factors": farmer_context.get(
                "active_factors", []
            ),
            "personalization_reasons": personalization.get(
                "summary", {}
            ).get("reasons", []),
            "final_recommendation": final_recommendation,
            "context_schema_version": farmer_context.get(
                "schema_version"
            ),
        }

    summary_a = _summary(advisory_a)
    summary_b = _summary(advisory_b)

    return {
        "status": "success",
        "comparison": {
            "same_crop": _normalize_crop(
                advisory_a.get("crop")
            ) == _normalize_crop(
                advisory_b.get("crop")
            ) == _normalize_crop(crop),
            "same_stage": _normalize_stage(
                advisory_a.get("stage")
            ) == _normalize_stage(
                advisory_b.get("stage")
            ) == _normalize_stage(stage),
            "same_location": (
                _normalize_text(state)
                == _normalize_text(
                    _safe_dict(advisory_a.get("location")).get("state")
                )
                == _normalize_text(
                    _safe_dict(advisory_b.get("location")).get("state")
                )
                and
                _normalize_text(district)
                == _normalize_text(
                    _safe_dict(advisory_a.get("location")).get("district")
                )
                == _normalize_text(
                    _safe_dict(advisory_b.get("location")).get("district")
                )
            ),
            "different_farmer_context": (
                summary_a["active_factors"]
                != summary_b["active_factors"]
                or summary_a["personalization_reasons"]
                != summary_b["personalization_reasons"]
            ),
            "different_overall_priority": (
                summary_a["priority"]
                != summary_b["priority"]
            ),
            "different_top_recommendation": (
                summary_a["top_recommendation"]
                != summary_b["top_recommendation"]
            ),
            "different_personalization_reasons": (
                summary_a["personalization_reasons"]
                != summary_b["personalization_reasons"]
            ),
            "different_decision_outcome": (
                summary_a["priority"]
                != summary_b["priority"]
                or summary_a["top_recommendation"]
                != summary_b["top_recommendation"]
                or summary_a["personalization_reasons"]
                != summary_b["personalization_reasons"]
            ),
        },
        label_a: summary_a,
        label_b: summary_b,
        "advisory_a": advisory_a,
        "advisory_b": advisory_b,
    }


# ============================================================
# Phase 3B Real End-to-End Validation
# ============================================================

def _build_validation_profiles():
    """
    Build two realistic source profiles.

    These are PROFILE FIXTURES, not decision-engine contexts.
    The validation MUST pass them through build_farmer_context().
    """
    farmer_a = {
        "farmer_id": "FA",
        "name": "Farmer A",
        "age": 42,
        "preferred_language": "Kannada",
        "farming_experience_years": 18,
        "farming_type": "Commercial",
        "primary_objective": "Income",
        "farming_goals": [
            "Maximize yield",
            "Maintain reliable production",
        ],
        "labor_availability": "Sufficient",
        "budget_constraint": "High",
        "market_access": "Multiple mandis",
        "guidance_preference": "Preventive",
        "preferred_input_type": "Integrated",
        "equipment_available": [
            "Tractor",
            "Manual knapsack sprayer",
        ],
        "crops_grown_historically": ["rice", "ragi"],
        "known_recurring_problems": [],
    }

    farm_a = {
        "farm_id": "FMA",
        "farmer_id": "FA",
        "farm_name": "Resource Strong Farm",
        "state": "Karnataka",
        "district": "Mandya",
        "village": "Validation Village A",
        "gps_coordinates": {},
        "total_area_acres": 5.0,
        "fields": [
            {
                "field_id": "FLA1",
                "name": "Main Rice Field",
                "area_acres": 5.0,
                "current_crop": "rice",
                "current_stage": "Flowering",
                "soil_profile_id": "SPA",
            }
        ],
        "current_season": "Kharif",
        "current_crops": ["rice"],
        "previous_season_crops": ["ragi"],
        "irrigation_source": "Canal",
        "irrigation_type": "Flood",
        "irrigation_reliability": "Reliable",
        "farming_practice": "Integrated",
        "uses_crop_rotation": True,
    }

    soil_a = {
        "soil_profile_id": "SPA",
        "field_id": "FLA1",
        "soil_type": "Clay",
        "soil_texture": "Fine",
        "drainage_characteristics": "Moderately drained",
        "soil_ph": 6.2,
        "ph_category": "Slightly acidic",
        "organic_carbon_percent": 0.62,
        "fertility_level": "Medium",
        "nitrogen_status": "Adequate",
        "phosphorus_status": "Adequate",
        "potassium_status": "Adequate",
        "moisture_retention": "High",
        "waterlogging_risk": "Low",
        "suitable_crops": ["rice", "sugarcane"],
        "soil_limitations": [],
        "soil_risks": [],
    }

    farmer_b = {
        "farmer_id": "FB",
        "name": "Farmer B",
        "age": 42,
        "preferred_language": "Kannada",
        "farming_experience_years": 6,
        "farming_type": "Semi-commercial",
        "primary_objective": "Income",
        "farming_goals": [
            "Reduce production cost",
            "Protect crop from recurring disease",
        ],
        "labor_availability": "Limited",
        "budget_constraint": "Low",
        "market_access": "Local mandi only",
        "guidance_preference": "Preventive",
        "preferred_input_type": "Integrated",
        "equipment_available": [
            "Manual knapsack sprayer",
        ],
        "crops_grown_historically": ["rice", "ragi"],
        "known_recurring_problems": [
            "Blast Disease in rice",
            "Irregular monsoon rainfall",
        ],
    }

    farm_b = {
        "farm_id": "FMB",
        "farmer_id": "FB",
        "farm_name": "Resource Constrained Farm",
        "state": "Karnataka",
        "district": "Mandya",
        "village": "Validation Village B",
        "gps_coordinates": {},
        "total_area_acres": 2.0,
        "fields": [
            {
                "field_id": "FLB1",
                "name": "Main Rice Field",
                "area_acres": 2.0,
                "current_crop": "rice",
                "current_stage": "Flowering",
                "soil_profile_id": "SPB",
            }
        ],
        "current_season": "Kharif",
        "current_crops": ["rice"],
        "previous_season_crops": ["ragi"],
        "irrigation_source": "Canal",
        "irrigation_type": "Flood",
        "irrigation_reliability": "Unreliable",
        "farming_practice": "Conventional",
        "uses_crop_rotation": False,
    }

    soil_b = {
        "soil_profile_id": "SPB",
        "field_id": "FLB1",
        "soil_type": "Clay",
        "soil_texture": "Fine",
        "drainage_characteristics": "Poorly drained",
        "soil_ph": 6.2,
        "ph_category": "Slightly acidic",
        "organic_carbon_percent": 0.42,
        "fertility_level": "Medium",
        "nitrogen_status": "Deficient",
        "phosphorus_status": "Adequate",
        "potassium_status": "Adequate",
        "moisture_retention": "High",
        "waterlogging_risk": "Medium",
        "suitable_crops": ["rice", "sugarcane"],
        "soil_limitations": [
            "Low organic matter",
            "Waterlogging tendency in heavy rain",
        ],
        "soil_risks": [
            "Nitrogen depletion after heavy rainfall",
        ],
    }

    return {
        "farmer_a": farmer_a,
        "farm_a": farm_a,
        "soil_a": soil_a,
        "farmer_b": farmer_b,
        "farm_b": farm_b,
        "soil_b": soil_b,
    }


def run_phase3b_validation():
    """
    Real Phase 3B end-to-end validation.

    Pipeline:
        Farmer Profile
            ↓
        Farm Profile
            ↓
        Soil Profile
            ↓
        build_farmer_context()
            ↓
        farmer_search() [exactly once per farmer]
            ↓
        generate_contextual_advisory()
            ↓
        validation/comparison

    The validation deliberately uses the canonical context builder.
    No synthetic decision-engine context is constructed here.
    """
    if build_farmer_context is None:
        return {
            "status": "error",
            "phase": "3B",
            "message": (
                "farmer_context.py could not be imported; "
                "real E2E validation cannot run."
            ),
        }

    profiles = _build_validation_profiles()

    # --------------------------------------------------------
    # Build REAL canonical contexts.
    # --------------------------------------------------------
    context_a = build_farmer_context(
        profiles["farmer_a"],
        profiles["farm_a"],
        profiles["soil_a"],
    )
    context_b = build_farmer_context(
        profiles["farmer_b"],
        profiles["farm_b"],
        profiles["soil_b"],
    )

    validation_a = validate_farmer_context(context_a)
    validation_b = validate_farmer_context(context_b)

    if not validation_a.get("valid") or not validation_b.get("valid"):
        return {
            "status": "error",
            "phase": "3B",
            "message": "Canonical Farmer Context validation failed.",
            "farmer_a_context_validation": validation_a,
            "farmer_b_context_validation": validation_b,
        }

    # --------------------------------------------------------
    # Generate agricultural packets ONCE per farmer.
    #
    # The decision engine receives these packets and does not
    # call farmer_search() again.
    # --------------------------------------------------------
    agricultural_packet = farmer_search(
        crop="rice",
        stage="Flowering",
        state="Karnataka",
        district="Mandya",
    )

    if agricultural_packet.get("status") != "success":
        return {
            "status": "error",
            "phase": "3B",
            "message": "Agricultural packet generation failed.",
            "agricultural_packet": agricultural_packet,
        }

    # Same crop + stage + location means both farmers intentionally
    # consume the same agricultural intelligence snapshot. Their
    # decision differences must therefore come from Farmer Context.
    packet_a = agricultural_packet
    packet_b = agricultural_packet

    # --------------------------------------------------------
    # Feed the already-generated packets to the decision engine.
    # --------------------------------------------------------
    result = compare_farmer_contexts(
        crop="rice",
        stage="Flowering",
        state="Karnataka",
        district="Mandya",
        farmer_context_a=context_a,
        farmer_context_b=context_b,
        label_a="Farmer A",
        label_b="Farmer B",
        agricultural_packet_a=packet_a,
        agricultural_packet_b=packet_b,
    )

    if result.get("status") != "success":
        return result

    comparison = result["comparison"]

    # --------------------------------------------------------
    # Acceptance criteria.
    # --------------------------------------------------------
    same_crop = comparison.get("same_crop") is True
    same_stage = comparison.get("same_stage") is True
    same_location = comparison.get("same_location") is True

    different_context = (
        comparison.get("different_farmer_context") is True
    )
    different_priority = (
        comparison.get("different_overall_priority") is True
    )
    different_top_recommendation = (
        comparison.get("different_top_recommendation") is True
    )
    different_reasons = (
        comparison.get("different_personalization_reasons") is True
    )

    # "Different overall priority where applicable" is conditional.
    # For this fixture, the context differences are intentionally strong,
    # so at least one decision-level difference must be observed.
    meaningful_difference = (
        different_priority
        or different_top_recommendation
        or different_reasons
    )

    # Both contexts must have been built by the canonical builder.
    canonical_schema_ok = (
        validation_a.get("schema_version")
        == validation_b.get("schema_version")
        == FARMER_CONTEXT_SCHEMA_VERSION
    )

    # The decision engine must have consumed supplied packets.
    # This is reported from the advisory metadata.
    search_not_repeated_a = not _safe_dict(
        result["advisory_a"].get("meta")
    ).get("farmer_search_executed_here", True)

    search_not_repeated_b = not _safe_dict(
        result["advisory_b"].get("meta")
    ).get("farmer_search_executed_here", True)

    backend_personalization = (
        result["advisory_a"].get("meta", {}).get(
            "personalization_active"
        ) is True
        and result["advisory_b"].get("meta", {}).get(
            "personalization_active"
        ) is True
    )

    passed = all(
        (
            canonical_schema_ok,
            same_crop,
            same_stage,
            same_location,
            different_context,
            meaningful_difference,
            search_not_repeated_a,
            search_not_repeated_b,
            backend_personalization,
        )
    )

    return {
        "status": "success" if passed else "failed",
        "phase": "3B",
        "validation": {
            "one_canonical_farmer_context_schema": canonical_schema_ok,
            "real_build_farmer_context_used": True,
            "same_crop": same_crop,
            "same_stage": same_stage,
            "same_location": same_location,
            "different_farmer_context": different_context,
            "different_overall_priority": different_priority,
            "different_top_recommendation": different_top_recommendation,
            "different_personalization_reasons": different_reasons,
            "meaningful_decision_difference": meaningful_difference,
            "backend_owns_personalization": backend_personalization,
            "farmer_search_not_repeated_inside_engine": (
                search_not_repeated_a
                and search_not_repeated_b
            ),
            "single_shared_agricultural_packet_used_for_a_and_b": True,
            "overall_pass": passed,
        },
        "farmer_a_context_validation": validation_a,
        "farmer_b_context_validation": validation_b,
        "comparison": {
            "Farmer A": result.get("Farmer A"),
            "Farmer B": result.get("Farmer B"),
            "decision_comparison": comparison,
        },
        "pipeline": {
            "context_builder": "build_farmer_context()",
            "agricultural_search": (
                "farmer_search() once per farmer"
            ),
            "decision_engine": (
                "generate_contextual_advisory() consumes supplied packet"
            ),
            "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
        },
    }


# ============================================================
# Test Harness
# ============================================================

if __name__ == "__main__":

    print(
        "\n================================================"
    )

    print(
        "RAYA — PHASE 3B CONTEXTUAL DECISION ENGINE"
    )

    print(
        "================================================\n"
    )

    # --------------------------------------------------------
    # Generic advisory
    # --------------------------------------------------------

    print(
        "1. GENERIC ADVISORY TEST"
    )

    advisory = generate_contextual_advisory(

        crop="rice",

        stage="flowering",

        state="Karnataka",

        district="Mandya"
    )

    print(
        json.dumps(
            advisory,
            indent=2,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # Farmer-context validation
    # --------------------------------------------------------

    print(
        "\n2. PHASE 3B PERSONALIZATION VALIDATION"
    )

    validation = run_phase3b_validation()

    print(
        json.dumps(
            validation,
            indent=2,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # Human-readable output
    # --------------------------------------------------------

    if (
        advisory.get(
            "status"
        )
        == "success"
    ):

        show_contextual_advisory(
            advisory
        )

    print(
        "\n================================================"
    )

    print(
        "PHASE 3B FINAL VALIDATION COMPLETE"
    )

    print(
        "================================================\n"
    )