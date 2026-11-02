
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ibtracs_ni_observations.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ibtracs_track_metrics.csv"
)


# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

EARTH_RADIUS_KM = 6371.0088

KM_PER_NAUTICAL_MILE = 1.852


# --------------------------------------------------
# HAVERSINE DISTANCE
# --------------------------------------------------

def calculate_haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2,
):
    """
    Calculate great-circle distance between
    two geographic coordinates.

    Returns distance in kilometres.
    """

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(delta_lon / 2) ** 2
    )

    a = np.clip(a, 0.0, 1.0)

    central_angle = 2 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1 - a),
    )

    return EARTH_RADIUS_KM * central_angle


# --------------------------------------------------
# INITIAL BEARING
# --------------------------------------------------

def calculate_initial_bearing(
    lat1,
    lon1,
    lat2,
    lon2,
):
    """
    Calculate initial bearing from the first
    coordinate to the second.

    Bearing is measured clockwise from true north.
    """

    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)

    delta_lon = np.radians(lon2 - lon1)

    y = (
        np.sin(delta_lon)
        * np.cos(lat2)
    )

    x = (
        np.cos(lat1)
        * np.sin(lat2)
        - np.sin(lat1)
        * np.cos(lat2)
        * np.cos(delta_lon)
    )

    bearing = np.degrees(
        np.arctan2(y, x)
    )

    return (bearing + 360) % 360


# --------------------------------------------------
# TRACK METRICS PIPELINE
# --------------------------------------------------

def calculate_track_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:

    required_columns = [
        "storm_id",
        "timestamp",
        "latitude",
        "longitude",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    if df[required_columns].isna().any().any():
        raise ValueError(
            "Missing required track observations detected."
        )

    if df.duplicated(
        subset=["storm_id", "timestamp"]
    ).any():
        raise ValueError(
            "Duplicate storm/timestamp observations detected."
        )

    if not df["latitude"].between(-90, 90).all():
        raise ValueError("Invalid latitude values.")

    if not df["longitude"].between(-180, 180).all():
        raise ValueError("Invalid longitude values.")

    # Sort observations within each storm.
    df = df.sort_values(
        ["storm_id", "timestamp"]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # PREVIOUS OBSERVATION
    # --------------------------------------------------

    grouped = df.groupby(
        "storm_id",
        sort=False,
    )

    df["previous_latitude"] = (
        grouped["latitude"].shift(1)
    )

    df["previous_longitude"] = (
        grouped["longitude"].shift(1)
    )

    df["previous_timestamp"] = (
        grouped["timestamp"].shift(1)
    )

    # --------------------------------------------------
# NEXT OBSERVATION
# --------------------------------------------------

    df["next_latitude"] = (
        grouped["latitude"].shift(-1)
    )

    df["next_longitude"] = (
        grouped["longitude"].shift(-1)
    )

    df["next_timestamp"] = (
        grouped["timestamp"].shift(-1)
    )

    # --------------------------------------------------
    # TIME DIFFERENCE
    # --------------------------------------------------

    df["elapsed_hours"] = (
        df["timestamp"] - df["previous_timestamp"]
    ).dt.total_seconds() / 3600

    if (df["elapsed_hours"].dropna() <= 0).any():
        raise ValueError(
            "Non-positive observation intervals detected."
        )

    # --------------------------------------------------
    # DISTANCE
    # --------------------------------------------------

    df["segment_distance_km"] = (
        calculate_haversine_distance(
            df["previous_latitude"],
            df["previous_longitude"],
            df["latitude"],
            df["longitude"],
        )
    )

    # --------------------------------------------------
    # MOVEMENT SPEED
    # --------------------------------------------------

    df["derived_speed_kmh"] = (
        df["segment_distance_km"]
        / df["elapsed_hours"]
    )

    df["derived_speed_kt"] = (
        df["derived_speed_kmh"]
        / KM_PER_NAUTICAL_MILE
    )

    # --------------------------------------------------
    # MOVEMENT DIRECTION
    # --------------------------------------------------

    df["derived_direction_deg"] = (
        calculate_initial_bearing(
            df["previous_latitude"],
            df["previous_longitude"],
            df["latitude"],
            df["longitude"],
        )
    )

    # Direction is undefined for a stationary segment.
    stationary = df["segment_distance_km"] < 1e-9

    df.loc[
        stationary,
        "derived_direction_deg",
    ] = np.nan

    # --------------------------------------------------
    # CENTRED MOVEMENT METRICS
    # --------------------------------------------------

    # Time between previous and next observations.
    df["centred_elapsed_hours"] = (
        df["next_timestamp"] - df["previous_timestamp"]
    ).dt.total_seconds() / 3600

    # Calculate distance from previous to next observation.
    df["centred_distance_km"] = (
        calculate_haversine_distance(
            df["previous_latitude"],
            df["previous_longitude"],
            df["next_latitude"],
            df["next_longitude"],
        )
    )

    # Calculate centred movement speed.
    df["centred_speed_kmh"] = (
        df["centred_distance_km"]
        / df["centred_elapsed_hours"]
    )

    df["centred_speed_kt"] = (
        df["centred_speed_kmh"]
        / KM_PER_NAUTICAL_MILE
    )

    # Calculate centred movement direction.
    df["centred_direction_deg"] = (
        calculate_initial_bearing(
            df["previous_latitude"],
            df["previous_longitude"],
            df["next_latitude"],
            df["next_longitude"],
        )
    )

    # Direction is undefined when the centred displacement is zero.
    centred_stationary = (
        df["centred_distance_km"] < 1e-9
    )

    df.loc[
        centred_stationary,
        "centred_direction_deg",
    ] = np.nan

    # Validate centred time intervals where available.
    valid_centred_intervals = (
        df["centred_elapsed_hours"].dropna()
    )

    if (valid_centred_intervals <= 0).any():
        raise ValueError(
            "Non-positive centred observation intervals detected."
        )

    # --------------------------------------------------
    # EXPORT
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    return df


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {INPUT_FILE}"
        )

    print("Loading processed cyclone observations...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        parse_dates=["timestamp"],
    )

    print("Calculating cyclone track metrics...")

    result = calculate_track_metrics(df)

    print("\n--- TRACK INTELLIGENCE SUCCESS ---")

    print("Output:", OUTPUT_FILE)

    print("Observations:", len(result))

    print(
        "Unique storms:",
        result["storm_id"].nunique(),
    )

    print(
        "Calculated track segments:",
        result["segment_distance_km"].notna().sum(),
    )

    print("\n--- TRACK METRIC SUMMARY ---")

    print(
        result[
            [
    "segment_distance_km",
    "elapsed_hours",
    "derived_speed_kmh",
    "derived_speed_kt",
    "derived_direction_deg",
    "centred_distance_km",
    "centred_elapsed_hours",
    "centred_speed_kmh",
    "centred_speed_kt",
    "centred_direction_deg",
]
        ].describe().round(2).to_string()
    )

    print("\n--- SAMPLE TRACK OBSERVATIONS ---")

    print(
        result[
            [
                "storm_id",
                "timestamp",
                "latitude",
                "longitude",
                "elapsed_hours",
                "segment_distance_km",
                "derived_speed_kmh",
                "centred_speed_kt",
                "derived_speed_kt",
                "derived_direction_deg",
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()
