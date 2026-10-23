"""
RAYA — Phase 3 Farmer Context Foundation
=========================================

Phase 3 Goal
------------
Give RAYA the context it needs to eventually make
farmer-specific decisions — not just crop-specific ones.

Today RAYA understands:
    Rice + Flowering + Mandya → advisory

After Phase 3 RAYA understands:
    Ramesh + his 2 acres + his clay soil +
    rice at flowering + Mandya conditions → advisory

This module defines:

    A. Farmer Profile   — Who is this farmer?
    B. Farm Profile     — What land are they managing?
    C. Soil Profile     — What is the soil condition?
    D. Field Schema     — Individual plots within a farm
    E. Relationship map — Farmer → Farm → Field → Soil → Crop
    F. Personalization  — How context enriches each intelligence engine
    G. Canonical Farmer Context Contract
    H. Sample prototype — Ramesh, Mandya, Karnataka (working demo)

What this module does NOT do
-----------------------------
    ✗ Replace the Crop Master
    ✗ Rewrite existing engines
    ✗ Build an AI decision model
    ✗ Collect unnecessary data
    ✗ Assume information we don't have

Every field answers one question:
    "Will this eventually help RAYA give better agricultural guidance?"
"""

from datetime import datetime, timezone


# =======================================================
# A. Farmer Profile Schema
# =======================================================
#
# Question RAYA should answer: WHO am I helping?
#
# Required fields are marked (R). Optional marked (O).
# Fields reserved for future Decision Engine marked (F).
#
# =======================================================

FARMER_PROFILE_SCHEMA = {

    # -----------------------------------------------
    # Identity
    # -----------------------------------------------

    "farmer_id":                str,   # (R) Unique identifier
    "name":                     str,   # (R) Farmer's name
    "age":                      int,   # (O) Age in years — affects labor capacity
    "preferred_language":       str,   # (R) Kannada / Hindi / Telugu — future multilingual output

    # -----------------------------------------------
    # Farming background
    # Drives advice complexity — a 2-year farmer
    # needs different guidance than an 18-year veteran
    # -----------------------------------------------

    "farming_experience_years": int,   # (R) Total years farming
    "farming_type":             str,   # (R) Subsistence / Semi-commercial / Commercial

    # -----------------------------------------------
    # Objectives
    # Drives recommendation priority — a farmer
    # optimizing for income needs different actions
    # than one optimizing for food security
    # -----------------------------------------------

    "primary_objective":        str,   # (R) Subsistence / Income / Market / Export
    "farming_goals":            list,  # (O) e.g. ["maximize yield", "reduce cost"]

    # -----------------------------------------------
    # Constraints
    # Every constraint changes what advice is practical.
    # A labor-limited farmer cannot act on "spray daily".
    # A budget-limited farmer cannot act on "apply drip kit".
    # -----------------------------------------------

    "labor_availability":       str,   # (R) Limited / Adequate / Sufficient
    "budget_constraint":        str,   # (R) Low / Medium / High
    "market_access":            str,   # (R) Local mandi / Multiple mandis / Direct buyer

    # -----------------------------------------------
    # Guidance preference
    # Determines whether RAYA recommends preventive
    # actions upfront or reactive actions when problems
    # appear
    # -----------------------------------------------

    "guidance_preference":      str,   # (R) Preventive / Reactive / Both
    "preferred_input_type":     str,   # (O) Organic / Chemical / Integrated

    # -----------------------------------------------
    # Resources
    # Determines feasibility of specific actions —
    # a farmer with only a manual sprayer cannot use
    # boom sprayer recommendations
    # -----------------------------------------------

    "equipment_available":      list,  # (O) ["tractor", "manual sprayer", "drip kit"]

    # -----------------------------------------------
    # Farming history
    # Allows RAYA to elevate known recurring risks.
    # If Ramesh has had blast disease 3 years running,
    # RAYA should prioritize blast prevention above
    # the generic disease advisory
    # -----------------------------------------------

    "crops_grown_historically":     list,  # (O) Historical crop list
    "known_recurring_problems":     list,  # (R) Diseases / pests / failures

    # -----------------------------------------------
    # Reserved for future Decision Engine
    # -----------------------------------------------

    # "credit_access":            str,   # (F) Loan / No loan / Kisan Credit Card
    # "insurance_enrolled":       bool,  # (F) PM Fasal Bima / None
    # "cooperative_member":       bool,  # (F) FPO membership affects market access
}


# =======================================================
# B. Farm Profile Schema
# =======================================================
#
# Question RAYA should answer: WHAT FARM are they managing?
#
# Farmer Profile = the person
# Farm Profile   = the land / farming operation
#
# One farmer can eventually have multiple farms.
#
# =======================================================

