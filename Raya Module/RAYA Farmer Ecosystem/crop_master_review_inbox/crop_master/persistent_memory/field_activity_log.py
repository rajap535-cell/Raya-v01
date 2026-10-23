"""Persistent, field-scoped activity events for agricultural timelines."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from persistent_memory.storage_manager import (
    StorageManager,
    get_storage_manager,
)

FIELD_ACTIVITY_ENTITY_TYPE = "field_activity"
FIELD_ACTIVITY_ID_FIELD = "event_id"

EVENT_SOWING = "sowing"
EVENT_IRRIGATION = "irrigation"
EVENT_FERTILIZER_APPLICATION = "fertilizer_application"
EVENT_HEAVY_RAINFALL = "heavy_rainfall"
EVENT_DISEASE_OBSERVATION = "disease_observation"
EVENT_HARVEST = "harvest"
EVENT_ADVISORY_GENERATED = "advisory_generated"

VALID_EVENT_TYPES = {
    EVENT_SOWING,
    EVENT_IRRIGATION,
    EVENT_FERTILIZER_APPLICATION,
    EVENT_HEAVY_RAINFALL,
    EVENT_DISEASE_OBSERVATION,
    EVENT_HARVEST,
    EVENT_ADVISORY_GENERATED,
}


class FieldActivityLog:
    """Write and retrieve durable events belonging to one field."""

    def __init__(self, storage: Optional[StorageManager] = None):
        self.storage = storage or get_storage_manager()

    def add_event(
        self,
        field_id: str,
        event_type: str,
        title: str,
        occurred_at: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        season_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        field_id = self._required_text(field_id, "field_id")
        event_type = self._required_text(
            event_type, "event_type"
        ).lower()
        if event_type not in VALID_EVENT_TYPES:
            raise ValueError(
                f"Unsupported event_type {event_type!r}. "
                f"Supported: {sorted(VALID_EVENT_TYPES)}"
            )

        title = self._required_text(title, "title")
        if details is not None and not isinstance(details, dict):
            raise TypeError("details must be a dictionary.")

        timestamp = self._normalize_timestamp(occurred_at)
        key = self._required_text(
            idempotency_key or self.storage.generate_id("ACTIVITY"),
            "idempotency_key",
        )
        record = {
            "event_id": self.storage.generate_id("EVENT"),
            "field_id": field_id,
            "event_type": event_type,
            "title": title,
            "occurred_at": timestamp,
            "season_id": season_id,
            "idempotency_key": f"{field_id}:{key}",
            "details": dict(details or {}),
            "created_at": self.storage.utc_timestamp(),
        }
        saved, _created = self.storage.insert_if_unique(
            FIELD_ACTIVITY_ENTITY_TYPE,
            record,
            "idempotency_key",
        )
        return saved

    def get_field_history(
        self, field_id: str
    ) -> List[Dict[str, Any]]:
        field_id = self._required_text(field_id, "field_id")
        events = [
            event
            for event in self.storage.read_all(
                FIELD_ACTIVITY_ENTITY_TYPE
            )
            if event.get("field_id") == field_id
        ]
        return self._sort_chronologically(events)

    @classmethod
    def _sort_chronologically(
        cls, events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return sorted(
            events,
            key=lambda event: (
                cls._parse_timestamp(event["occurred_at"]),
                str(event.get("event_id", "")),
            ),
        )

    @staticmethod
    def _required_text(value: Any, name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string.")
        return value.strip()

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid event timestamp: {value!r}"
            ) from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @classmethod
    def _normalize_timestamp(
        cls, value: Optional[str]
    ) -> str:
        parsed = (
            datetime.now(timezone.utc)
            if value is None
            else cls._parse_timestamp(value)
        )
        return parsed.isoformat()


_default_field_activity_log: Optional[FieldActivityLog] = None


def get_field_activity_log() -> FieldActivityLog:
    global _default_field_activity_log
    if _default_field_activity_log is None:
        _default_field_activity_log = FieldActivityLog()
    return _default_field_activity_log
