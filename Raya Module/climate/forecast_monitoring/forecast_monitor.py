import logging
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

FORECAST_PATH = (
    BASE_DIR
    / "data"
    / "temperature_forecast.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "outputs"
    / "forecast_monitoring.csv"
)

LOG_PATH = (
    BASE_DIR
    / "logs"
    / "forecast_monitoring.log"
)


# Temperature threshold for elevated forecast monitoring
HIGH_TEMP_THRESHOLD = 32.0


# ============================================================
# LOGGING
# ============================================================

LOG_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ============================================================
# LOAD FORECAST
# ============================================================

def load_forecast():

    if not FORECAST_PATH.exists():

        raise FileNotFoundError(
            f"Forecast file not found: {FORECAST_PATH}"
        )

    df = pd.read_csv(
        FORECAST_PATH
    )

    if "ds" not in df.columns:

        raise ValueError(
            "Forecast file does not contain 'ds' column."
        )

    if "yhat" not in df.columns:

        raise ValueError(
            "Forecast file does not contain 'yhat' column."
        )

    df["ds"] = pd.to_datetime(
        df["ds"],
        errors="coerce"
    )

    df["yhat"] = pd.to_numeric(
        df["yhat"],
        errors="coerce"
    )

    if "yhat_lower" in df.columns:

        df["yhat_lower"] = pd.to_numeric(
            df["yhat_lower"],
            errors="coerce"
        )

    if "yhat_upper" in df.columns:

        df["yhat_upper"] = pd.to_numeric(
            df["yhat_upper"],
            errors="coerce"
        )

    df = (
        df.dropna(
            subset=["ds", "yhat"]
        )
        .sort_values("ds")
        .reset_index(drop=True)
    )

    return df


# ============================================================
# SELECT FUTURE FORECAST
# ============================================================

def get_future_forecast(df):

    today = pd.Timestamp.today().normalize()

    future = df[
        df["ds"] >= today
    ].copy()

    # If the machine date is later than the stored forecast,
    # use the complete forecast dataset instead.
    if future.empty:

        future = df.copy()

    return future.reset_index(
        drop=True
    )


# ============================================================
# CALCULATE FORECAST STATISTICS
# ============================================================

def calculate_statistics(df):

    statistics = {

        "forecast_records": len(df),

        "forecast_start": df["ds"].min(),

        "forecast_end": df["ds"].max(),

        "average_predicted_temperature":
            df["yhat"].mean(),

        "minimum_predicted_temperature":
            df["yhat"].min(),

        "maximum_predicted_temperature":
            df["yhat"].max()
    }

    if "yhat_lower" in df.columns:

        statistics[
            "average_lower_bound"
        ] = df["yhat_lower"].mean()

    else:

        statistics[
            "average_lower_bound"
        ] = None

    if "yhat_upper" in df.columns:

        statistics[
            "average_upper_bound"
        ] = df["yhat_upper"].mean()

    else:

        statistics[
            "average_upper_bound"
        ] = None

    return statistics


# ============================================================
# DETECT FORECAST TREND
# ============================================================

def detect_forecast_trend(df):

    if len(df) < 2:

        return "INSUFFICIENT DATA"

    first_value = df.iloc[0]["yhat"]
    last_value = df.iloc[-1]["yhat"]

    difference = last_value - first_value

    if difference >= 1.0:

        return "RISING"

    elif difference <= -1.0:

        return "FALLING"

    else:

        return "STABLE"


# ============================================================
# DETECT HIGH TEMPERATURE FORECASTS
# ============================================================

def detect_temperature_risk(df):

    high_temp_days = df[
        df["yhat"] >= HIGH_TEMP_THRESHOLD
    ].copy()

    if len(high_temp_days) == 0:

        risk_level = "LOW"

    elif len(high_temp_days) <= 3:

        risk_level = "MODERATE"

    else:

        risk_level = "HIGH"

    return (
        high_temp_days,
        risk_level
    )


# ============================================================
# GENERATE MONITORING SUMMARY
# ============================================================

