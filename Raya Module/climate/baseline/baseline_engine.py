import logging
from pathlib import Path

import pandas as pd

from configs.settings import DATA_PATH


# --------------------------------------------------
# Configuration
# --------------------------------------------------

OUTPUT_PATH = Path("outputs") / "climate_baseline.csv"

logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# --------------------------------------------------
# Baseline Generation
# --------------------------------------------------

def generate_baseline():
    """
    Generate historical seasonal climate baseline.

    The baseline represents the historical expected
    climate condition for each calendar day based on
    available historical observations.
    """

    logging.info("Starting climate baseline generation.")

    # --------------------------------------------------
    # 1. Load historical climate data
    # --------------------------------------------------

    data_path = Path(DATA_PATH)

    if not data_path.exists():
        logging.error(
            f"Climate dataset not found: {DATA_PATH}"
        )
        raise FileNotFoundError(
            f"Climate dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(data_path)

    if df.empty:
        logging.error("Climate dataset is empty.")
        raise ValueError("Climate dataset is empty.")

    # --------------------------------------------------
    # 2. Prepare Date column
    # --------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    if df["Date"].isna().any():
        raise ValueError(
            "Invalid dates found in climate dataset."
        )

    # --------------------------------------------------
    # 3. Extract calendar information
    # --------------------------------------------------

    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day

    # --------------------------------------------------
    # 4. Calculate historical baseline
    # --------------------------------------------------

    baseline = (
        df.groupby(["Month", "Day"])
        .agg(
            Expected_Temp_Max=("Temp_Max", "mean"),
            Expected_Temp_Min=("Temp_Min", "mean"),
            Expected_Rainfall=("Rainfall", "mean"),
            Expected_WindSpeed=("WindSpeed", "mean")
        )
        .reset_index()
    )

    # --------------------------------------------------
    # 5. Round baseline values
    # --------------------------------------------------

    numeric_columns = [
        "Expected_Temp_Max",
        "Expected_Temp_Min",
        "Expected_Rainfall",
        "Expected_WindSpeed"
    ]

    baseline[numeric_columns] = baseline[
        numeric_columns
    ].round(2)

    # --------------------------------------------------
    # 6. Save baseline
    # --------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    baseline.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------
    # 7. Logging
    # --------------------------------------------------

    logging.info(
        f"Climate baseline generated successfully. "
        f"Rows: {len(baseline)}"
    )

    # --------------------------------------------------
    # 8. Console output
    # --------------------------------------------------

    print("=" * 60)
    print("CLIMATE BASELINE GENERATED SUCCESSFULLY")
    print("=" * 60)

    print(f"Historical Rows : {len(df)}")
    print(f"Baseline Rows   : {len(baseline)}")

    print("\nBaseline Columns:")
    print(list(baseline.columns))

    print("\nFirst 5 Baseline Records:")
    print(baseline.head())

    print("\nLast 5 Baseline Records:")
    print(baseline.tail())

    print("\nSaved to:")
    print(OUTPUT_PATH)

    return baseline


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    generate_baseline()