"""
RAYA Phase 4B
Persistent Farmer Intelligence Layer

File: persistent_memory/soil_memory.py

Purpose:
Persistent field-specific soil memory.

Architecture:
Farmer
-> Farm
-> Field
-> Soil Profile

Features:
- One active soil profile per field
- Persistent JSON-backed storage
- Soil profile updates
- Historical soil snapshots
- Restart persistence validation
- Field ownership validation

Phase 4B does NOT modify:
- Crop Master
- Weather Intelligence
- Water Intelligence
- Disease Intelligence
- Market Intelligence
- Agricultural rule logic
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ============================================================

# IMPORTS

# ============================================================

from persistent_memory.storage_manager import (
    StorageManager,
    get_storage_manager,
)

from persistent_memory.farm_field_registry import (
    FarmFieldRegistry,
    get_farm_field_registry,
)

# ============================================================

# CONSTANTS

# ============================================================

SOIL_ENTITY_TYPE = "soil_profiles"

SOIL_ID_FIELD = "soil_profile_id"

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"

VALID_STATUSES = {
    STATUS_ACTIVE,
    STATUS_INACTIVE,
}

# ============================================================

# SOIL MEMORY

# ============================================================

class SoilMemory:
    """
    Persistent field-specific soil memory.

    Design:

        One Field
            |
            +-- One Active Soil Profile

    Every update preserves the previous soil values
    inside the profile history.

    Example:

        Farmer
            |
            +-- Farm
                  |
                  +-- Field
                        |
                        +-- Soil Profile
    """

    def __init__(
        self,
        storage: Optional[StorageManager] = None,
        farm_field_registry: Optional[
            FarmFieldRegistry
        ] = None,
    ):
        """
        Initialize Soil Memory.
        """

        self.storage = (
            storage
            if storage is not None
            else get_storage_manager()
        )

        self.farm_field_registry = (
            farm_field_registry
            if farm_field_registry is not None
            else get_farm_field_registry()
        )

    # ========================================================
    # CREATE SOIL PROFILE
    # ========================================================

    def create_soil_profile(
        self,
        field_id: str,
        soil_type: Optional[str] = None,
        ph: Optional[float] = None,
        nitrogen: Optional[float] = None,
        phosphorus: Optional[float] = None,
        potassium: Optional[float] = None,
        organic_carbon: Optional[float] = None,
        moisture_percent: Optional[float] = None,
        electrical_conductivity: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a persistent soil profile for a field.

        Rules:
            - Field must exist.
            - Only one active soil profile per field.
        """

        self._validate_field_exists(field_id)

        existing_profile = (
            self.get_field_soil_profile(
                field_id=field_id,
                include_inactive=False,
            )
        )

        if existing_profile is not None:
            raise ValueError(
                "An active soil profile already exists "
                f"for field: {field_id}. "
                "Use update_soil_profile() instead."
            )

        timestamp = self.storage.utc_timestamp()

        soil_record = {
            "soil_profile_id": (
                self.storage.generate_id("SOIL")
            ),
            "field_id": field_id,
            "soil_type": (
                self._clean_optional_string(soil_type)
            ),
            "ph": self._validate_optional_range(
                ph,
                "ph",
                minimum=0.0,
                maximum=14.0,
            ),
            "nitrogen": (
                self._validate_optional_non_negative(
                    nitrogen,
                    "nitrogen",
                )
            ),
            "phosphorus": (
                self._validate_optional_non_negative(
                    phosphorus,
                    "phosphorus",
                )
            ),
            "potassium": (
                self._validate_optional_non_negative(
                    potassium,
                    "potassium",
                )
            ),
            "organic_carbon": (
                self._validate_optional_non_negative(
                    organic_carbon,
                    "organic_carbon",
                )
            ),
            "moisture_percent": (
                self._validate_optional_range(
                    moisture_percent,
                    "moisture_percent",
                    minimum=0.0,
                    maximum=100.0,
                )
            ),
            "electrical_conductivity": (
                self._validate_optional_non_negative(
                    electrical_conductivity,
                    "electrical_conductivity",
                )
            ),
            "status": STATUS_ACTIVE,
            "created_at": timestamp,
            "updated_at": timestamp,
            "history": [],
            "metadata": (
                metadata.copy()
                if isinstance(metadata, dict)
                else {}
            ),
        }

        self.storage.insert(
            entity_type=SOIL_ENTITY_TYPE,
            record=soil_record,
        )

        return soil_record

    # ========================================================
    # GET SOIL PROFILE BY ID
    # ========================================================

    def get_soil_profile(
        self,
        soil_profile_id: str,
        include_inactive: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a soil profile by profile ID.
        """

        profile = self.storage.get_by_id(
            entity_type=SOIL_ENTITY_TYPE,
            record_id=soil_profile_id,
            id_field=SOIL_ID_FIELD,
        )

        if profile is None:
            return None

        if (
            not include_inactive
            and profile.get("status") != STATUS_ACTIVE
        ):
            return None

        return profile

    # ========================================================
    # GET FIELD SOIL PROFILE
    # ========================================================

    def get_field_soil_profile(
        self,
        field_id: str,
        include_inactive: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve the soil profile belonging to a field.

        By default, returns only the active profile.
        """

        profiles = self.storage.read_all(
            SOIL_ENTITY_TYPE
        )

        matching_profiles = []

        for profile in profiles:

            if profile.get("field_id") != field_id:
                continue

            if (
                not include_inactive
                and profile.get("status")
                != STATUS_ACTIVE
            ):
                continue

            matching_profiles.append(profile)

        if not matching_profiles:
            return None

        matching_profiles.sort(
            key=lambda item: (
                item.get("updated_at") or ""
            ),
            reverse=True,
        )

        return matching_profiles[0]

    # ========================================================
    # LIST SOIL PROFILES
    # ========================================================

    def list_soil_profiles(
        self,
        status: Optional[str] = STATUS_ACTIVE,
    ) -> List[Dict[str, Any]]:
        """
        List soil profiles.

        Args:
            status:
                "active"
                "inactive"
                None -> all profiles
        """

        if (
            status is not None
            and status not in VALID_STATUSES
        ):
            raise ValueError(
                "Invalid status. Supported values: "
                f"{sorted(VALID_STATUSES)} or None."
            )

        profiles = self.storage.read_all(
            SOIL_ENTITY_TYPE
        )

        if status is not None:

            profiles = [
                profile
                for profile in profiles
                if profile.get("status") == status
            ]

        return sorted(
            profiles,
            key=lambda item: (
                item.get("updated_at") or ""
            ),
            reverse=True,
        )

    # ========================================================
    # UPDATE SOIL PROFILE
    # ========================================================

    def update_soil_profile(
        self,
        field_id: str,
        **updates: Any,
    ) -> Dict[str, Any]:
        """
        Update an active field soil profile.

        Before applying changes, the current soil values
        are saved into the profile history.
        """

        profile = self.get_field_soil_profile(
            field_id=field_id,
            include_inactive=False,
        )

        if profile is None:
            raise ValueError(
                "No active soil profile found for field: "
                f"{field_id}"
            )

        forbidden_fields = {
            "soil_profile_id",
            "field_id",
            "status",
            "created_at",
            "updated_at",
            "history",
        }

        invalid_fields = (
            set(updates.keys())
            & forbidden_fields
        )

        if invalid_fields:
            raise ValueError(
                "These fields cannot be updated: "
                f"{sorted(invalid_fields)}"
            )

        allowed_fields = {
            "soil_type",
            "ph",
            "nitrogen",
            "phosphorus",
            "potassium",
            "organic_carbon",
            "moisture_percent",
            "electrical_conductivity",
            "metadata",
        }

        unknown_fields = (
            set(updates.keys())
            - allowed_fields
        )

        if unknown_fields:
            raise ValueError(
                "Unsupported soil update fields: "
                f"{sorted(unknown_fields)}"
            )

        # ----------------------------------------------------
        # CREATE HISTORY SNAPSHOT
        # ----------------------------------------------------

        previous_snapshot = {
            "timestamp": (
                self.storage.utc_timestamp()
            ),
            "soil_type": profile.get(
                "soil_type"
            ),
            "ph": profile.get("ph"),
            "nitrogen": profile.get(
                "nitrogen"
            ),
            "phosphorus": profile.get(
                "phosphorus"
            ),
            "potassium": profile.get(
                "potassium"
            ),
            "organic_carbon": profile.get(
                "organic_carbon"
            ),
            "moisture_percent": profile.get(
                "moisture_percent"
            ),
            "electrical_conductivity": profile.get(
                "electrical_conductivity"
            ),
        }

        history = list(
            profile.get("history", [])
        )

        history.append(
            previous_snapshot
        )

        # ----------------------------------------------------
        # VALIDATE UPDATES
        # ----------------------------------------------------

        sanitized_updates: Dict[str, Any] = {}

        if "soil_type" in updates:

            sanitized_updates["soil_type"] = (
                self._clean_optional_string(
                    updates["soil_type"]
                )
            )

        if "ph" in updates:

            sanitized_updates["ph"] = (
                self._validate_optional_range(
                    updates["ph"],
                    "ph",
                    minimum=0.0,
                    maximum=14.0,
                )
            )

        nutrient_fields = [
            "nitrogen",
            "phosphorus",
            "potassium",
            "organic_carbon",
            "electrical_conductivity",
        ]

        for nutrient_field in nutrient_fields:

            if nutrient_field in updates:

                sanitized_updates[
                    nutrient_field
                ] = (
                    self._validate_optional_non_negative(
                        updates[nutrient_field],
                        nutrient_field,
                    )
                )

        if "moisture_percent" in updates:

            sanitized_updates[
                "moisture_percent"
            ] = (
                self._validate_optional_range(
                    updates["moisture_percent"],
                    "moisture_percent",
                    minimum=0.0,
                    maximum=100.0,
                )
            )

        if "metadata" in updates:

            metadata = updates["metadata"]

            if metadata is None:
                metadata = {}

            if not isinstance(metadata, dict):
                raise ValueError(
                    "metadata must be a dictionary."
                )

            sanitized_updates["metadata"] = (
                metadata.copy()
            )

        # ----------------------------------------------------
        # FINAL UPDATE DATA
        # ----------------------------------------------------

        sanitized_updates["history"] = history

        sanitized_updates["updated_at"] = (
            self.storage.utc_timestamp()
        )

        updated_profile = (
            self.storage.update_by_id(
                entity_type=SOIL_ENTITY_TYPE,
                record_id=profile[
                    "soil_profile_id"
                ],
                id_field=SOIL_ID_FIELD,
                updates=sanitized_updates,
            )
        )

        if updated_profile is None:
            raise RuntimeError(
                "Soil profile update failed."
            )

        return updated_profile

    # ========================================================
    # GET SOIL HISTORY
    # ========================================================

    def get_soil_history(
        self,
        field_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Return soil history snapshots for a field.
        """

        profile = self.get_field_soil_profile(
            field_id=field_id,
            include_inactive=True,
        )

        if profile is None:
            return []

        history = profile.get("history", [])

        if not isinstance(history, list):
            return []

        return list(history)

    # ========================================================
    # DEACTIVATE SOIL PROFILE
    # ========================================================

    def deactivate_soil_profile(
        self,
        field_id: str,
    ) -> Dict[str, Any]:
        """
        Soft-deactivate the active soil profile
        for a field.
        """

        profile = self.get_field_soil_profile(
            field_id=field_id,
            include_inactive=False,
        )

        if profile is None:
            raise ValueError(
                "No active soil profile found for field: "
                f"{field_id}"
            )

        updated_profile = (
            self.storage.update_by_id(
                entity_type=SOIL_ENTITY_TYPE,
                record_id=profile[
                    "soil_profile_id"
                ],
                id_field=SOIL_ID_FIELD,
                updates={
                    "status": STATUS_INACTIVE,
                    "updated_at": (
                        self.storage.utc_timestamp()
                    ),
                },
            )
        )

        if updated_profile is None:
            raise RuntimeError(
                "Failed to deactivate soil profile."
            )

        return updated_profile

    # ========================================================
    # FIELD SOIL CONTEXT
    # ========================================================

    def get_field_soil_context(
        self,
        field_id: str,
    ) -> Dict[str, Any]:
        """
        Return backend-friendly field + soil context.

        Designed for future integration:

            Field
                ->
            Soil Memory
                ->
            Season Manager
                ->
            Farmer Context
                ->
            Contextual Decision Engine
        """

        field = self.farm_field_registry.get_field(
            field_id=field_id,
            include_inactive=False,
        )

        if field is None:
            raise ValueError(
                f"Active field not found: {field_id}"
            )

        profile = self.get_field_soil_profile(
            field_id=field_id,
            include_inactive=False,
        )

        return {
            "field_id": field_id,
            "farm_id": field.get("farm_id"),
            "farmer_id": field.get("farmer_id"),
            "soil_profile": profile,
        }

    # ========================================================
    # VALIDATION HELPERS
    # ========================================================

    def _validate_field_exists(
        self,
        field_id: str,
    ) -> None:
        """
        Ensure the field exists and is active.
        """

        field = self.farm_field_registry.get_field(
            field_id=field_id,
            include_inactive=False,
        )

        if field is None:
            raise ValueError(
                "Active field not found: "
                f"{field_id}"
            )

    @staticmethod
    def _clean_optional_string(
        value: Any,
    ) -> Optional[str]:
        """
        Normalize optional strings.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        return value or None

    @staticmethod
    def _validate_optional_non_negative(
        value: Any,
        field_name: str,
    ) -> Optional[float]:
        """
        Validate optional non-negative numeric value.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be numeric."
            )

        try:
            number = float(value)

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{field_name} must be numeric."
            ) from exc

        if number < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

        return number

    @staticmethod
    def _validate_optional_range(
        value: Any,
        field_name: str,
        minimum: float,
        maximum: float,
    ) -> Optional[float]:
        """
        Validate optional numeric value inside a range.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be numeric."
            )

        try:
            number = float(value)

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{field_name} must be numeric."
            ) from exc

        if (
            number < minimum
            or number > maximum
        ):
            raise ValueError(
                f"{field_name} must be between "
                f"{minimum} and {maximum}."
            )

        return number


