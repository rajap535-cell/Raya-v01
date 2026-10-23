from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from persistent_memory.field_activity_log import (
    EVENT_ADVISORY_GENERATED,
    EVENT_FERTILIZER_APPLICATION,
    EVENT_HEAVY_RAINFALL,
    EVENT_IRRIGATION,
    FieldActivityLog,
)
from persistent_memory.advisory_history import AdvisoryHistory
from persistent_memory.persistent_pipeline import PersistentFarmerPipeline
from persistent_memory.season_manager import SeasonManager
from persistent_memory.storage_manager import StorageManager
from persistent_memory.timeline_manager import TimelineManager


def timestamp_days_ago(days: int) -> str:
    return (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).isoformat()


class FieldTimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = TemporaryDirectory()
        self.storage = StorageManager(
            Path(self.temp_directory.name)
        )
        self.timeline = TimelineManager(
            activity_log=FieldActivityLog(self.storage)
        )
        self.field_id = "FIELD_TEST"
        self.season_id = "SEASON_TEST"

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_events_are_field_scoped_chronological_and_deduplicated(self):
        fertilizer = self.timeline.add_event(
            field_id=self.field_id,
            event_type=EVENT_FERTILIZER_APPLICATION,
            title="Urea applied",
            occurred_at=timestamp_days_ago(8),
            season_id=self.season_id,
            idempotency_key="fertilizer-1",
            details={"nutrient": "nitrogen"},
        )
        duplicate = self.timeline.add_event(
            field_id=self.field_id,
            event_type=EVENT_FERTILIZER_APPLICATION,
            title="Urea applied again",
            occurred_at=timestamp_days_ago(8),
            season_id=self.season_id,
            idempotency_key="fertilizer-1",
        )
        rain = self.timeline.add_event(
            field_id=self.field_id,
            event_type=EVENT_HEAVY_RAINFALL,
            title="Heavy rainfall",
            occurred_at=timestamp_days_ago(4),
            season_id=self.season_id,
            idempotency_key="rain-1",
        )

        self.assertEqual(fertilizer["event_id"], duplicate["event_id"])
        self.assertEqual(
            [fertilizer["event_id"], rain["event_id"]],
            [
                event["event_id"]
                for event in self.timeline.get_field_history(
                    self.field_id
                )
            ],
        )
        self.assertEqual(
            [],
            self.timeline.get_field_history("ANOTHER_FIELD"),
        )

    def test_date_windows_are_inclusive_chronological_and_persistent(self):
        for key, days in (
            ("outside-30", 45),
            ("inside-30", 20),
            ("inside-60", 50),
        ):
            self.timeline.add_event(
                field_id=self.field_id,
                event_type=EVENT_IRRIGATION,
                title=key,
                occurred_at=timestamp_days_ago(days),
                idempotency_key=key,
            )

        restarted = TimelineManager(
            activity_log=FieldActivityLog(
                StorageManager(Path(self.temp_directory.name))
            )
        )
        history = restarted.get_field_history(self.field_id)
        self.assertEqual(
            ["inside-60", "outside-30", "inside-30"],
            [event["title"] for event in history],
        )
        self.assertEqual(
            ["inside-30"],
            [
                event["title"]
                for event in restarted.get_last_30_days(
                    self.field_id
                )
            ],
        )
        self.assertEqual(
            ["inside-60", "outside-30", "inside-30"],
            [
                event["title"]
                for event in restarted.get_last_60_days(
                    self.field_id
                )
            ],
        )

    def test_historical_rules_return_explainable_recommendations(self):
        fertilizer_date = datetime.now(timezone.utc) - timedelta(days=8)
        self.timeline.add_event(
            field_id=self.field_id,
            event_type=EVENT_FERTILIZER_APPLICATION,
            title="Nitrogen applied",
            occurred_at=fertilizer_date.isoformat(),
            season_id=self.season_id,
            idempotency_key="nitrogen",
            details={"nutrient": "nitrogen"},
        )
        self.timeline.add_event(
            field_id=self.field_id,
            event_type=EVENT_HEAVY_RAINFALL,
            title="Heavy rainfall",
            occurred_at=(fertilizer_date + timedelta(days=4)).isoformat(),
            season_id=self.season_id,
            idempotency_key="heavy-rain",
        )
        self.timeline.add_event(
            field_id=self.field_id,
            event_type=EVENT_IRRIGATION,
            title="Irrigation one",
            occurred_at=timestamp_days_ago(3),
            season_id=self.season_id,
            idempotency_key="irrigation-1",
        )
        self.timeline.add_event(
            field_id=self.field_id,
            event_type=EVENT_IRRIGATION,
            title="Irrigation two",
            occurred_at=timestamp_days_ago(2),
            season_id=self.season_id,
            idempotency_key="irrigation-2",
        )
        self.timeline.add_event(
            field_id=self.field_id,
            event_type="disease_observation",
            title="Blast observed",
            occurred_at=timestamp_days_ago(10),
            season_id=self.season_id,
            idempotency_key="blast",
            details={"disease": "blast"},
        )

        context = self.timeline.build_reasoning_context(
            self.field_id,
            season_id=self.season_id,
        )
        rules = {signal["rule"] for signal in context["signals"]}

        self.assertEqual(
            {
                "heavy_rain_after_fertilizer",
                "repeated_irrigation",
                "previous_blast_observation",
            },
            rules,
        )
        self.assertTrue(
            any(
                "4 days after nitrogen application" in reason
                for reason in context["personalization_reasons"]
            )
        )
        self.assertEqual(3, len(context["recommendations"]))

    def test_invalid_event_and_window_are_rejected(self):
        with self.assertRaises(ValueError):
            self.timeline.add_event(
                field_id=self.field_id,
                event_type="unknown",
                title="Invalid event",
            )
        with self.assertRaises(ValueError):
            self.timeline.get_recent_history(self.field_id, -1)

    def test_new_season_records_one_sowing_event(self):
        class ExistingFieldRegistry:
            @staticmethod
            def get_field(field_id, **_kwargs):
                return {"field_id": field_id}

        seasons = SeasonManager(
            storage=self.storage,
            farm_field_registry=ExistingFieldRegistry(),
            timeline_manager=self.timeline,
        )
        season = seasons.create_season(
            field_id=self.field_id,
            season_name="Kharif",
            crop="Rice",
            current_stage="Sowing",
            start_date=timestamp_days_ago(2),
        )
        events = self.timeline.get_field_history(self.field_id)

        self.assertEqual(1, len(events))
        self.assertEqual("sowing", events[0]["event_type"])
        self.assertEqual(season["season_id"], events[0]["season_id"])

    def test_pipeline_records_one_advisory_event_after_success(self):
        farmer = {
            "farmer_id": "FARMER_TEST",
            "name": "Test farmer",
            "state": "Karnataka",
            "district": "Mandya",
        }
        farm = {
            "farm_id": "FARM_TEST",
            "farmer_id": farmer["farmer_id"],
            "state": "Karnataka",
            "district": "Mandya",
        }
        field = {
            "field_id": self.field_id,
            "farm_id": farm["farm_id"],
            "farmer_id": farmer["farmer_id"],
            "state": "Karnataka",
            "district": "Mandya",
        }
        season = {
            "season_id": self.season_id,
            "field_id": self.field_id,
            "crop": "Rice",
            "current_stage": "Flowering",
        }

        class FarmerRegistry:
            @staticmethod
            def get_farmer(_farmer_id):
                return farmer

        class FarmFieldRegistry:
            @staticmethod
            def get_farm(**_kwargs):
                return farm

            @staticmethod
            def get_field(**_kwargs):
                return field

        class SoilMemory:
            @staticmethod
            def get_field_soil_profile(_field_id):
                return {"field_id": self.field_id, "soil_type": "Loamy"}

        class SeasonStore:
            @staticmethod
            def get_active_season(_field_id):
                return season

        calls = []

        def search(**kwargs):
            calls.append(kwargs)
            return {
                "status": "success",
                "location": {
                    "state": "Karnataka",
                    "district": "Mandya",
                },
                "crop": "rice",
                "stage": "Flowering",
            }

        def decision_engine(**kwargs):
            self.assertEqual(
                self.field_id,
                kwargs["timeline_context"]["field_id"],
            )
            return {
                "status": "success",
                "priority": "High",
                "recommendations": [],
                "personalization_reasons": [],
            }

        pipeline = PersistentFarmerPipeline(
            farmer_registry=FarmerRegistry(),
            farm_field_registry=FarmFieldRegistry(),
            soil_memory=SoilMemory(),
            season_manager=SeasonStore(),
            advisory_history=AdvisoryHistory(self.storage),
            timeline_manager=self.timeline,
            search_function=search,
            decision_engine=decision_engine,
        )

        import persistent_memory.persistent_pipeline as pipeline_module

        previous_builder = pipeline_module.build_farmer_context
        pipeline_module.build_farmer_context = (
            lambda **_kwargs: {"status": "active"}
        )
        try:
            result = pipeline.generate_advisory(
                farmer_id=farmer["farmer_id"],
                farm_id=farm["farm_id"],
                field_id=self.field_id,
            )
        finally:
            pipeline_module.build_farmer_context = previous_builder

        self.assertEqual(1, len(calls))
        self.assertEqual(
            EVENT_ADVISORY_GENERATED,
            result["timeline_event"]["event_type"],
        )
        self.assertEqual(
            [EVENT_ADVISORY_GENERATED],
            [
                event["event_type"]
                for event in self.timeline.get_field_history(
                    self.field_id
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
