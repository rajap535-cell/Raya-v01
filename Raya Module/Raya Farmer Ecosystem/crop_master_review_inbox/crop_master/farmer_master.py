"""
RAYA Phase-2 — Farmer Master Module (LOCKED VERSION)

✔ Input Validation
✔ Data Normalization
✔ Metadata Layer (created_at, updated_at)
✔ Safe Update Handling
✔ Full CRUD + Search
✔ Timezone-Aware UTC Timestamps
✔ CLI Test Runner Included
"""

import json
import os

from typing import Dict, List, Optional
from datetime import datetime, timezone


# -------------------------------------------------
# Config
# -------------------------------------------------

DATA_FILE = "data/farmer_data.json"


# -------------------------------------------------
# Timestamp Helper (UPDATED)
# -------------------------------------------------

def _current_timestamp() -> str:
    """
    Return timezone-aware UTC timestamp.
    """

    return datetime.now(timezone.utc).isoformat()


# -------------------------------------------------
# Normalization Helpers
# -------------------------------------------------

def _normalize_crop(crop: str) -> str:
    return crop.strip().lower()


def _normalize_stage(stage: str) -> str:
    return stage.strip().capitalize()


def _normalize_state(state: str) -> str:
    return state.strip().title()


def _normalize_district(district: str) -> str:
    return district.strip().title()


# -------------------------------------------------
# Validation
# -------------------------------------------------

def _validate_required_fields(
    farmer_id: str,
    state: str,
    district: str,
    current_crop: str,
    crop_stage: str
):

    if not farmer_id:
        raise ValueError("❌ farmer_id is required")

    if not state:
        raise ValueError("❌ state is required")

    if not district:
        raise ValueError("❌ district is required")

    if not current_crop:
        raise ValueError("❌ current_crop is required")

    if not crop_stage:
        raise ValueError("❌ crop_stage is required")


# -------------------------------------------------
# Load / Save
# -------------------------------------------------

