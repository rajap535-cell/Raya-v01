"""Timeline retrieval and deterministic field-history reasoning."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from persistent_memory.field_activity_log import (
    EVENT_ADVISORY_GENERATED,
    EVENT_DISEASE_OBSERVATION,
    EVENT_FERTILIZER_APPLICATION,
    EVENT_HEAVY_RAINFALL,
    EVENT_IRRIGATION,
    EVENT_SOWING,
    FieldActivityLog,
    get_field_activity_log,
)
from persistent_memory.storage_manager import (
    StorageManager,
    get_storage_manager,
)


class TimelineManager:
    """Provide chronological field history and explainable rules."""

    def __init__(
        self,
        activity_log: Optional[FieldActivityLog] = None,
        storage: Optional[StorageManager] = None,
    ):
        self.activity_log = activity_log or FieldActivityLog(
            storage or get_storage_manager()
        )

    def add_event(self, **event: Any) -> Dict[str, Any]:
        return self.activity_log.add_event(**event)

    def get_field_history(
        self, field_id: str
    ) -> List[Dict[str, Any]]:
        return self.activity_log.get_field_history(field_id)

    def get_recent_history(
        self,
        field_id: str,
        days: int,
        as_of: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        if isinstance(days, bool) or not isinstance(days, int) or days < 0:
            raise ValueError("days must be a non-negative integer.")
        end = self._as_utc(as_of or datetime.now(timezone.utc))
        start = end - timedelta(days=days)
        return [
            event
            for event in self.get_field_history(field_id)
            if start
            <= self._parse_timestamp(event["occurred_at"])
            <= end
        ]

    def get_last_30_days(
        self, field_id: str, as_of: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        return self.get_recent_history(field_id, 30, as_of)

    def get_last_60_days(
        self, field_id: str, as_of: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        return self.get_recent_history(field_id, 60, as_of)

    def build_reasoning_context(
        self,
        field_id: str,
        season_id: Optional[str] = None,
        as_of: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        events = self.get_last_60_days(field_id, as_of)
        seasonal_events = [
            event
            for event in events
            if season_id is None
            or event.get("season_id") in (None, season_id)
        ]
        signals: List[Dict[str, Any]] = []

        fertilizer = [
            event
            for event in seasonal_events
            if event["event_type"] == EVENT_FERTILIZER_APPLICATION
        ]
        rainfall = [
            event
            for event in seasonal_events
            if event["event_type"] == EVENT_HEAVY_RAINFALL
        ]
        for application in fertilizer:
            application_date = self._parse_timestamp(
                application["occurred_at"]
            )
            for rain in rainfall:
                rain_date = self._parse_timestamp(rain["occurred_at"])
                elapsed = rain_date - application_date
                days_after = elapsed.days
                if timedelta(0) <= elapsed <= timedelta(days=7):
                    nutrient = (
                        application.get("details", {}).get("nutrient")
                        or application.get("details", {}).get("product")
                        or "fertilizer"
                    )
                    signals.append(
                        {
                            "rule": "heavy_rain_after_fertilizer",
                            "event_ids": [
                                application["event_id"],
                                rain["event_id"],
                            ],
                            "message": (
                                f"Heavy rainfall occurred {days_after} "
                                f"days after {nutrient} application; "
                                "inspect for nutrient loss before the "
                                "next fertilizer operation."
                            ),
                            "recommendation": {
                                "priority": "High",
                                "action": (
                                    "Inspect the field for nutrient loss "
                                    "before the next fertilizer application"
                                ),
                                "personalization_reasons": [
                                    (
                                        f"Timeline evidence: heavy rainfall "
                                        f"{days_after} days after "
                                        f"{nutrient} application."
                                    )
                                ],
                            },
                        }
                    )

        irrigation = [
            event
            for event in seasonal_events
            if event["event_type"] == EVENT_IRRIGATION
        ]
        recent_irrigation = [
            event
            for event in irrigation
            if self._as_utc(as_of or datetime.now(timezone.utc))
            - self._parse_timestamp(event["occurred_at"])
            <= timedelta(days=7)
        ]
        if len(recent_irrigation) >= 2:
            signals.append(
                {
                    "rule": "repeated_irrigation",
                    "event_ids": [
                        event["event_id"] for event in recent_irrigation
                    ],
                    "message": (
                        f"{len(recent_irrigation)} irrigation events "
                        "occurred within 7 days; review the recent soil "
                        "moisture pattern before irrigating again."
                    ),
                    "recommendation": {
                        "priority": "Medium",
                        "action": (
                            "Review the recent soil moisture pattern "
                            "before the next irrigation"
                        ),
                        "personalization_reasons": [
                            (
                                "Timeline evidence: repeated irrigation "
                                "within 7 days."
                            )
                        ],
                    },
                }
            )

        blast_events = [
            event
            for event in seasonal_events
            if event["event_type"] == EVENT_DISEASE_OBSERVATION
            and (
                season_id is None
                or event.get("season_id") == season_id
            )
            and "blast"
            in " ".join(
                [
                    event.get("title", ""),
                    str(event.get("details", {}).get("disease", "")),
                ]
            ).lower()
        ]
        if blast_events:
            signals.append(
                {
                    "rule": "previous_blast_observation",
                    "event_ids": [
                        event["event_id"] for event in blast_events
                    ],
                    "message": (
                        "A blast disease observation was recorded this "
                        "season; maintain elevated disease monitoring."
                    ),
                    "recommendation": {
                        "priority": "High",
                        "action": (
                            "Increase blast scouting based on the "
                            "previous field observation"
                        ),
                        "personalization_reasons": [
                            (
                                "Timeline evidence: blast was previously "
                                "observed in this season."
                            )
                        ],
                    },
                }
            )

        return {
            "field_id": field_id,
            "season_id": season_id,
            "window_days": 60,
            "events": events,
            "signals": signals,
            "personalization_reasons": [
                signal["message"] for signal in signals
            ],
            "recommendations": [
                signal["recommendation"] for signal in signals
            ],
        }

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return TimelineManager._as_utc(parsed)

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


_default_timeline_manager: Optional[TimelineManager] = None


def get_timeline_manager() -> TimelineManager:
    global _default_timeline_manager
    if _default_timeline_manager is None:
        _default_timeline_manager = TimelineManager(
            activity_log=get_field_activity_log()
        )
    return _default_timeline_manager
