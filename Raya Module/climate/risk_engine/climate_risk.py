import logging
from pathlib import Path

import pandas as pd


ANOMALY_PATH = Path("outputs") / "climate_anomalies.csv"
STATE_PATH = Path("outputs") / "climate_state.csv"
OUTPUT_PATH = Path("outputs") / "climate_risk.csv"


logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def calculate_risk_level(level):
    """
    Convert anomaly classification into a risk level.
    """

    if level == "Extreme":
        return "High"

    if level == "Elevated":
        return "Moderate"

    return "Low"


def determine_overall_risk(row):
    """
    Determine the overall climate risk from
    temperature, rainfall and wind conditions.
    """

    risk_values = {
        "Low": 1,
        "Moderate": 2,
        "High": 3
    }

    temperature_risk = risk_values[
        row["Temperature_Risk"]
    ]

    rainfall_risk = risk_values[
        row["Rainfall_Risk"]
    ]

    wind_risk = risk_values[
        row["Wind_Risk"]
    ]

    highest_risk = max(
        temperature_risk,
        rainfall_risk,
        wind_risk
    )

    if highest_risk == 3:
        return "High"

    if highest_risk == 2:
        return "Moderate"

    return "Low"


def generate_risk_reason(row):
    """
    Generate a human-readable explanation
    for the identified climate risk.
    """

    reasons = []

    if row["Temperature_Risk"] == "High":
        reasons.append(
            "Extreme temperature anomaly"
        )

    elif row["Temperature_Risk"] == "Moderate":
        reasons.append(
            "Elevated temperature anomaly"
        )

    if row["Rainfall_Risk"] == "High":
        reasons.append(
            "Extreme rainfall anomaly"
        )

    elif row["Rainfall_Risk"] == "Moderate":
        reasons.append(
            "Elevated rainfall anomaly"
        )

    if row["Wind_Risk"] == "High":
        reasons.append(
            "Extreme wind anomaly"
        )

    elif row["Wind_Risk"] == "Moderate":
        reasons.append(
            "Elevated wind anomaly"
        )

    if not reasons:
        return (
            "Temperature, rainfall and wind conditions "
            "are within the historical seasonal range."
        )

    return "; ".join(reasons) + "."


def generate_climate_risk():

    logging.info(
        "Starting Climate Risk Intelligence Engine."
    )

    # --------------------------------------------------
    # 1. Check input files
    # --------------------------------------------------

    if not ANOMALY_PATH.exists():
        raise FileNotFoundError(
            f"Anomaly file not found: {ANOMALY_PATH}"
        )

    if not STATE_PATH.exists():
        raise FileNotFoundError(
            f"Climate state file not found: {STATE_PATH}"
        )

    # --------------------------------------------------
    # 2. Load data
    # --------------------------------------------------

    anomaly_df = pd.read_csv(
        ANOMALY_PATH
    )

    state_df = pd.read_csv(
        STATE_PATH
    )

    if anomaly_df.empty:
        raise ValueError(
            "Climate anomaly dataset is empty."
        )

    if state_df.empty:
        raise ValueError(
            "Climate state dataset is empty."
        )

    # --------------------------------------------------
    # 3. Keep required columns from climate state
    # --------------------------------------------------

    state_columns = [
        "Date",
        "Climate_State"
    ]

    state_df = state_df[
        state_columns
    ]

    # --------------------------------------------------
    # 4. Merge anomaly and climate state
    # --------------------------------------------------

    df = anomaly_df.merge(
        state_df,
        on="Date",
        how="left"
    )

    # --------------------------------------------------
    # 5. Calculate individual risks
    # --------------------------------------------------

    df["Temperature_Risk"] = (
        df["Temperature_Level"]
        .apply(calculate_risk_level)
    )

    df["Rainfall_Risk"] = (
        df["Rainfall_Level"]
        .apply(calculate_risk_level)
    )

    df["Wind_Risk"] = (
        df["Wind_Level"]
        .apply(calculate_risk_level)
    )

    # --------------------------------------------------
    # 6. Calculate overall climate risk
    # --------------------------------------------------

    df["Overall_Risk"] = df.apply(
        determine_overall_risk,
        axis=1
    )

    # --------------------------------------------------
    # 7. Generate risk explanation
    # --------------------------------------------------

    df["Risk_Reason"] = df.apply(
        generate_risk_reason,
        axis=1
    )

    # --------------------------------------------------
    # 8. Select useful output columns
    # --------------------------------------------------

    output_columns = [
        "Date",

        "Climate_State",

        "Temperature_Anomaly",
        "Temperature_Level",
        "Temperature_Risk",

        "Rainfall_Anomaly",
        "Rainfall_Level",
        "Rainfall_Risk",

        "Wind_Anomaly",
        "Wind_Level",
        "Wind_Risk",

        "Overall_Risk",
        "Risk_Reason"
    ]

    df = df[
        output_columns
    ]

    # --------------------------------------------------
    # 9. Round anomaly values
    # --------------------------------------------------

    anomaly_columns = [
        "Temperature_Anomaly",
        "Rainfall_Anomaly",
        "Wind_Anomaly"
    ]

    df[anomaly_columns] = df[
        anomaly_columns
    ].round(2)

    # --------------------------------------------------
    # 10. Save result
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
        "Climate Risk Intelligence Engine "
        "completed successfully."
    )

    logging.info(
        f"Risk records generated: {len(df)}"
    )

    # --------------------------------------------------
    # 12. Console output
    # --------------------------------------------------

    print("=" * 60)
    print("CLIMATE RISK INTELLIGENCE COMPLETED")
    print("=" * 60)

    print(
        f"Records Analysed : {len(df)}"
    )

    print("\nOverall Risk Distribution:")

    print(
        df["Overall_Risk"]
        .value_counts()
    )

    print("\nTemperature Risk:")

    print(
        df["Temperature_Risk"]
        .value_counts()
    )

    print("\nRainfall Risk:")

    print(
        df["Rainfall_Risk"]
        .value_counts()
    )

    print("\nWind Risk:")

    print(
        df["Wind_Risk"]
        .value_counts()
    )

    print("\nSample Risk Records:")

    print(
        df[
            [
                "Date",
                "Climate_State",
                "Temperature_Risk",
                "Rainfall_Risk",
                "Wind_Risk",
                "Overall_Risk",
                "Risk_Reason"
            ]
        ].head(10)
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)

    return df


if __name__ == "__main__":
    generate_climate_risk()