FARM_PROFILE_SCHEMA = {

    # -----------------------------------------------
    # Identity
    # -----------------------------------------------

    "farm_id":                  str,   # (R) Unique farm identifier
    "farmer_id":                str,   # (R) FK → Farmer Profile
    "farm_name":                str,   # (R) Name the farmer uses for this farm

    # -----------------------------------------------
    # Location
    # Drives: weather data, market data, local crop norms
    # -----------------------------------------------

    "state":                    str,   # (R) Indian state name
    "district":                 str,   # (R) District — drives mandi + weather data
    "village":                  str,   # (O) More precise location
    "gps_coordinates":          dict,  # (O) {"lat": float, "lon": float} — future precision

    # -----------------------------------------------
    # Land area
    # Drives: fertilizer quantities, water volumes,
    # market value estimates, labor requirements
    # -----------------------------------------------

    "total_area_acres":         float, # (R) Total farm size
    "fields":                   list,  # (R) List of individual Field records

    # -----------------------------------------------
    # Season
    # -----------------------------------------------

    "current_season":           str,   # (R) Kharif / Rabi / Zaid
    "current_crops":            list,  # (R) Crop names currently growing
    "previous_season_crops":    list,  # (O) Last season's crops — for rotation logic

    # -----------------------------------------------
    # Irrigation
    # Drives: water intelligence, irrigation schedule advice
    # -----------------------------------------------

    "irrigation_source":        str,   # (R) Canal / Borewell / Rainfed / Tank / Mixed
    "irrigation_type":          str,   # (R) Flood / Drip / Sprinkler / Furrow
    "irrigation_reliability":   str,   # (R) Reliable / Seasonal / Unreliable

    # -----------------------------------------------
    # Farming practices
    # Drives: fertilizer type, pest management advice
    # -----------------------------------------------

    "farming_practice":         str,   # (R) Organic / Conventional / Integrated
    "uses_crop_rotation":       bool,  # (O) Informs soil health trajectory

    # -----------------------------------------------
    # Reserved for future Decision Engine
    # -----------------------------------------------

    # "has_storage":              bool,  # (F) Grain storage affects selling strategy
    # "nearest_mandi_km":         float, # (F) Transport cost affects net price
    # "soil_test_done":           bool,  # (F) Whether formal soil testing exists
}


# =======================================================
# C. Field Schema
# =======================================================
#
# One farm → many fields/plots.
# Each field can have a different crop, stage, and soil.
#
# =======================================================

FIELD_SCHEMA = {

    "field_id":                 str,   # (R) Unique field identifier
    "name":                     str,   # (R) Human name for this plot
    "area_acres":               float, # (R) This field's area — scales recommendations
    "current_crop":             str,   # (R) Crop being grown now
    "current_stage":            str,   # (R) Growth stage → drives all intelligence
    "soil_profile_id":          str,   # (R) FK → Soil Profile
}


# =======================================================
# D. Soil Profile Schema
# =======================================================
#
# Question RAYA should answer: WHAT IS THE SOIL?
#
# Soil Profile enriches:
#   • Water intelligence   — drainage + moisture retention
#   • Fertilizer logic     — nutrient deficiency priorities
#   • Disease intelligence — waterlogging increases disease pressure
#   • Crop suitability     — validates crop choice vs. soil type
#
# =======================================================

SOIL_PROFILE_SCHEMA = {

    # -----------------------------------------------
    # Identity
    # -----------------------------------------------

    "soil_profile_id":          str,   # (R) Unique identifier
    "field_id":                 str,   # (R) FK → Field

    # -----------------------------------------------
    # Physical characteristics
    # -----------------------------------------------

    "soil_type":                str,   # (R) Clay / Loamy / Sandy / Red laterite / Black cotton
    "soil_texture":             str,   # (O) Fine / Medium / Coarse
    "drainage_characteristics": str,   # (R) Well-drained / Moderately / Poorly drained

    # -----------------------------------------------
    # Chemical characteristics
    # Drives: fertilizer recommendations
    # pH affects nutrient availability
    # -----------------------------------------------

    "soil_ph":                  float, # (O) e.g. 6.2
    "ph_category":              str,   # (O) Strongly acidic / Slightly acidic / Neutral / Alkaline
    "organic_carbon_percent":   float, # (O) Low < 0.5% / Medium 0.5–0.75% / High > 0.75%
    "fertility_level":          str,   # (R) Low / Medium / High

    # -----------------------------------------------
    # Nutrient status
    # Drives: specific fertilizer application priority
    # -----------------------------------------------

    "nitrogen_status":          str,   # (R) Deficient / Adequate / Excess
    "phosphorus_status":        str,   # (R) Deficient / Adequate / Excess
    "potassium_status":         str,   # (R) Deficient / Adequate / Excess

    # -----------------------------------------------
    # Moisture characteristics
    # Drives: irrigation frequency, drainage actions
    # -----------------------------------------------

    "moisture_retention":       str,   # (R) Low / Medium / High
    "waterlogging_risk":        str,   # (R) Low / Medium / High

    # -----------------------------------------------
    # Suitability and limitations
    # -----------------------------------------------

    "suitable_crops":           list,  # (O) Validates crop choice
    "soil_limitations":         list,  # (O) Known issues for RAYA to flag
    "soil_risks":               list,  # (O) Dynamic risks under weather events
}