# ============================================================

# SINGLETON ACCESSOR

# ============================================================

_default_soil_memory: Optional[
    SoilMemory
] = None

def get_soil_memory() -> SoilMemory:
    """
    Return the default SoilMemory instance.
    """

    global _default_soil_memory

    if _default_soil_memory is None:

        _default_soil_memory = SoilMemory()

    return _default_soil_memory


# ============================================================

# LOCAL RUNTIME VALIDATION

# ============================================================

def _run_local_test() -> None:
    """
    Phase 4B Soil Memory runtime validation.
    """

    print("=" * 70)
    print("RAYA PHASE 4B - SOIL MEMORY TEST")
    print("=" * 70)

    registry = get_farm_field_registry()

    soil_memory = get_soil_memory()

    # --------------------------------------------------------
    # GET EXISTING FIELD
    # --------------------------------------------------------

    fields = registry.list_fields()

    if not fields:

        raise RuntimeError(
            "No fields found. "
            "Run Phase 4A validation first."
        )

    field = fields[0]

    field_id = field["field_id"]

    print(
        f"\nUsing Field: "
        f"{field.get('field_name')}"
    )

    print(
        f"Field ID: {field_id}"
    )

    # --------------------------------------------------------
    # CREATE OR LOAD SOIL PROFILE
    # --------------------------------------------------------

    profile = soil_memory.get_field_soil_profile(
        field_id=field_id,
        include_inactive=False,
    )

    if profile is None:

        print(
            "\nCreating soil profile..."
        )

        profile = soil_memory.create_soil_profile(
            field_id=field_id,
            soil_type="Loamy",
            ph=6.8,
            nitrogen=240,
            phosphorus=32,
            potassium=280,
            organic_carbon=0.75,
            moisture_percent=45,
            electrical_conductivity=0.42,
        )

        print(
            "Soil profile created successfully."
        )

    else:

        print(
            "\nExisting soil profile loaded."
        )

    # --------------------------------------------------------
    # DISPLAY PROFILE
    # --------------------------------------------------------

    print("\nCURRENT SOIL PROFILE")
    print("-" * 70)

    display_fields = [
        "soil_profile_id",
        "field_id",
        "soil_type",
        "ph",
        "nitrogen",
        "phosphorus",
        "potassium",
        "organic_carbon",
        "moisture_percent",
        "electrical_conductivity",
        "status",
        "created_at",
        "updated_at",
    ]

    for key in display_fields:

        print(
            f"{key}: {profile.get(key)}"
        )

    # --------------------------------------------------------
    # UPDATE SOIL PROFILE
    # --------------------------------------------------------

    print(
        "\nUpdating soil moisture..."
    )

    updated_profile = (
        soil_memory.update_soil_profile(
            field_id=field_id,
            moisture_percent=52,
        )
    )

    print(
        "Updated moisture_percent:",
        updated_profile.get(
            "moisture_percent"
        ),
    )

    # --------------------------------------------------------
    # HISTORY VALIDATION
    # --------------------------------------------------------

    history = soil_memory.get_soil_history(
        field_id=field_id
    )

    print(
        f"\nSoil history records: "
        f"{len(history)}"
    )

    assert len(history) > 0, (
        "FAIL: Soil history was not created."
    )

    print(
        "PASS: Soil history preserved."
    )

    # --------------------------------------------------------
    # RESTART SIMULATION
    # --------------------------------------------------------

    print(
        "\nSimulating application restart..."
    )

    restarted_storage = StorageManager()

    restarted_registry = FarmFieldRegistry(
        storage=restarted_storage
    )

    restarted_soil_memory = SoilMemory(
        storage=restarted_storage,
        farm_field_registry=restarted_registry,
    )

    reloaded_profile = (
        restarted_soil_memory.get_field_soil_profile(
            field_id=field_id,
            include_inactive=False,
        )
    )

    assert reloaded_profile is not None, (
        "FAIL: Soil profile was not restored."
    )

    assert (
        reloaded_profile.get(
            "moisture_percent"
        )
        == 52.0
    ), (
        "FAIL: Updated soil data "
        "was not persisted."
    )

    print(
        "PASS: Soil profile restored "
        "after restart."
    )

    # --------------------------------------------------------
    # FIELD CONTEXT VALIDATION
    # --------------------------------------------------------

    field_context = (
        restarted_soil_memory.get_field_soil_context(
            field_id=field_id
        )
    )

    assert (
        field_context.get("soil_profile")
        is not None
    ), (
        "FAIL: Field soil context "
        "does not contain soil profile."
    )

    print(
        "PASS: Field soil context generated."
    )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("PHASE 4B VALIDATION REPORT")
    print("=" * 70)

    print(
        "[PASS] Field-specific soil profile"
    )

    print(
        "[PASS] Soil profile persisted"
    )

    print(
        "[PASS] Soil update history preserved"
    )

    print(
        "[PASS] Soil survives application restart"
    )

    print(
        "[PASS] Backend field soil context available"
    )

    print("-" * 70)

    print(
        "PHASE 4B - SOIL MEMORY COMPLETE"
    )

    print("=" * 70)


# ============================================================

# MAIN

# ============================================================


# ============================================================

if __name__ == "__main__":
    _run_local_test()
