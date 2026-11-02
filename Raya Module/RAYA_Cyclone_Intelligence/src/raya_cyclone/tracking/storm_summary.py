
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ibtracs_track_metrics.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ibtracs_storm_summaries.csv"
)


# ============================================================
# ACCEPTED TRACK TYPES
# ============================================================

TRACK_TYPES = [
    "main",
    "US-PROVISIONAL",
    "PROVISIONAL",
    "spur-merge",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def ordered_unique(values):
    """Return distinct non-missing values in chronological order."""

    result = []

    for value in values:
        if pd.isna(value):
            continue

        value = str(value)

        if value not in result:
            result.append(value)

    return result


# ============================================================
# INDIVIDUAL STORM SUMMARY
# ============================================================

def summarize_storm(group):
    """Create one historical summary record for one cyclone."""

    group = group.sort_values("timestamp").copy()

    first = group.iloc[0]
    last = group.iloc[-1]

    # Every storm must have exactly one non-missing track type.
    storm_track_types = group["track_type"].dropna().unique()

    if len(storm_track_types) != 1:
        raise ValueError(
            f"Storm {first['storm_id']} has missing or mixed track types."
        )

    storm_track_type = storm_track_types[0]

    # Validate timestamps.
    timestamps = pd.to_datetime(
        group["timestamp"],
        errors="coerce"
    )

    if timestamps.isna().any():
        raise ValueError(
            f"Invalid timestamps found for storm {first['storm_id']}"
        )

    # Storm duration.
    duration_hours = (
        timestamps.iloc[-1] - timestamps.iloc[0]
    ).total_seconds() / 3600

    if duration_hours < 0:
        raise ValueError(
            f"Negative duration found for storm {first['storm_id']}"
        )

    # Consecutive observed segment distances.
    segment_distances = pd.to_numeric(
        group["segment_distance_km"],
        errors="coerce"
    ).dropna()

    # Movement speeds: missing values are excluded, not converted to zero.
    backward_speeds = pd.to_numeric(
        group["derived_speed_kt"],
        errors="coerce"
    ).dropna()

    centred_speeds = pd.to_numeric(
        group["centred_speed_kt"],
        errors="coerce"
    ).dropna()

    # Actual observation intervals.
    observation_intervals = (
        timestamps.diff().dt.total_seconds() / 3600
    ).dropna()

    if (observation_intervals <= 0).any():
        raise ValueError(
            f"Non-positive observation interval found for storm "
            f"{first['storm_id']}"
        )

    # Geographic coverage.
    latitude = pd.to_numeric(
        group["latitude"],
        errors="coerce"
    )

    longitude = pd.to_numeric(
        group["longitude"],
        errors="coerce"
    )

    # Distance to nearest land.
    land_distances = pd.to_numeric(
        group["distance_to_land_km"],
        errors="coerce"
    ).dropna()

    # Basin and subbasin transitions.
    basins = ordered_unique(group["basin"])
    subbasins = ordered_unique(group["subbasin"])

    # Track-type observation counts.
    track_counts = (
        group["track_type"]
        .value_counts(dropna=False)
        .to_dict()
    )

    # Missing coordinate observations.
    missing_coordinate_count = (
        latitude.isna() | longitude.isna()
    ).sum()

    # One summary record per storm.
    return {

        # Identity
        "storm_id": first["storm_id"],
        "season": first["season"],
        "storm_name": first["storm_name"],
        "track_type": storm_track_type,

        # Geography
        "first_basin": first["basin"],
        "last_basin": last["basin"],
        "basins_encountered": "|".join(basins),
        "first_subbasin": first["subbasin"],
        "last_subbasin": last["subbasin"],
        "subbasins_encountered": "|".join(subbasins),

        # Lifetime
        "start_time": timestamps.iloc[0],
        "end_time": timestamps.iloc[-1],
        "duration_hours": duration_hours,
        "observation_count": len(group),

        "mean_observation_interval_hours": (
            observation_intervals.mean()
            if not observation_intervals.empty
            else None
        ),

        # Track characteristics
        "total_track_length_km": segment_distances.sum(),
        "valid_segment_count": len(segment_distances),

        "mean_segment_speed_kt": (
            backward_speeds.mean()
            if not backward_speeds.empty
            else None
        ),

        "max_segment_speed_kt": (
            backward_speeds.max()
            if not backward_speeds.empty
            else None
        ),

        "mean_centred_speed_kt": (
            centred_speeds.mean()
            if not centred_speeds.empty
            else None
        ),

        "max_centred_speed_kt": (
            centred_speeds.max()
            if not centred_speeds.empty
            else None
        ),

        # Geographic coverage
        "min_latitude": latitude.min(),
        "max_latitude": latitude.max(),
        "min_longitude": longitude.min(),
        "max_longitude": longitude.max(),

        # Coastal proximity
        "minimum_distance_to_land_km": (
            land_distances.min()
            if not land_distances.empty
            else None
        ),

        "valid_distance_to_land_count": len(land_distances),

        # Data quality
        "missing_coordinate_count": missing_coordinate_count,
        "missing_basin_count": group["basin"].isna().sum(),

        # Track provenance
        "main_observation_count": track_counts.get("main", 0),

        "us_provisional_observation_count": track_counts.get(
            "US-PROVISIONAL", 0
        ),

        "provisional_observation_count": track_counts.get(
            "PROVISIONAL", 0
        ),

        "spur_merge_observation_count": track_counts.get(
            "spur-merge", 0
        ),

        "missing_track_type_count": group["track_type"].isna().sum(),

        # Valid movement observations
        "valid_backward_speed_count": len(backward_speeds),
        "valid_centred_speed_count": len(centred_speeds),
    }


# ============================================================
# BUILD HISTORICAL STORM SUMMARIES
# ============================================================

def build_storm_summaries():
    """Load track metrics and build historical cyclone summaries."""

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    print("Loading historical track metrics...")

    data = pd.read_csv(
        INPUT_PATH,
        low_memory=False
    )

    # Required input columns.
    required_columns = [
        "storm_id",
        "season",
        "storm_name",
        "timestamp",
        "basin",
        "subbasin",
        "track_type",
        "latitude",
        "longitude",
        "segment_distance_km",
        "derived_speed_kt",
        "centred_speed_kt",
        "distance_to_land_km",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Storm ID validation.
    if data["storm_id"].isna().any():
        raise ValueError("Missing storm IDs found.")

    # Timestamp validation.
    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce"
    )

    if data["timestamp"].isna().any():
        raise ValueError("Invalid timestamps found.")

    # Duplicate observation validation.
    if data.duplicated(["storm_id", "timestamp"]).any():
        raise ValueError(
            "Duplicate storm/timestamp records found."
        )

    # Track type integrity validation.
    if data["track_type"].isna().any():
        raise ValueError(
            "Missing track types found in historical observations."
        )

    observed_track_types = set(
        data["track_type"].unique()
    )

    unexpected_track_types = (
        observed_track_types - set(TRACK_TYPES)
    )

    if unexpected_track_types:
        raise ValueError(
            f"Unexpected track types found: "
            f"{sorted(unexpected_track_types)}"
        )

    # Confirm that each storm belongs to exactly one track type.
    track_type_counts = (
        data.groupby("storm_id")["track_type"].nunique()
    )

    mixed_track_storms = track_type_counts[
        track_type_counts != 1
    ]

    if not mixed_track_storms.empty:
        raise ValueError(
            "Storms with missing or mixed track types found: "
            f"{mixed_track_storms.index.tolist()}"
        )

    print("Track type validation: passed")

    # Generate one summary per storm.
    print("Generating one summary per storm...")

    summaries = []

    for storm_id, group in data.groupby(
        "storm_id",
        sort=True,
        dropna=False
    ):
        summaries.append(
            summarize_storm(group)
        )

    summary_df = pd.DataFrame(summaries)

    # Summary uniqueness validation.
    if summary_df["storm_id"].duplicated().any():
        raise ValueError(
            "Duplicate storm summaries generated."
        )

    # Verify that every input storm has a summary.
    if summary_df["storm_id"].nunique() != data["storm_id"].nunique():
        raise ValueError(
            "Storm summary count does not match input storm count."
        )

    # Verify that all observations are accounted for.
    if int(summary_df["observation_count"].sum()) != len(data):
        raise ValueError(
            "Observation count reconciliation failed."
        )

    # Sort final summaries.
    summary_df = summary_df.sort_values(
        ["season", "storm_id"]
    ).reset_index(drop=True)

    # Save processed output.
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    summary_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\nSTORM SUMMARY REPORT")
    print("--------------------")

    print("Input observations:", len(data))
    print("Unique storm IDs:", data["storm_id"].nunique())
    print("Summary records:", len(summary_df))

    print(
        "Observation count reconciled:",
        int(summary_df["observation_count"].sum()) == len(data)
    ) 

    print("Track type validation: passed")
    print("Output:", OUTPUT_PATH)

    print("\nTRACK TYPE DISTRIBUTION")
    print("-----------------------")

    print(
        summary_df.groupby("track_type").agg(
            storm_count=("storm_id", "nunique"),
            observation_count=("observation_count", "sum"),
        ).to_string()
    )

    print("\nSUMMARY STATISTICS")
    print("------------------")

    print(
        summary_df[
            [
                "duration_hours",
                "observation_count",
                "total_track_length_km",
                "mean_segment_speed_kt",
                "max_segment_speed_kt",
            ]
        ].describe().round(2)
    )

    print("\nFIRST FIVE STORM SUMMARIES")
    print("--------------------------")

    print(
        summary_df[
            [
                "storm_id",
                "season",
                "storm_name",
                "track_type",
                "observation_count",
                "duration_hours",
                "total_track_length_km",
                "basins_encountered",
                "subbasins_encountered",
            ]
        ].head().to_string(index=False)
    )

    return summary_df


if __name__ == "__main__":
    build_storm_summaries()
