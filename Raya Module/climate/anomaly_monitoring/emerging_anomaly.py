import logging
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "climate_data.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "emerging_anomalies.csv"
LOG_PATH = BASE_DIR / "logs" / "emerging_anomaly.log"


# Number of recent days used for monitoring
RECENT_WINDOW = 30

# Number of previous days used as reference
BASELINE_WINDOW = 90


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
# LOAD DATA
# ============================================================

def load_data():

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"Climate data file not found: {DATA_PATH}"
        )

    df = pd.read_csv(
        DATA_PATH
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

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

    df = (
        df.dropna(
            subset=[
                "Date",
                "Temp_Max",
                "Temp_Min",
                "Rainfall",
                "WindSpeed"
            ]
        )
        .sort_values("Date")
        .reset_index(drop=True)
    )

    return df


# ============================================================
# CALCULATE BASELINE
# ============================================================

def calculate_baseline(df):

    if len(df) < BASELINE_WINDOW + RECENT_WINDOW:

        raise ValueError(
            "Not enough climate records for anomaly monitoring."
        )

    baseline = df.iloc[
        -(
            BASELINE_WINDOW
            + RECENT_WINDOW
        ):
        -RECENT_WINDOW
    ]

    return {
        "Temp_Max": baseline["Temp_Max"].mean(),
        "Temp_Min": baseline["Temp_Min"].mean(),
        "Rainfall": baseline["Rainfall"].mean(),
        "WindSpeed": baseline["WindSpeed"].mean()
    }


# ============================================================
# CALCULATE RECENT CONDITIONS
# ============================================================

def calculate_recent_conditions(df):

    recent = df.tail(
        RECENT_WINDOW
    )

    return {
        "Temp_Max": recent["Temp_Max"].mean(),
        "Temp_Min": recent["Temp_Min"].mean(),
        "Rainfall": recent["Rainfall"].mean(),
        "WindSpeed": recent["WindSpeed"].mean()
    }


# ============================================================
# CALCULATE ANOMALY SCORE
# ============================================================

def calculate_anomaly_score(
    baseline,
    recent
):

    differences = {}

    for variable in baseline:

        base_value = baseline[variable]
        recent_value = recent[variable]

        if base_value == 0:

            difference_percent = 0.0

        else:

            difference_percent = (
                (
                    recent_value
                    - base_value
                )
                / abs(base_value)
            ) * 100

        differences[variable] = difference_percent


    # --------------------------------------------------------
    # Individual anomaly flags
    # --------------------------------------------------------

    flags = []

    if abs(differences["Temp_Max"]) >= 5:

        flags.append(
            "Temperature change"
        )

    if abs(differences["Temp_Min"]) >= 5:

        flags.append(
            "Minimum temperature change"
        )

    if abs(differences["Rainfall"]) >= 30:

        flags.append(
            "Rainfall change"
        )

    if abs(differences["WindSpeed"]) >= 15:

        flags.append(
            "Wind speed change"
        )


    # --------------------------------------------------------
    # Determine anomaly level
    # --------------------------------------------------------

    flag_count = len(flags)

    if flag_count >= 3:

        anomaly_level = "HIGH"

    elif flag_count == 2:

        anomaly_level = "MODERATE"

    elif flag_count == 1:

        anomaly_level = "LOW"

    else:

        anomaly_level = "NORMAL"


    return (
        differences,
        flags,
        anomaly_level
    )


# ============================================================
# GENERATE MONITORING RECORD
# ============================================================

def generate_monitoring_record(
    df,
    baseline,
    recent
):

    differences, flags, anomaly_level = (
        calculate_anomaly_score(
            baseline,
            recent
        )
    )

    latest_date = (
        df["Date"].max()
    )

    record = {

        "Date": latest_date,

        "Baseline_Temp_Max": round(
            baseline["Temp_Max"],
            2
        ),

        "Recent_Temp_Max": round(
            recent["Temp_Max"],
            2
        ),

        "Temp_Max_Change_Percent": round(
            differences["Temp_Max"],
            2
        ),

        "Baseline_Temp_Min": round(
            baseline["Temp_Min"],
            2
        ),

        "Recent_Temp_Min": round(
            recent["Temp_Min"],
            2
        ),

        "Temp_Min_Change_Percent": round(
            differences["Temp_Min"],
            2
        ),

        "Baseline_Rainfall": round(
            baseline["Rainfall"],
            2
        ),

        "Recent_Rainfall": round(
            recent["Rainfall"],
            2
        ),

        "Rainfall_Change_Percent": round(
            differences["Rainfall"],
            2
        ),

        "Baseline_WindSpeed": round(
            baseline["WindSpeed"],
            2
        ),

        "Recent_WindSpeed": round(
            recent["WindSpeed"],
            2
        ),

        "WindSpeed_Change_Percent": round(
            differences["WindSpeed"],
            2
        ),

        "Anomaly_Flags": (
            ", ".join(flags)
            if flags
            else "None"
        ),

        "Emerging_Anomaly_Level": (
            anomaly_level
        )
    }

    return record


# ============================================================
# PIPELINE
# ============================================================

def run_emerging_anomaly_detection():

    try:

        print(
            "\n============================================================"
        )

        print(
            "TASK 005 - EMERGING ANOMALY DETECTION"
        )

        print(
            "============================================================"
        )


        # ----------------------------------------------------
        # 1. LOAD DATA
        # ----------------------------------------------------

        df = load_data()

        print(
            f"\nRecords analysed: {len(df)}"
        )


        # ----------------------------------------------------
        # 2. CALCULATE BASELINE
        # ----------------------------------------------------

        baseline = calculate_baseline(
            df
        )

        print(
            "\nReference Baseline"
        )

        print(
            "------------------"
        )

        print(
            f"Temperature Max : {baseline['Temp_Max']:.2f} °C"
        )

        print(
            f"Temperature Min : {baseline['Temp_Min']:.2f} °C"
        )

        print(
            f"Rainfall        : {baseline['Rainfall']:.2f} mm"
        )

        print(
            f"Wind Speed      : {baseline['WindSpeed']:.2f} km/h"
        )


        # ----------------------------------------------------
        # 3. RECENT CONDITIONS
        # ----------------------------------------------------

        recent = calculate_recent_conditions(
            df
        )

        print(
            "\nRecent 30-Day Conditions"
        )

        print(
            "------------------------"
        )

        print(
            f"Temperature Max : {recent['Temp_Max']:.2f} °C"
        )

        print(
            f"Temperature Min : {recent['Temp_Min']:.2f} °C"
        )

        print(
            f"Rainfall        : {recent['Rainfall']:.2f} mm"
        )

        print(
            f"Wind Speed      : {recent['WindSpeed']:.2f} km/h"
        )


        # ----------------------------------------------------
        # 4. DETECT EMERGING ANOMALY
        # ----------------------------------------------------

        record = generate_monitoring_record(
            df,
            baseline,
            recent
        )


        print(
            "\nEmerging Anomaly Assessment"
        )

        print(
            "----------------------------"
        )

        print(
            f"Anomaly Level   : "
            f"{record['Emerging_Anomaly_Level']}"
        )

        print(
            f"Anomaly Flags   : "
            f"{record['Anomaly_Flags']}"
        )


        # ----------------------------------------------------
        # 5. SAVE RESULT
        # ----------------------------------------------------

        output_df = pd.DataFrame(
            [record]
        )

        output_df.to_csv(
            OUTPUT_PATH,
            index=False
        )


        logging.info(
            "Emerging anomaly detection completed. "
            "Level=%s",
            record[
                "Emerging_Anomaly_Level"
            ]
        )


        # ----------------------------------------------------
        # 6. FINAL STATUS
        # ----------------------------------------------------

        print(
            "\n============================================================"
        )

        print(
            "EMERGING ANOMALY DETECTION COMPLETED"
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
            "Unexpected anomaly detection error."
        )

        print(
            f"\nANOMALY DETECTION ERROR: {error}"
        )

        return None


# ============================================================
# MODULE EXECUTION
# ============================================================

if __name__ == "__main__":

    run_emerging_anomaly_detection()