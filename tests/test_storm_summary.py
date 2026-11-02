
# test_storm_summary.py

import unittest

import pandas as pd

from raya_cyclone.tracking.storm_summary import summarize_storm


def make_observation(
    timestamp,
    basin="NI",
    subbasin="BB",
    track_type="main",
    segment_distance_km=None,
    derived_speed_kt=None,
    centred_speed_kt=None,
):
    """Create a minimal observation for summary tests."""

    return {
        "storm_id": "TEST_STORM",
        "season": 2020,
        "storm_name": "TEST",
        "timestamp": pd.Timestamp(timestamp),
        "basin": basin,
        "subbasin": subbasin,
        "track_type": track_type,
        "latitude": 15.0,
        "longitude": 85.0,
        "segment_distance_km": segment_distance_km,
        "derived_speed_kt": derived_speed_kt,
        "centred_speed_kt": centred_speed_kt,
        "distance_to_land_km": 50.0,
    }


class TestStormSummary(unittest.TestCase):

    def test_single_observation_storm(self):
        """A one-observation storm has zero duration and no movement."""

        data = pd.DataFrame([
            make_observation("2020-05-01 00:00:00")
        ])

        result = summarize_storm(data)

        self.assertEqual(result["observation_count"], 1)
        self.assertEqual(result["duration_hours"], 0)
        self.assertEqual(result["total_track_length_km"], 0)
        self.assertIsNone(result["max_segment_speed_kt"])
        self.assertEqual(result["valid_segment_count"], 0)
        self.assertEqual(result["track_type"], "main")
        self.assertEqual(result["main_observation_count"], 1)

    def test_track_length_and_geographical_transition(self):
        """Track length and subbasin transitions are preserved."""

        data = pd.DataFrame([
            make_observation(
                "2020-05-01 00:00:00",
                subbasin="BB",
            ),
            make_observation(
                "2020-05-01 03:00:00",
                subbasin="BB",
                segment_distance_km=10.0,
                derived_speed_kt=5.0,
                track_type="main",
            ),
            make_observation(
                "2020-05-01 06:00:00",
                subbasin="AS",
                segment_distance_km=20.0,
                derived_speed_kt=8.0,
                track_type="main",
            ),
        ])

        result = summarize_storm(data)

        self.assertEqual(result["observation_count"], 3)
        self.assertEqual(result["duration_hours"], 6)

        self.assertAlmostEqual(
            result["total_track_length_km"], 30.0
        )

        self.assertEqual(result["first_subbasin"], "BB")
        self.assertEqual(result["last_subbasin"], "AS")

        self.assertEqual(
            result["subbasins_encountered"], "BB|AS"
        )

        self.assertEqual(result["track_type"], "main")
        self.assertEqual(result["main_observation_count"], 3)
        self.assertEqual(result["provisional_observation_count"], 0)

    def test_missing_speeds_are_not_treated_as_zero(self):
        """Only valid speed values contribute to speed statistics."""

        data = pd.DataFrame([
            make_observation("2020-05-01 00:00:00"),

            make_observation(
                "2020-05-01 03:00:00",
                segment_distance_km=10.0,
                derived_speed_kt=6.0,
                centred_speed_kt=8.0,
            ),

            make_observation(
                "2020-05-01 06:00:00",
                segment_distance_km=15.0,
                derived_speed_kt=None,
                centred_speed_kt=10.0,
            ),
        ])

        result = summarize_storm(data)

        self.assertEqual(result["valid_backward_speed_count"], 1)
        self.assertEqual(result["valid_centred_speed_count"], 2)

        self.assertAlmostEqual(
            result["mean_segment_speed_kt"], 6.0
        )

        self.assertAlmostEqual(
            result["max_segment_speed_kt"], 6.0
        )

        self.assertAlmostEqual(
            result["mean_centred_speed_kt"], 9.0
        )

        self.assertAlmostEqual(
            result["max_centred_speed_kt"], 10.0
        )


if __name__ == "__main__":
    unittest.main()