# =======================================================
# E. Relationship Map (Farmer → Farm → Field → Soil → Crop)
# =======================================================
#
# RAYA's understanding chain:
#
#   Farmer (Ramesh, 18 yrs exp, Kannada, income-objective)
#       └── Farm (2 acres, Mandya, Canal irrigation)
#               ├── Field 1 (1.5 acres → Rice → Flowering → SP001)
#               │       └── Soil SP001 (Clay, pH 6.2, N-deficient)
#               └── Field 2 (0.5 acres → Tomato → Flowering → SP001)
#
#   Crop + Stage + Location
#       → Weather Engine
#       → Market Engine
#       → Water Engine
#       → Disease Engine
#       → Fertilizer Engine
#
#   + Farmer Context → PERSONALIZED ADVISORY
#
# =======================================================

ENTITY_RELATIONSHIPS = {

    "farmer":   {"has_many": ["farms"]},
    "farm":     {"belongs_to": "farmer",  "has_many": ["fields"]},
    "field":    {"belongs_to": "farm",    "has_one":  "soil_profile",
                 "has_one_crop": True},
    "soil":     {"belongs_to": "field"},
    "crop":     {"drives": ["weather_engine", "market_engine", "water_engine",
                             "disease_engine", "fertilizer_engine"]},
}


# =======================================================
# F. Personalization Mapping
# =======================================================
#
# Documents how Farmer + Farm + Soil provide additional
# context to each existing RAYA intelligence engine.
#
# Current engine output is NOT rewritten.
# Farmer context adds an annotation/enrichment layer.
#
# =======================================================

PERSONALIZATION_MAP = {

    "weather": {

        "farm_factors": [
            "irrigation_reliability",
            "current_season",
        ],

        "soil_factors": [
            "waterlogging_risk",
            "drainage_characteristics",
        ],

        "personalization_example": (
            "Clay soil (poorly drained) + heavy rainfall forecast "
            "→ RAYA elevates waterlogging warning above the generic advisory"
        ),
    },

    "water": {

        "farm_factors": [
            "irrigation_source",
            "irrigation_type",
            "irrigation_reliability",
        ],

        "soil_factors": [
            "moisture_retention",
            "drainage_characteristics",
            "waterlogging_risk",
        ],

        "personalization_example": (
            "Canal-irrigated + flood irrigation + high moisture-retention clay "
            "→ reduce irrigation frequency vs. generic schedule"
        ),
    },

    "fertilizer": {

        "soil_factors": [
            "nitrogen_status",
            "phosphorus_status",
            "potassium_status",
            "soil_ph",
            "fertility_level",
            "organic_carbon_percent",
        ],

        "farmer_factors": [
            "preferred_input_type",
            "budget_constraint",
        ],

        "personalization_example": (
            "Nitrogen-deficient soil + medium budget + conventional practice "
            "→ prioritize urea application at Flowering stage"
        ),
    },

    "disease": {

        "soil_factors": [
            "waterlogging_risk",
            "drainage_characteristics",
        ],

        "farm_factors": [
            "farming_practice",
            "previous_season_crops",
        ],

        "farmer_factors": [
            "known_recurring_problems",
        ],

        "personalization_example": (
            "Ramesh's 3-year Blast Disease history + high humidity forecast "
            "→ Blast advisory moves from standard to elevated priority"
        ),
    },

    "market": {

        "farm_factors": [
            "total_area_acres",
            "current_crops",
        ],

        "farmer_factors": [
            "market_access",
            "primary_objective",
            "farming_goals",
        ],

        "personalization_example": (
            "1.5 acres rice × ~2500 kg/acre × ₹2000/quintal modal price "
            "→ estimated field value = ₹75,000 shown to farmer"
        ),
    },

    "advisory_priority": {

        "farmer_factors": [
            "guidance_preference",
            "labor_availability",
            "budget_constraint",
            "equipment_available",
        ],

        "personalization_example": (
            "Limited labor + manual sprayer + preventive preference "
            "→ RAYA prioritizes low-effort preventive actions, "
            "deprioritizes high-labor reactive interventions"
        ),
    },
}


# =======================================================
# G. Canonical Farmer Context Contract
# =======================================================
#
# Phase 3B rule:
#   build_farmer_context() is the SINGLE source of truth for
#   the Farmer Context contract.
#
# The Contextual Decision Engine MUST consume these names.
# Do not introduce alternate aliases such as:
#   labor, budget, guidance_pref, input_preference
#
# Canonical names:
#   labor_availability
#   budget_constraint
#   guidance_preference
#   preferred_input_type
#
# The same contract is used by:
#   Farmer Setup → build_farmer_context()
#   → Contextual Decision Engine → UI renderer
#
# =======================================================

