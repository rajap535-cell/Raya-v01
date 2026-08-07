"""
RAYA — Farmer Search Engine
(PRODUCTION READY — FINAL LOCKED VERSION)

Purpose
-------
Central orchestration engine combining:

• Query Engine
• Weather Engine
• Market Engine
• Crop Knowledge Engine

Design Principles
-----------------
• Deterministic orchestration
• No ML
• Structured packets internally
• Human-readable farmer output
"""

# ---------------------------------------------------
# Imports
# ---------------------------------------------------

import json

from datetime import datetime, timezone

from query_engine import (
    get_stage_snapshot,
    get_water_requirement
)

from crop_knowledge_engine import (
    get_stage_advice,
    get_relevant_diseases,
    get_fertilizer_logic
)

from weather_intelligence.weather_engine import get_weather_risk

# ✅ ONLY MARKET ACCESS POINT
from market_engine import get_market_price


# ---------------------------------------------------
# Timezone-Aware UTC Timestamp
# ---------------------------------------------------

def utc_timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()


# ---------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------

def _normalize_crop(crop: str) -> str:

    return crop.strip().lower()


def _normalize_stage(stage: str) -> str:

    return stage.strip().capitalize()


def _normalize_location(value: str) -> str:

    return value.strip().title()


# ---------------------------------------------------
# Packet Builder
# ---------------------------------------------------

def build_farmer_packet(
    crop,
    stage,
    state,
    district
):

    # ------------------------------------------------
    # Normalization
    # ------------------------------------------------

    crop = _normalize_crop(crop)

    stage = _normalize_stage(stage)

    state = _normalize_location(state)

    district = _normalize_location(district)

    location = {

        "state": state,

        "district": district
    }

    # ------------------------------------------------
    # Track-1
    # ------------------------------------------------

    stage_snapshot = get_stage_snapshot(
        crop,
        stage
    )

    # ------------------------------------------------
    # Early Error Propagation
    # ------------------------------------------------

    if stage_snapshot.get("status") == "error":

        return stage_snapshot

    water_packet = get_water_requirement(
        crop,
        stage
    )

    weather_packet = get_weather_risk(
        crop=crop,
        stage=stage,
        state=state,
        district=district
    )

    # ------------------------------------------------
    # ✅ CENTRALIZED MARKET ENGINE
    # ------------------------------------------------
    # IMPORTANT:
    # NO local market loaders
    # NO JSON parsing here
    # NO load_market_file usage
    # ONLY market_engine.py handles market data
    # ------------------------------------------------

    market_packet = get_market_price(
        crop=crop,
        state=state,
        district=district
    )

    # ------------------------------------------------
    # Track-2
    # ------------------------------------------------

    stage_advice = get_stage_advice(
        crop,
        stage
    )

    disease_info = get_relevant_diseases(
        crop,
        stage
    )

    fertilizer_info = get_fertilizer_logic(
        crop,
        stage
    )

    # ------------------------------------------------
    # Final Unified Packet
    # ------------------------------------------------

    packet = {

        "status": "success",

        "meta": {

            "generated_at": utc_timestamp(),

            "engine": "RAYA Farmer Search Engine"
        },

        "location": location,

        "crop": crop,

        "stage": stage,

        # --------------------------------------------
        # Track-1
        # --------------------------------------------

        "stage_snapshot": stage_snapshot,

        "weather": weather_packet,

        "water": water_packet,

        "market": market_packet,

        # --------------------------------------------
        # Track-2
        # --------------------------------------------

        "stage_advice": stage_advice,

        "diseases": disease_info,

        "fertilizer": fertilizer_info
    }

    return packet


# ---------------------------------------------------
# Public API
# ---------------------------------------------------

