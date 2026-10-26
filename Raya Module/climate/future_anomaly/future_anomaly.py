import os
import pandas as pd
import numpy as np

# ============================================================
# FUTURE ANOMALY ENGINE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

FORECAST_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "future_climate_state.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "future_anomaly.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading predictive climate state data...")

    if not os.path.exists(FORECAST_FILE):

        raise FileNotFoundError(
            f"Forecast state file not found:\n{FORECAST_FILE}"
        )

    df = pd.read_csv(FORECAST_FILE)

    required_columns = [
        "Date",
        "Predicted_Temp_Max",
        "Predicted_Rainfall",
        "Predicted_WindSpeed",
        "Climate_State",
        "State_Severity",
        "Confidence_Score"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df["Date"] = pd.to_datetime(df["Date"])

    return df


# ============================================================
# FUTURE ANOMALY CLASSIFICATION
# ============================================================

def classify_anomaly(row):

    temperature = row["Predicted_Temp_Max"]
    rainfall = row["Predicted_Rainfall"]
    wind = row["Predicted_WindSpeed"]

    anomaly_signals = []

    # --------------------------------------------------------
    # Temperature anomaly
    # --------------------------------------------------------

    if temperature >= 35:

        anomaly_signals.append("HIGH_TEMPERATURE")

    # --------------------------------------------------------
    # Heavy rainfall anomaly
    # --------------------------------------------------------

    if rainfall >= 10:

        anomaly_signals.append("HEAVY_RAINFALL")

    # --------------------------------------------------------
    # High wind anomaly
    # --------------------------------------------------------

    if wind >= 30:

        anomaly_signals.append("HIGH_WIND")

    # --------------------------------------------------------
    # No anomaly
    # --------------------------------------------------------

    if len(anomaly_signals) == 0:

        return "NORMAL", "None"

    # --------------------------------------------------------
    # Multiple anomaly signals
    # --------------------------------------------------------

    if len(anomaly_signals) >= 2:

        return "MULTIPLE", ", ".join(anomaly_signals)

    # --------------------------------------------------------
    # Single anomaly
    # --------------------------------------------------------

    return "ANOMALY", anomaly_signals[0]


# ============================================================
# ANOMALY SEVERITY
# ============================================================

def calculate_anomaly_severity(anomaly_type):

    if anomaly_type == "MULTIPLE":

        return "HIGH"

    elif anomaly_type == "ANOMALY":

        return "MEDIUM"

    else:

        return "LOW"


# ============================================================
# MAIN ENGINE
# ============================================================

def main():

    print("=" * 60)
    print("TASK 006 - FUTURE ANOMALY ENGINE")
    print("=" * 60)

    df = load_data()

    print()

    print(
        "Forecast Records :",
        len(df)
    )

    print(
        "Forecast Period  :",
        df["Date"].min().date(),
        "to",
        df["Date"].max().date()
    )

    print()

    print("Detecting future climate anomalies...")

    # --------------------------------------------------------
    # Detect anomaly
    # --------------------------------------------------------

    anomaly_results = df.apply(
        classify_anomaly,
        axis=1
    )

    df["Future_Anomaly"] = [
        result[0]
        for result in anomaly_results
    ]

    df["Anomaly_Signal"] = [
        result[1]
        for result in anomaly_results
    ]

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    df["Anomaly_Severity"] = (
        df["Future_Anomaly"]
        .apply(calculate_anomaly_severity)
    )

    # --------------------------------------------------------
    # Persistence
    # --------------------------------------------------------

    df["Anomaly_Persistence"] = (
        df["Future_Anomaly"]
        .eq("NORMAL")
        .groupby(
            df["Future_Anomaly"]
            .ne("NORMAL")
            .cumsum()
        )
        .cumsum()
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()

    print(
        "Future anomaly file saved successfully:"
    )

    print(OUTPUT_FILE)

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 60)
    print("FUTURE ANOMALY SUMMARY")
    print("=" * 60)

    print()

    print("Anomaly Distribution:")

    print(
        df["Future_Anomaly"]
        .value_counts()
        .to_string()
    )

    print()

    print("Anomaly Severity:")

    print(
        df["Anomaly_Severity"]
        .value_counts()
        .to_string()
    )

    print()

    print("Anomaly Signals:")

    print(
        df["Anomaly_Signal"]
        .value_counts()
        .to_string()
    )

    print()

    print("First 5 Forecast Days:")

    print(
        df[
            [
                "Date",
                "Predicted_Temp_Max",
                "Predicted_Rainfall",
                "Predicted_WindSpeed",
                "Climate_State",
                "Future_Anomaly",
                "Anomaly_Signal",
                "Anomaly_Severity",
                "Confidence_Score"
            ]
        ]
        .head()
        .to_string(index=False)
    )

    print()

    print("=" * 60)
    print(
        "FUTURE ANOMALY ENGINE "
        "COMPLETED SUCCESSFULLY"
    )
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()