FARMER_CONTEXT_SCHEMA_VERSION = "3B.1"

FARMER_CONTEXT_SCHEMA = {
    "status": str,
    "farmer": {
        "farmer_id": str,
        "name": str,
        "preferred_language": str,
        "farming_experience_years": int,
        "primary_objective": str,
        "farming_goals": list,
        "labor_availability": str,
        "budget_constraint": str,
        "market_access": str,
        "guidance_preference": str,
        "preferred_input_type": str,
        "equipment_available": list,
        "crops_grown_historically": list,
        "known_recurring_problems": list,
    },
    "farm": {
        "farm_id": str,
        "farm_name": str,
        "farmer_id": str,
        "state": str,
        "district": str,
        "village": str,
        "gps_coordinates": dict,
        "total_area_acres": float,
        "current_season": str,
        "current_crops": list,
        "previous_season_crops": list,
        "fields": list,
        "irrigation_source": str,
        "irrigation_type": str,
        "irrigation_reliability": str,
        "farming_practice": str,
        "uses_crop_rotation": bool,
    },
    "soil": {
        "soil_profile_id": str,
        "field_id": str,
        "soil_type": str,
        "soil_texture": str,
        "drainage_characteristics": str,
        "soil_ph": float,
        "ph_category": str,
        "organic_carbon_percent": float,
        "fertility_level": str,
        "nitrogen_status": str,
        "phosphorus_status": str,
        "potassium_status": str,
        "moisture_retention": str,
        "waterlogging_risk": str,
        "suitable_crops": list,
        "soil_limitations": list,
        "soil_risks": list,
    },
    "personalization": dict,
    "meta": {
        "generated_at": str,
        "schema_version": str,
    },
}


def validate_farmer_context(context: dict, strict: bool = False) -> dict:
    """
    Validate the canonical Farmer Context contract.

    Parameters
    ----------
    context:
        Output returned by build_farmer_context().
    strict:
        If True, missing required canonical fields are reported as errors.
        If False, the validator reports warnings for optional/missing values.

    Returns
    -------
    dict:
        {
            "valid": bool,
            "errors": [...],
            "warnings": [...],
            "schema_version": ...
        }

    This validator intentionally checks the canonical names only. It does
    not accept legacy aliases because Phase 3B must have one shared contract.
    """
    errors = []
    warnings = []

    if not isinstance(context, dict):
        return {
            "valid": False,
            "errors": ["Farmer context must be a dictionary."],
            "warnings": [],
            "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
        }

    for section in ("farmer", "farm", "soil", "personalization", "meta"):
        if section not in context:
            errors.append(f"Missing required context section: {section}")

    farmer = context.get("farmer", {})
    farm = context.get("farm", {})
    soil = context.get("soil", {})
    meta = context.get("meta", {})

    canonical_farmer_fields = (
        "farmer_id",
        "name",
        "preferred_language",
        "farming_experience_years",
        "primary_objective",
        "farming_goals",
        "labor_availability",
        "budget_constraint",
        "market_access",
        "guidance_preference",
        "preferred_input_type",
        "equipment_available",
        "crops_grown_historically",
        "known_recurring_problems",
    )

    canonical_farm_fields = (
        "farm_id",
        "farm_name",
        "farmer_id",
        "state",
        "district",
        "village",
        "gps_coordinates",
        "total_area_acres",
        "current_season",
        "current_crops",
        "previous_season_crops",
        "fields",
        "irrigation_source",
        "irrigation_type",
        "irrigation_reliability",
        "farming_practice",
        "uses_crop_rotation",
    )

    canonical_soil_fields = (
        "soil_profile_id",
        "field_id",
        "soil_type",
        "soil_texture",
        "drainage_characteristics",
        "soil_ph",
        "ph_category",
        "organic_carbon_percent",
        "fertility_level",
        "nitrogen_status",
        "phosphorus_status",
        "potassium_status",
        "moisture_retention",
        "waterlogging_risk",
        "suitable_crops",
        "soil_limitations",
        "soil_risks",
    )

    for field in canonical_farmer_fields:
        if field not in farmer:
            errors.append(f"Missing canonical farmer field: farmer.{field}")

    for field in canonical_farm_fields:
        if field not in farm:
            errors.append(f"Missing canonical farm field: farm.{field}")

    for field in canonical_soil_fields:
        if field not in soil:
            errors.append(f"Missing canonical soil field: soil.{field}")

    if meta.get("schema_version") != FARMER_CONTEXT_SCHEMA_VERSION:
        errors.append(
            "Invalid Farmer Context schema version: "
            f"{meta.get('schema_version')!r}; "
            f"expected {FARMER_CONTEXT_SCHEMA_VERSION!r}."
        )

    # Detect the old Phase 3B aliases explicitly so a regression is obvious.
    legacy_aliases = {
        "farmer.labor": "farmer.labor_availability",
        "farmer.budget": "farmer.budget_constraint",
        "farmer.guidance_pref": "farmer.guidance_preference",
        "farmer.input_preference": "farmer.preferred_input_type",
    }

    for legacy_path, canonical_path in legacy_aliases.items():
        parent_name, field_name = legacy_path.split(".", 1)
        parent = context.get(parent_name, {})
        if field_name in parent:
            errors.append(
                f"Legacy Farmer Context alias found: {legacy_path}. "
                f"Use {canonical_path} only."
            )

    if strict:
        # Required top-level state.
        if context.get("status") != "active":
            errors.append(
                "Farmer Context status must be 'active' for an active context."
            )
    else:
        if context.get("status") != "active":
            warnings.append(
                "Farmer Context status is not 'active'."
            )

    # Relationship consistency checks.
    farmer_id = farmer.get("farmer_id")
    farm_farmer_id = farm.get("farmer_id")
    if farmer_id and farm_farmer_id and farmer_id != farm_farmer_id:
        errors.append(
            "Farmer/Farm relationship mismatch: "
            "farmer.farmer_id != farm.farmer_id."
        )

    if not farm.get("fields"):
        warnings.append("Farm contains no fields.")

    if not soil.get("soil_profile_id"):
        warnings.append("Soil profile has no soil_profile_id.")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
    }


