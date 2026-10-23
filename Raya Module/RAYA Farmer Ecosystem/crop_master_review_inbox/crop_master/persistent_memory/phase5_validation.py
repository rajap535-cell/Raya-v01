"""Runtime validation for persistent field timelines and history reasoning."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from contextual_decision_engine import generate_contextual_advisory
from farmer_search_engine import farmer_search
from persistent_memory.field_activity_log import (
    EVENT_DISEASE_OBSERVATION,
    EVENT_FERTILIZER_APPLICATION,
    EVENT_HEAVY_RAINFALL,
    EVENT_IRRIGATION,
    FieldActivityLog,
)
from persistent_memory.storage_manager import StorageManager
from persistent_memory.timeline_manager import TimelineManager


def _days_ago(days: int) -> str:
    return (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).isoformat()


def run_validation() -> dict:
    with TemporaryDirectory(prefix="raya_phase5_") as directory:
        storage = StorageManager(Path(directory))
        timeline = TimelineManager(
            activity_log=FieldActivityLog(storage)
        )
        field_id = "FIELD_PHASE5_VALIDATION"
        season_id = "SEASON_PHASE5_VALIDATION"

        fertilizer_date = datetime.now(timezone.utc) - timedelta(days=8)
        timeline.add_event(
            field_id=field_id,
            event_type=EVENT_FERTILIZER_APPLICATION,
            title="Nitrogen fertilizer applied",
            occurred_at=fertilizer_date.isoformat(),
            season_id=season_id,
            idempotency_key="validation:nitrogen",
            details={"nutrient": "nitrogen"},
        )
        timeline.add_event(
            field_id=field_id,
            event_type=EVENT_HEAVY_RAINFALL,
            title="Heavy rainfall",
            occurred_at=(fertilizer_date + timedelta(days=4)).isoformat(),
            season_id=season_id,
            idempotency_key="validation:rain",
        )
        for key, days in (("irrigation-1", 3), ("irrigation-2", 2)):
            timeline.add_event(
                field_id=field_id,
                event_type=EVENT_IRRIGATION,
                title="Irrigation recorded",
                occurred_at=_days_ago(days),
                season_id=season_id,
                idempotency_key=f"validation:{key}",
            )
        timeline.add_event(
            field_id=field_id,
            event_type=EVENT_DISEASE_OBSERVATION,
            title="Blast observed",
            occurred_at=_days_ago(10),
            season_id=season_id,
            idempotency_key="validation:blast",
            details={"disease": "blast"},
        )

        duplicate = timeline.add_event(
            field_id=field_id,
            event_type=EVENT_FERTILIZER_APPLICATION,
            title="Duplicate should not be added",
            occurred_at=fertilizer_date.isoformat(),
            season_id=season_id,
            idempotency_key="validation:nitrogen",
        )
        assert len(timeline.get_field_history(field_id)) == 5
        assert duplicate["title"] == "Nitrogen fertilizer applied"

        restarted_timeline = TimelineManager(
            activity_log=FieldActivityLog(
                StorageManager(Path(directory))
            )
        )
        history = restarted_timeline.get_field_history(field_id)
        assert len(history) == 5
        assert [
            event["occurred_at"] for event in history
        ] == sorted(event["occurred_at"] for event in history)
        assert len(restarted_timeline.get_last_30_days(field_id)) == 5
        assert len(restarted_timeline.get_last_60_days(field_id)) == 5

        reasoning = restarted_timeline.build_reasoning_context(
            field_id,
            season_id=season_id,
        )
        assert {
            "heavy_rain_after_fertilizer",
            "repeated_irrigation",
            "previous_blast_observation",
        } == {signal["rule"] for signal in reasoning["signals"]}

        packet = farmer_search(
            state="Karnataka",
            district="Mandya",
            crop="rice",
            stage="flowering",
        )
        if packet.get("status") != "success":
            raise RuntimeError(
                "Farmer Search failed during Phase 5 validation: "
                f"{packet.get('message', packet)}"
            )

        baseline = generate_contextual_advisory(
            crop="rice",
            stage="flowering",
            state="Karnataka",
            district="Mandya",
            agricultural_packet=packet,
            timeline_context={
                "field_id": field_id,
                "season_id": season_id,
                "signals": [],
                "recommendations": [],
                "personalization_reasons": [],
            },
        )
        history_aware = generate_contextual_advisory(
            crop="rice",
            stage="flowering",
            state="Karnataka",
            district="Mandya",
            agricultural_packet=packet,
            timeline_context=reasoning,
        )
        if (
            baseline.get("status") != "success"
            or history_aware.get("status") != "success"
        ):
            raise RuntimeError(
                "Contextual advisory generation failed during validation."
            )

        baseline_actions = {
            item.get("action")
            for item in baseline.get("recommendations", [])
        }
        timeline_actions = {
            item.get("action")
            for item in history_aware.get("recommendations", [])
        }
        different_reasons = (
            baseline.get("personalization_reasons")
            != history_aware.get("personalization_reasons")
        )
        assert timeline_actions - baseline_actions
        assert different_reasons

        return {
            "status": "PASS",
            "field_id": field_id,
            "event_count_after_deduplication": len(history),
            "last_30_days_count": len(
                restarted_timeline.get_last_30_days(field_id)
            ),
            "last_60_days_count": len(
                restarted_timeline.get_last_60_days(field_id)
            ),
            "temporal_rules": [
                signal["rule"] for signal in reasoning["signals"]
            ],
            "timeline_recommendations": sorted(
                timeline_actions - baseline_actions
            ),
            "timeline_reasons": history_aware[
                "personalization_reasons"
            ],
        }


if __name__ == "__main__":
    import json

    print(json.dumps(run_validation(), indent=2))
