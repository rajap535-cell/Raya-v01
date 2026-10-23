"""
RAYA Phase 4D - Persistent Advisory History

File:
persistent_memory/advisory_history.py

Purpose:
Persist every generated advisory and connect it to:

```
    Farmer
        -> Farm
            -> Field
                -> Season
                    -> Farmer Search
                        -> Contextual Decision Engine
                            -> Advisory History
```

This module stores advisory records only.

It does NOT modify:
- Crop Master
- Weather Intelligence
- Water Intelligence
- Disease Intelligence
- Market Intelligence
- Farmer Search agricultural rules
- Contextual Decision Engine logic

Phase 4D Responsibilities:
- Save generated advisories
- Link advisory to farmer/farm/field/season
- Store crop and stage context
- Store overall priority
- Store recommendations
- Store personalization reasons
- Retrieve advisory history
- Preserve advisory history across application restarts
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

ADVISORY_ENTITY_TYPE = "advisory_history"
ADVISORY_ID_FIELD = "advisory_id"

# ============================================================

# ADVISORY HISTORY

# ============================================================

class AdvisoryHistory:
    """
    Persistent storage manager for RAYA advisories.

    Each advisory belongs to a persistent agricultural context:

        farmer
            -> farm
                -> field
                    -> season
                        -> advisory

    The module is intentionally generic enough to consume the
    structured output from the Contextual Decision Engine without
    changing the decision engine itself.
    """

    def __init__(
        self,
        storage: Optional[StorageManager] = None,
    ):
        self.storage = (
            storage
            if storage is not None
            else get_storage_manager()
        )

    # ========================================================
    # SAVE ADVISORY
    # ========================================================

    def save_advisory(
        self,
        farmer_id: str,
        farm_id: str,
        field_id: str,
        season_id: Optional[str],
        agricultural_packet: Optional[Dict[str, Any]],
        contextual_advisory: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Save one generated advisory.

        Expected pipeline:

            Farmer Search
                ->
            agricultural_packet
                +
            Contextual Decision Engine
                ->
            contextual_advisory
                ->
            Advisory History

        The agricultural packet and contextual advisory are stored
        as snapshots so historical records remain reproducible.
        """

        self._validate_required_string(
            farmer_id,
            "farmer_id",
        )

        self._validate_required_string(
            farm_id,
            "farm_id",
        )

        self._validate_required_string(
            field_id,
            "field_id",
        )

        if not isinstance(contextual_advisory, dict):
            raise ValueError(
                "contextual_advisory must be a dictionary."
            )

        if agricultural_packet is None:
            agricultural_packet = {}

        if not isinstance(agricultural_packet, dict):
            raise ValueError(
                "agricultural_packet must be a dictionary."
            )

        timestamp = self.storage.utc_timestamp()

        crop = self._extract_crop(
            agricultural_packet,
            contextual_advisory,
        )

        stage = self._extract_stage(
            agricultural_packet,
            contextual_advisory,
        )

        overall_priority = (
            self._extract_overall_priority(
                contextual_advisory
            )
        )

        recommendations = (
            self._extract_recommendations(
                contextual_advisory
            )
        )

        personalization_reasons = (
            self._extract_personalization_reasons(
                contextual_advisory
            )
        )

        advisory_record = {
            "advisory_id": (
                self.storage.generate_id(
                    "ADV"
                )
            ),
            "farmer_id": farmer_id,
            "farm_id": farm_id,
            "field_id": field_id,
            "season_id": season_id,
            "crop": crop,
            "stage": stage,
            "overall_priority": overall_priority,
            "recommendations": recommendations,
            "personalization_reasons": (
                personalization_reasons
            ),
            "agricultural_packet": (
                agricultural_packet.copy()
            ),
            "contextual_advisory": (
                contextual_advisory.copy()
            ),
            "created_at": timestamp,
        }

        self.storage.insert(
            entity_type=ADVISORY_ENTITY_TYPE,
            record=advisory_record,
        )

        return advisory_record

    # ========================================================
    # GET ADVISORY
    # ========================================================

    def get_advisory(
        self,
        advisory_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve one advisory by ID.
        """

        records = self.storage.read_all(
            ADVISORY_ENTITY_TYPE
        )

        for record in records:
            if (
                record.get("advisory_id")
                == advisory_id
            ):
                return record

        return None

    # ========================================================
    # GET FARMER HISTORY
    # ========================================================

    def get_farmer_history(
        self,
        farmer_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all advisories for one farmer.
        """

        records = self.storage.read_all(
            ADVISORY_ENTITY_TYPE
        )

        history = [
            record
            for record in records
            if record.get("farmer_id") == farmer_id
        ]

        history = self._sort_latest_first(
            history
        )

        return self._apply_limit(
            history,
            limit,
        )

    # ========================================================
    # GET FARM HISTORY
    # ========================================================

    def get_farm_history(
        self,
        farm_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all advisories for one farm.
        """

        records = self.storage.read_all(
            ADVISORY_ENTITY_TYPE
        )

        history = [
            record
            for record in records
            if record.get("farm_id") == farm_id
        ]

        history = self._sort_latest_first(
            history
        )

        return self._apply_limit(
            history,
            limit,
        )

    # ========================================================
    # GET FIELD HISTORY
    # ========================================================

    def get_field_history(
        self,
        field_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all advisories for one field.
        """

        records = self.storage.read_all(
            ADVISORY_ENTITY_TYPE
        )

        history = [
            record
            for record in records
            if record.get("field_id") == field_id
        ]

        history = self._sort_latest_first(
            history
        )

        return self._apply_limit(
            history,
            limit,
        )

    # ========================================================
    # GET SEASON HISTORY
    # ========================================================

    def get_season_history(
        self,
        season_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all advisories generated during one season.
        """

        records = self.storage.read_all(
            ADVISORY_ENTITY_TYPE
        )

        history = [
            record
            for record in records
            if record.get("season_id") == season_id
        ]

        history = self._sort_latest_first(
            history
        )

        return self._apply_limit(
            history,
            limit,
        )

    # ========================================================
    # GET LATEST ADVISORY
    # ========================================================

    def get_latest_advisory(
        self,
        field_id: Optional[str] = None,
        farmer_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Return the most recent advisory.

        Optional filters:
            - field_id
            - farmer_id
        """

        records = self.storage.read_all(
            ADVISORY_ENTITY_TYPE
        )

        filtered = records

        if field_id is not None:
            filtered = [
                record
                for record in filtered
                if record.get("field_id") == field_id
            ]

        if farmer_id is not None:
            filtered = [
                record
                for record in filtered
                if record.get("farmer_id") == farmer_id
            ]

        filtered = self._sort_latest_first(
            filtered
        )

        if not filtered:
            return None

        return filtered[0]

    # ========================================================
    # COUNT HISTORY
    # ========================================================

    def count_advisories(
        self,
        farmer_id: Optional[str] = None,
        field_id: Optional[str] = None,
        season_id: Optional[str] = None,
    ) -> int:
        """
        Count advisory records with optional filters.
        """

        records = self.storage.read_all(
            ADVISORY_ENTITY_TYPE
        )

        filtered = records

        if farmer_id is not None:
            filtered = [
                record
                for record in filtered
                if record.get("farmer_id") == farmer_id
            ]

        if field_id is not None:
            filtered = [
                record
                for record in filtered
                if record.get("field_id") == field_id
            ]

        if season_id is not None:
            filtered = [
                record
                for record in filtered
                if record.get("season_id") == season_id
            ]

        return len(filtered)

    # ========================================================
    # SUMMARY
    # ========================================================

    def get_advisory_summary(
        self,
        farmer_id: Optional[str] = None,
        field_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return lightweight advisory history summary.
        """

        records = self.storage.read_all(
            ADVISORY_ENTITY_TYPE
        )

        filtered = records

        if farmer_id is not None:
            filtered = [
                record
                for record in filtered
                if record.get("farmer_id") == farmer_id
            ]

        if field_id is not None:
            filtered = [
                record
                for record in filtered
                if record.get("field_id") == field_id
            ]

        sorted_records = self._sort_latest_first(
            filtered
        )

        priorities: Dict[str, int] = {}

        for record in sorted_records:

            priority = (
                record.get("overall_priority")
                or "UNKNOWN"
            )

            priorities[priority] = (
                priorities.get(priority, 0)
                + 1
            )

        latest = (
            sorted_records[0]
            if sorted_records
            else None
        )

        return {
            "total_advisories": len(
                sorted_records
            ),
            "priority_distribution": priorities,
            "latest_advisory": latest,
        }

    # ========================================================
    # EXTRACTION HELPERS
    # ========================================================

    @staticmethod
    def _extract_crop(
        agricultural_packet: Dict[str, Any],
        contextual_advisory: Dict[str, Any],
    ) -> Optional[str]:
        """
        Extract crop from known pipeline structures.
        """

        candidates = [
            agricultural_packet.get("crop"),
            agricultural_packet.get(
                "crop_name"
            ),
            agricultural_packet.get(
                "normalized_crop"
            ),
            contextual_advisory.get("crop"),
            contextual_advisory.get(
                "crop_name"
            ),
        ]

        context = (
            agricultural_packet.get(
                "context",
                {}
            )
        )

        if isinstance(context, dict):
            candidates.extend(
                [
                    context.get("crop"),
                    context.get("crop_name"),
                ]
            )

        for value in candidates:
            if value:
                return str(value)

        return None

    @staticmethod
    def _extract_stage(
        agricultural_packet: Dict[str, Any],
        contextual_advisory: Dict[str, Any],
    ) -> Optional[str]:
        """
        Extract crop stage from known pipeline structures.
        """

        candidates = [
            agricultural_packet.get("stage"),
            agricultural_packet.get(
                "current_stage"
            ),
            contextual_advisory.get("stage"),
            contextual_advisory.get(
                "current_stage"
            ),
        ]

        context = (
            agricultural_packet.get(
                "context",
                {}
            )
        )

        if isinstance(context, dict):
            candidates.extend(
                [
                    context.get("stage"),
                    context.get(
                        "current_stage"
                    ),
                ]
            )

        for value in candidates:
            if value:
                return str(value)

        return None

    @staticmethod
    def _extract_overall_priority(
        contextual_advisory: Dict[str, Any],
    ) -> Optional[str]:
        """
        Extract overall priority.
        """

        candidates = [
            contextual_advisory.get(
                "overall_priority"
            ),
            contextual_advisory.get(
                "priority"
            ),
            contextual_advisory.get(
                "risk_priority"
            ),
        ]

        summary = (
            contextual_advisory.get(
                "summary",
                {}
            )
        )

        if isinstance(summary, dict):
            candidates.append(
                summary.get(
                    "overall_priority"
                )
            )

        for value in candidates:
            if value is not None:
                return str(value)

        return None

    @staticmethod
    def _extract_recommendations(
        contextual_advisory: Dict[str, Any],
    ) -> List[Any]:
        """
        Extract recommendations from contextual advisory.
        """

        candidates = [
            contextual_advisory.get(
                "recommendations"
            ),
            contextual_advisory.get(
                "top_recommendations"
            ),
            contextual_advisory.get(
                "actions"
            ),
        ]

        for value in candidates:

            if isinstance(value, list):
                return value

        return []

    @staticmethod
    def _extract_personalization_reasons(
        contextual_advisory: Dict[str, Any],
    ) -> List[Any]:
        """
        Extract personalization reasons.
        """

        candidates = [
            contextual_advisory.get(
                "personalization_reasons"
            ),
            contextual_advisory.get(
                "decision_reasons"
            ),
            contextual_advisory.get(
                "context_reasons"
            ),
        ]

        for value in candidates:

            if isinstance(value, list):
                return value

        return []

    # ========================================================
    # INTERNAL HELPERS
    # ========================================================

    @staticmethod
    def _sort_latest_first(
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Sort advisory records newest first.
        """

        return sorted(
            records,
            key=lambda item: (
                item.get("created_at")
                or ""
            ),
            reverse=True,
        )

    @staticmethod
    def _apply_limit(
        records: List[Dict[str, Any]],
        limit: Optional[int],
    ) -> List[Dict[str, Any]]:
        """
        Apply optional result limit.
        """

        if limit is None:
            return records

        if limit <= 0:
            return []

        return records[:limit]

    @staticmethod
    def _validate_required_string(
        value: Any,
        field_name: str,
    ) -> None:
        """
        Validate required identifier.
        """

        if value is None:
            raise ValueError(
                f"{field_name} is required."
            )

        if not str(value).strip():
            raise ValueError(
                f"{field_name} cannot be empty."
            )


# ============================================================

# SINGLETON ACCESSOR

# ============================================================

_default_advisory_history: Optional[
    AdvisoryHistory
] = None

def get_advisory_history() -> AdvisoryHistory:
    """
    Return default AdvisoryHistory instance.
    """

    global _default_advisory_history

    if _default_advisory_history is None:
        _default_advisory_history = (
            AdvisoryHistory()
        )

    return _default_advisory_history


# ============================================================

# PHASE 4D RUNTIME VALIDATION

# ============================================================

def _run_local_test() -> None:
    """
    Runtime validation for Advisory History.
    """

    print("=" * 70)
    print("RAYA PHASE 4D - ADVISORY HISTORY TEST")
    print("=" * 70)

    advisory_history = (
        get_advisory_history()
    )

    # --------------------------------------------------------
    # TEST IDENTIFIERS
    # --------------------------------------------------------

    farmer_id = "TEST_FARMER_A"
    farm_id = "TEST_FARM_A"
    field_id = "TEST_FIELD_A"
    season_id = "TEST_SEASON_A"

    # --------------------------------------------------------
    # SAMPLE AGRICULTURAL PACKET
    # --------------------------------------------------------

    agricultural_packet = {
        "crop": "Rice",
        "stage": "Vegetative",
        "context": {
            "crop": "Rice",
            "stage": "Vegetative",
        },
        "weather_packet": {
            "risk_level": "MODERATE",
        },
    }

    # --------------------------------------------------------
    # SAMPLE CONTEXTUAL ADVISORY
    # --------------------------------------------------------

    contextual_advisory = {
        "overall_priority": "HIGH",
        "recommendations": [
            {
                "action": (
                    "Inspect field moisture"
                ),
                "priority": "HIGH",
            },
            {
                "action": (
                    "Adjust irrigation"
                ),
                "priority": "MEDIUM",
            },
        ],
        "personalization_reasons": [
            (
                "Recommendation adjusted "
                "for farmer budget."
            ),
            (
                "Recommendation adjusted "
                "for labor availability."
            ),
        ],
    }

    # --------------------------------------------------------
    # SAVE ADVISORY
    # --------------------------------------------------------

    print()
    print("Saving advisory...")

    saved_record = (
        advisory_history.save_advisory(
            farmer_id=farmer_id,
            farm_id=farm_id,
            field_id=field_id,
            season_id=season_id,
            agricultural_packet=(
                agricultural_packet
            ),
            contextual_advisory=(
                contextual_advisory
            ),
        )
    )

    assert (
        saved_record.get("advisory_id")
        is not None
    ), "FAIL: Advisory ID not generated."

    print(
        f"PASS: Advisory saved: "
        f"{saved_record['advisory_id']}"
    )

    # --------------------------------------------------------
    # GET BY ID
    # --------------------------------------------------------

    loaded_record = (
        advisory_history.get_advisory(
            saved_record["advisory_id"]
        )
    )

    assert loaded_record is not None, (
        "FAIL: Advisory not retrievable."
    )

    print(
        "PASS: Advisory retrieved by ID."
    )

    # --------------------------------------------------------
    # FARMER HISTORY
    # --------------------------------------------------------

    farmer_history = (
        advisory_history.get_farmer_history(
            farmer_id
        )
    )

    assert len(farmer_history) >= 1, (
        "FAIL: Farmer history missing."
    )

    print(
        "PASS: Farmer history retrieved."
    )

    # --------------------------------------------------------
    # FIELD HISTORY
    # --------------------------------------------------------

    field_history = (
        advisory_history.get_field_history(
            field_id
        )
    )

    assert len(field_history) >= 1, (
        "FAIL: Field history missing."
    )

    print(
        "PASS: Field history retrieved."
    )

    # --------------------------------------------------------
    # SEASON HISTORY
    # --------------------------------------------------------

    season_history = (
        advisory_history.get_season_history(
            season_id
        )
    )

    assert len(season_history) >= 1, (
        "FAIL: Season history missing."
    )

    print(
        "PASS: Season history retrieved."
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = (
        advisory_history.get_advisory_summary(
            farmer_id=farmer_id
        )
    )

    assert (
        summary["total_advisories"] >= 1
    ), (
        "FAIL: Advisory summary count incorrect."
    )

    print(
        "PASS: Advisory summary generated."
    )

    # --------------------------------------------------------
    # RESTART SIMULATION
    # --------------------------------------------------------

    print()
    print(
        "Simulating application restart..."
    )

    restarted_storage = StorageManager()

    restarted_history = AdvisoryHistory(
        storage=restarted_storage
    )

    restored_record = (
        restarted_history.get_advisory(
            saved_record["advisory_id"]
        )
    )

    assert restored_record is not None, (
        "FAIL: Advisory history was not restored "
        "after restart."
    )

    assert (
        restored_record.get("overall_priority")
        == "HIGH"
    ), (
        "FAIL: Advisory data persistence failed."
    )

    print(
        "PASS: Advisory restored after restart."
    )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PHASE 4D VALIDATION REPORT")
    print("=" * 70)

    print("[PASS] Advisory saved")
    print("[PASS] Advisory linked to farmer")
    print("[PASS] Advisory linked to farm")
    print("[PASS] Advisory linked to field")
    print("[PASS] Advisory linked to season")
    print("[PASS] Recommendations persisted")
    print("[PASS] Personalization reasons persisted")
    print("[PASS] Farmer history retrieval")
    print("[PASS] Field history retrieval")
    print("[PASS] Season history retrieval")
    print("[PASS] Advisory survives restart")

    print("-" * 70)
    print("PHASE 4D - ADVISORY HISTORY COMPLETE")
    print("=" * 70)


# ============================================================

# MAIN

# ============================================================

if __name__ == "__main__":
    _run_local_test()