# =======================================================
# H. Sample Prototype — Ramesh, Mandya, Karnataka
# =======================================================
#
# Purpose: Demonstrate that RAYA can load farmer context
# and combine it with existing crop intelligence.
#
# This is a working prototype, not a real farmer record.
#
# =======================================================

SAMPLE_FARMER = {

    "farmer_id":                    "F001",
    "name":                         "Ramesh",
    "age":                          42,
    "preferred_language":           "Kannada",

    "farming_experience_years":     18,
    "farming_type":                 "Semi-commercial",

    "primary_objective":            "Income",
    "farming_goals":                [
        "Maximize rice yield",
        "Reduce fertilizer cost",
        "Improve soil health over time",
    ],

    "labor_availability":           "Limited",
    "budget_constraint":            "Medium",
    "market_access":                "Local mandi only",

    "guidance_preference":          "Preventive",
    "preferred_input_type":         "Integrated",

    "equipment_available":          [
        "Hand tractor",
        "Manual knapsack sprayer",
    ],

    "crops_grown_historically":     ["rice", "ragi", "sugarcane"],
    "known_recurring_problems":     [
        "Blast Disease in rice",
        "Irregular monsoon rainfall",
        "Soil fertility decline",
    ],
}


SAMPLE_FARM = {

    "farm_id":                      "FM001",
    "farmer_id":                    "F001",
    "farm_name":                    "Ramesh's Mandya Farm",

    "state":                        "Karnataka",
    "district":                     "Mandya",
    "village":                      "Srirangapatna",
    "gps_coordinates":              {"lat": 12.4167, "lon": 76.6833},

    "total_area_acres":             2.0,

    "fields": [
        {
            "field_id":         "FL001",
            "name":             "Main Paddy Field",
            "area_acres":       1.5,
            "current_crop":     "rice",
            "current_stage":    "Flowering",
            "soil_profile_id":  "SP001",
        },
        {
            "field_id":         "FL002",
            "name":             "Kitchen Garden",
            "area_acres":       0.5,
            "current_crop":     "tomato",
            "current_stage":    "Flowering",
            "soil_profile_id":  "SP001",
        },
    ],

    "current_season":               "Kharif",
    "current_crops":                ["rice", "tomato"],
    "previous_season_crops":        ["ragi"],

    "irrigation_source":            "Canal",
    "irrigation_type":              "Flood",
    "irrigation_reliability":       "Seasonal",

    "farming_practice":             "Conventional",
    "uses_crop_rotation":           True,
}


SAMPLE_SOIL = {

    "soil_profile_id":              "SP001",
    "field_id":                     "FL001",

    "soil_type":                    "Clay",
    "soil_texture":                 "Fine",
    "drainage_characteristics":     "Poorly drained",

    "soil_ph":                      6.2,
    "ph_category":                  "Slightly acidic",
    "organic_carbon_percent":       0.42,
    "fertility_level":              "Medium",

    "nitrogen_status":              "Deficient",
    "phosphorus_status":            "Adequate",
    "potassium_status":             "Adequate",

    "moisture_retention":           "High",
    "waterlogging_risk":            "Medium",

    "suitable_crops":               ["rice", "sugarcane", "jute"],
    "soil_limitations":             [
        "Low organic matter",
        "Waterlogging tendency in heavy rain",
    ],
    "soil_risks":                   [
        "Nitrogen depletion after heavy rainfall",
        "Surface cracking when dry",
    ],
}


