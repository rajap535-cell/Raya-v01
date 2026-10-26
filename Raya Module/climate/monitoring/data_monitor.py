import logging
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "climate_data.csv"
LOG_PATH = BASE_DIR / "logs" / "task5_monitoring.log"


REQUIRED_COLUMNS = [
    "Date",
    "Temp_Max",
    "Temp_Min",
    "Rainfall",
    "WindSpeed"
]


# ============================================================
# LOGGING
# ============================================================

LOG_PATH.parent.mkdir(
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

    return df


# ============================================================
# MONITOR DATASET
# ============================================================

def monitor_dataset(df):

    return {
        "total_records": len(df),

        "missing_values": int(
            df[REQUIRED_COLUMNS]
            .isna()
            .sum()
            .sum()
        ),

        "duplicate_dates": int(
            df["Date"]
            .duplicated()
            .sum()
        ),

        "start_date": df["Date"].min(),

        "end_date": df["Date"].max()
    }


# ============================================================
# CHECK DATE CONTINUITY
# ============================================================

def check_date_continuity(df):

    dates = (
        df["Date"]
        .dropna()
        .sort_values()
        .drop_duplicates()
    )

    if len(dates) < 2:

        return {
            "missing_dates": 0,
            "status": "INSUFFICIENT DATA"
        }

    expected_dates = pd.date_range(
        start=dates.min(),
        end=dates.max(),
        freq="D"
    )

    missing_dates = expected_dates.difference(
        dates
    )

    if len(missing_dates) == 0:

        status = "CONTINUOUS"

    else:

        status = "GAPS DETECTED"

    return {
        "missing_dates": len(missing_dates),
        "status": status,
        "missing_date_values": missing_dates
    }


# ============================================================
# GET LATEST OBSERVATION
# ============================================================

def get_latest_observation(df):

    latest_row = (
        df.sort_values("Date")
        .iloc[-1]
    )

    return latest_row


# ============================================================
# MONITORING PIPELINE
# ============================================================

def run_monitoring():

    try:

        print(
            "\n============================================================"
        )

        print(
            "TASK 005 - CLIMATE DATA MONITORING"
        )

        print(
            "============================================================"
        )


        # ----------------------------------------------------
        # 1. LOAD DATA
        # ----------------------------------------------------

        df = load_data()

        print(
            f"\nRecords monitored: {len(df)}"
        )


        # ----------------------------------------------------
        # 2. DATASET MONITORING
        # ----------------------------------------------------

        result = monitor_dataset(
            df
        )

        print(
            "\nDataset Monitoring"
        )

        print(
            "------------------"
        )

        print(
            f"Total records   : {result['total_records']}"
        )

        print(
            f"Missing values  : {result['missing_values']}"
        )

        print(
            f"Duplicate dates : {result['duplicate_dates']}"
        )

        print(
            f"Start date      : {result['start_date'].date()}"
        )

        print(
            f"End date        : {result['end_date'].date()}"
        )


        # ----------------------------------------------------
        # 3. DATE CONTINUITY
        # ----------------------------------------------------

        continuity = check_date_continuity(
            df
        )

        print(
            "\nDate Continuity"
        )

        print(
            "---------------"
        )

        print(
            f"Status          : {continuity['status']}"
        )

        print(
            f"Missing dates   : {continuity['missing_dates']}"
        )


        # ----------------------------------------------------
        # 4. LATEST OBSERVATION
        # ----------------------------------------------------

        latest = get_latest_observation(
            df
        )

        print(
            "\nLatest Climate Observation"
        )

        print(
            "--------------------------"
        )

        print(
            f"Date            : {latest['Date'].date()}"
        )

        print(
            f"Temp Max        : {latest['Temp_Max']:.2f} °C"
        )

        print(
            f"Temp Min        : {latest['Temp_Min']:.2f} °C"
        )

        print(
            f"Rainfall        : {latest['Rainfall']:.2f} mm"
        )

        print(
            f"Wind Speed      : {latest['WindSpeed']:.2f} km/h"
        )


        # ----------------------------------------------------
        # 5. LOG RESULT
        # ----------------------------------------------------

        logging.info(
            "Monitoring completed successfully. "
            "Records=%s, Missing=%s, Duplicates=%s, "
            "Start=%s, End=%s, Continuity=%s",
            result["total_records"],
            result["missing_values"],
            result["duplicate_dates"],
            result["start_date"],
            result["end_date"],
            continuity["status"]
        )


        # ----------------------------------------------------
        # 6. FINAL STATUS
        # ----------------------------------------------------

        print(
            "\n============================================================"
        )

        print(
            "CLIMATE DATA MONITORING COMPLETED SUCCESSFULLY"
        )

        print(
            "============================================================"
        )


        return {
            "dataset": result,
            "continuity": continuity
        }


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
            "Unexpected monitoring error."
        )

        print(
            f"\nMONITORING ERROR: {error}"
        )

        return None


# ============================================================
# MODULE EXECUTION
# ============================================================

if __name__ == "__main__":

    run_monitoring()