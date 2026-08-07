"""
RAYA — Farmer Interactive Prototype (Streamlit)
================================================

Purpose
-------
First interactive prototype of the RAYA Farmer module.
A 4-page multipage app that visualizes everything already
built in the `crop_master` backend engines as a farmer and
developer would experience it.

Pages
-----
1. RAYA Farmer Dashboard   — Ask RAYA for a full advisory
2. Crop Knowledge Explorer — Inspect the Universal Crop Master
3. Crop Stage Explorer     — Inspect one specific growth stage
4. Engine Debug            — Inspect each engine's raw output

This is an internal testing environment before moving to
React, Android, WhatsApp, and RAYA OS.

Run
---
    streamlit run raya_farmer_interface.py
"""

import os
import sys
import json
from pathlib import Path

# -----------------------------------------------------
# Ensure the crop_master backend is importable
# -----------------------------------------------------
CROP_MASTER_DIR = Path(__file__).resolve().parent.parent / "crop_master"
CROPS_DIR = CROP_MASTER_DIR / "crops"

if str(CROP_MASTER_DIR) not in sys.path:
    sys.path.insert(0, str(CROP_MASTER_DIR))

# -----------------------------------------------------
# Streamlit
# -----------------------------------------------------
import streamlit as st

# -----------------------------------------------------
# Backend Engines
# -----------------------------------------------------
from farmer_search_engine import farmer_search
from contextual_decision_engine import generate_contextual_advisory 
from advisory_engine import build_advisory
from query_engine import get_stage_snapshot, get_water_requirement
from crop_knowledge_engine import (
    get_stage_advice,
    get_relevant_diseases,
    get_fertilizer_logic,
    get_stage_weather_actions,
)
from weather_intelligence.weather_engine import get_weather_risk
from market_engine import get_market_price

# -----------------------------------------------------
# Available Data (drives the dropdowns)
# -----------------------------------------------------
CROPS = {
    "Rice": ["Germination", "Seedling", "Tillering", "Panicle_Initiation", "Flowering", "Grain Filling", "Harvest"],
    "Tomato": ["Seedling", "Vegetative", "Flowering", "Fruit_Set", "Fruit_Maturity"],
    "Banana": ["Planting_Establishment", "Vegetative_Growth", "Flowering", "Fruit_Development", "Maturity"],
    "Wheat": ["Germination", "Tillering", "Stem_Elongation", "Flowering", "Grain_Filling", "Maturity"],
}

STATES = ["Karnataka"]
DISTRICTS = ["Mandya"]

# -----------------------------------------------------
# Page configuration
# -----------------------------------------------------
st.set_page_config(
    page_title="RAYA Farmer Interface",
    page_icon="🌾",
    layout="wide",
)

# =====================================================
# Presentation Helpers
# =====================================================

def _safe_get(data, key, default=None):
    if isinstance(data, dict):
        return data.get(key, default)
    return default


def _metric(label, value):
    """Render a single label/value pair as a clean line."""
    if value is None or value == "":
        return
    st.markdown(f"**{label}:** {value}")


def _list_items(items):
    """Render a list of strings as bullet points."""
    if not items:
        return
    if isinstance(items, str):
        items = [items]
    for item in items:
        if item:
            st.markdown(f"• {item}")


def _render_value(value, depth=0):
    """Recursively render a nested dict/list/scalar in a readable way."""
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                st.markdown(f"**{k}:**")
                _render_value(v, depth + 1)
            else:
                _metric(k, v)
    elif isinstance(value, list):
        _list_items(value)
    else:
        st.markdown(str(value))


