"""
RAYA Phase 4C - Season Manager

File:
persistent_memory/season_manager.py

Purpose:
Maintain persistent crop and season history for each field.

Architecture:

Farmer
    -> Farm
        -> Field
            -> Soil Memory
            -> Season Manager

Rules:
- One field can have multiple seasons over time.
- A field can have only one ACTIVE season at a time.
- Completed seasons remain permanently stored as history.
- Season Manager does not modify agricultural intelligence.
- It only stores persistent crop/season state.

Phase 4C does NOT modify:
- Crop Master
- Weather Intelligence
- Water Intelligence
- Disease Intelligence
- Market Intelligence
- Agricultural rules
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from persistent_memory.storage_manager import (
    StorageManager,
    get_storage_manager,
)

from persistent_memory.farm_field_registry import (
    FarmFieldRegistry,
    get_farm_field_registry,
)
from persistent_memory.timeline_manager import (
    TimelineManager,
    get_timeline_manager,
)

# ============================================================

# CONSTANTS

# ============================================================

SEASON_ENTITY_TYPE = "seasons"
SEASON_ID_FIELD = "season_id"

STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"

VALID_STATUSES = {
    STATUS_ACTIVE,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
}

# ============================================================

# SEASON MANAGER

# ============================================================

class SeasonManager:
    """
    Persistent season and crop history manager.

    A field can have multiple seasons:

        Field A
            |
            +-- Kharif 2025
            |     crop = Rice
            |     status = completed
            |
            +-- Rabi 2025-26
            |     crop = Wheat
            |     status = completed
            |
            +-- Kharif 2026
                  crop = Rice
                  status = active

    Only one active season is allowed per field.
    """

    def __init__(
        self,
        storage: Optional[StorageManager] = None,
        farm_field_registry: Optional[
            FarmFieldRegistry
        ] = None,
        timeline_manager: Optional[TimelineManager] = None,
    ):
        """
        Initialize Season Manager.
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

        self.timeline_manager = (
            timeline_manager
            if timeline_manager is not None
            else TimelineManager(storage=self.storage)
        )

    # ========================================================
    # CREATE SEASON
    # ========================================================

    def create_season(
        self,
        field_id: str,
        season_name: str,
        crop: str,
        current_stage: Optional[str] = None,
        start_date: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new active season for a field.

        Rules:
            - Field must exist.
            - Only one active season per field.
            - Crop and season_name are required.
        """

        self._validate_field_exists(
            field_id
        )

        season_name = self._clean_required_string(
            season_name,
            "season_name",
        )

        crop = self._clean_required_string(
            crop,
            "crop",
        )

        current_stage = self._clean_optional_string(
            current_stage
        )

        existing_active_season = (
            self.get_active_season(
                field_id
            )
        )

        if existing_active_season is not None:
            raise ValueError(
                "An active season already exists "
                f"for field: {field_id}. "
                "Complete or cancel the existing season "
                "before creating a new one."
            )

        timestamp = self.storage.utc_timestamp()

        season_record = {
            "season_id": (
                self.storage.generate_id(
                    "SEASON"
                )
            ),
            "field_id": field_id,
            "season_name": season_name,
            "crop": crop,
            "current_stage": current_stage,
            "start_date": (
                start_date
                if start_date
                else timestamp
            ),
            "end_date": None,
            "status": STATUS_ACTIVE,
            "created_at": timestamp,
            "updated_at": timestamp,
            "stage_history": [],
            "metadata": (
                metadata.copy()
                if isinstance(metadata, dict)
                else {}
            ),
        }

        self.storage.insert(
            entity_type=SEASON_ENTITY_TYPE,
            record=season_record,
        )

        self.timeline_manager.add_event(
            field_id=field_id,
            event_type="sowing",
            title=f"{crop} sown",
            occurred_at=season_record["start_date"],
            season_id=season_record["season_id"],
            idempotency_key=(
                f"season:{season_record['season_id']}:sowing"
            ),
            details={
                "crop": crop,
                "season_name": season_name,
            },
        )

        return season_record

    # ========================================================
    # GET SEASON BY ID
    # ========================================================

    def get_season(
        self,
        season_id: str,
        include_inactive: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve season by ID.
        """

        seasons = self.storage.read_all(
            SEASON_ENTITY_TYPE
        )

        for season in seasons:

            if (
                season.get("season_id")
                != season_id
            ):
                continue

            if (
                not include_inactive
                and season.get("status")
                != STATUS_ACTIVE
            ):
                continue

            return season

        return None

    # ========================================================
    # GET ACTIVE SEASON
    # ========================================================

    def get_active_season(
        self,
        field_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return the currently active season
        for a field.
        """

        seasons = self.storage.read_all(
            SEASON_ENTITY_TYPE
        )

        active_seasons = [
            season
            for season in seasons
            if (
                season.get("field_id") == field_id
                and season.get("status")
                == STATUS_ACTIVE
            )
        ]

        if not active_seasons:
            return None

        active_seasons.sort(
            key=lambda item: (
                item.get("updated_at")
                or item.get("created_at")
                or ""
            ),
            reverse=True,
        )

        return active_seasons[0]

    # ========================================================
    # GET FIELD SEASONS
    # ========================================================

    def get_field_seasons(
        self,
        field_id: str,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return all seasons belonging to a field.

        status:
            None        -> all seasons
            active
            completed
            cancelled
        """

        if (
            status is not None
            and status not in VALID_STATUSES
        ):
            raise ValueError(
                "Invalid status. "
                f"Allowed: "
                f"{sorted(VALID_STATUSES)} or None."
            )

        seasons = self.storage.read_all(
            SEASON_ENTITY_TYPE
        )

        results = []

        for season in seasons:

            if (
                season.get("field_id")
                != field_id
            ):
                continue

            if (
                status is not None
                and season.get("status")
                != status
            ):
                continue

            results.append(season)

        return sorted(
            results,
            key=lambda item: (
                item.get("created_at")
                or ""
            ),
            reverse=True,
        )

    # ========================================================
    # LIST ALL SEASONS
    # ========================================================

    def list_seasons(
        self,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all persistent seasons.
        """

        if (
            status is not None
            and status not in VALID_STATUSES
        ):
            raise ValueError(
                "Invalid status. "
                f"Allowed: "
                f"{sorted(VALID_STATUSES)} or None."
            )

        seasons = self.storage.read_all(
            SEASON_ENTITY_TYPE
        )

        if status is not None:

            seasons = [
                season
                for season in seasons
                if season.get("status")
                == status
            ]

        return sorted(
            seasons,
            key=lambda item: (
                item.get("created_at")
                or ""
            ),
            reverse=True,
        )

    # ========================================================
    # UPDATE CROP STAGE
    # ========================================================

    def update_crop_stage(
        self,
        field_id: str,
        new_stage: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update current crop stage.

        Previous stage information is preserved
        inside stage_history.
        """

        active_season = self.get_active_season(
            field_id
        )

        if active_season is None:
            raise ValueError(
                "No active season found for field: "
                f"{field_id}"
            )

        new_stage = self._clean_required_string(
            new_stage,
            "new_stage",
        )

        previous_stage = active_season.get(
            "current_stage"
        )

        history = list(
            active_season.get(
                "stage_history",
                [],
            )
        )

        history.append(
            {
                "timestamp": (
                    self.storage.utc_timestamp()
                ),
                "previous_stage": (
                    previous_stage
                ),
                "new_stage": new_stage,
                "notes": (
                    self._clean_optional_string(
                        notes
                    )
                ),
            }
        )

        updated_season = (
            self.storage.update_by_id(
                entity_type=SEASON_ENTITY_TYPE,
                record_id=active_season[
                    "season_id"
                ],
                id_field=SEASON_ID_FIELD,
                updates={
                    "current_stage": new_stage,
                    "stage_history": history,
                    "updated_at": (
                        self.storage.utc_timestamp()
                    ),
                },
            )
        )

        if updated_season is None:
            raise RuntimeError(
                "Failed to update crop stage."
            )

        return updated_season

    # ========================================================
    # COMPLETE SEASON
    # ========================================================

    def complete_season(
        self,
        field_id: str,
        end_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Mark the active season as completed.

        The completed season remains permanently
        stored as crop history.
        """

        active_season = self.get_active_season(
            field_id
        )

        if active_season is None:
            raise ValueError(
                "No active season found for field: "
                f"{field_id}"
            )

        metadata = dict(
            active_season.get(
                "metadata",
                {},
            )
        )

        if notes is not None:
            metadata["completion_notes"] = (
                self._clean_optional_string(
                    notes
                )
            )

        timestamp = self.storage.utc_timestamp()

        updated_season = (
            self.storage.update_by_id(
                entity_type=SEASON_ENTITY_TYPE,
                record_id=active_season[
                    "season_id"
                ],
                id_field=SEASON_ID_FIELD,
                updates={
                    "status": STATUS_COMPLETED,
                    "end_date": (
                        end_date
                        if end_date
                        else timestamp
                    ),
                    "metadata": metadata,
                    "updated_at": timestamp,
                },
            )
        )

        if updated_season is None:
            raise RuntimeError(
                "Failed to complete season."
            )

        return updated_season

    # ========================================================
    # CANCEL SEASON
    # ========================================================

    def cancel_season(
        self,
        field_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cancel the active season.

        The cancelled season remains stored
        in historical records.
        """

        active_season = self.get_active_season(
            field_id
        )

        if active_season is None:
            raise ValueError(
                "No active season found for field: "
                f"{field_id}"
            )

        metadata = dict(
            active_season.get(
                "metadata",
                {},
            )
        )

        metadata["cancellation_reason"] = (
            self._clean_optional_string(
                reason
            )
        )

        timestamp = self.storage.utc_timestamp()

        updated_season = (
            self.storage.update_by_id(
                entity_type=SEASON_ENTITY_TYPE,
                record_id=active_season[
                    "season_id"
                ],
                id_field=SEASON_ID_FIELD,
                updates={
                    "status": STATUS_CANCELLED,
                    "end_date": timestamp,
                    "metadata": metadata,
                    "updated_at": timestamp,
                },
            )
        )

        if updated_season is None:
            raise RuntimeError(
                "Failed to cancel season."
            )

        return updated_season

    # ========================================================
    # ACTIVE SEASON CONTEXT
    # ========================================================

    def get_active_season_context(
        self,
        field_id: str,
    ) -> Dict[str, Any]:
        """
        Return backend-friendly active season context.

        Designed for integration:

            Field
                ->
            Soil Memory
                ->
            Active Season
                ->
            Farmer Search
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

        active_season = self.get_active_season(
            field_id
        )

        return {
            "field_id": field_id,
            "farm_id": field.get("farm_id"),
            "farmer_id": field.get("farmer_id"),
            "active_season": active_season,
        }

    # ========================================================
    # CROP HISTORY
    # ========================================================

    def get_crop_history(
        self,
        field_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Return persistent crop history for a field.

        Includes completed and cancelled seasons.
        """

        seasons = self.get_field_seasons(
            field_id=field_id,
            status=None,
        )

        return [
            {
                "season_id": season.get(
                    "season_id"
                ),
                "season_name": season.get(
                    "season_name"
                ),
                "crop": season.get("crop"),
                "current_stage": season.get(
                    "current_stage"
                ),
                "start_date": season.get(
                    "start_date"
                ),
                "end_date": season.get(
                    "end_date"
                ),
                "status": season.get("status"),
            }
            for season in seasons
        ]

    # ========================================================
    # VALIDATION HELPERS
    # ========================================================

    def _validate_field_exists(
        self,
        field_id: str,
    ) -> None:
        """
        Ensure field exists and is active.
        """

        field = self.farm_field_registry.get_field(
            field_id=field_id,
            include_inactive=False,
        )

        if field is None:
            raise ValueError(
                f"Active field not found: {field_id}"
            )

    @staticmethod
    def _clean_required_string(
        value: Any,
        field_name: str,
    ) -> str:
        """
        Validate required string.
        """

        if value is None:
            raise ValueError(
                f"{field_name} is required."
            )

        value = str(value).strip()

        if not value:
            raise ValueError(
                f"{field_name} cannot be empty."
            )

        return value

    @staticmethod
    def _clean_optional_string(
        value: Any,
    ) -> Optional[str]:
        """
        Normalize optional string.
        """

        if value is None:
            return None

        value = str(value).strip()

        return value or None


# ============================================================

# SINGLETON ACCESSOR

# ============================================================

_default_season_manager: Optional[
    SeasonManager
] = None

def get_season_manager() -> SeasonManager:
    """
    Return default SeasonManager instance.
    """

    global _default_season_manager

    if _default_season_manager is None:
        _default_season_manager = SeasonManager()

    return _default_season_manager


# ============================================================

# PHASE 4C RUNTIME VALIDATION

# ============================================================

def _run_local_test() -> None:
    """
    Runtime validation for Phase 4C.
    """

    print("=" * 70)
    print("RAYA PHASE 4C - SEASON MANAGER TEST")
    print("=" * 70)

    registry = get_farm_field_registry()

    season_manager = get_season_manager()

    # --------------------------------------------------------
    # GET TEST FIELD
    # --------------------------------------------------------

    fields = registry.list_fields()

    if not fields:
        raise RuntimeError(
            "No fields found. "
            "Run Phase 4A validation first."
        )

    field = fields[0]

    field_id = field["field_id"]

    print()
    print(
        f"Using Field: "
        f"{field.get('field_name')}"
    )

    print(
        f"Field ID: {field_id}"
    )

    # --------------------------------------------------------
    # HANDLE EXISTING ACTIVE SEASON
    # --------------------------------------------------------

    existing_active = (
        season_manager.get_active_season(
            field_id
        )
    )

    if existing_active is not None:

        print()
        print(
            "Existing active season found:"
        )

        print(
            existing_active.get(
                "season_name"
            )
        )

        print(
            "Completing existing season "
            "for validation..."
        )

        season_manager.complete_season(
            field_id=field_id,
            notes=(
                "Automatically completed "
                "before Phase 4C validation."
            ),
        )

    # --------------------------------------------------------
    # CREATE SEASON 1
    # --------------------------------------------------------

    print()
    print(
        "Creating historical season..."
    )

    season_one = (
        season_manager.create_season(
            field_id=field_id,
            season_name="Kharif 2025",
            crop="Rice",
            current_stage="Harvest",
        )
    )

    print(
        f"Created: "
        f"{season_one['season_name']}"
    )

    # --------------------------------------------------------
    # UPDATE STAGE
    # --------------------------------------------------------

    season_manager.update_crop_stage(
        field_id=field_id,
        new_stage="Post Harvest",
        notes="Harvest completed.",
    )

    # --------------------------------------------------------
    # COMPLETE SEASON
    # --------------------------------------------------------

    completed_season = (
        season_manager.complete_season(
            field_id=field_id,
            notes="Validation season completed.",
        )
    )

    assert (
        completed_season.get("status")
        == STATUS_COMPLETED
    ), "FAIL: Season completion failed."

    print(
        "PASS: Historical season completed."
    )

    # --------------------------------------------------------
    # CREATE ACTIVE SEASON
    # --------------------------------------------------------

    print()
    print(
        "Creating new active season..."
    )

    season_two = (
        season_manager.create_season(
            field_id=field_id,
            season_name="Rabi 2026",
            crop="Wheat",
            current_stage="Vegetative",
        )
    )

    assert (
        season_two.get("status")
        == STATUS_ACTIVE
    ), "FAIL: Active season creation failed."

    print(
        "PASS: New active season created."
    )

    # --------------------------------------------------------
    # VALIDATE ONE ACTIVE SEASON
    # --------------------------------------------------------

    active_season = (
        season_manager.get_active_season(
            field_id
        )
    )

    assert active_season is not None, (
        "FAIL: Active season missing."
    )

    assert (
        active_season.get("crop")
        == "Wheat"
    ), (
        "FAIL: Incorrect active crop."
    )

    print(
        "PASS: One active season maintained."
    )

    # --------------------------------------------------------
    # VALIDATE HISTORY
    # --------------------------------------------------------

    crop_history = (
        season_manager.get_crop_history(
            field_id
        )
    )

    assert len(crop_history) >= 2, (
        "FAIL: Crop history not preserved."
    )

    print()
    print(
        f"Crop history records: "
        f"{len(crop_history)}"
    )

    print(
        "PASS: Crop history preserved."
    )

    # --------------------------------------------------------
    # RESTART SIMULATION
    # --------------------------------------------------------

    print()
    print(
        "Simulating application restart..."
    )

    restarted_storage = StorageManager()

    restarted_registry = (
        FarmFieldRegistry(
            storage=restarted_storage
        )
    )

    restarted_manager = (
        SeasonManager(
            storage=restarted_storage,
            farm_field_registry=(
                restarted_registry
            ),
        )
    )

    reloaded_history = (
        restarted_manager.get_crop_history(
            field_id
        )
    )

    reloaded_active = (
        restarted_manager.get_active_season(
            field_id
        )
    )

    assert len(reloaded_history) >= 2, (
        "FAIL: Season history was not restored."
    )

    assert reloaded_active is not None, (
        "FAIL: Active season was not restored."
    )

    assert (
        reloaded_active.get("crop")
        == "Wheat"
    ), (
        "FAIL: Active season crop "
        "was not restored."
    )

    print(
        "PASS: Season history restored "
        "after restart."
    )

    # --------------------------------------------------------
    # ACTIVE CONTEXT
    # --------------------------------------------------------

    context = (
        restarted_manager.get_active_season_context(
            field_id
        )
    )

    assert (
        context.get("active_season")
        is not None
    ), (
        "FAIL: Active season context missing."
    )

    print(
        "PASS: Backend season context available."
    )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PHASE 4C VALIDATION REPORT")
    print("=" * 70)

    print("[PASS] Multiple seasons per field")
    print("[PASS] One active season per field")
    print("[PASS] Crop stage tracking")
    print("[PASS] Season completion")
    print("[PASS] Crop history preserved")
    print("[PASS] Season data survives restart")
    print("[PASS] Backend active season context")

    print("-" * 70)

    print(
        "PHASE 4C - SEASON MANAGER COMPLETE"
    )

    print("=" * 70)


# ============================================================

# MAIN

# ============================================================

if __name__ == "__main__":
    _run_local_test()
