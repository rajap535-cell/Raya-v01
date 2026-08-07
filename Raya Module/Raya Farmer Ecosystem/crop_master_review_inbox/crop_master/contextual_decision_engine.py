"""
RAYA — Contextual Decision Intelligence Layer
(PHASE-3 ADVANCED INTELLIGENCE VERSION)

Purpose
-------
Convert agricultural intelligence signals into
actionable farmer recommendations.

This layer consumes:
• Weather Intelligence
• Market Intelligence
• Crop Knowledge
• Stage Snapshot
• Water Intelligence

Advanced Features
-----------------
✔ Weather-to-action mapping
✔ Stage-aware intervention logic
✔ Priority escalation
✔ Multi-signal advisory synthesis
✔ Future API-ready architecture

Design Principles
-----------------
• Deterministic
• Rule-based only
• No ML
• Explainable outputs
• Structured recommendations
"""

# ---------------------------------------------------
# Imports
# ---------------------------------------------------

import json

from datetime import datetime, timezone

from farmer_search_engine import farmer_search


# ---------------------------------------------------
# Timezone-Aware UTC Timestamp
# ---------------------------------------------------

def utc_timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()


# ---------------------------------------------------
# Priority Scoring Engine
# ---------------------------------------------------

def _priority_score(level):

    mapping = {

        "Critical": 4,

        "High": 3,

        "Medium": 2,

        "Low": 1
    }

    return mapping.get(level, 1)


# ---------------------------------------------------
# Dynamic Priority Escalation
# ---------------------------------------------------

def calculate_priority(
    weather_risk,
    crop_stage,
    disease_count
):

    crop_stage = (
        crop_stage or ""
    ).capitalize()

    weather_risk = (
        weather_risk or ""
    ).capitalize()

    disease_count = disease_count or 0

    # -----------------------------------------------
    # Critical Escalation
    # -----------------------------------------------

    if (
        crop_stage == "Flowering"
        and weather_risk == "High"
    ):
        return "Critical"

    if (
        disease_count >= 2
        and weather_risk == "High"
    ):
        return "Critical"

    # -----------------------------------------------
    # High
    # -----------------------------------------------

    if weather_risk == "High":
        return "High"

    # -----------------------------------------------
    # Medium
    # -----------------------------------------------

    if weather_risk == "Medium":
        return "Medium"

    return "Low"


# ---------------------------------------------------
# Weather-to-Action Intelligence
# ---------------------------------------------------

def generate_weather_actions(
    weather_packet
):

    recommendations = []

    if weather_packet.get("status") != "success":

        return recommendations

    risk = weather_packet.get(
        "risk"
    ) or {}

    signals = weather_packet.get(
        "signals"
    ) or {}

    risk_level = risk.get(
        "risk_level"
    )

    risk_type = risk.get(
        "risk_type"
    )

    impacts = risk.get(
        "impact"
    ) or []

    # -----------------------------------------------
    # Flood / Rain
    # -----------------------------------------------

    if risk_type == "flood":

        recommendations.append({

            "type": "weather_management",

            "priority": "High",

            "action":
                "Improve field drainage immediately"
        })

        recommendations.append({

            "type": "crop_protection",

            "priority": "High",

            "action":
                "Avoid standing water around root zone"
        })

    # -----------------------------------------------
    # Drought
    # -----------------------------------------------

    elif risk_type == "drought":

        recommendations.append({

            "type": "irrigation_management",

            "priority": "High",

            "action":
                "Increase irrigation scheduling frequency"
        })

        recommendations.append({

            "type": "soil_management",

            "priority": "Medium",

            "action":
                "Reduce soil moisture loss using mulching"
        })

    # -----------------------------------------------
    # Heat Stress
    # -----------------------------------------------

    elif risk_type == "heat_stress":

        recommendations.append({

            "type": "heat_management",

            "priority": "High",

            "action":
                "Maintain adequate soil moisture during heat stress"
        })

        recommendations.append({

            "type": "crop_monitoring",

            "priority": "Medium",

            "action":
                "Monitor leaf rolling and flower stress symptoms"
        })

    # -----------------------------------------------
    # Humidity
    # -----------------------------------------------

    elif risk_type == "humidity":

        recommendations.append({

            "type": "disease_prevention",

            "priority": "High",

            "action":
                "Increase disease scouting frequency"
        })

        recommendations.append({

            "type": "field_management",

            "priority": "Medium",

            "action":
                "Improve field aeration and drainage"
        })

    # -----------------------------------------------
    # Signal-Based Intelligence
    # -----------------------------------------------

    if signals.get("spraying_safe") is False:

        recommendations.append({

            "type": "spraying_advisory",

            "priority": "Medium",

            "action":
                "Avoid pesticide spraying during expected rainfall"
        })

    if signals.get("irrigation_needed"):

        recommendations.append({

            "type": "irrigation_alert",

            "priority": "High",

            "action":
                "Immediate irrigation planning recommended"
        })

    # -----------------------------------------------
    # Impact Intelligence
    # -----------------------------------------------

    for impact in impacts:

        recommendations.append({

            "type": "risk_impact",

            "priority": risk_level,

            "action":
                f"Monitor crop impact: {impact}"
        })

    return recommendations