# =======================================================
# Context Assembly
# =======================================================

def build_farmer_context(
    farmer: dict,
    farm: dict,
    soil: dict
) -> dict:
    """
    Assemble the canonical Phase 3B Farmer Context.

    This function is the single source of truth for the context contract.
    The Contextual Decision Engine should consume this output directly.

    Pipeline:
        Farmer Profile
              +
        Farm Profile
              +
        Soil Profile
              ↓
        build_farmer_context()
              ↓
        Canonical Farmer Context
              ↓
        Contextual Decision Engine

    No legacy field aliases are emitted.
    """
    if not isinstance(farmer, dict):
        raise TypeError("farmer must be a dictionary.")
    if not isinstance(farm, dict):
        raise TypeError("farm must be a dictionary.")
    if not isinstance(soil, dict):
        raise TypeError("soil must be a dictionary.")

    context = {
        "status": "active",

        "farmer": {
            "farmer_id": farmer.get("farmer_id"),
            "name": farmer.get("name"),
            "preferred_language": farmer.get("preferred_language"),
            "farming_experience_years": farmer.get(
                "farming_experience_years"
            ),
            "primary_objective": farmer.get("primary_objective"),
            "farming_goals": farmer.get("farming_goals", []),

            # Canonical Phase 3B names.
            "labor_availability": farmer.get("labor_availability"),
            "budget_constraint": farmer.get("budget_constraint"),
            "market_access": farmer.get("market_access"),
            "guidance_preference": farmer.get("guidance_preference"),
            "preferred_input_type": farmer.get("preferred_input_type"),

            "equipment_available": farmer.get(
                "equipment_available", []
            ),
            "crops_grown_historically": farmer.get(
                "crops_grown_historically", []
            ),
            "known_recurring_problems": farmer.get(
                "known_recurring_problems", []
            ),
        },

        "farm": {
            "farm_id": farm.get("farm_id"),
            "farm_name": farm.get("farm_name"),
            "farmer_id": farm.get("farmer_id"),

            "state": farm.get("state"),
            "district": farm.get("district"),
            "village": farm.get("village"),
            "gps_coordinates": farm.get("gps_coordinates", {}),

            "total_area_acres": farm.get("total_area_acres"),
            "current_season": farm.get("current_season"),
            "current_crops": farm.get("current_crops", []),
            "previous_season_crops": farm.get(
                "previous_season_crops", []
            ),
            "fields": farm.get("fields", []),

            # Canonical farm fields are kept flat so the decision engine
            # does not need a second nested naming convention.
            "irrigation_source": farm.get("irrigation_source"),
            "irrigation_type": farm.get("irrigation_type"),
            "irrigation_reliability": farm.get(
                "irrigation_reliability"
            ),
            "farming_practice": farm.get("farming_practice"),
            "uses_crop_rotation": farm.get(
                "uses_crop_rotation"
            ),
        },

        "soil": {
            "soil_profile_id": soil.get("soil_profile_id"),
            "field_id": soil.get("field_id"),

            "soil_type": soil.get("soil_type"),
            "soil_texture": soil.get("soil_texture"),
            "drainage_characteristics": soil.get(
                "drainage_characteristics"
            ),

            "soil_ph": soil.get("soil_ph"),
            "ph_category": soil.get("ph_category"),
            "organic_carbon_percent": soil.get(
                "organic_carbon_percent"
            ),
            "fertility_level": soil.get("fertility_level"),

            "nitrogen_status": soil.get("nitrogen_status"),
            "phosphorus_status": soil.get("phosphorus_status"),
            "potassium_status": soil.get("potassium_status"),

            "moisture_retention": soil.get("moisture_retention"),
            "waterlogging_risk": soil.get("waterlogging_risk"),

            "suitable_crops": soil.get("suitable_crops", []),
            "soil_limitations": soil.get(
                "soil_limitations", []
            ),
            "soil_risks": soil.get("soil_risks", []),
        },

        "personalization": _derive_personalization_signals(
            farmer, farm, soil
        ),

        "meta": {
            "generated_at": _utc_timestamp(),
            "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
        },
    }

    validation = validate_farmer_context(context, strict=False)
    context["meta"]["validation"] = validation

    return context


