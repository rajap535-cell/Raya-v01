"""
RAYA Phase 4A
Persistent Farmer Intelligence Layer

# Farm and Field Registry

This module manages:

```
Farmer
    └── Farm
          └── Field
```

Responsibilities:
- Create farms for persistent farmers
- Create fields for persistent farms
- Retrieve farms and fields
- List farmer farms
- List farm fields
- Update farms and fields
- Activate / deactivate records
- Preserve persistent ownership relationships

Persistence:
data/persistent_memory/farms.json
data/persistent_memory/fields.json

Architecture:

```
FarmerRegistry
      ↓
FarmFieldRegistry
      ↓
StorageManager
      ↓
Persistent JSON Storage
```

Phase 4A intentionally does NOT contain:
- Soil intelligence
- Season management
- Advisory history
- Weather logic
- Crop logic
- Farmer Search logic
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from persistent_memory.storage_manager import (
StorageManager,
get_storage_manager,
)

from persistent_memory.farmer_registry import (
FarmerRegistry,
get_farmer_registry,
)

# ============================================================

# CONSTANTS

# ============================================================

FARM_ENTITY_TYPE = "farms"
FIELD_ENTITY_TYPE = "fields"

FARM_ID_FIELD = "farm_id"
FIELD_ID_FIELD = "field_id"
FARMER_ID_FIELD = "farmer_id"

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"

VALID_STATUSES = {
STATUS_ACTIVE,
STATUS_INACTIVE,
}

# ============================================================

# FARM AND FIELD REGISTRY

# ============================================================

class FarmFieldRegistry:
    """
    Persistent registry for Farms and Fields.

    ```
    Relationship:

        Farmer
          |
          | farmer_id
          v
        Farm
          |
          | farm_id
          v
        Field

    A farmer can own multiple farms.

    A farm can contain multiple fields.
    """

    def __init__(
        self,
        storage: Optional[StorageManager] = None,
        farmer_registry: Optional[FarmerRegistry] = None,
    ):
        """
        Initialize registry dependencies.
        """

        self.storage = (
            storage
            if storage is not None
            else get_storage_manager()
        )

        self.farmer_registry = (
            farmer_registry
            if farmer_registry is not None
            else get_farmer_registry()
        )

    # ========================================================
    # FARM OPERATIONS
    # ========================================================

    def create_farm(
        self,
        farmer_id: str,
        farm_name: str,
        location: Optional[str] = None,
        village: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        total_area_acres: Optional[float] = None,
        irrigation_source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a persistent farm for an existing farmer.
        """

        self._validate_farmer_exists(
            farmer_id
        )

        normalized_farm_name = (
            self._validate_required_string(
                farm_name,
                "farm_name",
            )
        )

        normalized_area = (
            self._validate_optional_positive_number(
                total_area_acres,
                "total_area_acres",
            )
        )

        timestamp = self.storage.utc_timestamp()

        farm_record = {
            "farm_id": self.storage.generate_id(
                "FARM"
            ),
            "farmer_id": farmer_id,
            "farm_name": normalized_farm_name,
            "location": self._clean_optional_string(
                location
            ),
            "village": self._clean_optional_string(
                village
            ),
            "district": self._clean_optional_string(
                district
            ),
            "state": self._clean_optional_string(
                state
            ),
            "total_area_acres": normalized_area,
            "irrigation_source": (
                self._clean_optional_string(
                    irrigation_source
                )
            ),
            "status": STATUS_ACTIVE,
            "created_at": timestamp,
            "updated_at": timestamp,
            "metadata": (
                metadata.copy()
                if isinstance(metadata, dict)
                else {}
            ),
        }

        self.storage.insert(
            entity_type=FARM_ENTITY_TYPE,
            record=farm_record,
        )

        return farm_record

    def get_farm(
        self,
        farm_id: str,
        include_inactive: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a farm by ID.
        """

        farm = self.storage.get_by_id(
            entity_type=FARM_ENTITY_TYPE,
            record_id=farm_id,
            id_field=FARM_ID_FIELD,
        )

        if farm is None:
            return None

        if (
            not include_inactive
            and farm.get("status") != STATUS_ACTIVE
        ):
            return None

        return farm

    def list_farms(
        self,
        farmer_id: Optional[str] = None,
        status: Optional[str] = STATUS_ACTIVE,
    ) -> List[Dict[str, Any]]:
        """
        List farms.

        Args:
            farmer_id:
                Optional filter for a specific farmer.

            status:
                "active", "inactive", or None.
        """

        if (
            status is not None
            and status not in VALID_STATUSES
        ):
            raise ValueError(
                "Invalid status. "
                f"Supported: {sorted(VALID_STATUSES)} or None."
            )

        farms = self.storage.read_all(
            FARM_ENTITY_TYPE
        )

        if farmer_id is not None:
            farms = [
                farm
                for farm in farms
                if farm.get("farmer_id") == farmer_id
            ]

        if status is not None:
            farms = [
                farm
                for farm in farms
                if farm.get("status") == status
            ]

        return sorted(
            farms,
            key=lambda item: (
                item.get("farm_name") or ""
            ).lower(),
        )

    def get_farmer_farms(
        self,
        farmer_id: str,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all farms belonging to a farmer.
        """

        status = (
            None
            if include_inactive
            else STATUS_ACTIVE
        )

        return self.list_farms(
            farmer_id=farmer_id,
            status=status,
        )

    def update_farm(
        self,
        farm_id: str,
        **updates: Any,
    ) -> Dict[str, Any]:
        """
        Update farm information.
        """

        existing_farm = self.get_farm(
            farm_id
        )

        if existing_farm is None:
            raise ValueError(
                f"Farm not found: {farm_id}"
            )

        forbidden_fields = {
            "farm_id",
            "farmer_id",
            "created_at",
            "updated_at",
            "status",
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
            "farm_name",
            "location",
            "village",
            "district",
            "state",
            "total_area_acres",
            "irrigation_source",
            "metadata",
        }

        unknown_fields = (
            set(updates.keys())
            - allowed_fields
        )

        if unknown_fields:
            raise ValueError(
                "Unsupported farm update fields: "
                f"{sorted(unknown_fields)}"
            )

        sanitized_updates: Dict[str, Any] = {}

        if "farm_name" in updates:
            sanitized_updates["farm_name"] = (
                self._validate_required_string(
                    updates["farm_name"],
                    "farm_name",
                )
            )

        optional_string_fields = [
            "location",
            "village",
            "district",
            "state",
            "irrigation_source",
        ]

        for field in optional_string_fields:
            if field in updates:
                sanitized_updates[field] = (
                    self._clean_optional_string(
                        updates[field]
                    )
                )

        if "total_area_acres" in updates:
            sanitized_updates[
                "total_area_acres"
            ] = (
                self._validate_optional_positive_number(
                    updates["total_area_acres"],
                    "total_area_acres",
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

        sanitized_updates["updated_at"] = (
            self.storage.utc_timestamp()
        )

        updated_farm = self.storage.update_by_id(
            entity_type=FARM_ENTITY_TYPE,
            record_id=farm_id,
            id_field=FARM_ID_FIELD,
            updates=sanitized_updates,
        )

        if updated_farm is None:
            raise RuntimeError(
                "Farm update failed unexpectedly."
            )

        return updated_farm

    def deactivate_farm(
        self,
        farm_id: str,
    ) -> Dict[str, Any]:
        """
        Soft deactivate a farm.
        """

        return self._set_farm_status(
            farm_id,
            STATUS_INACTIVE,
        )

    def activate_farm(
        self,
        farm_id: str,
    ) -> Dict[str, Any]:
        """
        Reactivate a farm.
        """

        return self._set_farm_status(
            farm_id,
            STATUS_ACTIVE,
        )

    def _set_farm_status(
        self,
        farm_id: str,
        status: str,
    ) -> Dict[str, Any]:
        """
        Update farm status.
        """

        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status: {status}"
            )

        farm = self.get_farm(
            farm_id
        )

        if farm is None:
            raise ValueError(
                f"Farm not found: {farm_id}"
            )

        updated_farm = self.storage.update_by_id(
            entity_type=FARM_ENTITY_TYPE,
            record_id=farm_id,
            id_field=FARM_ID_FIELD,
            updates={
                "status": status,
                "updated_at": (
                    self.storage.utc_timestamp()
                ),
            },
        )

        if updated_farm is None:
            raise RuntimeError(
                "Farm status update failed."
            )

        return updated_farm

    def delete_farm(
        self,
        farm_id: str,
        permanent: bool = False,
    ) -> bool:
        """
        Delete a farm.

        Default:
            Soft deactivate.

        permanent=True:
            Remove farm record.

        Note:
            Relationship validation for fields should be
            handled by higher-level orchestration before
            permanent deletion in production.
        """

        farm = self.get_farm(
            farm_id
        )

        if farm is None:
            return False

        if not permanent:
            self.deactivate_farm(
                farm_id
            )
            return True

        return self.storage.delete_by_id(
            entity_type=FARM_ENTITY_TYPE,
            record_id=farm_id,
            id_field=FARM_ID_FIELD,
        )

    # ========================================================
    # FIELD OPERATIONS
    # ========================================================

    def create_field(
        self,
        farm_id: str,
        field_name: str,
        area_acres: Optional[float] = None,
        irrigation_available: Optional[bool] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a persistent field for an existing farm.
        """

        farm = self.get_farm(
            farm_id,
            include_inactive=False,
        )

        if farm is None:
            raise ValueError(
                f"Active farm not found: {farm_id}"
            )

        normalized_field_name = (
            self._validate_required_string(
                field_name,
                "field_name",
            )
        )

        normalized_area = (
            self._validate_optional_positive_number(
                area_acres,
                "area_acres",
            )
        )

        normalized_latitude = (
            self._validate_latitude(
                latitude
            )
        )

        normalized_longitude = (
            self._validate_longitude(
                longitude
            )
        )

        timestamp = self.storage.utc_timestamp()

        field_record = {
            "field_id": self.storage.generate_id(
                "FIELD"
            ),
            "farm_id": farm_id,
            "farmer_id": farm["farmer_id"],
            "field_name": normalized_field_name,
            "area_acres": normalized_area,
            "irrigation_available": (
                self._validate_optional_boolean(
                    irrigation_available,
                    "irrigation_available",
                )
            ),
            "latitude": normalized_latitude,
            "longitude": normalized_longitude,
            "status": STATUS_ACTIVE,
            "created_at": timestamp,
            "updated_at": timestamp,
            "metadata": (
                metadata.copy()
                if isinstance(metadata, dict)
                else {}
            ),
        }

        self.storage.insert(
            entity_type=FIELD_ENTITY_TYPE,
            record=field_record,
        )

        return field_record

    def get_field(
        self,
        field_id: str,
        include_inactive: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve field by ID.
        """

        field = self.storage.get_by_id(
            entity_type=FIELD_ENTITY_TYPE,
            record_id=field_id,
            id_field=FIELD_ID_FIELD,
        )

        if field is None:
            return None

        if (
            not include_inactive
            and field.get("status") != STATUS_ACTIVE
        ):
            return None

        return field

    def list_fields(
        self,
        farm_id: Optional[str] = None,
        farmer_id: Optional[str] = None,
        status: Optional[str] = STATUS_ACTIVE,
    ) -> List[Dict[str, Any]]:
        """
        List fields with optional ownership filters.
        """

        if (
            status is not None
            and status not in VALID_STATUSES
        ):
            raise ValueError(
                "Invalid status. "
                f"Supported: {sorted(VALID_STATUSES)} or None."
            )

        fields = self.storage.read_all(
            FIELD_ENTITY_TYPE
        )

        if farm_id is not None:
            fields = [
                field
                for field in fields
                if field.get("farm_id") == farm_id
            ]

        if farmer_id is not None:
            fields = [
                field
                for field in fields
                if field.get("farmer_id") == farmer_id
            ]

        if status is not None:
            fields = [
                field
                for field in fields
                if field.get("status") == status
            ]

        return sorted(
            fields,
            key=lambda item: (
                item.get("field_name") or ""
            ).lower(),
        )

    def get_farm_fields(
        self,
        farm_id: str,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all fields belonging to a farm.
        """

        status = (
            None
            if include_inactive
            else STATUS_ACTIVE
        )

        return self.list_fields(
            farm_id=farm_id,
            status=status,
        )

    def get_farmer_fields(
        self,
        farmer_id: str,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all fields belonging to a farmer.
        """

        status = (
            None
            if include_inactive
            else STATUS_ACTIVE
        )

        return self.list_fields(
            farmer_id=farmer_id,
            status=status,
        )

    def update_field(
        self,
        field_id: str,
        **updates: Any,
    ) -> Dict[str, Any]:
        """
        Update persistent field information.
        """

        existing_field = self.get_field(
            field_id
        )

        if existing_field is None:
            raise ValueError(
                f"Field not found: {field_id}"
            )

        forbidden_fields = {
            "field_id",
            "farm_id",
            "farmer_id",
            "created_at",
            "updated_at",
            "status",
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
            "field_name",
            "area_acres",
            "irrigation_available",
            "latitude",
            "longitude",
            "metadata",
        }

        unknown_fields = (
            set(updates.keys())
            - allowed_fields
        )

        if unknown_fields:
            raise ValueError(
                "Unsupported field update fields: "
                f"{sorted(unknown_fields)}"
            )

        sanitized_updates: Dict[str, Any] = {}

        if "field_name" in updates:
            sanitized_updates["field_name"] = (
                self._validate_required_string(
                    updates["field_name"],
                    "field_name",
                )
            )

        if "area_acres" in updates:
            sanitized_updates["area_acres"] = (
                self._validate_optional_positive_number(
                    updates["area_acres"],
                    "area_acres",
                )
            )

        if "irrigation_available" in updates:
            sanitized_updates[
                "irrigation_available"
            ] = self._validate_optional_boolean(
                updates["irrigation_available"],
                "irrigation_available",
            )

        if "latitude" in updates:
            sanitized_updates["latitude"] = (
                self._validate_latitude(
                    updates["latitude"]
                )
            )

        if "longitude" in updates:
            sanitized_updates["longitude"] = (
                self._validate_longitude(
                    updates["longitude"]
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

        sanitized_updates["updated_at"] = (
            self.storage.utc_timestamp()
        )

        updated_field = self.storage.update_by_id(
            entity_type=FIELD_ENTITY_TYPE,
            record_id=field_id,
            id_field=FIELD_ID_FIELD,
            updates=sanitized_updates,
        )

        if updated_field is None:
            raise RuntimeError(
                "Field update failed unexpectedly."
            )

        return updated_field

    def deactivate_field(
        self,
        field_id: str,
    ) -> Dict[str, Any]:
        """
        Soft deactivate a field.
        """

        return self._set_field_status(
            field_id,
            STATUS_INACTIVE,
        )

    def activate_field(
        self,
        field_id: str,
    ) -> Dict[str, Any]:
        """
        Reactivate a field.
        """

        return self._set_field_status(
            field_id,
            STATUS_ACTIVE,
        )

    def _set_field_status(
        self,
        field_id: str,
        status: str,
    ) -> Dict[str, Any]:
        """
        Update field status.
        """

        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status: {status}"
            )

        field = self.get_field(
            field_id
        )

        if field is None:
            raise ValueError(
                f"Field not found: {field_id}"
            )

        updated_field = self.storage.update_by_id(
            entity_type=FIELD_ENTITY_TYPE,
            record_id=field_id,
            id_field=FIELD_ID_FIELD,
            updates={
                "status": status,
                "updated_at": (
                    self.storage.utc_timestamp()
                ),
            },
        )

        if updated_field is None:
            raise RuntimeError(
                "Field status update failed."
            )

        return updated_field

    def delete_field(
        self,
        field_id: str,
        permanent: bool = False,
    ) -> bool:
        """
        Delete a field.

        Default:
            Soft deactivate.

        permanent=True:
            Physically remove field.
        """

        field = self.get_field(
            field_id
        )

        if field is None:
            return False

        if not permanent:
            self.deactivate_field(
                field_id
            )
            return True

        return self.storage.delete_by_id(
            entity_type=FIELD_ENTITY_TYPE,
            record_id=field_id,
            id_field=FIELD_ID_FIELD,
        )

    # ========================================================
    # HIERARCHY HELPERS
    # ========================================================

    def get_farmer_hierarchy(
        self,
        farmer_id: str,
        include_inactive: bool = False,
    ) -> Dict[str, Any]:
        """
        Return persistent Farmer -> Farm -> Field hierarchy.

        This is useful for Streamlit and future APIs.

        Business logic remains in backend.
        """

        farmer = self.farmer_registry.get_farmer(
            farmer_id=farmer_id,
            include_inactive=include_inactive,
        )

        if farmer is None:
            raise ValueError(
                f"Farmer not found: {farmer_id}"
            )

        farms = self.get_farmer_farms(
            farmer_id=farmer_id,
            include_inactive=include_inactive,
        )

        hierarchy_farms = []

        for farm in farms:
            fields = self.get_farm_fields(
                farm_id=farm["farm_id"],
                include_inactive=include_inactive,
            )

            hierarchy_farms.append(
                {
                    "farm": farm,
                    "fields": fields,
                }
            )

        return {
            "farmer": farmer,
            "farms": hierarchy_farms,
        }

    def get_registry_summary(
        self,
    ) -> Dict[str, int]:
        """
        Return Farm and Field registry statistics.
        """

        all_farms = self.storage.read_all(
            FARM_ENTITY_TYPE
        )

        all_fields = self.storage.read_all(
            FIELD_ENTITY_TYPE
        )

        active_farms = sum(
            1
            for farm in all_farms
            if farm.get("status") == STATUS_ACTIVE
        )

        inactive_farms = sum(
            1
            for farm in all_farms
            if farm.get("status") == STATUS_INACTIVE
        )

        active_fields = sum(
            1
            for field in all_fields
            if field.get("status") == STATUS_ACTIVE
        )

        inactive_fields = sum(
            1
            for field in all_fields
            if field.get("status") == STATUS_INACTIVE
        )

        return {
            "total_farms": len(all_farms),
            "active_farms": active_farms,
            "inactive_farms": inactive_farms,
            "total_fields": len(all_fields),
            "active_fields": active_fields,
            "inactive_fields": inactive_fields,
        }

    # ========================================================
    # VALIDATION HELPERS
    # ========================================================

    def _validate_farmer_exists(
        self,
        farmer_id: str,
    ) -> None:
        """
        Ensure farmer exists and is active.
        """

        farmer = self.farmer_registry.get_farmer(
            farmer_id=farmer_id,
            include_inactive=False,
        )

        if farmer is None:
            raise ValueError(
                "Active farmer not found: "
                f"{farmer_id}"
            )

    @staticmethod
    def _validate_required_string(
        value: Any,
        field_name: str,
    ) -> str:
        """
        Validate required string.
        """

        if not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be a string."
            )

        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                f"{field_name} cannot be empty."
            )

        if len(cleaned) > 150:
            raise ValueError(
                f"{field_name} cannot exceed "
                "150 characters."
            )

        return cleaned

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

        cleaned = value.strip()

        if not cleaned:
            return None

        return cleaned

    @staticmethod
    def _validate_optional_positive_number(
        value: Any,
        field_name: str,
    ) -> Optional[float]:
        """
        Validate optional positive number.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be numeric."
            )

        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} must be numeric."
            ) from exc

        if number <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return number

    @staticmethod
    def _validate_optional_boolean(
        value: Any,
        field_name: str,
    ) -> Optional[bool]:
        """
        Validate optional boolean.
        """

        if value is None:
            return None

        if not isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be True or False."
            )

        return value

    @staticmethod
    def _validate_latitude(
        latitude: Any,
    ) -> Optional[float]:
        """
        Validate latitude.
        """

        if latitude is None:
            return None

        if isinstance(latitude, bool):
            raise ValueError(
                "latitude must be numeric."
            )

        try:
            latitude = float(latitude)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "latitude must be numeric."
            ) from exc

        if latitude < -90 or latitude > 90:
            raise ValueError(
                "latitude must be between -90 and 90."
            )

        return latitude

    @staticmethod
    def _validate_longitude(
        longitude: Any,
    ) -> Optional[float]:
        """
        Validate longitude.
        """

        if longitude is None:
            return None

        if isinstance(longitude, bool):
            raise ValueError(
                "longitude must be numeric."
            )

        try:
            longitude = float(longitude)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "longitude must be numeric."
            ) from exc

        if longitude < -180 or longitude > 180:
            raise ValueError(
                "longitude must be between -180 and 180."
            )

        return longitude

# ============================================================

# SINGLETON ACCESSOR

# ============================================================

_default_farm_field_registry: Optional[
    FarmFieldRegistry
] = None


def get_farm_field_registry() -> FarmFieldRegistry:
    """
    Return default FarmFieldRegistry instance.
    """
    global _default_farm_field_registry

    if _default_farm_field_registry is None:
        _default_farm_field_registry = FarmFieldRegistry()

    return _default_farm_field_registry


# ============================================================

# LOCAL RUNTIME TEST

# ============================================================


def _run_local_test() -> None:
    """
    Phase 4A runtime validation.

    Test flow:
        Farmer
          ↓
        Create Farm A
          ↓
        Create Field A1
        Create Field A2
          ↓
        Create Farm B
          ↓
        Create Field B1
          ↓
        Reload hierarchy
    """

    farmer_registry = get_farmer_registry()

    registry = get_farm_field_registry()

    print("=" * 70)
    print("RAYA PHASE 4A - FARM AND FIELD REGISTRY TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # GET OR CREATE TEST FARMER
    # --------------------------------------------------------

    test_phone = "9999000001"

    farmer = farmer_registry.get_farmer_by_phone(
        test_phone
    )

    if farmer is None:

        farmer = farmer_registry.create_farmer(
            name="Persistent Test Farmer",
            phone=test_phone,
            village="Demo Village",
            district="Mandya",
            state="Karnataka",
            farming_experience_years=12,
        )

        print(
            "\nCreated test farmer:",
            farmer["farmer_id"],
        )

    else:

        print(
            "\nLoaded test farmer:",
            farmer["farmer_id"],
        )

    farmer_id = farmer["farmer_id"]

    # --------------------------------------------------------
    # CREATE FARM 1
    # --------------------------------------------------------

    existing_farms = registry.get_farmer_farms(
        farmer_id
    )

    farm_1 = None

    for farm in existing_farms:

        if farm["farm_name"] == "North Farm":

            farm_1 = farm
            break

    if farm_1 is None:

        farm_1 = registry.create_farm(
            farmer_id=farmer_id,
            farm_name="North Farm",
            village="Demo Village",
            district="Mandya",
            state="Karnataka",
            total_area_acres=10.5,
            irrigation_source="Borewell",
        )

        print(
            "\nCreated Farm:",
            farm_1["farm_id"],
        )

    else:

        print(
            "\nLoaded Farm:",
            farm_1["farm_id"],
        )

    # --------------------------------------------------------
    # CREATE FARM 2
    # --------------------------------------------------------

    farm_2 = None

    for farm in existing_farms:

        if farm["farm_name"] == "South Farm":

            farm_2 = farm
            break

    if farm_2 is None:

        farm_2 = registry.create_farm(
            farmer_id=farmer_id,
            farm_name="South Farm",
            village="Demo Village",
            district="Mandya",
            state="Karnataka",
            total_area_acres=6.0,
            irrigation_source="Canal",
        )

        print(
            "Created Farm:",
            farm_2["farm_id"],
        )

    else:

        print(
            "Loaded Farm:",
            farm_2["farm_id"],
        )

    # --------------------------------------------------------
    # CREATE FIELD 1
    # --------------------------------------------------------

    farm_1_fields = registry.get_farm_fields(
        farm_1["farm_id"]
    )

    field_names = {
        field["field_name"]
        for field in farm_1_fields
    }

    if "Field A1" not in field_names:

        field_a1 = registry.create_field(
            farm_id=farm_1["farm_id"],
            field_name="Field A1",
            area_acres=4.0,
            irrigation_available=True,
        )

        print(
            "\nCreated Field:",
            field_a1["field_id"],
        )

    else:

        print(
            "\nField A1 already exists."
        )

    # --------------------------------------------------------
    # CREATE FIELD 2
    # --------------------------------------------------------

    if "Field A2" not in field_names:

        field_a2 = registry.create_field(
            farm_id=farm_1["farm_id"],
            field_name="Field A2",
            area_acres=6.5,
            irrigation_available=True,
        )

        print(
            "Created Field:",
            field_a2["field_id"],
        )

    else:

        print(
            "Field A2 already exists."
        )

    # --------------------------------------------------------
    # CREATE FIELD 3
    # --------------------------------------------------------

    farm_2_fields = registry.get_farm_fields(
        farm_2["farm_id"]
    )

    farm_2_field_names = {
        field["field_name"]
        for field in farm_2_fields
    }

    if "Field B1" not in farm_2_field_names:

        field_b1 = registry.create_field(
            farm_id=farm_2["farm_id"],
            field_name="Field B1",
            area_acres=6.0,
            irrigation_available=False,
        )

        print(
            "Created Field:",
            field_b1["field_id"],
        )

    else:

        print(
            "Field B1 already exists."
        )

    # --------------------------------------------------------
    # LOAD COMPLETE HIERARCHY
    # --------------------------------------------------------

    hierarchy = registry.get_farmer_hierarchy(
        farmer_id
    )

    print("\n" + "=" * 70)
    print("PERSISTENT FARMER HIERARCHY")
    print("=" * 70)

    print(
        f"\nFarmer: "
        f"{hierarchy['farmer']['name']}"
    )

    for item in hierarchy["farms"]:

        farm = item["farm"]
        fields = item["fields"]

        print(
            f"\n  Farm: {farm['farm_name']}"
        )

        print(
            f"  Farm ID: {farm['farm_id']}"
        )

        print(
            f"  Area: {farm['total_area_acres']} acres"
        )

        for field in fields:

            print(
                f"      Field: "
                f"{field['field_name']}"
            )

            print(
                f"      Field ID: "
                f"{field['field_id']}"
            )

            print(
                f"      Area: "
                f"{field['area_acres']} acres"
            )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = registry.get_registry_summary()

    print("\n" + "=" * 70)
    print("REGISTRY SUMMARY")
    print("=" * 70)

    for key, value in summary.items():

        print(
            f"{key}: {value}"
        )

    print("\n" + "=" * 70)
    print("FARM AND FIELD REGISTRY TEST: PASS")
    print("=" * 70)


# ============================================================

# MAIN

# ============================================================

if __name__ == "__main__":
    _run_local_test()
