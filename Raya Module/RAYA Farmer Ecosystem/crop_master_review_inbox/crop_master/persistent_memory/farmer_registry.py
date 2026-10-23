"""
RAYA Phase 4A
Persistent Farmer Intelligence Layer

# Farmer Registry

This module manages permanent farmer identity.

Responsibilities:
- Create persistent farmers
- Retrieve farmers
- List farmers
- Update farmer profiles
- Activate / deactivate farmers
- Delete farmers
- Validate duplicate identities

Persistence:
data/persistent_memory/farmers.json

Architecture:
Streamlit/UI
↓
FarmerRegistry
↓
StorageManager
↓
Persistent JSON Storage
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from persistent_memory.storage_manager import (
    StorageManager,
    get_storage_manager,
)

# ============================================================

# CONSTANTS

# ============================================================

FARMER_ENTITY_TYPE = "farmers"
FARMER_ID_FIELD = "farmer_id"

FARMER_STATUS_ACTIVE = "active"
FARMER_STATUS_INACTIVE = "inactive"

VALID_FARMER_STATUSES = {
    FARMER_STATUS_ACTIVE,
    FARMER_STATUS_INACTIVE,
}

# ============================================================

# FARMER REGISTRY

# ============================================================


class FarmerRegistry:
    """
    Backend registry for persistent farmer identity.

    Hierarchy:

        Farmer
            ↓
        Farms
            ↓
        Fields
            ↓
        Soil / Seasons / Advisory History

    This module only manages the Farmer entity.
    """

    def __init__(
        self,
        storage: Optional[StorageManager] = None,
    ):
        """
        Initialize Farmer Registry.
        """

        self.storage = (
            storage
            if storage is not None
            else get_storage_manager()
        )

    # ========================================================
    # CREATE FARMER
    # ========================================================

    def create_farmer(
        self,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        village: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        farming_experience_years: Optional[int] = None,
        labor_availability: Optional[str] = None,
        budget_constraint: Optional[str] = None,
        guidance_preference: Optional[str] = None,
        preferred_input_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create and persist a new farmer.
        """

        normalized_name = self._validate_name(name)

        normalized_phone = self._normalize_phone(phone)

        normalized_email = self._normalize_email(email)

        normalized_experience = self._validate_experience(
            farming_experience_years
        )

        # ----------------------------------------------------
        # DUPLICATE PHONE VALIDATION
        # ----------------------------------------------------

        if normalized_phone:

            existing = self.get_farmer_by_phone(
                normalized_phone
            )

            if existing is not None:

                raise ValueError(
                    "A farmer with this phone number "
                    "already exists. "
                    f"farmer_id={existing[FARMER_ID_FIELD]}"
                )

        # ----------------------------------------------------
        # DUPLICATE EMAIL VALIDATION
        # ----------------------------------------------------

        if normalized_email:

            existing = self.get_farmer_by_email(
                normalized_email
            )

            if existing is not None:

                raise ValueError(
                    "A farmer with this email already exists. "
                    f"farmer_id={existing[FARMER_ID_FIELD]}"
                )

        # ----------------------------------------------------
        # CREATE RECORD
        # ----------------------------------------------------

        timestamp = self.storage.utc_timestamp()

        farmer_id = self.storage.generate_id(
            "FARMER"
        )

        farmer_record = {
            "farmer_id": farmer_id,

            # Identity
            "name": normalized_name,
            "phone": normalized_phone,
            "email": normalized_email,

            # Location
            "village": self._clean_optional_string(
                village
            ),
            "district": self._clean_optional_string(
                district
            ),
            "state": self._clean_optional_string(
                state
            ),

            # Farmer profile
            "farming_experience_years": (
                normalized_experience
            ),
            "labor_availability": (
                self._clean_optional_string(
                    labor_availability
                )
            ),
            "budget_constraint": (
                self._clean_optional_string(
                    budget_constraint
                )
            ),
            "guidance_preference": (
                self._clean_optional_string(
                    guidance_preference
                )
            ),
            "preferred_input_type": (
                self._clean_optional_string(
                    preferred_input_type
                )
            ),

            # Status
            "status": FARMER_STATUS_ACTIVE,

            # Timestamps
            "created_at": timestamp,
            "updated_at": timestamp,

            # Extensible metadata
            "metadata": (
                metadata.copy()
                if isinstance(metadata, dict)
                else {}
            ),
        }

        self.storage.insert(
            entity_type=FARMER_ENTITY_TYPE,
            record=farmer_record,
        )

        return farmer_record

    # ========================================================
    # GET FARMER
    # ========================================================

    def get_farmer(
        self,
        farmer_id: str,
        include_inactive: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a farmer by farmer_id.
        """

        farmer = self.storage.get_by_id(
            entity_type=FARMER_ENTITY_TYPE,
            record_id=farmer_id,
            id_field=FARMER_ID_FIELD,
        )

        if farmer is None:
            return None

        if (
            not include_inactive
            and farmer.get("status")
            != FARMER_STATUS_ACTIVE
        ):
            return None

        return farmer

    # ========================================================
    # GET FARMER BY PHONE
    # ========================================================

    def get_farmer_by_phone(
        self,
        phone: str,
        include_inactive: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve farmer using phone number.
        """

        normalized_phone = self._normalize_phone(
            phone
        )

        if not normalized_phone:
            return None

        matches = self.storage.find(
            entity_type=FARMER_ENTITY_TYPE,
            filters={
                "phone": normalized_phone
            },
        )

        for farmer in matches:

            if (
                include_inactive
                or farmer.get("status")
                == FARMER_STATUS_ACTIVE
            ):
                return farmer

        return None

    # ========================================================
    # GET FARMER BY EMAIL
    # ========================================================

    def get_farmer_by_email(
        self,
        email: str,
        include_inactive: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve farmer using email.
        """

        normalized_email = self._normalize_email(
            email
        )

        if not normalized_email:
            return None

        matches = self.storage.find(
            entity_type=FARMER_ENTITY_TYPE,
            filters={
                "email": normalized_email
            },
        )

        for farmer in matches:

            if (
                include_inactive
                or farmer.get("status")
                == FARMER_STATUS_ACTIVE
            ):
                return farmer

        return None

    # ========================================================
    # LIST FARMERS
    # ========================================================

    def list_farmers(
        self,
        status: Optional[str] = FARMER_STATUS_ACTIVE,
    ) -> List[Dict[str, Any]]:
        """
        List persistent farmers.

        status:
            "active"
            "inactive"
            None -> all farmers
        """

        if (
            status is not None
            and status not in VALID_FARMER_STATUSES
        ):
            raise ValueError(
                "Invalid farmer status. "
                f"Supported statuses: "
                f"{sorted(VALID_FARMER_STATUSES)} "
                "or None."
            )

        farmers = self.storage.read_all(
            FARMER_ENTITY_TYPE
        )

        if status is not None:

            farmers = [
                farmer
                for farmer in farmers
                if farmer.get("status") == status
            ]

        return sorted(
            farmers,
            key=lambda farmer: (
                farmer.get("name") or ""
            ).lower(),
        )

    # ========================================================
    # CHECK EXISTENCE
    # ========================================================

    def farmer_exists(
        self,
        farmer_id: str,
        active_only: bool = False,
    ) -> bool:
        """
        Check whether farmer exists.
        """

        farmer = self.get_farmer(
            farmer_id=farmer_id,
            include_inactive=not active_only,
        )

        return farmer is not None

    # ========================================================
    # UPDATE FARMER
    # ========================================================

    def update_farmer(
        self,
        farmer_id: str,
        **updates: Any,
    ) -> Dict[str, Any]:
        """
        Update an existing farmer.
        """

        existing_farmer = self.get_farmer(
            farmer_id
        )

        if existing_farmer is None:
            raise ValueError(
                f"Farmer not found: {farmer_id}"
            )

        forbidden_fields = {
            FARMER_ID_FIELD,
            "created_at",
            "updated_at",
            "status",
        }

        supplied_fields = set(updates.keys())

        invalid_fields = (
            supplied_fields & forbidden_fields
        )

        if invalid_fields:
            raise ValueError(
                "These fields cannot be updated: "
                f"{sorted(invalid_fields)}"
            )

        allowed_fields = {
            "name",
            "phone",
            "email",
            "village",
            "district",
            "state",
            "farming_experience_years",
            "labor_availability",
            "budget_constraint",
            "guidance_preference",
            "preferred_input_type",
            "metadata",
        }

        unknown_fields = (
            supplied_fields - allowed_fields
        )

        if unknown_fields:
            raise ValueError(
                "Unsupported update fields: "
                f"{sorted(unknown_fields)}"
            )

        sanitized_updates: Dict[str, Any] = {}

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if "name" in updates:
            sanitized_updates["name"] = (
                self._validate_name(
                    updates["name"]
                )
            )

        # ----------------------------------------------------
        # PHONE
        # ----------------------------------------------------

        if "phone" in updates:

            normalized_phone = (
                self._normalize_phone(
                    updates["phone"]
                )
            )

            if normalized_phone:

                duplicate = (
                    self.get_farmer_by_phone(
                        normalized_phone
                    )
                )

                if (
                    duplicate is not None
                    and duplicate[FARMER_ID_FIELD]
                    != farmer_id
                ):
                    raise ValueError(
                        "Another farmer already uses "
                        "this phone number."
                    )

            sanitized_updates["phone"] = (
                normalized_phone
            )

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        if "email" in updates:

            normalized_email = (
                self._normalize_email(
                    updates["email"]
                )
            )

            if normalized_email:

                duplicate = (
                    self.get_farmer_by_email(
                        normalized_email
                    )
                )

                if (
                    duplicate is not None
                    and duplicate[FARMER_ID_FIELD]
                    != farmer_id
                ):
                    raise ValueError(
                        "Another farmer already uses "
                        "this email."
                    )

            sanitized_updates["email"] = (
                normalized_email
            )

        # ----------------------------------------------------
        # FARMING EXPERIENCE
        # ----------------------------------------------------

        if (
            "farming_experience_years"
            in updates
        ):
            sanitized_updates[
                "farming_experience_years"
            ] = self._validate_experience(
                updates[
                    "farming_experience_years"
                ]
            )

        # ----------------------------------------------------
        # OPTIONAL STRING FIELDS
        # ----------------------------------------------------

        optional_string_fields = [
            "village",
            "district",
            "state",
            "labor_availability",
            "budget_constraint",
            "guidance_preference",
            "preferred_input_type",
        ]

        for field in optional_string_fields:

            if field in updates:
                sanitized_updates[field] = (
                    self._clean_optional_string(
                        updates[field]
                    )
                )

        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

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
        # UPDATED TIMESTAMP
        # ----------------------------------------------------

        sanitized_updates["updated_at"] = (
            self.storage.utc_timestamp()
        )

        updated_farmer = (
            self.storage.update_by_id(
                entity_type=FARMER_ENTITY_TYPE,
                record_id=farmer_id,
                id_field=FARMER_ID_FIELD,
                updates=sanitized_updates,
            )
        )

        if updated_farmer is None:
            raise RuntimeError(
                "Farmer update failed unexpectedly."
            )

        return updated_farmer

    # ========================================================
    # ACTIVATE / DEACTIVATE
    # ========================================================

    def deactivate_farmer(
        self,
        farmer_id: str,
    ) -> Dict[str, Any]:
        """
        Soft delete farmer.
        Historical records remain preserved.
        """

        return self._set_status(
            farmer_id,
            FARMER_STATUS_INACTIVE,
        )

    def activate_farmer(
        self,
        farmer_id: str,
    ) -> Dict[str, Any]:
        """
        Reactivate farmer.
        """

        return self._set_status(
            farmer_id,
            FARMER_STATUS_ACTIVE,
        )

    def _set_status(
        self,
        farmer_id: str,
        status: str,
    ) -> Dict[str, Any]:
        """
        Update farmer status.
        """

        if status not in VALID_FARMER_STATUSES:
            raise ValueError(
                f"Invalid farmer status: {status}"
            )

        existing_farmer = self.get_farmer(
            farmer_id
        )

        if existing_farmer is None:
            raise ValueError(
                f"Farmer not found: {farmer_id}"
            )

        updated_farmer = (
            self.storage.update_by_id(
                entity_type=FARMER_ENTITY_TYPE,
                record_id=farmer_id,
                id_field=FARMER_ID_FIELD,
                updates={
                    "status": status,
                    "updated_at": (
                        self.storage.utc_timestamp()
                    ),
                },
            )
        )

        if updated_farmer is None:
            raise RuntimeError(
                "Farmer status update failed."
            )

        return updated_farmer

    # ========================================================
    # DELETE FARMER
    # ========================================================

    def delete_farmer(
        self,
        farmer_id: str,
        permanent: bool = False,
    ) -> bool:
        """
        Delete farmer.

        Default:
            Soft delete.

        permanent=True:
            Physically removes farmer record.
        """

        existing_farmer = self.get_farmer(
            farmer_id
        )

        if existing_farmer is None:
            return False

        if not permanent:

            self.deactivate_farmer(
                farmer_id
            )

            return True

        return self.storage.delete_by_id(
            entity_type=FARMER_ENTITY_TYPE,
            record_id=farmer_id,
            id_field=FARMER_ID_FIELD,
        )

    # ========================================================
    # REGISTRY SUMMARY
    # ========================================================

    def get_registry_summary(
        self,
    ) -> Dict[str, int]:
        """
        Return Farmer Registry statistics.
        """

        all_farmers = self.storage.read_all(
            FARMER_ENTITY_TYPE
        )

        active = sum(
            1
            for farmer in all_farmers
            if farmer.get("status")
            == FARMER_STATUS_ACTIVE
        )

        inactive = sum(
            1
            for farmer in all_farmers
            if farmer.get("status")
            == FARMER_STATUS_INACTIVE
        )

        return {
            "total_farmers": len(all_farmers),
            "active_farmers": active,
            "inactive_farmers": inactive,
        }

    # ========================================================
    # VALIDATION HELPERS
    # ========================================================

    @staticmethod
    def _validate_name(
        name: Any,
    ) -> str:
        """
        Validate farmer name.
        """

        if not isinstance(name, str):
            raise ValueError(
                "Farmer name must be a string."
            )

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError(
                "Farmer name cannot be empty."
            )

        if len(normalized_name) < 2:
            raise ValueError(
                "Farmer name must contain at least "
                "2 characters."
            )

        if len(normalized_name) > 120:
            raise ValueError(
                "Farmer name cannot exceed "
                "120 characters."
            )

        return normalized_name

    @staticmethod
    def _normalize_phone(
        phone: Any,
    ) -> Optional[str]:
        """
        Normalize phone number.
        """

        if phone is None:
            return None

        if not isinstance(phone, str):
            phone = str(phone)

        normalized_phone = phone.strip()

        if not normalized_phone:
            return None

        normalized_phone = (
            normalized_phone
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        if len(normalized_phone) < 6:
            raise ValueError(
                "Phone number appears invalid."
            )

        return normalized_phone

    @staticmethod
    def _normalize_email(
        email: Any,
    ) -> Optional[str]:
        """
        Normalize email.
        """

        if email is None:
            return None

        if not isinstance(email, str):
            raise ValueError(
                "Email must be a string."
            )

        normalized_email = email.strip().lower()

        if not normalized_email:
            return None

        if "@" not in normalized_email:
            raise ValueError(
                "Email appears invalid."
            )

        return normalized_email

    @staticmethod
    def _validate_experience(
        experience: Any,
    ) -> Optional[int]:
        """
        Validate farming experience.
        """

        if experience is None:
            return None

        if isinstance(experience, bool):
            raise ValueError(
                "farming_experience_years "
                "must be an integer."
            )

        try:
            normalized_experience = int(
                experience
            )

        except (TypeError, ValueError) as exc:
            raise ValueError(
                "farming_experience_years "
                "must be an integer."
            ) from exc

        if normalized_experience < 0:
            raise ValueError(
                "farming_experience_years "
                "cannot be negative."
            )

        if normalized_experience > 100:
            raise ValueError(
                "farming_experience_years "
                "appears unrealistic."
            )

        return normalized_experience

    @staticmethod
    def _clean_optional_string(
        value: Any,
    ) -> Optional[str]:
        """
        Normalize optional string fields.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        cleaned_value = value.strip()

        if not cleaned_value:
            return None

        return cleaned_value


# ============================================================

# SINGLETON ACCESSOR

# ============================================================

_default_farmer_registry: Optional[
FarmerRegistry
] = None

def get_farmer_registry() -> FarmerRegistry:
    """
    Return default application Farmer Registry.
    """
    global _default_farmer_registry

    if _default_farmer_registry is None:
        _default_farmer_registry = FarmerRegistry()

    return _default_farmer_registry


# ============================================================

# LOCAL RUNTIME TEST

# ============================================================

def _run_local_test() -> None:
    """
    Basic Farmer Registry runtime test.
    """
    registry = get_farmer_registry()

    print("=" * 70)
    print("RAYA PHASE 4A - FARMER REGISTRY TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # FARMER A
    # --------------------------------------------------------

    farmer_a_phone = "9999000001"

    farmer_a = registry.get_farmer_by_phone(
        farmer_a_phone
    )

    if farmer_a is None:

        farmer_a = registry.create_farmer(
            name="Farmer A",
            phone=farmer_a_phone,
            village="Demo Village A",
            district="Mandya",
            state="Karnataka",
            farming_experience_years=18,
            labor_availability="low",
            budget_constraint="high",
            guidance_preference="simple",
            preferred_input_type="organic",
        )

        print(
            "\nCreated Farmer A:",
            farmer_a["farmer_id"],
        )

    else:

        print(
            "\nLoaded existing Farmer A:",
            farmer_a["farmer_id"],
        )

    # --------------------------------------------------------
    # FARMER B
    # --------------------------------------------------------

    farmer_b_phone = "9999000002"

    farmer_b = registry.get_farmer_by_phone(
        farmer_b_phone
    )

    if farmer_b is None:

        farmer_b = registry.create_farmer(
            name="Farmer B",
            phone=farmer_b_phone,
            village="Demo Village B",
            district="Mandya",
            state="Karnataka",
            farming_experience_years=4,
            labor_availability="high",
            budget_constraint="low",
            guidance_preference="detailed",
            preferred_input_type="chemical",
        )

        print(
            "Created Farmer B:",
            farmer_b["farmer_id"],
        )

    else:

        print(
            "Loaded existing Farmer B:",
            farmer_b["farmer_id"],
        )

    # --------------------------------------------------------
    # LIST FARMERS
    # --------------------------------------------------------

    farmers = registry.list_farmers(
        status=None
    )

    print("\nPersistent Farmers:")

    for farmer in farmers:

        print(
            f"  - {farmer['name']} | "
            f"{farmer['farmer_id']} | "
            f"{farmer['status']}"
        )

    # --------------------------------------------------------
    # UPDATE TEST
    # --------------------------------------------------------

    updated_farmer = registry.update_farmer(
        farmer_a["farmer_id"],
        guidance_preference="step_by_step",
    )

    print(
        "\nUpdated Farmer A guidance preference:",
        updated_farmer[
            "guidance_preference"
        ],
    )

    # --------------------------------------------------------
    # DUPLICATE PROTECTION TEST
    # --------------------------------------------------------

    print(
        "\nTesting duplicate phone protection..."
    )

    try:

        registry.create_farmer(
            name="Duplicate Farmer",
            phone=farmer_a_phone,
        )

        print(
            "ERROR: Duplicate farmer was created."
        )

    except ValueError:

        print(
            "PASS: Duplicate identity blocked."
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = registry.get_registry_summary()

    print("\nRegistry Summary:")

    for key, value in summary.items():

        print(
            f"  {key}: {value}"
        )

    print("\n" + "=" * 70)
    print("FARMER REGISTRY TEST: PASS")
    print("=" * 70)


# ============================================================

# MAIN

# ============================================================

if __name__ == "__main__":
    _run_local_test()