def generate_summary(df):

    statistics = calculate_statistics(
        df
    )

    trend = detect_forecast_trend(
        df
    )

    high_temp_days, risk_level = (
        detect_temperature_risk(
            df
        )
    )

    summary = {

        "Forecast_Start":
            statistics["forecast_start"],

        "Forecast_End":
            statistics["forecast_end"],

        "Forecast_Records":
            statistics["forecast_records"],

        "Average_Predicted_Temp":
            round(
                statistics[
                    "average_predicted_temperature"
                ],
                2
            ),

        "Minimum_Predicted_Temp":
            round(
                statistics[
                    "minimum_predicted_temperature"
                ],
                2
            ),

        "Maximum_Predicted_Temp":
            round(
                statistics[
                    "maximum_predicted_temperature"
                ],
                2
            ),

        "Forecast_Trend":
            trend,

        "High_Temperature_Days":
            len(high_temp_days),

        "Temperature_Risk":
            risk_level
    }

    return summary


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_forecast_monitoring():

    try:

        print(
            "\n============================================================"
        )

        print(
            "TASK 005 - FORECAST MONITORING"
        )

        print(
            "============================================================"
        )


        # ----------------------------------------------------
        # 1. LOAD FORECAST
        # ----------------------------------------------------

        df = load_forecast()

        print(
            f"\nForecast records loaded: {len(df)}"
        )


        # ----------------------------------------------------
        # 2. SELECT FORECAST PERIOD
        # ----------------------------------------------------

        future = get_future_forecast(
            df
        )

        print(
            f"Forecast records monitored: {len(future)}"
        )


        # ----------------------------------------------------
        # 3. CALCULATE SUMMARY
        # ----------------------------------------------------

        summary = generate_summary(
            future
        )


        print(
            "\nForecast Summary"
        )

        print(
            "----------------"
        )

        print(
            f"Start Date              : "
            f"{summary['Forecast_Start'].date()}"
        )

        print(
            f"End Date                : "
            f"{summary['Forecast_End'].date()}"
        )

        print(
            f"Forecast Records        : "
            f"{summary['Forecast_Records']}"
        )

        print(
            f"Average Predicted Temp  : "
            f"{summary['Average_Predicted_Temp']:.2f} °C"
        )

        print(
            f"Minimum Predicted Temp  : "
            f"{summary['Minimum_Predicted_Temp']:.2f} °C"
        )

        print(
            f"Maximum Predicted Temp  : "
            f"{summary['Maximum_Predicted_Temp']:.2f} °C"
        )


        # ----------------------------------------------------
        # 4. TREND
        # ----------------------------------------------------

        print(
            "\nForecast Trend"
        )

        print(
            "--------------"
        )

        print(
            f"Trend                    : "
            f"{summary['Forecast_Trend']}"
        )


        # ----------------------------------------------------
        # 5. TEMPERATURE RISK
        # ----------------------------------------------------

        print(
            "\nForecast Temperature Risk"
        )

        print(
            "-------------------------"
        )

        print(
            f"High Temperature Days    : "
            f"{summary['High_Temperature_Days']}"
        )

        print(
            f"Temperature Risk         : "
            f"{summary['Temperature_Risk']}"
        )


        # ----------------------------------------------------
        # 6. SAVE SUMMARY
        # ----------------------------------------------------

        output_df = pd.DataFrame(
            [summary]
        )

        output_df.to_csv(
            OUTPUT_PATH,
            index=False
        )


        # ----------------------------------------------------
        # 7. LOGGING
        # ----------------------------------------------------

        logging.info(
            "Forecast monitoring completed. "
            "Records=%s, Trend=%s, Risk=%s",
            summary["Forecast_Records"],
            summary["Forecast_Trend"],
            summary["Temperature_Risk"]
        )


        # ----------------------------------------------------
        # 8. FINAL STATUS
        # ----------------------------------------------------

        print(
            "\n============================================================"
        )

        print(
            "FORECAST MONITORING COMPLETED SUCCESSFULLY"
        )

        print(
            "============================================================"
        )

        print(
            f"Result saved to: {OUTPUT_PATH}"
        )


        return output_df


    except FileNotFoundError as error:

        logging.error(
            str(error)
        )

        print(
            f"\nERROR: {error}"
        )

        return None


    except ValueError as error:

        logging.error(
            str(error)
        )

        print(
            f"\nVALIDATION ERROR: {error}"
        )

        return None


    except Exception as error:

        logging.exception(
            "Unexpected forecast monitoring error."
        )

        print(
            f"\nFORECAST MONITORING ERROR: {error}"
        )

        return None


# ============================================================
# MODULE EXECUTION
# ============================================================

if __name__ == "__main__":

    run_forecast_monitoring()