# ---------------------------------------------------
# Stage-Aware Intervention Logic
# ---------------------------------------------------

def generate_stage_actions(
    crop_stage,
    stage_packet
):

    recommendations = []

    if stage_packet.get("status") != "success":

        return recommendations

    crop_stage = (
        crop_stage or ""
    ).capitalize()

    sensitivity = stage_packet.get(
        "sensitivity"
    )

    critical_operations = stage_packet.get(
        "critical_operations"
    ) or []

    avoid_actions = stage_packet.get(
        "avoid_actions"
    ) or []

    # -----------------------------------------------
    # Flowering Stage Intelligence
    # -----------------------------------------------

    if crop_stage == "Flowering":

        recommendations.append({

            "type": "flowering_protection",

            "priority": "Critical",

            "action":
                "Avoid moisture stress during flowering"
        })

        recommendations.append({

            "type": "pollination_protection",

            "priority": "High",

            "action":
                "Maintain stable field conditions during pollination"
        })

    # -----------------------------------------------
    # Sensitivity Escalation
    # -----------------------------------------------

    if sensitivity == "High":

        recommendations.append({

            "type": "sensitivity_management",

            "priority": "High",

            "action":
                "High sensitivity stage requires continuous monitoring"
        })

    # -----------------------------------------------
    # Critical Operations
    # -----------------------------------------------

    for operation in critical_operations:

        recommendations.append({

            "type": "critical_operation",

            "priority": "Medium",

            "action":
                str(operation)
        })

    # -----------------------------------------------
    # Avoid Actions
    # -----------------------------------------------

    for item in avoid_actions:

        recommendations.append({

            "type": "avoid_action",

            "priority": "High",

            "action":
                f"Avoid: {str(item)}"
        })

    return recommendations


# ---------------------------------------------------
# Market Intelligence Mapping
# ---------------------------------------------------

def generate_market_actions(
    market_packet
):

    recommendations = []

    if market_packet.get("status") != "success":

        return recommendations

    trend = market_packet.get(
        "trend"
    ) or {}

    signals = market_packet.get(
        "signals"
    ) or {}

    direction = trend.get(
        "direction"
    )

    # -----------------------------------------------
    # Upward Trend
    # -----------------------------------------------

    if direction == "increasing":

        recommendations.append({

            "type": "market_strategy",

            "priority": "Low",

            "action":
                "Consider delayed selling if storage is available"
        })

    # -----------------------------------------------
    # Downward Trend
    # -----------------------------------------------

    elif direction == "decreasing":

        recommendations.append({

            "type": "market_strategy",

            "priority": "Medium",

            "action":
                "Monitor mandi prices closely for selling opportunity"
        })

    # -----------------------------------------------
    # Market Signals
    # -----------------------------------------------

    if signals.get("sell"):

        recommendations.append({

            "type": "market_signal",

            "priority": "Medium",

            "action":
                "Current market conditions support selling"
        })

    if signals.get("hold"):

        recommendations.append({

            "type": "market_signal",

            "priority": "Low",

            "action":
                "Holding crop may improve future returns"
        })

    return recommendations


# ---------------------------------------------------
# Water Management Formatter
# ---------------------------------------------------

def _format_water_management(
    water_management
):

    if not water_management:

        return None

    if isinstance(water_management, dict):

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

            freq_text = str(irrigation_frequency).strip()
            freq_lower = freq_text.lower()

            if freq_lower.startswith((
                "irrigate",
                "maintain",
                "keep",
                "avoid",
                "stop"
            )):

                parts.append(freq_text)

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

            return ". ".join(parts) + "."

    if isinstance(water_management, list):

        return "; ".join(
            str(item)
            for item in water_management
        )

    return str(water_management)


# ---------------------------------------------------
# Water Intelligence Mapping
# ---------------------------------------------------

def generate_water_actions(
    water_packet
):

    recommendations = []

    if water_packet.get("status") != "success":

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
                water_advisory
        })

    return recommendations
# ---------------------------------------------------
# Multi-Signal Advisory Synthesizer
# ---------------------------------------------------

