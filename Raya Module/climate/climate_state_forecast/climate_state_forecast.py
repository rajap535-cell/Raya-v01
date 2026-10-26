import os
import pandas as pd
import numpy as np

# ============================================================
# PREDICTIVE CLIMATE STATE ENGINE
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FORECAST_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "forecast_with_uncertainty.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "future_climate_state.csv"
)


# ============================================================
# LOAD FORECAST DATA
# ============================================================

def load_forecast():

    print("Loading forecast with uncertainty...")

    if not os.path.exists(FORECAST_FILE):
        raise FileNotFoundError(
            f"Forecast file not found:\n{FORECAST_FILE}"
        )

    forecast = pd.read_csv(FORECAST_FILE)

    required_columns = [
        "Date",
        "Predicted_Temp_Max",
        "Predicted_Rainfall",
        "Predicted_WindSpeed",
        "Temp_Lower",
        "Temp_Upper",
        "Rainfall_Lower",
        "Rainfall_Upper",
        "WindSpeed_Lower",
        "WindSpeed_Upper"
    ]

    missing = [
        column
        for column in required_columns
        if column not in forecast.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    forecast["Date"] = pd.to_datetime(
        forecast["Date"]
    )

    return forecast


# ============================================================
# CLIMATE STATE CLASSIFICATION
# ============================================================

def classify_climate_state(row):

    temperature = row["Predicted_Temp_Max"]
    rainfall = row["Predicted_Rainfall"]

    # --------------------------------------------------------
    # HOT
    # --------------------------------------------------------

    if temperature >= 35:

        return "Hot"

    # --------------------------------------------------------
    # WET
    # --------------------------------------------------------

    elif rainfall >= 10:

        return "Wet"

    # --------------------------------------------------------
    # DRY
    # --------------------------------------------------------

    elif rainfall <= 1:

        return "Dry"

    # --------------------------------------------------------
    # NORMAL
    # --------------------------------------------------------

    else:

        return "Normal"


# ============================================================
# CLIMATE STATE SEVERITY
# ============================================================

def calculate_severity(state):

    if state == "Hot":

        return "HIGH"

    elif state == "Wet":

        return "MEDIUM"

    elif state == "Dry":

        return "MEDIUM"

    else:

        return "LOW"


# ============================================================
# CONFIDENCE SCORE
# ============================================================

def calculate_confidence(forecast):

    # Temperature uncertainty width
    temp_range = (
        forecast["Temp_Upper"]
        - forecast["Temp_Lower"]
    )

    average_range = temp_range.mean()

    # Stable confidence calculation
    confidence = (
        100 / (1 + average_range / 10)
    )

    return round(
        float(np.clip(confidence, 0, 100)),
        2
    )


# ============================================================
# MAIN ENGINE
# ============================================================

def main():

    print("=" * 60)
    print("TASK 006 - PREDICTIVE CLIMATE STATE ENGINE")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    forecast = load_forecast()

    print()

    print(
        "Forecast Records :",
        len(forecast)
    )

    print(
        "Forecast Period  :",
        forecast["Date"].min().date(),
        "to",
        forecast["Date"].max().date()
    )

    # --------------------------------------------------------
    # Climate State
    # --------------------------------------------------------

    print()

    print("Classifying future climate states...")

    forecast["Climate_State"] = forecast.apply(
        classify_climate_state,
        axis=1
    )

    # --------------------------------------------------------
    # State Severity
    # --------------------------------------------------------

    forecast["State_Severity"] = (
        forecast["Climate_State"]
        .apply(calculate_severity)
    )

    # --------------------------------------------------------
    # Confidence Score
    # --------------------------------------------------------

    confidence_score = calculate_confidence(
        forecast
    )

    forecast["Confidence_Score"] = confidence_score

    # --------------------------------------------------------
    # Previous State
    # --------------------------------------------------------

    forecast["Previous_State"] = (
        forecast["Climate_State"].shift(1)
    )

    # --------------------------------------------------------
    # State Change
    # --------------------------------------------------------

    forecast["State_Change"] = np.where(

        forecast["Previous_State"].isna(),

        "Initial State",

        np.where(

            forecast["Climate_State"]
            == forecast["Previous_State"],

            "Persistent",

            "State Change"
        )
    )

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    forecast.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()

    print(
        "Future climate state file saved successfully:"
    )

    print(OUTPUT_FILE)

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 60)
    print("PREDICTIVE CLIMATE STATE SUMMARY")
    print("=" * 60)

    print()

    # --------------------------------------------------------
    # Climate state distribution
    # --------------------------------------------------------

    print("Climate State Distribution:")

    print(
        forecast["Climate_State"]
        .value_counts()
        .to_string()
    )

    print()

    # --------------------------------------------------------
    # Severity distribution
    # --------------------------------------------------------

    print("State Severity Distribution:")

    print(
        forecast["State_Severity"]
        .value_counts()
        .to_string()
    )

    print()

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    print(
        "Average Confidence Score :",
        f"{forecast['Confidence_Score'].mean():.2f}%"
    )

    print()

    # --------------------------------------------------------
    # First 5 forecast states
    # --------------------------------------------------------

    print("First 5 Forecast States:")

    print(
        forecast[
            [
                "Date",
                "Predicted_Temp_Max",
                "Predicted_Rainfall",
                "Predicted_WindSpeed",
                "Climate_State",
                "State_Severity",
                "Confidence_Score",
                "State_Change"
            ]
        ]
        .head()
        .to_string(index=False)
    )

    print()

    print("=" * 60)
    print(
        "PREDICTIVE CLIMATE STATE ENGINE "
        "COMPLETED SUCCESSFULLY"
    )
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()