def _derive_personalization_signals(
    farmer: dict,
    farm: dict,
    soil: dict
) -> dict:
    """
    Derive deterministic personalization signals from the source profiles.

    Important:
        These are backend context signals, not UI decisions.
        The Contextual Decision Engine can use them to produce structured
        priorities, recommendations, and reasons.
    """
    signals = {}

    problems = farmer.get("known_recurring_problems", []) or []
    normalized_problems = [
        str(problem).lower() for problem in problems
    ]

    # Disease/history signals.
    if any("blast" in problem for problem in normalized_problems):
        signals["blast_disease_history"] = True

    if any(
        "irregular" in problem and "rain" in problem
        for problem in normalized_problems
    ):
        signals["irregular_rainfall_history"] = True

    if any(
        "fertility" in problem or "soil" in problem
        for problem in normalized_problems
    ):
        signals["soil_fertility_concern"] = True

    # Soil signals.
    waterlogging = str(
        soil.get("waterlogging_risk") or "Low"
    )
    drainage = str(
        soil.get("drainage_characteristics") or ""
    )

    if (
        waterlogging in {"Medium", "High"}
        or "poor" in drainage.lower()
    ):
        signals["elevated_waterlogging_risk"] = True

    if soil.get("nitrogen_status") == "Deficient":
        signals["nitrogen_deficient"] = True

    if soil.get("fertility_level") == "Low":
        signals["low_soil_fertility"] = True

    organic = soil.get("organic_carbon_percent")
    if organic is not None and organic < 0.5:
        signals["low_organic_carbon"] = True

    # Farm/irrigation signals.
    reliability = farm.get("irrigation_reliability")
    if reliability == "Unreliable":
        signals["unreliable_irrigation"] = True
    elif reliability == "Seasonal":
        signals["seasonal_irrigation"] = True

    # Farmer constraints/preferences.
    if farmer.get("labor_availability") == "Limited":
        signals["labor_limited"] = True

    if farmer.get("budget_constraint") == "Low":
        signals["budget_limited"] = True

    if farmer.get("market_access") == "Local mandi only":
        signals["single_market"] = True

    guidance = farmer.get("guidance_preference")
    if guidance:
        signals["guidance_preference"] = guidance

    input_type = farmer.get("preferred_input_type")
    if input_type:
        signals["preferred_input_type"] = input_type

    # Scale signal.
    signals["farm_area_acres"] = farm.get(
        "total_area_acres", 1.0
    )

    return signals


def get_personalization_notes(
    context: dict,
    crop: str
) -> list:
    """
    Returns a list of human-readable personalization
    notes for the given crop, derived from farmer context.

    These are annotations on top of standard advisory —
    they do not replace engine output.
    """

    notes = []

    signals = context.get("personalization", {})

    farmer = context.get("farmer", {})
    soil = context.get("soil", {})
    farm = context.get("farm", {})

    # Disease history
    if (
        signals.get("blast_disease_history")
        and crop == "rice"
    ):
        notes.append(
            "⚠️ Blast Disease history detected on this farm. "
            "Preventive fungicide application is strongly advised "
            "before symptoms appear."
        )

    # Waterlogging
    if signals.get("elevated_waterlogging_risk"):
        notes.append(
            "⚠️ Your clay soil has poor drainage. "
            "Watch for waterlogging after heavy rainfall and "
            "ensure outlet channels are clear."
        )

    # Nitrogen deficiency
    if signals.get("nitrogen_deficient") and crop == "rice":
        notes.append(
            "⚠️ Soil nitrogen is deficient. "
            "Prioritize top-dressing nitrogen (urea) at this stage "
            "to support grain filling."
        )

    # Soil fertility
    if signals.get("soil_fertility_concern"):
        notes.append(
            "ℹ️ You have flagged soil fertility decline as a recurring "
            "concern. Consider adding green manure or compost "
            "after harvest."
        )

    # Irregular rainfall
    if signals.get("irregular_rainfall_history"):
        notes.append(
            "ℹ️ Irregular rainfall is a known risk on this farm. "
            "Maintain irrigation readiness even in monsoon season."
        )

    # Irrigation
    if signals.get("seasonal_irrigation"):
        notes.append(
            "ℹ️ Canal irrigation is seasonal on this farm. "
            "Plan water-intensive operations around reliable supply windows."
        )

    # Labor constraints
    if signals.get("labor_limited"):
        notes.append(
            "ℹ️ Labor is limited. Actions recommended below are "
            "prioritized for minimal manual effort."
        )

    # Low organic carbon
    if signals.get("low_organic_carbon"):
        notes.append(
            "ℹ️ Organic carbon is below 0.5% — soil health is declining. "
            "Incorporate crop residues rather than burning after harvest."
        )

    return notes


def estimate_field_value(
    field: dict,
    market_packet: dict
) -> dict | None:
    """
    Estimates approximate market value for a field's crop
    based on area, standard yield assumptions, and modal price.

    Returns None if market data is unavailable.

    This is an estimate only — actual yield varies widely.
    """

    if not market_packet:
        return None

    if market_packet.get("status") != "success":
        return None

    crop = field.get("current_crop", "")
    area = field.get("area_acres", 0)

    price = (market_packet.get("price") or {})
    modal = price.get("modal")

    if not modal or not area:
        return None

    # Standard yield assumptions (kg/acre) — conservative estimates
    yield_assumptions = {
        "rice":   2500,
        "wheat":  1800,
        "tomato": 8000,
        "banana": 7000,
    }

    kg_per_acre = yield_assumptions.get(
        crop.lower(), 2000
    )

    estimated_yield_kg = area * kg_per_acre

    # Modal price is per quintal (100 kg)
    estimated_value_inr = (
        estimated_yield_kg / 100
    ) * modal

    return {
        "crop":                 crop,
        "area_acres":           area,
        "assumed_yield_kg_acre": kg_per_acre,
        "estimated_yield_kg":   estimated_yield_kg,
        "modal_price_per_quintal": modal,
        "estimated_value_inr":  round(estimated_value_inr, 0),
        "note": (
            "Estimate only. Actual yield depends on "
            "weather, soil, and management."
        ),
    }