def farmer_search(
    state,
    district,
    crop,
    stage,
    weather_event=None,
    weather_intensity=None
):
    """
    Standard API for Advisory Engine.

    weather_event/intensity reserved
    for future real-time API integration.
    """

    # ------------------------------------------------
    # Validation
    # ------------------------------------------------

    if not crop:

        return {
            "status": "error",
            "message": "Crop not specified"
        }

    if not stage:

        return {
            "status": "error",
            "message": "Stage not specified"
        }

    if not state:

        return {
            "status": "error",
            "message": "State not specified"
        }

    if not district:

        return {
            "status": "error",
            "message": "District not specified"
        }

    # ------------------------------------------------
    # Build Unified Packet
    # ------------------------------------------------

    return build_farmer_packet(
        crop=crop,
        stage=stage,
        state=state,
        district=district
    )


# ---------------------------------------------------
# Farmer-Friendly Output Formatter
# ---------------------------------------------------

def farmer_view(packet):

    if packet.get("status") != "success":

        print("\n❌ ERROR")

        print(packet.get("message"))

        return

    print("\n================================================")

    print("🌾 RAYA FARMER INTELLIGENCE REPORT")

    print("================================================\n")

    crop = packet.get("crop")

    stage = packet.get("stage")

    location = packet.get("location") or {}

    print(f"Crop       : {crop}")

    print(f"Stage      : {stage}")

    print(
        f"Location   : "
        f"{location.get('district')}, "
        f"{location.get('state')}"
    )

    # ------------------------------------------------
    # Weather
    # ------------------------------------------------

    weather = packet.get("weather") or {}

    print("\n🌧 WEATHER")

    if weather.get("status") == "success":

        current = weather.get("current") or {}

        risk = weather.get("risk") or {}

        forecast = weather.get("forecast") or {}

        signals = weather.get("signals") or {}

        climate_risks = weather.get("climate_risks") or []

        print(
            f"Temperature : "
            f"{current.get('temperature_avg')}°C "
            f"(Min {current.get('temperature_min')}°C / "
            f"Max {current.get('temperature_max')}°C)"
        )

        print(
            f"Humidity    : "
            f"{current.get('humidity_percent')}%"
        )

        print(
            f"Rainfall    : "
            f"{current.get('rainfall_mm')} mm"
        )

        if current.get("wind_speed_kmh") is not None:

            print(
                f"Wind Speed  : "
                f"{current.get('wind_speed_kmh')} km/h"
            )

        print(
            f"Condition   : "
            f"{current.get('condition')}"
        )

        print(
            f"Risk Level  : "
            f"{risk.get('risk_level')} "
            f"({risk.get('risk_type')})"
        )

        impacts = risk.get("impact") or []

        if impacts:

            print(
                "Impact      :",
                ", ".join(impacts)
            )

        print(
            f"Forecast    : "
            f"{forecast.get('expected_event')} "
            f"(Probability: "
            f"{forecast.get('forecast_probability')})"
        )

        # --------------------------------------------
        # Multi-Risk Climate Intelligence
        # --------------------------------------------

        if climate_risks:

            print("\n  Climate Risk Breakdown:")

            for cr in climate_risks:

                cr_level = cr.get(
                    "risk_level", "Low"
                )

                cr_type = cr.get("type", "unknown")

                cr_effects = cr.get(
                    "effects"
                ) or []

                effects_text = (
                    ", ".join(cr_effects)
                    if cr_effects
                    else "No specific effects"
                )

                print(
                    f"  • {cr_type} "
                    f"(Risk: {cr_level}) "
                    f"— {effects_text}"
                )

        # --------------------------------------------
        # Operational Signals
        # --------------------------------------------

        if signals:

            print("\n  Operational Signals:")

            if signals.get("irrigation_needed"):

                print(
                    "  • Irrigation planning "
                    "recommended"
                )

            if signals.get("spraying_safe") is False:

                print(
                    "  • Avoid pesticide spraying "
                    "- rain may be expected"
                )

            if signals.get("harvest_risk"):

                print(
                    "  • Harvest risk level: "
                    f"{signals.get('harvest_risk')}"
                )

            if signals.get("reason"):

                print(
                    "  • Reason: "
                    f"{signals.get('reason')}"
                )

    else:

        print(
            weather.get(
                "message",
                "No weather data available"
            )
        )

    # ------------------------------------------------
    # Water
    # ------------------------------------------------

    water = packet.get("water") or {}

    print("\n💧 WATER")

    if water.get("status") == "success":

        water_mgmt = water.get(
            "water_management"
        ) or {}

        if isinstance(water_mgmt, dict):

            requirement = water_mgmt.get(
                "requirement"
            )

            irrigation = water_mgmt.get(
                "irrigation_frequency"
            )

            drainage = water_mgmt.get(
                "drainage_required"
            )

            critical = water_mgmt.get(
                "critical_condition"
            )

            soil_moisture = water_mgmt.get(
                "soil_moisture"
            )

            if requirement:

                print(
                    f"Requirement : "
                    f"{requirement} water "
                    f"requirement"
                )

            if irrigation:

                print(
                    f"Irrigation  : "
                    f"{irrigation}"
                )

            if drainage is True:

                print(
                    "Drainage    : "
                    "Keep drainage ready"
                )

            elif drainage is False:

                print(
                    "Drainage    : "
                    "Drainage not required"
                )

            if critical:

                print(
                    f"Critical    : "
                    f"{critical}"
                )

            if soil_moisture:

                print(
                    f"Soil Moisture: "
                    f"{soil_moisture}"
                )

        else:

            # Fallback for legacy string format
            print(
                "Guidance    :",
                water_mgmt
            )

        # Legacy compatibility
        legacy_req = water.get(
            "water_requirement"
        )

        if (
            legacy_req
            and not isinstance(
                water.get("water_management"),
                dict
            )
        ):

            print(
                "Requirement :",
                legacy_req
            )

    else:

        print(
            "No water guidance available"
        )

    # ------------------------------------------------
    # Market
    # ------------------------------------------------

    market = packet.get("market") or {}

    print("\n🌾 MARKET")

    if market.get("status") == "success":

        market_location = market.get("location") or {}

        price = market.get("price") or {}

        trend = market.get("trend") or {}

        forecast = market.get("forecast") or {}

        arrival = market.get("arrival") or {}

        print(
            f"Mandi       : "
            f"{market_location.get('mandi')}"
        )

        print(
            f"Price Range : "
            f"₹{price.get('min')} - "
            f"₹{price.get('max')}"
        )

        print(
            f"Modal Price : "
            f"₹{price.get('modal')} "
            f"{price.get('currency')}"
        )

        # Arrival data
        arrival_qty = arrival.get("quantity")

        arrival_unit = arrival.get("unit")

        if arrival_qty is not None:

            # Use unit from data if available,
            # fallback to "quintal"
            unit_label = (
                arrival_unit
                if arrival_unit
                else "quintal"
            )

            print(
                f"Arrival     : "
                f"{arrival_qty} {unit_label}"
            )

        print(
            f"Trend       : "
            f"{trend.get('direction')} "
            f"({trend.get('change_percent')}%)"
        )

        print(
            f"Forecast    : "
            f"{forecast.get('next_7_days')} "
            f"(Confidence: "
            f"{forecast.get('confidence')})"
        )

    else:

        print(
            market.get(
                "message",
                "No market data available"
            )
        )

    # ------------------------------------------------
    # Crop Status
    # ------------------------------------------------

    snapshot = packet.get(
        "stage_snapshot"
    ) or {}

    print("\n🌱 CROP STATUS")

    if snapshot.get("status") == "success":

        if snapshot.get("sensitivity"):

            print(
                "Sensitivity :",
                snapshot.get("sensitivity")
            )

        if snapshot.get("yield_risk_level"):

            print(
                "Yield Risk  :",
                snapshot.get(
                    "yield_risk_level"
                )
            )

        critical_ops = snapshot.get(
            "critical_operations"
        ) or []

        if critical_ops:

            print(
                "Operations  :",
                ", ".join(critical_ops)
            )

        if snapshot.get("risk_summary"):

            print(
                "Risk Summary:",
                snapshot.get("risk_summary")
            )

        stage_risk_map = snapshot.get(
            "risk_impact_map"
        ) or {}

        if stage_risk_map:

            print("\n  Risk Impact Map:")

            for event, details in \
                    stage_risk_map.items():

                severity = details.get(
                    "severity"
                )

                primary = (
                    details.get(
                        "primary_impacts"
                    ) or []
                )

                print(
                    f"  • {event} "
                    f"(Severity: {severity})"
                )

                if primary:

                    print(
                        "    Impacts: " +
                        "; ".join(primary)
                    )

    else:

        print(
            "No crop snapshot available"
        )

    # ------------------------------------------------
    # Stage Advice
    # ------------------------------------------------

    advice_packet = packet.get(
        "stage_advice"
    ) or {}

    print("\n📘 STAGE ADVICE")

    if advice_packet.get("status") == "success":

        advice = advice_packet.get(
            "advice"
        ) or {}

        if advice.get("sowing_guidance"):

            print(
                "Sowing      :",
                advice.get("sowing_guidance")
            )

        if advice.get("water_principles"):

            print(
                "Water       :",
                advice.get("water_principles")
            )

        if advice.get("fertilizer_principles"):

            print(
                "Fertilizer  :",
                advice.get(
                    "fertilizer_principles"
                )
            )

        # --- Preventive Actions ---
        # Try new field name first (preventive_actions)
        # then fallback to legacy (preventive_care)

        preventive = advice.get(
            "preventive_actions"
        ) or advice.get(
            "preventive_care"
        ) or []

        if preventive:

            print("\n  Preventive Actions:")

            for item in preventive:

                print(f"  • {item}")

        # --- Avoid Actions ---
        avoid = advice.get(
            "avoid_actions"
        ) or []

        if avoid:

            print("\n  Avoid Actions:")

            for item in avoid:

                print(f"  • {item}")

        # --- Critical Operations ---
        crit_ops = advice.get(
            "critical_operations"
        ) or []

        if crit_ops:

            print(
                "\n  Critical Operations: " +
                ", ".join(crit_ops)
            )

        # --- Water Management ---
        wm = advice.get("water_management")

        if isinstance(wm, dict):

            print("\n  Water Management:")

            if wm.get("requirement"):

                print(
                    f"  • Requirement: "
                    f"{wm.get('requirement')}"
                )

            if wm.get("irrigation_frequency"):

                print(
                    f"  • Irrigation: "
                    f"{wm.get('irrigation_frequency')}"
                )

            if wm.get("critical_condition"):

                print(
                    f"  • Critical: "
                    f"{wm.get('critical_condition')}"
                )

        # --- Risk Summary ---
        if advice.get("risk_summary"):

            print(
                "\n  Risk Summary:",
                advice.get("risk_summary")
            )

        # --- Yield Risk Level ---
        if advice.get("yield_risk_level"):

            print(
                "  Yield Risk Level:",
                advice.get(
                    "yield_risk_level"
                )
            )

    else:

        print(
            "No stage advice available"
        )

    # ------------------------------------------------
    # Disease Watch
    # ------------------------------------------------

    disease_packet = packet.get(
        "diseases"
    ) or {}

    print("\n🦠 DISEASE WATCH")

    if disease_packet.get("status") == "success":

        diseases = disease_packet.get(
            "diseases"
        ) or []

        if not diseases:

            print(
                "No active disease watch"
            )

        for disease in diseases:

            print(
                f"\n• {disease.get('name')} "
                f"(Severity: "
                f"{disease.get('severity')})"
            )

            symptoms = disease.get(
                "symptoms"
            ) or []

            if symptoms:

                print(
                    "  Symptoms  :",
                    ", ".join(symptoms)
                )

            if disease.get("prevention"):

                print(
                    "  Prevention:",
                    disease.get("prevention")
                )

            # --- Weather Risk Links ---
            weather_links = disease.get(
                "weather_risk_links"
            ) or []

            if weather_links:

                print(
                    "  Weather Links: " +
                    "; ".join(weather_links)
                )

            # --- Climate Triggers ---
            triggers = disease.get(
                "climate_triggers"
            ) or []

            if triggers:

                print(
                    "  Climate Triggers: " +
                    ", ".join(triggers)
                )

    else:

        print(
            "No disease information available"
        )

    # ------------------------------------------------
    # Fertilizer Guidance
    # ------------------------------------------------

    fert_packet = packet.get(
        "fertilizer"
    ) or {}

    print("\n🧪 FERTILIZER GUIDANCE")

    if fert_packet.get("status") == "success":

        fert = fert_packet.get(
            "fertilizer"
        ) or {}

        if fert.get("nutrient_principles"):

            print(
                "Nutrients   :",
                fert.get(
                    "nutrient_principles"
                )
            )

        if fert.get("primary_nutrients"):

            print(
                "Primary N   :",
                ", ".join(
                    fert.get(
                        "primary_nutrients"
                    )
                )
            )

        if fert.get("timing_guidance"):

            print(
                "Timing      :",
                fert.get("timing_guidance")
            )

        if fert.get("application_stage"):

            print(
                "Apply At    :",
                fert.get(
                    "application_stage"
                )
            )

        if fert.get("application_method"):

            print(
                "Method      :",
                fert.get(
                    "application_method"
                )
            )

        if fert.get("risk_if_skipped"):

            print(
                "Risk If Skipped:",
                fert.get("risk_if_skipped")
            )

        if fert.get("soil_type_adjustment"):

            print(
                "Soil Adjust :",
                fert.get(
                    "soil_type_adjustment"
                )
            )

        if fert.get("deficiency_symptoms"):

            print(
                "Deficiency  :",
                fert.get(
                    "deficiency_symptoms"
                )
            )

        if fert.get("avoid_overuse"):

            print(
                "Avoid       :",
                fert.get("avoid_overuse")
            )

        if fert.get("weather_precautions"):

            print(
                "Weather Prec:",
                fert.get(
                    "weather_precautions"
                )
            )

        if fert.get("recommended_focus"):

            print(
                "Focus       :",
                fert.get(
                    "recommended_focus"
                )
            )

        if fert.get("organic_alternatives"):

            print(
                "Organic     :",
                fert.get(
                    "organic_alternatives"
                )
            )

        if fert.get("cost_efficiency_tip"):

            print(
                "Cost Tip    :",
                fert.get(
                    "cost_efficiency_tip"
                )
            )

        if fert.get("notes"):

            print(
                "Notes       :",
                fert.get("notes")
            )

    else:

        print(
            "No fertilizer guidance available"
        )

    print("\n================================================")

    print("✅ REPORT COMPLETE")

    print("================================================\n")


# ---------------------------------------------------
# Backward-Compatible Formatting Alias
# ---------------------------------------------------
# Some tests / legacy callers use `format_for_farmer`
# as the public formatting entry point. We alias it
# to `farmer_view` for compatibility.
# ---------------------------------------------------

def format_for_farmer(packet):

    # Return the formatted string for callers that
    # expect a return value (e.g. tests), while
    # preserving the printable view.
    import io as _io
    import contextlib as _ctx

    buffer = _io.StringIO()

    with _ctx.redirect_stdout(buffer):

        farmer_view(packet)

    return buffer.getvalue()


# ---------------------------------------------------
# Test Harness (ONLY TEST BLOCK KEPT)
# ---------------------------------------------------

if __name__ == "__main__":

    packet = farmer_search(
        crop="rice",
        stage="flowering",
        state="Karnataka",
        district="Mandya"
    )

    print("\n--- STRUCTURED PACKET ---\n")

    print(
        json.dumps(
            packet,
            indent=2
        )
    )

    farmer_view(packet)