def _load_crop_master(crop_name):
    """Load the raw Crop Master JSON for a crop."""
    crop_file = CROPS_DIR / f"{crop_name.lower()}.crop_master.json"
    if not crop_file.exists():
        return None
    with open(crop_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _render_json_block(data, title=None):
    """Render a dict as readable lines."""
    if title:
        st.markdown(f"**{title}**")
    _render_value(data)


def _render_stage_fields(stage_name, stage_data):
    """Render all fields stored for a single stage."""
    st.markdown(f"### {stage_name}")
    for key, value in stage_data.items():
        st.markdown(f"**{key}:**")
        _render_value(value)


# =====================================================
# Shared input block (used across pages)
# =====================================================

def render_shared_inputs(sidebar=False):
    """Render crop/stage/state/district selectors. Returns (crop, stage, state, district)."""
    if sidebar:
        st.sidebar.subheader("🎛️ Inputs")
        crop = st.sidebar.selectbox("Crop", list(CROPS.keys()), key="s_crop")
        stage = st.sidebar.selectbox("Growth Stage", CROPS[crop], key="s_stage")
        state = st.sidebar.selectbox("State", STATES, key="s_state")
        district = st.sidebar.selectbox("District", DISTRICTS, key="s_district")
    else:
        with st.form("shared_inputs"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                crop = st.selectbox("Crop", list(CROPS.keys()), key="m_crop")
            with col2:
                stage = st.selectbox("Growth Stage", CROPS[crop], key="m_stage")
            with col3:
                state = st.selectbox("State", STATES, key="m_state")
            with col4:
                district = st.selectbox("District", DISTRICTS, key="m_district")
            st.form_submit_button("Apply", use_container_width=True)
    return crop, stage, state, district


# =====================================================
# PAGE 1 — RAYA Farmer Dashboard
# =====================================================

def page_dashboard():
    st.title("🌾 RAYA Farmer Dashboard")
    st.caption("Your AI farming assistant — first interactive prototype")

    # ---- Today's Weather & Market Overview (live data) ----
    _dash_crop = st.selectbox("Crop for dashboard snapshot", list(CROPS.keys()), key="dash_crop")
    _dash_stage = st.selectbox("Growth Stage", CROPS[_dash_crop], key="dash_stage")
    _dash_state = st.selectbox("State", STATES, key="dash_state")
    _dash_district = st.selectbox("District", DISTRICTS, key="dash_district")

    _dc = _dash_crop.lower()
    _ds = _dash_state.title()
    _dd = _dash_district.title()

    col_w, col_m = st.columns(2)

    with col_w:
        st.subheader("☀️ Today's Weather")
        try:
            w = get_weather_risk(crop=_dc, stage=_dash_stage, state=_ds, district=_dd)
            if w.get("status") == "success":
                cur = w.get("current") or {}
                risk = w.get("risk") or {}
                fc = w.get("forecast") or {}
                m1, m2, m3 = st.columns(3)
                m1.metric("Temperature", f"{cur.get('temperature_avg')}°C")
                m2.metric("Humidity", f"{cur.get('humidity_percent')}%")
                m3.metric("Rainfall", f"{cur.get('rainfall_mm')} mm")
                _metric("Condition", cur.get("condition"))
                _metric("Wind Speed", f"{cur.get('wind_speed_kmh')} km/h")
                _metric("Risk Level", f"{risk.get('risk_level')} ({risk.get('risk_type')})")
                _metric("Forecast", f"{fc.get('expected_event')} (Prob: {fc.get('forecast_probability')})")
            else:
                st.info("_Live weather module coming soon._")
        except Exception as e:
            st.info("_Live weather module coming soon._")

    with col_m:
        st.subheader("📊 Market Overview")
        try:
            mk = get_market_price(crop=_dc, state=_ds, district=_dd)
            if mk.get("status") == "success":
                price = mk.get("price") or {}
                trend = mk.get("trend") or {}
                fc = mk.get("forecast") or {}
                loc = mk.get("location") or {}
                m1, m2, m3 = st.columns(3)
                m1.metric("Modal Price", f"₹{price.get('modal')}")
                m2.metric("Range", f"₹{price.get('min')}–₹{price.get('max')}")
                m3.metric("Trend", trend.get("direction"))
                _metric("Mandi", loc.get("mandi"))
                _metric("Forecast", f"{fc.get('next_7_days')} (Conf: {fc.get('confidence')})")
            else:
                st.info("_Live market module coming soon._")
        except Exception as e:
            st.info("_Live market module coming soon._")

    st.divider()

    st.header("🤖 Ask RAYA")

    with st.form("ask_raya_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            crop = st.selectbox("Crop", list(CROPS.keys()))
        with col2:
            stage = st.selectbox("Growth Stage", CROPS[crop])
        with col3:
            state = st.selectbox("State", STATES)
        with col4:
            district = st.selectbox("District", DISTRICTS)
        generate = st.form_submit_button("Generate Advisory", type="primary", use_container_width=True)

    if not generate:
        return

    with st.spinner("Asking RAYA..."):
        crop_key = crop.lower()
        state_key = state.title()
        district_key = district.title()

        packet = farmer_search(crop=crop_key, stage=stage, state=state_key, district=district_key)
        advisory = generate_contextual_advisory(crop=crop_key, stage=stage, state=state_key, district=district_key)

    if packet.get("status") != "success":
        st.error(packet.get("message", "Could not generate advisory."))
        return

    st.divider()
    st.header("🌱 RAYA Advisory Report")
    st.caption(f"{crop} • {stage} • {district}, {state} • Generated {_safe_get(packet, 'meta', {}).get('generated_at', '')}")

    # ---- Weather Intelligence ----
    weather = packet.get("weather") or {}
    with st.expander("🌧️ Weather Intelligence", expanded=True):
        if weather.get("status") == "success":
            current = weather.get("current") or {}
            risk = weather.get("risk") or {}
            forecast = weather.get("forecast") or {}
            signals = weather.get("signals") or {}
            climate_risks = weather.get("climate_risks") or []

            st.subheader("Current Conditions")
            _metric("Condition", current.get("condition"))
            _metric("Temperature", f"{current.get('temperature_avg')}°C (Min {current.get('temperature_min')}°C / Max {current.get('temperature_max')}°C)")
            _metric("Humidity", f"{current.get('humidity_percent')}%")
            _metric("Rainfall", f"{current.get('rainfall_mm')} mm")
            _metric("Wind Speed", f"{current.get('wind_speed_kmh')} km/h")

            st.subheader("Forecast")
            _metric("Expected Event", forecast.get("expected_event"))
            _metric("Forecast Window", forecast.get("window"))
            _metric("Probability", f"{forecast.get('forecast_probability')}")

            st.subheader("Risk Level")
            _metric("Risk Level", f"{risk.get('risk_level')} ({risk.get('risk_type')})")
            _list_items(risk.get("impact"))

            st.subheader("Climate Risks")
            if climate_risks:
                for cr in climate_risks:
                    st.markdown(f"• **{cr.get('type')}** (Risk: {cr.get('risk_level')}) — {', '.join(cr.get('effects') or ['No specific effects'])}")
            else:
                st.markdown("• No climate risks detected")

            st.subheader("Operational Signals")
            _metric("Irrigation Needed", signals.get("irrigation_needed"))
            _metric("Spraying Safe", signals.get("spraying_safe"))
            _metric("Harvest Risk", signals.get("harvest_risk"))
            _metric("Reason", signals.get("reason"))
        else:
            st.warning(weather.get("message", "No weather data available."))

    # ---- Water Intelligence ----
    water = packet.get("water") or {}
    with st.expander("💧 Water Intelligence", expanded=True):
        if water.get("status") == "success":
            wm = water.get("water_management") or {}
            if isinstance(wm, dict):
                _metric("Water Requirement", wm.get("requirement"))
                _metric("Irrigation Guidance", wm.get("irrigation_frequency"))
                _metric("Drainage", "Required" if wm.get("drainage_required") is True else ("Not required" if wm.get("drainage_required") is False else None))
                _metric("Soil Moisture", wm.get("soil_moisture"))
                _metric("Ideal Soil Moisture", wm.get("ideal_soil_moisture"))
                _metric("Critical Water Conditions", wm.get("critical_condition"))
                _metric("Water Stress Symptoms", wm.get("water_stress_symptoms"))
                _metric("Recovery Guidance", wm.get("recovery_guidance"))
            else:
                st.markdown(str(wm))
        else:
            st.warning("No water guidance available.")

    # ---- Crop Intelligence ----
    snapshot = packet.get("stage_snapshot") or {}
    with st.expander("🌱 Crop Intelligence", expanded=True):
        if snapshot.get("status") == "success":
            _metric("Current Stage", snapshot.get("stage"))
            _metric("Duration", f"{snapshot.get('duration_days')} days")
            _metric("Sensitivity", snapshot.get("sensitivity"))
            _metric("Yield Risk", snapshot.get("yield_risk_level"))
            st.subheader("Critical Operations")
            _list_items(snapshot.get("critical_operations"))
            _metric("Risk Summary", snapshot.get("risk_summary"))
        else:
            st.warning("No crop snapshot available.")

    # ---- Disease Intelligence ----
    diseases = packet.get("diseases") or {}
    with st.expander("🦠 Disease Intelligence", expanded=True):
        if diseases.get("status") == "success":
            disease_list = diseases.get("diseases") or []
            if not disease_list:
                st.markdown("No active disease watch at this stage.")
            for d in disease_list:
                st.markdown(f"**{d.get('name')}** (Severity: {d.get('severity')})")
                _metric("Symptoms", ", ".join(d.get("symptoms") or []))
                _metric("Climate Triggers", ", ".join(d.get("climate_triggers") or []))
                _metric("Weather Relationships", "; ".join(d.get("weather_risk_links") or []))
                _metric("Prevention", "; ".join(d.get("prevention") or []))
                st.divider()
        else:
            st.warning("No disease information available.")

    # ---- Fertilizer Intelligence ----
    fert = packet.get("fertilizer") or {}
    with st.expander("🧪 Fertilizer Intelligence", expanded=True):
        if fert.get("status") == "success":
            f = fert.get("fertilizer") or {}
            _metric("Primary Nutrients", ", ".join(f.get("primary_nutrients") or []))
            _metric("Timing", f.get("timing_guidance"))
            _metric("Application Stage", f.get("application_stage"))
            _metric("Application Method", f.get("application_method"))
            _metric("Weather Precautions", f.get("weather_precautions"))
            _metric("Organic Alternatives", f.get("organic_alternatives"))
            _metric("Cost Tips", f.get("cost_efficiency_tip"))
            _metric("Nutrient Principles", f.get("nutrient_principles"))
            _metric("Avoid Overuse", f.get("avoid_overuse"))
        else:
            st.warning("No fertilizer guidance available.")

    # ---- Market Intelligence ----
    market = packet.get("market") or {}
    with st.expander("📊 Market Intelligence", expanded=True):
        if market.get("status") == "success":
            price = market.get("price") or {}
            trend = market.get("trend") or {}
            forecast = market.get("forecast") or {}
            arrival = market.get("arrival") or {}
            loc = market.get("location") or {}

            _metric("Mandi", loc.get("mandi"))
            _metric("Current Price", f"₹{price.get('modal')} (₹{price.get('min')} - ₹{price.get('max')}) {price.get('currency')}" if price.get('modal') is not None else "N/A")
            _metric("Trend", f"{trend.get('direction')} ({trend.get('change_percent')}%)")
            _metric("Forecast", f"{forecast.get('next_7_days')} (Confidence: {forecast.get('confidence')})")
            _metric("Arrival", f"{arrival.get('quantity')} {arrival.get('unit')}")

            st.subheader("Suggested Selling Strategy")
            direction = trend.get("direction")
            if direction == "increasing":
                st.markdown("• Prices are rising. Consider **delayed selling** if you have storage.")
            elif direction == "decreasing":
                st.markdown("• Prices are falling. Monitor mandi closely and consider selling.")
            else:
                st.markdown("• Prices are stable. Plan sales based on your needs.")
        else:
            st.warning(market.get("message", "No market data available."))

    # ---- Final RAYA Recommendation ----
    st.divider()
    if advisory.get("status") == "success":
        st.header("🧠 Final RAYA Recommendation")
        st.caption("Produced by the Contextual Decision Engine")

        priority = advisory.get("priority")
        color = 'red' if priority == 'Critical' else ('orange' if priority == 'High' else 'green')
        st.markdown(f"**Overall Priority:** :{color}[{priority}]")

        signals = advisory.get("signals") or {}
        sig_cols = st.columns(5)
        sig_items = [
            ("Weather Risk", signals.get("weather_risk")),
            ("Weather Type", signals.get("weather_type")),
            ("Market Trend", signals.get("market_trend")),
            ("Disease Count", signals.get("disease_count")),
            ("Crop Stage", signals.get("crop_stage")),
        ]
        for col, (label, value) in zip(sig_cols, sig_items):
            col.metric(label, value)

        st.markdown("**Recommended Actions:**")
        recommendations = advisory.get("recommendations") or []
        if not recommendations:
            st.markdown("No recommendations generated.")
        for rec in recommendations:
            rc = 'red' if rec.get('priority') == 'Critical' else ('orange' if rec.get('priority') == 'High' else 'green')
            st.markdown(f"• :{rc}[{rec.get('priority')}] **{rec.get('type')}** — {rec.get('action')}")
    else:
        st.error(advisory.get("message", "Could not generate final recommendation."))

    st.divider()
    st.caption("RAYA is currently an internal prototype. Data sources are mock/rule-based.")


# =====================================================
# PAGE 2 — Crop Knowledge Explorer
# =====================================================

def page_knowledge_explorer():
    st.title("📚 Crop Knowledge Explorer")
    st.caption("Inspect the Universal Crop Master directly. No intelligence engines used here.")

    crop = st.selectbox("Select Crop", list(CROPS.keys()))

    data = _load_crop_master(crop)
    if not data:
        st.error(f"Crop Master not found for '{crop}'.")
        return

    # Map requested sections to their data keys (where they exist)
    sections = [
        ("General Information", ["general_information"]),
        ("Varieties", ["varieties"]),
        ("Growth Stages", ["growth_lifecycle", "stages"]),
        ("Soil", ["soil_intelligence"]),
        ("Climate", ["climate_intelligence"]),
        ("Water", ["water_intelligence"]),
        ("Fertilizer", ["fertilizer_intelligence"]),
        ("Diseases", ["diseases"]),
        ("Pests", ["pests"]),
        ("Harvest", ["harvest_intelligence"]),
        ("Post Harvest", ["post_harvest_intelligence"]),
        ("Best Practices", ["best_practices"]),
    ]

    for title, path in sections:
        # Resolve the data at the given path
        node = data
        found = True
        for key in path:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                found = False
                break

        with st.expander(title, expanded=False):
            if not found:
                st.markdown(f"_Not available for {crop}._")
            elif title == "Growth Stages":
                # node is the stages dict
                for stage_name, stage_data in node.items():
                    st.markdown(f"**{stage_name}**")
                    _render_value(stage_data)
                    st.divider()
            elif isinstance(node, list):
                for item in node:
                    if isinstance(item, dict):
                        name = item.get("name") or item.get("common_name") or "Item"
                        st.markdown(f"**{name}**")
                        _render_value({k: v for k, v in item.items() if k not in ("name", "common_name")})
                        st.divider()
                    else:
                        st.markdown(f"• {item}")
            else:
                _render_value(node)


# =====================================================
# PAGE 3 — Crop Stage Explorer
# =====================================================

def page_stage_explorer():
    st.title("🔬 Crop Stage Explorer")
    st.caption("Inspect every field stored for one specific growth stage. No engine processing.")

    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox("Select Crop", list(CROPS.keys()), key="stage_crop")
    with col2:
        stage = st.selectbox("Select Stage", CROPS[crop], key="stage_stage")

    data = _load_crop_master(crop)
    if not data:
        st.error(f"Crop Master not found for '{crop}'.")
        return

    stages = _safe_get(_safe_get(data, "growth_lifecycle"), "stages", {})
    stage_data = stages.get(stage)

    if not stage_data:
        st.warning(f"No stored fields for stage '{stage}' in {crop}.")
        return

    # Display every field stored for the stage
    _render_stage_fields(stage, stage_data)

    # Also show climate interactions for this stage (raw data)
    climate = _safe_get(data, "climate_interactions", {}).get(stage)
    if climate:
        st.divider()
        st.markdown("### Climate Interactions (this stage)")
        _render_value(climate)


# =====================================================
# PAGE 4 — Engine Debug
# =====================================================

def page_engine_debug():
    st.title("🔧 Engine Debug")
    st.caption("Inspect what each engine is producing independently. For developers.")

    crop = st.selectbox("Crop", list(CROPS.keys()), key="debug_crop")
    stage = st.selectbox("Growth Stage", CROPS[crop], key="debug_stage")
    state = st.selectbox("State", STATES, key="debug_state")
    district = st.selectbox("District", DISTRICTS, key="debug_district")

    crop_key = crop.lower()
    state_key = state.title()
    district_key = district.title()

    run = st.button("Run All Engines", type="primary")

    if not run:
        st.info("Select inputs and click **Run All Engines** to inspect each engine independently.")
        return

    engines = [
        ("Query Engine",
         lambda: get_stage_snapshot(crop_key, stage),
         "get_stage_snapshot(crop, stage)"),
        ("Query Engine — Water",
         lambda: get_water_requirement(crop_key, stage),
         "get_water_requirement(crop, stage)"),
        ("Weather Engine",
         lambda: get_weather_risk(crop=crop_key, stage=stage, state=state_key, district=district_key),
         "get_weather_risk(crop, stage, state, district)"),
        ("Market Engine",
         lambda: get_market_price(crop=crop_key, state=state_key, district=district_key),
         "get_market_price(crop, state, district)"),
        ("Crop Knowledge Engine — Stage Advice",
         lambda: get_stage_advice(crop_key, stage),
         "get_stage_advice(crop, stage)"),
        ("Crop Knowledge Engine — Diseases",
         lambda: get_relevant_diseases(crop_key, stage),
         "get_relevant_diseases(crop, stage)"),
        ("Crop Knowledge Engine — Fertilizer",
         lambda: get_fertilizer_logic(crop_key, stage),
         "get_fertilizer_logic(crop, stage)"),
        ("Crop Knowledge Engine — Weather Actions",
         lambda: get_stage_weather_actions(crop_key, stage),
         "get_stage_weather_actions(crop, stage)"),
        ("Farmer Search Engine",
         lambda: farmer_search(crop=crop_key, stage=stage, state=state_key, district=district_key),
         "farmer_search(crop, stage, state, district)"),
        ("Advisory Engine",
         lambda: build_advisory(farmer_search(crop=crop_key, stage=stage, state=state_key, district=district_key)),
         "build_advisory(farmer_search(...))"),
        ("Contextual Decision Engine",
         lambda: generate_contextual_advisory(crop=crop_key, stage=stage, state=state_key, district=district_key),
         "generate_contextual_advisory(crop, stage, state, district)"),
    ]

    for title, func, signature in engines:
        with st.expander(f"{title}", expanded=False):
            st.code(signature, language="python")
            try:
                result = func()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")


# =====================================================
# Navigation & dispatch
# =====================================================

PAGES = {
    "🌾 Farmer Dashboard": page_dashboard,
    "📚 Crop Knowledge Explorer": page_knowledge_explorer,
    "🔬 Crop Stage Explorer": page_stage_explorer,
    "🔧 Engine Debug": page_engine_debug,
}

st.sidebar.title("🌾 RAYA")
selection = st.sidebar.radio("Navigate", list(PAGES.keys()))

# Dispatch to the selected page
PAGES[selection]()
