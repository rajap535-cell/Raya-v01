#multivariable_forecast.py
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


# ============================================================
#  MULTI-VARIABLE CLIMATE FORECASTING
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Use the regenerated 10-year historical dataset
DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "climate_data_10year.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "multivariable_forecast.csv"
)

# Number of future days to forecast
FORECAST_DAYS = 30


# ============================================================
# LOAD CLIMATE DATA
# ============================================================

def load_data():

    print("\nLoading climate database...")

    if not os.path.exists(DATA_FILE):

        raise FileNotFoundError(
            f"\nClimate data file not found:\n{DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    required_columns = [
        "Date",
        "Temp_Max",
        "Temp_Min",
        "Rainfall",
        "WindSpeed"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"\nMissing required columns: {missing_columns}"
        )

    # Convert Date column
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Convert climate variables to numeric
    numeric_columns = [
        "Temp_Max",
        "Temp_Min",
        "Rainfall",
        "WindSpeed"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "Date",
            "Temp_Max",
            "Temp_Min",
            "Rainfall",
            "WindSpeed"
        ]
    )

    # Remove duplicate dates
    df = df.drop_duplicates(
        subset=["Date"],
        keep="last"
    )

    # Sort chronologically
    df = df.sort_values(
        "Date"
    ).reset_index(
        drop=True
    )

    return df


# ============================================================
# CREATE FUTURE DATES
# ============================================================

def create_future_dates(last_date):

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=FORECAST_DAYS,
        freq="D"
    )

    return future_dates


# ============================================================
# FORECAST SINGLE CLIMATE VARIABLE
# ============================================================

def forecast_variable(
    df,
    target_column
):

    print(
        f"\nForecasting {target_column}..."
    )

    # Remove missing values
    data = df[
        [target_column]
    ].dropna()

    if len(data) < 30:

        raise ValueError(
            f"Not enough data for {target_column} forecasting."
        )

    # Time index
    X = np.arange(
        len(data)
    ).reshape(-1, 1)

    # Target values
    y = data[
        target_column
    ].values

    # Linear Regression model
    model = LinearRegression()

    model.fit(
        X,
        y
    )

    # Future time index
    future_X = np.arange(
        len(data),
        len(data) + FORECAST_DAYS
    ).reshape(-1, 1)

    # Generate predictions
    predictions = model.predict(
        future_X
    )

    # Rainfall cannot be negative
    if target_column == "Rainfall":

        predictions = np.maximum(
            predictions,
            0
        )

    # Wind speed cannot be negative
    if target_column == "WindSpeed":

        predictions = np.maximum(
            predictions,
            0
        )

    return predictions


# ============================================================
# GENERATE MULTI-VARIABLE FORECAST
# ============================================================

def generate_forecast(df):

    last_date = df[
        "Date"
    ].max()

    future_dates = create_future_dates(
        last_date
    )

    print(
        "\nLatest Historical Date :",
        last_date.date()
    )

    print(
        "Forecast Horizon       :",
        FORECAST_DAYS,
        "days"
    )

    print(
        "Forecast End Date      :",
        future_dates[-1].date()
    )

    # --------------------------------------------------------
    # Temperature Forecast
    # --------------------------------------------------------

    temp_predictions = forecast_variable(
        df,
        "Temp_Max"
    )

    # --------------------------------------------------------
    # Rainfall Forecast
    # --------------------------------------------------------

    rainfall_predictions = forecast_variable(
        df,
        "Rainfall"
    )

    # --------------------------------------------------------
    # Wind Speed Forecast
    # --------------------------------------------------------

    wind_predictions = forecast_variable(
        df,
        "WindSpeed"
    )

    # --------------------------------------------------------
    # Create Forecast DataFrame
    # --------------------------------------------------------

    forecast_df = pd.DataFrame({

        "Date": future_dates,

        "Predicted_Temp_Max":
            np.round(
                temp_predictions,
                2
            ),

        "Predicted_Rainfall":
            np.round(
                rainfall_predictions,
                2
            ),

        "Predicted_WindSpeed":
            np.round(
                wind_predictions,
                2
            )
    })

    return forecast_df


# ============================================================
# SAVE FORECAST
# ============================================================

def save_forecast(
    forecast_df
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    forecast_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\nForecast saved successfully:"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# DISPLAY FORECAST SUMMARY
# ============================================================

def display_summary(
    forecast_df
):

    print(
        "\n============================================================"
    )

    print(
        "MULTI-VARIABLE FORECAST SUMMARY"
    )

    print(
        "============================================================"
    )

    # Temperature
    print(
        f"\nAverage Predicted Temperature : "
        f"{forecast_df['Predicted_Temp_Max'].mean():.2f} °C"
    )

    print(
        f"Maximum Predicted Temperature : "
        f"{forecast_df['Predicted_Temp_Max'].max():.2f} °C"
    )

    print(
        f"Minimum Predicted Temperature : "
        f"{forecast_df['Predicted_Temp_Max'].min():.2f} °C"
    )

    # Rainfall
    print(
        f"\nAverage Predicted Rainfall    : "
        f"{forecast_df['Predicted_Rainfall'].mean():.2f} mm"
    )

    print(
        f"Maximum Predicted Rainfall    : "
        f"{forecast_df['Predicted_Rainfall'].max():.2f} mm"
    )

    # Wind
    print(
        f"\nAverage Predicted Wind Speed  : "
        f"{forecast_df['Predicted_WindSpeed'].mean():.2f} km/h"
    )

    print(
        f"Maximum Predicted Wind Speed  : "
        f"{forecast_df['Predicted_WindSpeed'].max():.2f} km/h"
    )

    # --------------------------------------------------------
    # First 5 forecast records
    # --------------------------------------------------------

    print(
        "\nFirst 5 Forecast Days:"
    )

    print(
        forecast_df.head(5).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Last 5 forecast records
    # --------------------------------------------------------

    print(
        "\nLast 5 Forecast Days:"
    )

    print(
        forecast_df.tail(5).to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n============================================================"
    )

    print(
        "TASK 006 - MULTI-VARIABLE CLIMATE FORECASTING"
    )

    print(
        "============================================================"
    )

    try:

        # Load historical dataset
        df = load_data()

        print(
            f"\nHistorical Records : {len(df)}"
        )

        print(
            f"Historical Period  : "
            f"{df['Date'].min().date()} "
            f"to "
            f"{df['Date'].max().date()}"
        )

        # Generate forecast
        forecast_df = generate_forecast(
            df
        )

        # Save forecast
        save_forecast(
            forecast_df
        )

        # Display summary
        display_summary(
            forecast_df
        )

        print(
            "\n============================================================"
        )

        print(
            "MULTI-VARIABLE FORECAST COMPLETED SUCCESSFULLY"
        )

        print(
            "============================================================"
        )

    except Exception as error:

        print(
            "\nERROR:"
        )

        print(
            str(error)
        )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()