def load_all_farmers() -> List[Dict]:

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_all_farmers(data: List[Dict]) -> None:

    with open(DATA_FILE, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# -------------------------------------------------
# Create Farmer
# -------------------------------------------------

def create_farmer(
    farmer_id: str,
    state: str,
    district: str,
    current_crop: str,
    crop_stage: str,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    village: Optional[str] = None,
    total_area_acres: Optional[float] = None,
    soil_type: Optional[str] = None,
    irrigation_type: Optional[str] = None,
    past_crop_history: Optional[List[str]] = None
) -> Dict:

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------

    _validate_required_fields(
        farmer_id,
        state,
        district,
        current_crop,
        crop_stage
    )

    # -------------------------------------------------
    # Normalization
    # -------------------------------------------------

    state = _normalize_state(state)
    district = _normalize_district(district)

    current_crop = _normalize_crop(current_crop)
    crop_stage = _normalize_stage(crop_stage)

    timestamp = _current_timestamp()

    # -------------------------------------------------
    # Farmer Record
    # -------------------------------------------------

    farmer = {

        "farmer_id": farmer_id,

        "identity": {
            "name": name,
            "phone": phone
        },

        "location": {
            "state": state,
            "district": district,
            "village": village
        },

        "land": {
            "total_area_acres": total_area_acres,
            "soil_type": soil_type
        },

        "crop_profile": {
            "current_crop": current_crop,
            "crop_stage": crop_stage
        },

        "additional": {
            "irrigation_type": irrigation_type,
            "past_crop_history": past_crop_history or []
        },

        "meta": {
            "created_at": timestamp,
            "updated_at": timestamp
        }
    }

    return farmer


# -------------------------------------------------
# Add Farmer
# -------------------------------------------------

def add_farmer(farmer: Dict) -> None:

    data = load_all_farmers()

    for existing_farmer in data:

        if existing_farmer["farmer_id"] == farmer["farmer_id"]:

            raise ValueError(
                f"❌ Farmer ID {farmer['farmer_id']} already exists"
            )

    data.append(farmer)

    save_all_farmers(data)


# -------------------------------------------------
# Get Farmer
# -------------------------------------------------

def get_farmer(farmer_id: str) -> Optional[Dict]:

    data = load_all_farmers()

    for farmer in data:

        if farmer["farmer_id"] == farmer_id:
            return farmer

    return None


# -------------------------------------------------
# Search Farmers
# -------------------------------------------------

def search_farmers(
    state: Optional[str] = None,
    district: Optional[str] = None,
    crop: Optional[str] = None
) -> List[Dict]:

    data = load_all_farmers()

    results = []

    if state:
        state = _normalize_state(state)

    if district:
        district = _normalize_district(district)

    if crop:
        crop = _normalize_crop(crop)

    for farmer in data:

        if (
            state and
            farmer["location"]["state"] != state
        ):
            continue

        if (
            district and
            farmer["location"]["district"] != district
        ):
            continue

        if (
            crop and
            farmer["crop_profile"]["current_crop"] != crop
        ):
            continue

        results.append(farmer)

    return results


# -------------------------------------------------
# Update Farmer
# -------------------------------------------------

def update_farmer(
    farmer_id: str,
    updates: Dict
) -> bool:

    data = load_all_farmers()

    for farmer in data:

        if farmer["farmer_id"] == farmer_id:

            _deep_update(farmer, updates)

            # -----------------------------------------
            # Normalize Updated Fields
            # -----------------------------------------

            if "location" in farmer:

                location = farmer["location"]

                if location.get("state"):
                    location["state"] = _normalize_state(
                        location["state"]
                    )

                if location.get("district"):
                    location["district"] = _normalize_district(
                        location["district"]
                    )

            if "crop_profile" in farmer:

                cp = farmer["crop_profile"]

                if cp.get("current_crop"):
                    cp["current_crop"] = _normalize_crop(
                        cp["current_crop"]
                    )

                if cp.get("crop_stage"):
                    cp["crop_stage"] = _normalize_stage(
                        cp["crop_stage"]
                    )

            # -----------------------------------------
            # Metadata Update
            # -----------------------------------------

            if "meta" not in farmer:
                farmer["meta"] = {}

            farmer["meta"]["updated_at"] = _current_timestamp()

            save_all_farmers(data)

            return True

    return False


# -------------------------------------------------
# Deep Update Helper
# -------------------------------------------------

def _deep_update(
    original: Dict,
    updates: Dict
) -> None:

    for key, value in updates.items():

        if (
            isinstance(value, dict)
            and key in original
            and isinstance(original[key], dict)
        ):

            _deep_update(original[key], value)

        else:
            original[key] = value


# -------------------------------------------------
# Delete Farmer
# -------------------------------------------------

def delete_farmer(farmer_id: str) -> bool:

    data = load_all_farmers()

    new_data = [

        farmer
        for farmer in data

        if farmer["farmer_id"] != farmer_id
    ]

    if len(new_data) == len(data):
        return False

    save_all_farmers(new_data)

    return True


# -------------------------------------------------
# Test Runner
# -------------------------------------------------

if __name__ == "__main__":

    print("\n🚜 Farmer Master Test Runner Started...\n")

    TEST_ID = "TEST001"

    # -------------------------------------------------
    # Create
    # -------------------------------------------------

    try:

        farmer = create_farmer(
            farmer_id=TEST_ID,
            state="karnataka",
            district="mysore",
            current_crop="Rice",
            crop_stage="flowering",
            name="Test User",
            total_area_acres=2
        )

        add_farmer(farmer)

        print("✅ Farmer Created & Added\n")

    except ValueError as e:

        print(e)

    # -------------------------------------------------
    # Fetch
    # -------------------------------------------------

    fetched = get_farmer(TEST_ID)

    print("📌 Fetched Farmer:\n")

    print(
        json.dumps(
            fetched,
            indent=4
        )
    )

    # -------------------------------------------------
    # Search
    # -------------------------------------------------

    results = search_farmers(
        state="Karnataka",
        crop="rice"
    )

    print("\n🔍 Search Results:\n")

    print(
        json.dumps(
            results,
            indent=4
        )
    )

    # -------------------------------------------------
    # Update
    # -------------------------------------------------

    updated_successfully = update_farmer(
        TEST_ID,
        {
            "crop_profile": {
                "crop_stage": "harvesting"
            }
        }
    )

    if updated_successfully:

        updated = get_farmer(TEST_ID)

        print("\n🔄 Updated Farmer:\n")

        print(
            json.dumps(
                updated,
                indent=4
            )
        )

    # -------------------------------------------------
    # Delete
    # -------------------------------------------------

    if delete_farmer(TEST_ID):

        print("\n🗑️ Deleted Test Farmer\n")

    print("✅ Test Completed 🚀\n")