def get_canonical_farmer_preferences(context: dict) -> dict:
    """
    Return the farmer-level Phase 3B decision inputs using ONLY canonical names.

    This helper is intentionally small so downstream engines can consume
    the shared contract without inventing aliases.
    """
    farmer = (context or {}).get("farmer", {})

    return {
        "labor_availability": farmer.get("labor_availability"),
        "budget_constraint": farmer.get("budget_constraint"),
        "guidance_preference": farmer.get("guidance_preference"),
        "preferred_input_type": farmer.get("preferred_input_type"),
        "primary_objective": farmer.get("primary_objective"),
        "farming_goals": farmer.get("farming_goals", []),
        "market_access": farmer.get("market_access"),
        "equipment_available": farmer.get(
            "equipment_available", []
        ),
        "farming_experience_years": farmer.get(
            "farming_experience_years"
        ),
        "known_recurring_problems": farmer.get(
            "known_recurring_problems", []
        ),
    }


# =======================================================
# Utilities
# =======================================================

def _utc_timestamp() -> str:

    return datetime.now(timezone.utc).isoformat()


# =======================================================
# Crop-Soil Compatibility Check
# =======================================================

def check_crop_soil_compatibility(
    crop: str,
    soil: dict
) -> dict:
    """
    Checks whether the chosen crop is well-suited to
    the soil profile on record.

    Returns: {"compatible": bool, "notes": list}
    """

    suitable = soil.get("suitable_crops", [])

    compatible = (
        any(
            crop.lower() == s.lower()
            for s in suitable
        )
        if suitable
        else None  # unknown — no data
    )

    notes = []

    ph = soil.get("soil_ph")
    ph_cat = soil.get("ph_category", "")

    # Rice prefers slightly acidic to neutral (5.5–7.0)
    if str(crop).lower() == "rice" and ph is not None:
        if ph < 5.0:
            notes.append(
                "Soil is strongly acidic (pH < 5.0) — "
                "rice yield may be reduced. "
                "Consider lime application."
            )
        elif ph > 8.0:
            notes.append(
                "Soil is alkaline (pH > 8.0) — "
                "rice nutrient uptake may be impaired."
            )

    # Waterlogging suits rice, risks others
    wl_risk = soil.get("waterlogging_risk", "Low")

    if wl_risk in ["Medium", "High"]:
        if str(crop).lower() == "rice":
            notes.append(
                "Clay soil with waterlogging tendency "
                "is well-suited for paddy rice."
            )
        else:
            notes.append(
                f"Waterlogging risk is {wl_risk} — "
                f"{crop} may suffer root damage in waterlogged conditions."
            )

    return {
        "crop":         crop,
        "compatible":   compatible,
        "notes":        notes,
    }

# =======================================================
# Phase 3B Contract Self-Test
# =======================================================

def run_context_contract_self_test() -> dict:
    """
    Lightweight local test for the canonical Farmer Context contract.

    This is intentionally separate from the full Farmer A/B E2E validation
    harness. It verifies only that the real sample profiles produce a valid
    canonical context and that no legacy aliases are emitted.
    """
    context = build_farmer_context(
        SAMPLE_FARMER,
        SAMPLE_FARM,
        SAMPLE_SOIL,
    )

    validation = validate_farmer_context(
        context,
        strict=True,
    )

    return {
        "passed": validation["valid"],
        "validation": validation,
        "schema_version": FARMER_CONTEXT_SCHEMA_VERSION,
        "farmer_id": context["farmer"].get("farmer_id"),
        "farm_id": context["farm"].get("farm_id"),
        "soil_profile_id": context["soil"].get("soil_profile_id"),
    }


if __name__ == "__main__":
    result = run_context_contract_self_test()
    print("Phase 3B Farmer Context Contract Test")
    print("=" * 45)
    print(f"Schema version: {result['schema_version']}")
    print(f"Farmer: {result['farmer_id']}")
    print(f"Farm: {result['farm_id']}")
    print(f"Soil: {result['soil_profile_id']}")
    print(f"PASS: {result['passed']}")

    if not result["passed"]:
        print("Errors:")
        for error in result["validation"]["errors"]:
            print(f"  - {error}")
        raise SystemExit(1)