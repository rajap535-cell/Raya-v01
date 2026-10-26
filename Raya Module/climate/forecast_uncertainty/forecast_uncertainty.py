import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ============================================================
# FORECAST UNCERTAINTY ENGINE
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HISTORICAL_FILE = os.path.join(
    BASE_DIR,
    "data",
    "climate_data_10year.csv"
)

FORECAST_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "multivariable_forecast.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "forecast_with_uncertainty.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading historical climate data...")

    historical = pd.read_csv(HISTORICAL_FILE)
    forecast = pd.read_csv(FORECAST_FILE)

    historical["Date"] = pd.to_datetime(historical["Date"])
    forecast["Date"] = pd.to_datetime(forecast["Date"])

    return historical, forecast


# ============================================================
# CALCULATE UNCERTAINTY
# ============================================================

def calculate_uncertainty(historical, forecast, variable):

    y = pd.to_numeric(
        historical[variable],
        errors="coerce"
    ).dropna()

    X = np.arange(len(y)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)

    predictions = model.predict(X)

    residuals = y.values - predictions

    # Standard deviation of historical prediction errors
    error_std = np.std(residuals)

    # Approximate 95% prediction range
    uncertainty = 1.96 * error_std

    return uncertainty


# ============================================================
# MAIN ENGINE
# ============================================================

def main():

    print("=" * 60)
    print("TASK 006 - FORECAST UNCERTAINTY ENGINE")
    print("=" * 60)

    historical, forecast = load_data()

    print()
    print("Historical Records :", len(historical))
    print(
        "Historical Period  :",
        historical["Date"].min().date(),
        "to",
        historical["Date"].max().date()
    )

    print(
        "Forecast Records   :",
        len(forecast)
    )

    print()

    # --------------------------------------------------------
    # Calculate uncertainty for each variable
    # --------------------------------------------------------

    print("Calculating forecast uncertainty...")

    temp_uncertainty = calculate_uncertainty(
        historical,
        forecast,
        "Temp_Max"
    )

    rainfall_uncertainty = calculate_uncertainty(
        historical,
        forecast,
        "Rainfall"
    )

    wind_uncertainty = calculate_uncertainty(
        historical,
        forecast,
        "WindSpeed"
    )

    print()
    print("Uncertainty Estimates")
    print("---------------------")

    print(
        f"Temperature : ±{temp_uncertainty:.2f} °C"
    )

    print(
        f"Rainfall    : ±{rainfall_uncertainty:.2f} mm"
    )

    print(
        f"Wind Speed  : ±{wind_uncertainty:.2f} km/h"
    )

    # --------------------------------------------------------
    # Add confidence ranges
    # --------------------------------------------------------

    result = forecast.copy()

    result["Temp_Lower"] = (
        result["Predicted_Temp_Max"]
        - temp_uncertainty
    )

    result["Temp_Upper"] = (
        result["Predicted_Temp_Max"]
        + temp_uncertainty
    )

    result["Rainfall_Lower"] = (
        result["Predicted_Rainfall"]
        - rainfall_uncertainty
    )

    result["Rainfall_Upper"] = (
        result["Predicted_Rainfall"]
        + rainfall_uncertainty
    )

    result["WindSpeed_Lower"] = (
        result["Predicted_WindSpeed"]
        - wind_uncertainty
    )

    result["WindSpeed_Upper"] = (
        result["Predicted_WindSpeed"]
        + wind_uncertainty
    )

    # Prevent negative physical values
    result["Rainfall_Lower"] = (
        result["Rainfall_Lower"].clip(lower=0)
    )

    result["WindSpeed_Lower"] = (
        result["WindSpeed_Lower"].clip(lower=0)
    )

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Forecast uncertainty file saved successfully:")
    print(OUTPUT_FILE)

    # --------------------------------------------------------
    # Display sample
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FORECAST UNCERTAINTY SUMMARY")
    print("=" * 60)

    print()

    print("First 5 Forecast Days:")

    print(
        result[
            [
                "Date",
                "Predicted_Temp_Max",
                "Temp_Lower",
                "Temp_Upper",
                "Predicted_Rainfall",
                "Rainfall_Lower",
                "Rainfall_Upper",
                "Predicted_WindSpeed",
                "WindSpeed_Lower",
                "WindSpeed_Upper"
            ]
        ].head().to_string(index=False)
    )

    print()
    print("=" * 60)
    print("FORECAST UNCERTAINTY ENGINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()