def synthesize_advisories(
    recommendations
):

    # -----------------------------------------------
    # Remove duplicates safely
    # -----------------------------------------------

    unique = []

    seen = set()

    for item in recommendations:

        action = item.get("action")

        # -------------------------------------------
        # Normalize action safely
        # -------------------------------------------

        if isinstance(action, dict):

            key = json.dumps(
                action,
                sort_keys=True
            )

        elif isinstance(action, list):

            key = json.dumps(
                action,
                sort_keys=True
            )

        else:

            key = str(action)

        # -------------------------------------------
        # Duplicate check
        # -------------------------------------------

        if key in seen:
            continue

        seen.add(key)

        unique.append(item)

    # -----------------------------------------------
    # Priority Sorting
    # -----------------------------------------------

    unique.sort(

        key=lambda x:
        _priority_score(
            x.get("priority")
        ),

        reverse=True
    )

    return unique


# ---------------------------------------------------
# Main Contextual Intelligence Engine
# ---------------------------------------------------

def generate_contextual_advisory(
    crop,
    stage,
    state,
    district
):

    # -----------------------------------------------
    # Fetch Unified Packet
    # -----------------------------------------------

    packet = farmer_search(

        crop=crop,

        stage=stage,

        state=state,

        district=district
    )

    if packet.get("status") != "success":

        return packet

    # -----------------------------------------------
    # Extract Signals
    # -----------------------------------------------

    weather_packet = packet.get(
        "weather"
    ) or {}

    market_packet = packet.get(
        "market"
    ) or {}

    water_packet = packet.get(
        "water"
    ) or {}

    stage_packet = packet.get(
        "stage_snapshot"
    ) or {}

    disease_packet = packet.get(
        "diseases"
    ) or {}

    diseases = disease_packet.get(
        "diseases"
    ) or []

    weather_risk = (
        weather_packet.get("risk")
        or {}
    )

    weather_level = weather_risk.get(
        "risk_level"
    )

    # -----------------------------------------------
    # Dynamic Priority
    # -----------------------------------------------

    priority = calculate_priority(

        weather_level,

        stage,

        len(diseases)
    )

    # -----------------------------------------------
    # Generate Recommendations
    # -----------------------------------------------

    recommendations = []

    recommendations.extend(

        generate_weather_actions(
            weather_packet
        )
    )

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

    # -----------------------------------------------
    # Multi-Signal Advisory Synthesis
    # -----------------------------------------------

    synthesized = synthesize_advisories(
        recommendations
    )

    # -----------------------------------------------
    # Final Structured Advisory
    # -----------------------------------------------

    return {

        "status": "success",

        "meta": {

            "generated_at":
                utc_timestamp(),

            "engine":
                "RAYA Contextual Decision Engine"
        },

        "location":
            packet.get("location"),

        "crop":
            packet.get("crop"),

        "stage":
            packet.get("stage"),

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
                (
                    market_packet.get(
                        "trend",
                        {}
                    ).get("direction")
                ),

            "disease_count":
                len(diseases),

            "crop_stage":
                stage
        },

        "recommendations":
            synthesized
    }


# ---------------------------------------------------
# Farmer-Friendly Advisory Viewer
# ---------------------------------------------------

def show_contextual_advisory(
    packet
):

    if packet.get("status") != "success":

        print("\n❌ ERROR")

        print(packet.get("message"))

        return

    print("\n================================================")

    print(
        "🧠 RAYA CONTEXTUAL DECISION REPORT"
    )

    print("================================================\n")

    print(
        f"Crop      : {packet.get('crop')}"
    )

    print(
        f"Stage     : {packet.get('stage')}"
    )

    location = packet.get(
        "location"
    ) or {}

    print(
        f"Location  : "
        f"{location.get('district')}, "
        f"{location.get('state')}"
    )

    print(
        f"Priority  : "
        f"{packet.get('priority')}"
    )

    print("\n📌 SIGNALS")

    signals = packet.get(
        "signals"
    ) or {}

    for key, value in signals.items():

        print(
            f"• {key}: {value}"
        )

    print("\n✅ RECOMMENDATIONS")

    recommendations = packet.get(
        "recommendations"
    ) or []

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

    print("\n================================================")

    print("✅ ADVISORY COMPLETE")

    print("================================================\n")


# ---------------------------------------------------
# Test Harness
# ---------------------------------------------------

if __name__ == "__main__":

    advisory = generate_contextual_advisory(

        crop="rice",

        stage="flowering",

        state="Karnataka",

        district="Mandya"
    )

    print(
        "\n--- STRUCTURED ADVISORY ---\n"
    )

    print(
        json.dumps(
            advisory,
            indent=2
        )
    )

    show_contextual_advisory(
        advisory
    )
