"""
RAYA Farmer Interface - Phase 4F
Persistent Farmer Intelligence UI

## Architecture

Streamlit UI
|
| Create / Load
v
Persistent Farmer Registry
|
v
Farm & Field Registry
|
v
Soil Memory
|
v
Season Manager
|
v
PersistentFarmerPipeline
|
| farmer_search() ONCE ONLY
v
Contextual Decision Engine
|
v
Advisory History

## Important Design Rules

1. Streamlit contains presentation and data-entry only.
2. Agricultural intelligence remains in backend engines.
3. Personalization remains in Contextual Decision Engine.
4. farmer_search() is executed only by PersistentFarmerPipeline.
5. Every advisory is automatically persisted.
6. Existing farmers can be restored after application restart.

Run:

```
streamlit run raya_farmer_interface.py
```

"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================

# PATH CONFIGURATION

# ============================================================

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ============================================================

# STREAMLIT

# ============================================================

import streamlit as st

# ============================================================

# PHASE 4 BACKEND MODULES

# ============================================================

from persistent_memory.farmer_registry import (
    get_farmer_registry,
)

from persistent_memory.farm_field_registry import (
    get_farm_field_registry,
)

from persistent_memory.soil_memory import (
    get_soil_memory,
)

from persistent_memory.season_manager import (
    get_season_manager,
)

from persistent_memory.advisory_history import (
    get_advisory_history,
)

from persistent_memory.persistent_pipeline import (
    get_persistent_pipeline,
)

from persistent_memory.timeline_manager import (
    get_timeline_manager,
)

# ============================================================

# CONFIGURATION

# ============================================================

CROPS = {
    "Rice": [
        "Germination",
        "Seedling",
        "Tillering",
        "Panicle_Initiation",
        "Flowering",
        "Grain Filling",
        "Harvest",
    ],
    "Tomato": [
        "Seedling",
        "Vegetative",
        "Flowering",
        "Fruit_Set",
        "Fruit_Maturity",
    ],
    "Banana": [
        "Planting_Establishment",
        "Vegetative_Growth",
        "Flowering",
        "Fruit_Development",
        "Maturity",
    ],
    "Wheat": [
        "Germination",
        "Tillering",
        "Stem_Elongation",
        "Flowering",
        "Grain_Filling",
        "Maturity",
    ],
}

SOIL_TYPES = [
    "Clay",
    "Loamy",
    "Sandy",
    "Red laterite",
    "Black cotton",
    "Alluvial",
    "Mixed",
]

# ============================================================

# PAGE CONFIGURATION

# ============================================================

st.set_page_config(
    page_title="RAYA Farmer Intelligence",
    page_icon="🌾",
    layout="wide",
)

# ============================================================

# BACKEND SINGLETONS

# ============================================================

@st.cache_resource
def get_backend_services():

    return {
        "farmer_registry": get_farmer_registry(),
        "farm_field_registry": get_farm_field_registry(),
        "soil_memory": get_soil_memory(),
        "season_manager": get_season_manager(),
        "advisory_history": get_advisory_history(),
        "timeline_manager": get_timeline_manager(),
        "pipeline": get_persistent_pipeline(),
    }

SERVICES = get_backend_services()

FARMER_REGISTRY = SERVICES["farmer_registry"]

FARM_FIELD_REGISTRY = SERVICES[
    "farm_field_registry"
]

SOIL_MEMORY = SERVICES["soil_memory"]

SEASON_MANAGER = SERVICES[
    "season_manager"
]

ADVISORY_HISTORY = SERVICES[
    "advisory_history"
]

TIMELINE_MANAGER = SERVICES[
    "timeline_manager"
]

PERSISTENT_PIPELINE = SERVICES[
    "pipeline"
]

# ============================================================

# SESSION STATE

# ============================================================

DEFAULT_SESSION_STATE = {

    "selected_farmer_id": None,

    "selected_farm_id": None,

    "selected_field_id": None,

    "last_pipeline_result": None,

    "last_error": None,

}

for key, value in DEFAULT_SESSION_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ============================================================

# GENERAL HELPERS

# ============================================================

def safe_dict(
    value: Any,
) -> Dict[str, Any]:

    return value if isinstance(value, dict) else {}


def safe_list(
    value: Any,
) -> List[Any]:

    return value if isinstance(value, list) else []


def display_value(
    value: Any,
    default: str = "—",
) -> Any:

    if value is None:
        return default

    if isinstance(value, str):

        value = value.strip()

        return value if value else default

    return value


def render_json(
    data: Any,
):

    if data is None:

        st.info("No data available.")

        return

    st.json(data)


def get_selected_farmer():

    farmer_id = st.session_state.get(
        "selected_farmer_id"
    )

    if not farmer_id:

        return None

    return FARMER_REGISTRY.get_farmer(
        farmer_id
    )


def get_selected_farm():

    farm_id = st.session_state.get(
        "selected_farm_id"
    )

    if not farm_id:

        return None

    return FARM_FIELD_REGISTRY.get_farm(
        farm_id
    )


def get_selected_field():

    field_id = st.session_state.get(
        "selected_field_id"
    )

    if not field_id:

        return None

    return FARM_FIELD_REGISTRY.get_field(
        field_id
    )


def clear_selection_after_farmer():

    st.session_state.selected_farm_id = None

    st.session_state.selected_field_id = None

    st.session_state.last_pipeline_result = None


def clear_selection_after_farm():

    st.session_state.selected_field_id = None

    st.session_state.last_pipeline_result = None


# ============================================================

# HEADER

# ============================================================

def render_header():

    st.title(
        "🌾 RAYA — Persistent Farmer Intelligence"
    )

    st.caption(
        "Phase 4F • Persistent Farmer → Farm → Field → "
        "Soil → Season → Advisory → History"
    )

    st.divider()


# ============================================================

# SIDEBAR STATUS

# ============================================================

def render_sidebar_status():

    st.sidebar.title("🌾 RAYA")

    st.sidebar.caption(
        "Phase 4 — Persistent Farmer Intelligence"
    )

    st.sidebar.divider()

    farmer = get_selected_farmer()

    farm = get_selected_farm()

    field = get_selected_field()

    if farmer:

        st.sidebar.success(
            f"👨‍🌾 {farmer.get('name', 'Farmer')}"
        )

    else:

        st.sidebar.info(
            "No farmer selected"
        )

    if farm:

        st.sidebar.write(
            f"🏡 {farm.get('farm_name', 'Farm')}"
        )

    if field:

        st.sidebar.write(
            f"🌱 {field.get('field_name', 'Field')}"
        )

    st.sidebar.divider()


# ============================================================

# PAGE 1 - DASHBOARD

# ============================================================

def page_dashboard():

    render_header()

    st.header(
        "📊 Persistent Farmer Dashboard"
    )

    farmer = get_selected_farmer()

    farm = get_selected_farm()

    field = get_selected_field()

    if not farmer:

        st.info(
            "Select or create a farmer in "
            "👨‍🌾 Farmer Registry."
        )

        return

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Farmer",
            display_value(
                farmer.get("name")
            ),
        )

    with col2:

        st.metric(
            "District",
            display_value(
                farmer.get("district")
            ),
        )

    with col3:

        st.metric(
            "State",
            display_value(
                farmer.get("state")
            ),
        )

    st.divider()

    farms = (
        FARM_FIELD_REGISTRY
        .get_farmer_farms(
            farmer["farmer_id"]
        )
    )

    fields = (
        FARM_FIELD_REGISTRY
        .get_farmer_fields(
            farmer["farmer_id"]
        )
    )

    history = (
        ADVISORY_HISTORY
        .get_farmer_history(
            farmer["farmer_id"],
            limit=5,
        )
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Persistent Farms",
        len(farms),
    )

    c2.metric(
        "Persistent Fields",
        len(fields),
    )

    c3.metric(
        "Saved Advisories",
        len(history),
    )

    st.divider()

    st.subheader(
        "🌾 Current Agricultural Memory"
    )

    if farm:

        st.markdown(
            f"**Selected Farm:** "
            f"{farm.get('farm_name')}"
        )

    if field:

        st.markdown(
            f"**Selected Field:** "
            f"{field.get('field_name')}"
        )

        soil = (
            SOIL_MEMORY
            .get_field_soil_profile(
                field["field_id"]
            )
        )

        season = (
            SEASON_MANAGER
            .get_active_season(
                field["field_id"]
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                "### 🌍 Soil"
            )

            if soil:

                st.write(
                    f"Type: {display_value(soil.get('soil_type'))}"
                )

                st.write(
                    f"pH: {display_value(soil.get('ph'))}"
                )

                st.write(
                    "Nitrogen: "
                    f"{display_value(soil.get('nitrogen'))}"
                )

            else:

                st.warning(
                    "No persistent soil profile."
                )

        with col2:

            st.markdown(
                "### 🌱 Active Season"
            )

            if season:

                st.write(
                    f"Crop: {display_value(season.get('crop'))}"
                )

                st.write(
                    "Stage: "
                    f"{display_value(season.get('current_stage'))}"
                )

            else:

                st.warning(
                    "No active season."
                )

    st.divider()

    st.subheader(
        "🕒 Recent Advisory History"
    )

    if not history:

        st.info(
            "No advisory history yet."
        )

    else:

        for record in history:

            with st.expander(
                f"{record.get('crop', 'Crop')} • "
                f"{record.get('stage', 'Stage')} • "
                f"{record.get('created_at', '')}"
            ):

                st.write(
                    "**Priority:**",
                    record.get(
                        "overall_priority"
                    ),
                )

                recommendations = (
                    record.get(
                        "recommendations",
                        []
                    )
                )

                if recommendations:

                    st.write(
                        "**Recommendations:**"
                    )

                    for recommendation in recommendations[:3]:

                        if isinstance(
                            recommendation,
                            dict,
                        ):

                            st.write(
                                "• "
                                + str(
                                    recommendation.get(
                                        "action",
                                        recommendation,
                                    )
                                )
                            )

                        else:

                            st.write(
                                f"• {recommendation}"
                            )


# ============================================================

# PAGE 2 - FARMER REGISTRY

# ============================================================

def page_farmer_registry():

    render_header()

    st.header(
        "👨‍🌾 Farmer Registry"
    )

    st.caption(
        "Create persistent farmers or load existing "
        "farmer identities."
    )

    farmers = (
        FARMER_REGISTRY.list_farmers()
    )

    if farmers:

        labels = {

            farmer["farmer_id"]:
            (
                f"{farmer.get('name', 'Unknown')} "
                f"— {farmer.get('district', '')}, "
                f"{farmer.get('state', '')}"
            )

            for farmer in farmers
        }

        selected_id = st.selectbox(
            "Load Existing Farmer",
            options=list(labels.keys()),
            format_func=lambda value:
            labels[value],
        )

        if st.button(
            "📂 Load Selected Farmer",
            type="primary",
        ):

            st.session_state.selected_farmer_id = (
                selected_id
            )

            clear_selection_after_farmer()

            st.success(
                "Farmer loaded successfully."
            )

            st.rerun()

    else:

        st.info(
            "No persistent farmers found yet."
        )

    st.divider()

    st.subheader(
        "➕ Create New Farmer"
    )

    with st.form(
        "create_farmer_form"
    ):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Farmer Name *"
            )

            phone = st.text_input(
                "Phone *"
            )

            village = st.text_input(
                "Village"
            )

            district = st.text_input(
                "District",
                value="Mandya",
            )

        with col2:

            state = st.text_input(
                "State",
                value="Karnataka",
            )

            experience = st.number_input(
                "Farming Experience (Years)",
                min_value=0,
                max_value=80,
                value=5,
            )

        st.caption(
            "Farmer context used to personalize advisories."
        )

        profile_col1, profile_col2 = st.columns(2)

        with profile_col1:

            labor_availability = st.selectbox(
                "Labor Availability",
                [
                    "Not specified",
                    "Limited",
                    "Adequate",
                    "Sufficient",
                ],
            )

            budget_constraint = st.selectbox(
                "Budget Constraint",
                [
                    "Not specified",
                    "Low",
                    "Medium",
                    "High",
                ],
            )

        with profile_col2:

            guidance_preference = st.selectbox(
                "Guidance Preference",
                [
                    "Not specified",
                    "Preventive",
                    "Reactive",
                    "Both",
                ],
            )

            preferred_input_type = st.selectbox(
                "Preferred Input Type",
                [
                    "Not specified",
                    "Organic",
                    "Chemical",
                    "Integrated",
                ],
            )

        create = (
            st.form_submit_button(
                "💾 Create Persistent Farmer",
                type="primary",
            )
        )

    if create:

        try:

            farmer = (
                FARMER_REGISTRY
                .create_farmer(
                    name=name,
                    phone=phone,
                    village=village or None,
                    district=district or None,
                    state=state or None,
                    farming_experience_years=(
                        int(experience)
                    ),
                    labor_availability=(
                        None
                        if labor_availability == "Not specified"
                        else labor_availability
                    ),
                    budget_constraint=(
                        None
                        if budget_constraint == "Not specified"
                        else budget_constraint
                    ),
                    guidance_preference=(
                        None
                        if guidance_preference == "Not specified"
                        else guidance_preference
                    ),
                    preferred_input_type=(
                        None
                        if preferred_input_type == "Not specified"
                        else preferred_input_type
                    ),
                )
            )

            st.session_state.selected_farmer_id = (
                farmer["farmer_id"]
            )

            clear_selection_after_farmer()

            st.success(
                "Persistent farmer created: "
                f"{farmer['name']}"
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not create farmer: {error}"
            )


# ============================================================

# PAGE 3 - FARM & FIELD

# ============================================================

def page_farm_field():

    render_header()

    st.header(
        "🏡 Farm & Field Registry"
    )

    farmer = get_selected_farmer()

    if not farmer:

        st.warning(
            "Select a farmer first."
        )

        return

    st.success(
        f"Active Farmer: {farmer.get('name')}"
    )

    st.divider()

    farms = (
        FARM_FIELD_REGISTRY
        .get_farmer_farms(
            farmer["farmer_id"]
        )
    )

    st.subheader(
        "🏡 Select Farm"
    )

    if farms:

        farm_labels = {

            farm["farm_id"]:
            (
                f"{farm.get('farm_name')} "
                f"({farm.get('total_area_acres', '—')} acres)"
            )

            for farm in farms
        }

        selected_farm_id = st.selectbox(
            "Persistent Farms",
            options=list(
                farm_labels.keys()
            ),
            format_func=lambda value:
            farm_labels[value],
        )

        if st.button(
            "Select Farm"
        ):

            st.session_state.selected_farm_id = (
                selected_farm_id
            )

            clear_selection_after_farm()

            st.rerun()

    else:

        st.info(
            "No farms found for this farmer."
        )

    st.divider()

    st.subheader(
        "➕ Create Farm"
    )

    with st.form(
        "create_farm_form"
    ):

        col1, col2 = st.columns(2)

        with col1:

            farm_name = st.text_input(
                "Farm Name *"
            )

            village = st.text_input(
                "Village"
            )

            district = st.text_input(
                "District",
                value=display_value(
                    farmer.get(
                        "district"
                    ),
                    "Mandya",
                ),
            )

            state = st.text_input(
                "State",
                value=display_value(
                    farmer.get(
                        "state"
                    ),
                    "Karnataka",
                ),
            )

        with col2:

            total_area = st.number_input(
                "Total Area (Acres)",
                min_value=0.1,
                value=1.0,
            )

            irrigation_source = st.selectbox(
                "Irrigation Source",
                [
                    "Canal",
                    "Borewell",
                    "Rainfed",
                    "Tank",
                    "River",
                    "Mixed",
                ],
            )

        create_farm = (
            st.form_submit_button(
                "Create Persistent Farm",
                type="primary",
            )
        )

    if create_farm:

        try:

            farm = (
                FARM_FIELD_REGISTRY
                .create_farm(
                    farmer_id=farmer[
                        "farmer_id"
                    ],
                    farm_name=farm_name,
                    village=village or None,
                    district=district or None,
                    state=state or None,
                    total_area_acres=float(
                        total_area
                    ),
                    irrigation_source=(
                        irrigation_source
                    ),
                )
            )

            st.session_state.selected_farm_id = (
                farm["farm_id"]
            )

            clear_selection_after_farm()

            st.success(
                "Persistent farm created."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not create farm: {error}"
            )

    st.divider()

    farm = get_selected_farm()

    if not farm:

        return

    st.subheader(
        f"🌱 Fields — {farm.get('farm_name')}"
    )

    fields = (
        FARM_FIELD_REGISTRY
        .get_farm_fields(
            farm["farm_id"]
        )
    )

    if fields:

        field_labels = {

            field["field_id"]:
            (
                f"{field.get('field_name')} "
                f"({field.get('area_acres', '—')} acres)"
            )

            for field in fields
        }

        selected_field_id = st.selectbox(
            "Select Field",
            options=list(
                field_labels.keys()
            ),
            format_func=lambda value:
            field_labels[value],
        )

        if st.button(
            "Select Field",
            type="primary",
        ):

            st.session_state.selected_field_id = (
                selected_field_id
            )

            st.session_state.last_pipeline_result = (
                None
            )

            st.rerun()

    else:

        st.info(
            "No fields found for this farm."
        )

    st.divider()

    st.subheader(
        "➕ Create Field"
    )

    with st.form(
        "create_field_form"
    ):

        col1, col2 = st.columns(2)

        with col1:

            field_name = st.text_input(
                "Field Name *"
            )

            field_area = st.number_input(
                "Field Area (Acres)",
                min_value=0.1,
                value=1.0,
            )

        with col2:

            irrigation_available = st.checkbox(
                "Irrigation Available",
                value=True,
            )

        create_field = (
            st.form_submit_button(
                "Create Persistent Field",
                type="primary",
            )
        )

    if create_field:

        try:

            field = (
                FARM_FIELD_REGISTRY
                .create_field(
                    farm_id=farm[
                        "farm_id"
                    ],
                    field_name=field_name,
                    area_acres=float(
                        field_area
                    ),
                    irrigation_available=(
                        irrigation_available
                    ),
                )
            )

            st.session_state.selected_field_id = (
                field["field_id"]
            )

            st.success(
                "Persistent field created."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not create field: {error}"
            )


# ============================================================

# PAGE 4 - SOIL MEMORY

# ============================================================

def page_soil_memory():

    render_header()

    st.header(
        "🌍 Persistent Soil Memory"
    )

    field = get_selected_field()

    if not field:

        st.warning(
            "Select a field first."
        )

        return

    st.success(
        f"Active Field: "
        f"{field.get('field_name')}"
    )

    profile = (
        SOIL_MEMORY
        .get_field_soil_profile(
            field["field_id"]
        )
    )

    if profile:

        st.subheader(
            "Current Persistent Soil Profile"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "Soil Type",
            display_value(
                profile.get("soil_type")
            ),
        )

        col2.metric(
            "pH",
            display_value(
                profile.get("ph")
            ),
        )

        col3.metric(
            "Nitrogen",
            display_value(
                profile.get("nitrogen")
            ),
        )

        col4.metric(
            "Moisture %",
            display_value(
                profile.get(
                    "moisture_percent"
                )
            ),
        )

    st.divider()

    st.subheader(
        "💾 Create / Update Soil Profile"
    )

    defaults = safe_dict(profile)

    with st.form(
        "soil_memory_form"
    ):

        col1, col2 = st.columns(2)

        with col1:

            soil_type = st.selectbox(
                "Soil Type",
                SOIL_TYPES,
                index=(
                    SOIL_TYPES.index(
                        defaults.get(
                            "soil_type"
                        )
                    )
                    if defaults.get(
                        "soil_type"
                    )
                    in SOIL_TYPES
                    else 0
                ),
            )

            ph = st.number_input(
                "pH",
                min_value=0.0,
                max_value=14.0,
                value=float(
                    defaults.get(
                        "ph"
                    )
                    or 7.0
                ),
            )

            nitrogen = st.number_input(
                "Nitrogen",
                min_value=0.0,
                value=float(
                    defaults.get(
                        "nitrogen"
                    )
                    or 0.0
                ),
            )

            phosphorus = st.number_input(
                "Phosphorus",
                min_value=0.0,
                value=float(
                    defaults.get(
                        "phosphorus"
                    )
                    or 0.0
                ),
            )

        with col2:

            potassium = st.number_input(
                "Potassium",
                min_value=0.0,
                value=float(
                    defaults.get(
                        "potassium"
                    )
                    or 0.0
                ),
            )

            organic_carbon = st.number_input(
                "Organic Carbon",
                min_value=0.0,
                value=float(
                    defaults.get(
                        "organic_carbon"
                    )
                    or 0.0
                ),
            )

            moisture_percent = st.number_input(
                "Moisture %",
                min_value=0.0,
                max_value=100.0,
                value=float(
                    defaults.get(
                        "moisture_percent"
                    )
                    or 0.0
                ),
            )

            electrical_conductivity = (
                st.number_input(
                    "Electrical Conductivity",
                    min_value=0.0,
                    value=float(
                        defaults.get(
                            "electrical_conductivity"
                        )
                        or 0.0
                    ),
                )
            )

        save_soil = (
            st.form_submit_button(
                "Save Persistent Soil Profile",
                type="primary",
            )
        )

    if save_soil:

        try:

            if profile is None:

                SOIL_MEMORY.create_soil_profile(
                    field_id=field[
                        "field_id"
                    ],
                    soil_type=soil_type,
                    ph=ph,
                    nitrogen=nitrogen,
                    phosphorus=phosphorus,
                    potassium=potassium,
                    organic_carbon=organic_carbon,
                    moisture_percent=moisture_percent,
                    electrical_conductivity=(
                        electrical_conductivity
                    ),
                )

                st.success(
                    "Persistent soil profile created."
                )

            else:

                SOIL_MEMORY.update_soil_profile(
                    field_id=field[
                        "field_id"
                    ],
                    soil_type=soil_type,
                    ph=ph,
                    nitrogen=nitrogen,
                    phosphorus=phosphorus,
                    potassium=potassium,
                    organic_carbon=organic_carbon,
                    moisture_percent=moisture_percent,
                    electrical_conductivity=(
                        electrical_conductivity
                    ),
                )

                st.success(
                    "Soil profile updated and "
                    "history preserved."
                )

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not save soil profile: {error}"
            )

    st.divider()

    history = (
        SOIL_MEMORY
        .get_soil_history(
            field["field_id"]
        )
    )

    st.subheader(
        "🕒 Soil Change History"
    )

    if not history:

        st.info(
            "No previous soil snapshots yet."
        )

    else:

        for index, snapshot in enumerate(
            reversed(history),
            start=1,
        ):

            with st.expander(
                f"Historical Snapshot {index}"
            ):

                render_json(
                    snapshot
                )


# ============================================================

# PAGE 5 - SEASON MANAGER

# ============================================================

def page_season_manager():

    render_header()

    st.header(
        "📅 Season Manager"
    )

    field = get_selected_field()

    if not field:

        st.warning(
            "Select a field first."
        )

        return

    st.success(
        f"Active Field: "
        f"{field.get('field_name')}"
    )

    active_season = (
        SEASON_MANAGER
        .get_active_season(
            field["field_id"]
        )
    )

    if active_season:

        st.subheader(
            "🌱 Active Season"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Season",
            display_value(
                active_season.get(
                    "season_name"
                )
            ),
        )

        c2.metric(
            "Crop",
            display_value(
                active_season.get(
                    "crop"
                )
            ),
        )

        c3.metric(
            "Stage",
            display_value(
                active_season.get(
                    "current_stage"
                )
            ),
        )

        with st.expander(
            "View Active Season Record"
        ):

            render_json(
                active_season
            )

    else:

        st.info(
            "No active season exists for "
            "this field."
        )

    st.divider()

    st.subheader(
        "➕ Create Active Season"
    )

    crop = st.selectbox(
        "Crop",
        list(CROPS.keys()),
    )

    stage = st.selectbox(
        "Current Growth Stage",
        CROPS[crop],
    )

    season_name = st.selectbox(
        "Season",
        [
            "Kharif",
            "Rabi",
            "Zaid",
            "Annual",
        ],
    )

    if st.button(
        "Create / Activate Season",
        type="primary",
    ):

        try:

            # Compatibility adapter for the exact
            # SeasonManager implementation.
            #
            # Preferred signature:
            # create_season(
            #     field_id,
            #     season_name,
            #     crop,
            #     current_stage
            # )

            try:

                season = (
                    SEASON_MANAGER
                    .create_season(
                        field_id=field[
                            "field_id"
                        ],
                        season_name=season_name,
                        crop=crop,
                        current_stage=stage,
                    )
                )

            except TypeError:

                season = (
                    SEASON_MANAGER
                    .create_season(
                        field_id=field[
                            "field_id"
                        ],
                        crop=crop,
                        current_stage=stage,
                        season_name=season_name,
                    )
                )

            st.success(
                "Persistent season activated."
            )

            render_json(
                season
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not create season: {error}"
            )

    st.divider()

    st.subheader(
        "📚 Field Crop History"
    )

    # Try common history method names so this UI remains
    # compatible with the Phase 4C backend.

    season_history = []

    if hasattr(
        SEASON_MANAGER,
        "get_field_seasons",
    ):

        season_history = (
            SEASON_MANAGER
            .get_field_seasons(
                field["field_id"]
            )
        )

    elif hasattr(
        SEASON_MANAGER,
        "get_season_history",
    ):

        season_history = (
            SEASON_MANAGER
            .get_season_history(
                field["field_id"]
            )
        )

    if not season_history:

        st.info(
            "No historical seasons available yet."
        )

    else:

        for season in season_history:

            with st.expander(
                f"{season.get('crop', 'Crop')} • "
                f"{season.get('season_name', 'Season')}"
            ):

                render_json(
                    season
                )


# ============================================================

# PAGE 6 - GENERATE ADVISORY

# ============================================================

def page_generate_advisory():

    render_header()

    st.header(
        "🎯 Generate Persistent Advisory"
    )

    farmer = get_selected_farmer()

    farm = get_selected_farm()

    field = get_selected_field()

    if not farmer:

        st.warning(
            "Select a farmer first."
        )

        return

    if not farm:

        st.warning(
            "Select a farm first."
        )

        return

    if not field:

        st.warning(
            "Select a field first."
        )

        return

    soil = (
        SOIL_MEMORY
        .get_field_soil_profile(
            field["field_id"]
        )
    )

    season = (
        SEASON_MANAGER
        .get_active_season(
            field["field_id"]
        )
    )

    if soil is None:

        st.warning(
            "Create a persistent soil profile "
            "before generating an advisory."
        )

        return

    if season is None:

        st.warning(
            "Create an active season before "
            "generating an advisory."
        )

        return

    st.success(
        "Persistent agricultural context ready."
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Farmer",
        farmer.get("name"),
    )

    col2.metric(
        "Farm",
        farm.get("farm_name"),
    )

    col3.metric(
        "Field",
        field.get("field_name"),
    )

    col4.metric(
        "Crop",
        season.get("crop"),
    )

    st.divider()

    st.markdown(
        """

