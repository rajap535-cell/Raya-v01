#def load_ibtracs.py
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ibtracs.NI.list.v04r01.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ibtracs_ni_observations.csv"
)


# --------------------------------------------------
# SOURCE-TO-STANDARDIZED COLUMN MAPPING
# --------------------------------------------------

COLUMN_MAP = {
    "SID": "storm_id",
    "SEASON": "season",
    "BASIN": "basin",
    "SUBBASIN": "subbasin",
    "NAME": "storm_name",
    "ISO_TIME": "timestamp",
    "NATURE": "nature",
    "TRACK_TYPE": "track_type",
    "IFLAG": "iflag",
    "LAT": "latitude",
    "LON": "longitude",
    "DIST2LAND": "distance_to_land_km",
    "LANDFALL": "landfall_distance_km",
    "WMO_WIND": "wmo_wind_kt",
    "WMO_PRES": "wmo_pressure_mb",
    "USA_WIND": "usa_wind_kt",
    "USA_PRES": "usa_pressure_mb",
    "USA_SSHS": "usa_sshs_code",
    "NEWDELHI_WIND": "newdelhi_wind_kt",
    "NEWDELHI_GRADE": "newdelhi_grade",
    "STORM_SPEED": "storm_speed_kt",
    "STORM_DIR": "storm_direction_deg",
}


# --------------------------------------------------
# DATA TYPES
# --------------------------------------------------

NUMERIC_COLUMNS = [
    "season",
    "latitude",
    "longitude",
    "distance_to_land_km",
    "landfall_distance_km",
    "wmo_wind_kt",
    "wmo_pressure_mb",
    "usa_wind_kt",
    "usa_pressure_mb",
    "usa_sshs_code",
    "newdelhi_wind_kt",
    "storm_speed_kt",
    "storm_direction_deg",
]

STRING_COLUMNS = [
    "storm_id",
    "basin",
    "subbasin",
    "storm_name",
    "nature",
    "track_type",
    "iflag",
    "newdelhi_grade",
]

REQUIRED_COLUMNS = [
    "storm_id",
    "season",
    "timestamp",
    "latitude",
    "longitude",
]


# --------------------------------------------------
# MAIN DATA LOADER
# --------------------------------------------------

def load_ibtracs() -> pd.DataFrame:

    # Check whether the original NOAA file exists.
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"NOAA source file not found: {RAW_FILE}"
        )

    print("Reading NOAA IBTrACS dataset...")

    # Row 2 contains measurement units, so skip it.
    # The original raw dataset remains unchanged.
    df = pd.read_csv(
        RAW_FILE,
        skiprows=[1],
        low_memory=False,
    )

    # Convert whitespace-only cells into proper missing values.
    df = df.replace(
        r"^\s*$",
        pd.NA,
        regex=True,
    )

    # Retain only the fields selected for our initial schema.
    available_columns = [
        column
        for column in COLUMN_MAP
        if column in df.columns
    ]

    df = df[available_columns].rename(
        columns=COLUMN_MAP
    )

    # Check that essential fields exist.
    missing_required = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_required:
        raise ValueError(
            f"Missing required columns: {missing_required}"
        )

    # Convert measurement fields to numeric values.
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # Preserve categorical and quality metadata as text.
    for column in STRING_COLUMNS:
        if column in df.columns:
            df[column] = df[column].astype("string")


    # Preserve New Delhi cyclone grades as categorical text.
    if "newdelhi_grade" in df.columns:
        df["newdelhi_grade"] = df[
            "newdelhi_grade"
        ].astype("string")

    # Parse observation timestamps.
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    # --------------------------------------------------
    # DATA VALIDATION
    # --------------------------------------------------

    # Essential fields must not contain missing values.
    if df[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError(
            "Missing values detected in required fields."
        )

    # Validate geographic coordinates.
    if not df["latitude"].between(-90, 90).all():
        raise ValueError(
            "Invalid latitude values detected."
        )

    if not df["longitude"].between(-180, 180).all():
        raise ValueError(
            "Invalid longitude values detected."
        )

    # Check duplicate storm observations.
    if df.duplicated(
        subset=["storm_id", "timestamp"]
    ).any():
        raise ValueError(
            "Duplicate storm/timestamp records detected."
        )

    # Validate USA SSHS codes without treating
    # documented negative classifications as missing.
    if "usa_sshs_code" in df.columns:
        valid_sshs_codes = [
            -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5
        ]

        unexpected_codes = (
            set(df["usa_sshs_code"].dropna().unique())
            - set(valid_sshs_codes)
        )

        if unexpected_codes:
            raise ValueError(
                f"Unexpected USA_SSHS codes: {unexpected_codes}"
            )

    # --------------------------------------------------
    # SORT OBSERVATIONS
    # --------------------------------------------------

    df = df.sort_values(
        ["storm_id", "timestamp"]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # EXPORT PROCESSED DATASET
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------
    # LOADER REPORT
    # --------------------------------------------------

    print("\n--- LOADER SUCCESS ---")

    print("Output:", OUTPUT_FILE)
    print("Observations:", len(df))
    print("Unique storms:", df["storm_id"].nunique())
    print("Columns:", len(df.columns))

    print("\n--- STANDARDIZED COLUMNS ---")
    print(df.columns.tolist())

    print("\n--- SAMPLE OBSERVATIONS ---")
    print(df.head(5).to_string(index=False))

    print("\n--- MISSING INTENSITY DATA ---")

    for column in [
        "wmo_wind_kt",
        "usa_wind_kt",
        "newdelhi_wind_kt",
        "newdelhi_grade",
    ]:
        if column in df.columns:
            print(
                f"{column}: "
                f"{df[column].notna().sum()} available / "
                f"{df[column].isna().sum()} missing"
            )

    print("\n--- USA SSHS CLASSIFICATION ---")

    if "usa_sshs_code" in df.columns:
        print(
            df["usa_sshs_code"]
            .value_counts(dropna=False)
            .sort_index()
            .to_string()
        )

    print("\n--- NEW DELHI GRADE DISTRIBUTION ---")

    if "newdelhi_grade" in df.columns:
        print(
            df["newdelhi_grade"]
            .value_counts(dropna=False)
            .to_string()
        )

    return df


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

if __name__ == "__main__":
    load_ibtracs()
