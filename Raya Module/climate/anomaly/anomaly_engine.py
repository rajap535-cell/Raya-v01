import logging
from pathlib import Path

import pandas as pd

from configs.settings import DATA_PATH


BASELINE_PATH = Path("outputs") / "climate_baseline.csv"
OUTPUT_PATH = Path("outputs") / "climate_anomalies.csv"


logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# --------------------------------------------------
# Anomaly Classification
# --------------------------------------------------

def classify_anomaly(anomaly, elevated_threshold, extreme_threshold):
    """
    Classify anomaly into Normal, Elevated or Extreme.
    """

    absolute_anomaly = abs(anomaly)

    if absolute_anomaly >= extreme_threshold:
        return "Extreme"

    elif absolute_anomaly >= elevated_threshold:
        return "Elevated"

    return "Normal"


# --------------------------------------------------
# Generate Climate Anomalies
# --------------------------------------------------

def generate_anomalies():

    logging.info(
        "Starting Climate Anomaly Detection Engine."
    )

    # --------------------------------------------------
    # 1. Check files
    # --------------------------------------------------

    if not Path(DATA_PATH).exists():
        raise FileNotFoundError(
            f"Climate dataset not found: {DATA_PATH}"
        )

    if not BASELINE_PATH.exists():
        raise FileNotFoundError(
            f"Baseline file not found: {BASELINE_PATH}"
        )

    # --------------------------------------------------
    # 2. Load data
    # --------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    baseline = pd.read_csv(BASELINE_PATH)

    # --------------------------------------------------
    # 3. Prepare dates
    # --------------------------------------------------

    df["Date"] = pd.to_datetime(df["Date"])

    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day

    # --------------------------------------------------
    # 4. Merge actual climate data with baseline
    # --------------------------------------------------

    df = df.merge(
        baseline,
        on=["Month", "Day"],
        how="left"
    )

    # --------------------------------------------------
    # 5. Calculate anomalies
    # --------------------------------------------------

    df["Temperature_Anomaly"] = (
        df["Temp_Max"]
        - df["Expected_Temp_Max"]
    )

    df["Rainfall_Anomaly"] = (
        df["Rainfall"]
        - df["Expected_Rainfall"]
    )

    df["Wind_Anomaly"] = (
        df["WindSpeed"]
        - df["Expected_WindSpeed"]
    )

    # --------------------------------------------------
    # 6. Classify anomalies
    # --------------------------------------------------

    df["Temperature_Level"] = df[
        "Temperature_Anomaly"
    ].apply(
        lambda x: classify_anomaly(
            x,
            elevated_threshold=2.0,
            extreme_threshold=4.0
        )
    )

    df["Rainfall_Level"] = df[
        "Rainfall_Anomaly"
    ].apply(
        lambda x: classify_anomaly(
            x,
            elevated_threshold=20.0,
            extreme_threshold=50.0
        )
    )

    df["Wind_Level"] = df[
        "Wind_Anomaly"
    ].apply(
        lambda x: classify_anomaly(
            x,
            elevated_threshold=5.0,
            extreme_threshold=10.0
        )
    )

    # --------------------------------------------------
    # 7. Generate explanations
    # --------------------------------------------------

    def temperature_reason(row):

        anomaly = row["Temperature_Anomaly"]

        if row["Temperature_Level"] == "Extreme":
            if anomaly > 0:
                return (
                    "Maximum temperature is significantly "
                    "above the historical seasonal baseline."
                )
            else:
                return (
                    "Maximum temperature is significantly "
                    "below the historical seasonal baseline."
                )

        if row["Temperature_Level"] == "Elevated":
            if anomaly > 0:
                return (
                    "Maximum temperature is above the "
                    "historical seasonal baseline."
                )
            else:
                return (
                    "Maximum temperature is below the "
                    "historical seasonal baseline."
                )

        return (
            "Maximum temperature is within the "
            "historical seasonal range."
        )

    def rainfall_reason(row):

        anomaly = row["Rainfall_Anomaly"]

        if row["Rainfall_Level"] == "Extreme":
            if anomaly > 0:
                return (
                    "Rainfall is significantly higher "
                    "than the historical seasonal baseline."
                )
            else:
                return (
                    "Rainfall is significantly lower "
                    "than the historical seasonal baseline."
                )

        if row["Rainfall_Level"] == "Elevated":
            if anomaly > 0:
                return (
                    "Rainfall is above the historical "
                    "seasonal baseline."
                )
            else:
                return (
                    "Rainfall is below the historical "
                    "seasonal baseline."
                )

        return (
            "Rainfall is within the historical "
            "seasonal range."
        )

    def wind_reason(row):

        anomaly = row["Wind_Anomaly"]

        if row["Wind_Level"] == "Extreme":
            if anomaly > 0:
                return (
                    "Wind speed is significantly higher "
                    "than the historical seasonal baseline."
                )
            else:
                return (
                    "Wind speed is significantly lower "
                    "than the historical seasonal baseline."
                )

        if row["Wind_Level"] == "Elevated":
            if anomaly > 0:
                return (
                    "Wind speed is above the historical "
                    "seasonal baseline."
                )
            else:
                return (
                    "Wind speed is below the historical "
                    "seasonal baseline."
                )

        return (
            "Wind speed is within the historical "
            "seasonal range."
        )

    df["Temperature_Reason"] = df.apply(
        temperature_reason,
        axis=1
    )

    df["Rainfall_Reason"] = df.apply(
        rainfall_reason,
        axis=1
    )

    df["Wind_Reason"] = df.apply(
        wind_reason,
        axis=1
    )

    # --------------------------------------------------
    # 8. Remove helper columns
    # --------------------------------------------------

    df.drop(
        columns=["Month", "Day"],
        inplace=True
    )

    # --------------------------------------------------
    # 9. Round numerical values
    # --------------------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    df[numeric_columns] = df[
        numeric_columns
    ].round(2)

    # --------------------------------------------------
    # 10. Save output
    # --------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------
    # 11. Logging
    # --------------------------------------------------

    logging.info(
        "Climate Anomaly Detection completed successfully."
    )

    logging.info(
        f"Anomaly records generated: {len(df)}"
    )

    # --------------------------------------------------
    # 12. Console output
    # --------------------------------------------------

    print("=" * 60)
    print("CLIMATE ANOMALY DETECTION COMPLETED")
    print("=" * 60)

    print(f"Records Analysed : {len(df)}")

    print("\nTemperature Levels:")
    print(
        df["Temperature_Level"]
        .value_counts()
    )

    print("\nRainfall Levels:")
    print(
        df["Rainfall_Level"]
        .value_counts()
    )

    print("\nWind Levels:")
    print(
        df["Wind_Level"]
        .value_counts()
    )

    print("\nSample Anomaly Records:")
    print(
        df[
            [
                "Date",
                "Temp_Max",
                "Expected_Temp_Max",
                "Temperature_Anomaly",
                "Temperature_Level"
            ]
        ].head(10)
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)

    return df


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    generate_anomalies()