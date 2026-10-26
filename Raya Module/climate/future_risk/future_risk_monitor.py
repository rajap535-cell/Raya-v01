import logging
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ANOMALY_PATH = (
    BASE_DIR
    / "outputs"
    / "emerging_anomalies.csv"
)

FORECAST_PATH = (
    BASE_DIR
    / "outputs"
    / "forecast_monitoring.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "outputs"
    / "future_risk_monitoring.csv"
)

LOG_PATH = (
    BASE_DIR
    / "logs"
    / "future_risk_monitoring.log"
)


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
# LOAD INPUTS
# ============================================================

def load_inputs():

    if not ANOMALY_PATH.exists():

        raise FileNotFoundError(
            f"Anomaly file not found: {ANOMALY_PATH}"
        )

    if not FORECAST_PATH.exists():

        raise FileNotFoundError(
            f"Forecast monitoring file not found: {FORECAST_PATH}"
        )

    anomaly_df = pd.read_csv(
        ANOMALY_PATH
    )

    forecast_df = pd.read_csv(
        FORECAST_PATH
    )

    return anomaly_df, forecast_df


# ============================================================
# CALCULATE FUTURE RISK
# ============================================================

def calculate_future_risk(
    anomaly_df,
    forecast_df
):

    anomaly_level = str(
        anomaly_df.iloc[-1][
            "Emerging_Anomaly_Level"
        ]
    ).upper()

    temperature_risk = str(
        forecast_df.iloc[-1][
            "Temperature_Risk"
        ]
    ).upper()

    forecast_trend = str(
        forecast_df.iloc[-1][
            "Forecast_Trend"
        ]
    ).upper()

    high_temperature_days = int(
        forecast_df.iloc[-1][
            "High_Temperature_Days"
        ]
    )

    maximum_temperature = float(
        forecast_df.iloc[-1][
            "Maximum_Predicted_Temp"
        ]
    )


    # --------------------------------------------------------
    # RISK SCORE
    # --------------------------------------------------------

    risk_score = 0


    if anomaly_level == "LOW":

        risk_score += 1

    elif anomaly_level == "MODERATE":

        risk_score += 2

    elif anomaly_level == "HIGH":

        risk_score += 3


    if temperature_risk == "LOW":

        risk_score += 1

    elif temperature_risk == "MODERATE":

        risk_score += 2

    elif temperature_risk == "HIGH":

        risk_score += 3


    if forecast_trend == "RISING":

        risk_score += 2

    elif forecast_trend == "STABLE":

        risk_score += 1


    if high_temperature_days >= 10:

        risk_score += 2

    elif high_temperature_days >= 3:

        risk_score += 1


    if maximum_temperature >= 40:

        risk_score += 2

    elif maximum_temperature >= 35:

        risk_score += 1


    # --------------------------------------------------------
    # FINAL RISK LEVEL
    # --------------------------------------------------------

    if risk_score >= 9:

        future_risk = "HIGH"

    elif risk_score >= 6:

        future_risk = "MODERATE"

    else:

        future_risk = "LOW"


    # --------------------------------------------------------
    # RISK REASONS
    # --------------------------------------------------------

    reasons = []


    if anomaly_level in [
        "MODERATE",
        "HIGH"
    ]:

        reasons.append(
            f"Emerging anomaly level is {anomaly_level}"
        )


    if temperature_risk in [
        "MODERATE",
        "HIGH"
    ]:

        reasons.append(
            f"Forecast temperature risk is "
            f"{temperature_risk}"
        )


    if forecast_trend == "RISING":

        reasons.append(
            "Forecast temperature trend is rising"
        )


    if high_temperature_days > 0:

        reasons.append(
            f"{high_temperature_days} "
            f"high-temperature forecast days detected"
        )


    if maximum_temperature >= 40:

        reasons.append(
            f"Maximum predicted temperature "
            f"reaches {maximum_temperature:.2f} °C"
        )


    if not reasons:

        reasons.append(
            "No significant future climate risk detected"
        )


    return {
        "Anomaly_Level": anomaly_level,
        "Forecast_Trend": forecast_trend,
        "Temperature_Risk": temperature_risk,
        "High_Temperature_Days": high_temperature_days,
        "Maximum_Predicted_Temp": round(
            maximum_temperature,
            2
        ),
        "Future_Risk_Score": risk_score,
        "Future_Risk_Level": future_risk,
        "Risk_Reason": "; ".join(
            reasons
        )
    }


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_future_risk_monitoring():

    try:

        print(
            "\n============================================================"
        )

        print(
            "TASK 005 - FUTURE CLIMATE RISK MONITORING"
        )

        print(
            "============================================================"
        )


        # ----------------------------------------------------
        # 1. LOAD DATA
        # ----------------------------------------------------

        anomaly_df, forecast_df = (
            load_inputs()
        )

        print(
            "\nInput intelligence loaded successfully."
        )


        # ----------------------------------------------------
        # 2. CALCULATE RISK
        # ----------------------------------------------------

        result = calculate_future_risk(
            anomaly_df,
            forecast_df
        )


        # ----------------------------------------------------
        # 3. DISPLAY RESULTS
        # ----------------------------------------------------

        print(
            "\nFuture Risk Assessment"
        )

        print(
            "----------------------"
        )

        print(
            f"Emerging Anomaly Level : "
            f"{result['Anomaly_Level']}"
        )

        print(
            f"Forecast Trend         : "
            f"{result['Forecast_Trend']}"
        )

        print(
            f"Temperature Risk       : "
            f"{result['Temperature_Risk']}"
        )

        print(
            f"High Temperature Days  : "
            f"{result['High_Temperature_Days']}"
        )

        print(
            f"Maximum Predicted Temp : "
            f"{result['Maximum_Predicted_Temp']:.2f} °C"
        )

        print(
            f"Future Risk Score      : "
            f"{result['Future_Risk_Score']}"
        )

        print(
            f"Future Risk Level      : "
            f"{result['Future_Risk_Level']}"
        )

        print(
            f"Risk Reason            : "
            f"{result['Risk_Reason']}"
        )


        # ----------------------------------------------------
        # 4. SAVE RESULT
        # ----------------------------------------------------

        output_df = pd.DataFrame(
            [result]
        )

        output_df.to_csv(
            OUTPUT_PATH,
            index=False
        )


        # ----------------------------------------------------
        # 5. LOG
        # ----------------------------------------------------

        logging.info(
            "Future risk monitoring completed. "
            "Score=%s, Level=%s",
            result["Future_Risk_Score"],
            result["Future_Risk_Level"]
        )


        # ----------------------------------------------------
        # 6. FINAL STATUS
        # ----------------------------------------------------

        print(
            "\n============================================================"
        )

        print(
            "FUTURE CLIMATE RISK MONITORING COMPLETED"
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


    except Exception as error:

        logging.exception(
            "Unexpected future risk monitoring error."
        )

        print(
            f"\nFUTURE RISK ERROR: {error}"
        )

        return None


# ============================================================
# MODULE EXECUTION
# ============================================================

if __name__ == "__main__":

    run_future_risk_monitoring()