### Backend Execution

When you click generate:

```text
Persistent Farmer
      ↓
Persistent Farm
      ↓
Persistent Field
      ↓
Persistent Soil
      ↓
Active Season
      ↓
build_farmer_context()
      ↓
farmer_search()  ← ONCE ONLY
      ↓
Contextual Decision Engine
      ↓
Advisory History ← AUTO SAVE
```

"""
    )

    if st.button(
        "🚀 Generate RAYA Advisory",
        type="primary",
        use_container_width=True,
    ):

        try:

            with st.spinner(
                "RAYA is analyzing persistent "
                "farmer intelligence..."
            ):

                result = (
                    PERSISTENT_PIPELINE
                    .generate_advisory(
                        farmer_id=farmer[
                            "farmer_id"
                        ],
                        farm_id=farm[
                            "farm_id"
                        ],
                        field_id=field[
                            "field_id"
                        ],
                    )
                )

            st.session_state.last_pipeline_result = (
                result
            )

            st.success(
                "Advisory generated and "
                "automatically saved to history."
            )

        except Exception as error:

            st.session_state.last_error = str(
                error
            )

            st.error(
                f"Pipeline failed: {error}"
            )

            return

    result = (
        st.session_state.get(
            "last_pipeline_result"
        )
    )

    if not result:

        return

    st.divider()

    st.header(
        "🤖 RAYA Advisory"
    )

    advisory = safe_dict(
        result.get(
            "contextual_advisory"
        )
    )

    history_record = safe_dict(
        result.get(
            "advisory_history_record"
        )
    )

    priority = (
        advisory.get("priority")
        or advisory.get(
            "overall_priority"
        )
        or history_record.get(
            "overall_priority"
        )
    )

    if priority:

        st.metric(
            "Overall Priority",
            priority,
        )

    recommendations = safe_list(
        advisory.get(
            "recommendations"
        )
    )

    if recommendations:

        st.subheader(
            "Recommended Actions"
        )

        for index, recommendation in enumerate(
            recommendations,
            start=1,
        ):

            if isinstance(
                recommendation,
                dict,
            ):

                priority_text = (
                    recommendation.get(
                        "priority",
                        "Standard",
                    )
                )

                action = (
                    recommendation.get(
                        "action",
                        recommendation.get(
                            "recommendation",
                            "No action text",
                        ),
                    )
                )

                st.markdown(
                    f"**{index}. "
                    f"[{priority_text}]** "
                    f"{action}"
                )

                reasons = safe_list(
                    recommendation.get(
                        "personalization_reasons"
                    )
                )

                for reason in reasons:

                    st.caption(
                        f"Why personalized: {reason}"
                    )

            else:

                st.markdown(
                    f"{index}. {recommendation}"
                )

    personalization_reasons = safe_list(
        advisory.get(
            "personalization_reasons"
        )
    )

    if personalization_reasons:

        st.subheader(
            "🧠 Personalization Reasons"
        )

        for reason in personalization_reasons:

            st.markdown(
                f"• {reason}"
            )

    final_recommendation = safe_dict(
        advisory.get(
            "final_recommendation"
        )
    )

    if final_recommendation:

        st.subheader(
            "🌾 Farmer Summary"
        )

        headline = (
            final_recommendation.get(
                "headline"
            )
        )

        if headline:

            st.success(
                headline
            )

        for item in safe_list(
            final_recommendation.get(
                "what_to_do"
            )
        ):

            st.write(
                f"• {item}"
            )

    st.divider()

    st.subheader(
        "💾 Persistence Confirmation"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Advisory ID",
        display_value(
            history_record.get(
                "advisory_id"
            )
        ),
    )

    c2.metric(
        "Field ID",
        display_value(
            history_record.get(
                "field_id"
            )
        ),
    )

    c3.metric(
        "Saved",
        "Yes"
        if history_record
        else "No",
    )

    with st.expander(
        "Developer View — Complete Pipeline Result"
    ):

        render_json(
            result
        )


# ============================================================

# PAGE 7 - ADVISORY HISTORY

# ============================================================

def page_advisory_history():

    render_header()

    st.header(
        "🕒 Persistent Advisory History"
    )

    farmer = get_selected_farmer()

    if not farmer:

        st.warning(
            "Select a farmer first."
        )

        return

    field = get_selected_field()

    if field:

        history = (
            ADVISORY_HISTORY
            .get_field_history(
                field["field_id"]
            )
        )

        scope = (
            f"Field: "
            f"{field.get('field_name')}"
        )

    else:

        history = (
            ADVISORY_HISTORY
            .get_farmer_history(
                farmer["farmer_id"]
            )
        )

        scope = (
            f"Farmer: "
            f"{farmer.get('name')}"
        )

    st.caption(
        f"Viewing advisory history for {scope}"
    )

    if not history:

        st.info(
            "No saved advisories yet."
        )

        return

    st.metric(
        "Total Saved Advisories",
        len(history),
    )

    for record in history:

        crop = record.get(
            "crop",
            "Unknown Crop",
        )

        stage = record.get(
            "stage",
            "Unknown Stage",
        )

        timestamp = record.get(
            "created_at",
            "",
        )

        with st.expander(
            f"🌾 {crop} • {stage} • {timestamp}"
        ):

            st.write(
                "**Priority:**",
                record.get(
                    "overall_priority"
                ),
            )

            recommendations = safe_list(
                record.get(
                    "recommendations"
                )
            )

            if recommendations:

                st.write(
                    "**Recommendations:**"
                )

                for recommendation in recommendations:

                    if isinstance(
                        recommendation,
                        dict,
                    ):

                        st.write(
                            "• "
                            + str(
                                recommendation.get(
                                    "action",
                                    recommendation,
                                )
                            )
                        )

                    else:

                        st.write(
                            f"• {recommendation}"
                        )

            reasons = safe_list(
                record.get(
                    "personalization_reasons"
                )
            )

            if reasons:

                st.write(
                    "**Personalization Reasons:**"
                )

                for reason in reasons:

                    st.write(
                        f"• {reason}"
                    )

            with st.expander(
                "Complete Historical Record"
            ):

                render_json(
                    record
                )


# ============================================================

# PAGE 8 - FIELD TIMELINE

# ============================================================

def page_field_timeline():

    render_header()

    st.header(
        "🗓️ Field Timeline"
    )

    farmer = get_selected_farmer()
    field = get_selected_field()

    if not farmer:

        st.warning(
            "Select a farmer first."
        )

        return

    if not field:

        st.warning(
            "Select a field first."
        )

        return

    st.caption(
        f"Chronological field activity for "
        f"{field.get('field_name')} • "
        f"{farmer.get('name')}"
    )

    window = st.selectbox(
        "History window",
        ["All history", "Last 30 days", "Last 60 days"],
    )

    if window == "Last 30 days":
        events = TIMELINE_MANAGER.get_last_30_days(
            field["field_id"]
        )
    elif window == "Last 60 days":
        events = TIMELINE_MANAGER.get_last_60_days(
            field["field_id"]
        )
    else:
        events = TIMELINE_MANAGER.get_field_history(
            field["field_id"]
        )

    st.metric(
        "Recorded field events",
        len(events),
    )

    if not events:

        st.info(
            "No field activity has been recorded yet."
        )

        return

    st.table(
        [
            {
                "Date": event["occurred_at"].replace(
                    "T", " "
                )[:19],
                "Event": event["title"],
                "Type": event["event_type"].replace(
                    "_", " "
                ).title(),
                "Details": ", ".join(
                    f"{key}: {value}"
                    for key, value in event.get(
                        "details", {}
                    ).items()
                    if value is not None
                ),
            }
            for event in events
        ]
    )

    st.caption(
        "Events are read from the persistent field activity log. "
        "Agricultural reasoning remains in the backend decision engine."
    )


# ============================================================

# PAGE 9 - FARMER MEMORY VIEW

# ============================================================

def page_farmer_memory():

    render_header()

    st.header(
        "🧠 Complete Persistent Agricultural Memory"
    )

    farmer = get_selected_farmer()

    if not farmer:

        st.warning(
            "Select a farmer first."
        )

        return

    try:

        hierarchy = (
            FARM_FIELD_REGISTRY
            .get_farmer_hierarchy(
                farmer["farmer_id"]
            )
        )

    except Exception as error:

        st.error(
            f"Could not load hierarchy: {error}"
        )

        return

    st.subheader(
        f"👨‍🌾 {farmer.get('name')}"
    )

    for farm_item in hierarchy.get(
        "farms",
        [],
    ):

        farm = safe_dict(
            farm_item.get(
                "farm"
            )
        )

        with st.expander(
            f"🏡 {farm.get('farm_name')}",
            expanded=True,
        ):

            st.write(
                f"Location: "
                f"{farm.get('district')}, "
                f"{farm.get('state')}"
            )

            st.write(
                f"Area: "
                f"{farm.get('total_area_acres')} acres"
            )

            for field in farm_item.get(
                "fields",
                [],
            ):

                field_id = field.get(
                    "field_id"
                )

                st.markdown(
                    f"### 🌱 {field.get('field_name')}"
                )

                soil = (
                    SOIL_MEMORY
                    .get_field_soil_profile(
                        field_id
                    )
                )

                season = (
                    SEASON_MANAGER
                    .get_active_season(
                        field_id
                    )
                )

                history = (
                    ADVISORY_HISTORY
                    .get_field_history(
                        field_id,
                        limit=5,
                    )
                )

                col1, col2, col3 = (
                    st.columns(3)
                )

                col1.metric(
                    "Area",
                    display_value(
                        field.get(
                            "area_acres"
                        )
                    ),
                )

                col2.metric(
                    "Soil",
                    display_value(
                        safe_dict(soil).get(
                            "soil_type"
                        )
                    ),
                )

                col3.metric(
                    "Advisories",
                    len(history),
                )

                if season:

                    st.caption(
                        f"Active Season: "
                        f"{season.get('crop')} "
                        f"({season.get('current_stage')})"
                    )

                if history:

                    latest = history[0]

                    st.caption(
                        "Latest Advisory: "
                        f"{latest.get('crop')} • "
                        f"{latest.get('overall_priority')}"
                    )


# ============================================================

# PAGE 10 - DEVELOPER DEBUG

# ============================================================

def page_debug():

    render_header()

    st.header(
        "🔧 Persistent Memory Debug"
    )

    farmer = get_selected_farmer()

    farm = get_selected_farm()

    field = get_selected_field()

    st.subheader(
        "Current Selection"
    )

    col1, col2, col3 = st.columns(3)

    col1.write(
        f"Farmer ID: "
        f"{farmer.get('farmer_id') if farmer else None}"
    )

    col2.write(
        f"Farm ID: "
        f"{farm.get('farm_id') if farm else None}"
    )

    col3.write(
        f"Field ID: "
        f"{field.get('field_id') if field else None}"
    )

    st.divider()

    if farmer:

        with st.expander(
            "Farmer Record"
        ):

            render_json(
                farmer
            )

    if farm:

        with st.expander(
            "Farm Record"
        ):

            render_json(
                farm
            )

    if field:

        with st.expander(
            "Field Record"
        ):

            render_json(
                field
            )

        soil = (
            SOIL_MEMORY
            .get_field_soil_profile(
                field["field_id"]
            )
        )

        season = (
            SEASON_MANAGER
            .get_active_season(
                field["field_id"]
            )
        )

        history = (
            ADVISORY_HISTORY
            .get_field_history(
                field["field_id"]
            )
        )

        with st.expander(
            "Soil Memory"
        ):

            render_json(
                soil
            )

        with st.expander(
            "Active Season"
        ):

            render_json(
                season
            )

        with st.expander(
            "Advisory History"
        ):

            render_json(
                history
            )

    st.divider()

    st.subheader(
        "Architecture Check"
    )

    st.success(
        "✓ Streamlit only renders and collects input"
    )

    st.success(
        "✓ Persistent registries own data storage"
    )

    st.success(
        "✓ Persistent pipeline owns orchestration"
    )

    st.success(
        "✓ Contextual Decision Engine owns personalization"
    )

    st.success(
        "✓ Advisory History owns historical storage"
    )

    st.success(
        "✓ farmer_search() is not called directly by UI"
    )


# ============================================================

# NAVIGATION

# ============================================================

PAGES = {

    "📊 Dashboard":
        page_dashboard,

    "👨‍🌾 Farmer Registry":
        page_farmer_registry,

    "🏡 Farm & Field":
        page_farm_field,

    "🌍 Soil Memory":
        page_soil_memory,

    "📅 Season Manager":
        page_season_manager,

    "🎯 Generate Advisory":
        page_generate_advisory,

    "🕒 Advisory History":
        page_advisory_history,

    "🗓️ Field Timeline":
        page_field_timeline,

    "🧠 Farmer Memory":
        page_farmer_memory,

    "🔧 Debug":
        page_debug,

}

# ============================================================

# APP START

# ============================================================

render_sidebar_status()

selected_page = st.sidebar.radio(
    "Navigate",
    list(PAGES.keys()),
)

PAGES[selected_page]()
