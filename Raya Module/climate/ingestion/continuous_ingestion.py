import logging
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "climate_data.csv"
LOG_PATH = BASE_DIR / "logs" / "task5_ingestion.log"


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
# LOAD CLIMATE DATA
# ============================================================

def load_climate_data():

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"Climate data file not found: {DATA_PATH}"
        )

    df = pd.read_csv(
        DATA_PATH
    )

    logging.info(
        "Climate dataset loaded successfully."
    )

    return df


# ============================================================
# VALIDATE DATA
# ============================================================

def validate_data(df):

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df = df.copy()

    # --------------------------------------------------------
    # DATE VALIDATION
    # --------------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # NUMERIC VALIDATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # REMOVE INVALID RECORDS
    # --------------------------------------------------------

    before_count = len(df)

    df = df.dropna(
        subset=REQUIRED_COLUMNS
    )

    removed_count = (
        before_count
        - len(df)
    )

    if removed_count > 0:

        logging.warning(
            "%s invalid records removed.",
            removed_count
        )

    # --------------------------------------------------------
    # SORT DATA
    # --------------------------------------------------------

    df = df.sort_values(
        "Date"
    ).reset_index(
        drop=True
    )

    return df


# ============================================================
# REMOVE DUPLICATE DATES
# ============================================================

def remove_duplicates(df):

    before_count = len(df)

    df = df.drop_duplicates(
        subset=["Date"],
        keep="last"
    )

    removed_count = (
        before_count
        - len(df)
    )

    if removed_count > 0:

        logging.info(
            "%s duplicate records removed.",
            removed_count
        )

    return df


# ============================================================
# DATA QUALITY SUMMARY
# ============================================================

def generate_data_quality_summary(df):

    summary = {
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
        "start_date": str(
            df["Date"].min().date()
        ),
        "end_date": str(
            df["Date"].max().date()
        )
    }

    return summary


# ============================================================
# CONTINUOUS INGESTION PIPELINE
# ============================================================

def run_ingestion():

    try:

        print(
            "\n============================================================"
        )

        print(
            "TASK 005 - CONTINUOUS CLIMATE DATA INGESTION"
        )

        print(
            "============================================================"
        )

        # ----------------------------------------------------
        # 1. LOAD DATA
        # ----------------------------------------------------

        df = load_climate_data()

        print(
            f"\nRecords loaded: {len(df)}"
        )

        # ----------------------------------------------------
        # 2. VALIDATE DATA
        # ----------------------------------------------------

        df = validate_data(
            df
        )

        print(
            f"Valid records: {len(df)}"
        )

        # ----------------------------------------------------
        # 3. REMOVE DUPLICATES
        # ----------------------------------------------------

        df = remove_duplicates(
            df
        )

        print(
            f"Records after duplicate removal: {len(df)}"
        )

        # ----------------------------------------------------
        # 4. DATA QUALITY CHECK
        # ----------------------------------------------------

        quality = generate_data_quality_summary(
            df
        )

        print(
            "\nData Quality Summary"
        )

        print(
            "--------------------"
        )

        print(
            f"Total records      : {quality['total_records']}"
        )

        print(
            f"Missing values     : {quality['missing_values']}"
        )

        print(
            f"Duplicate dates    : {quality['duplicate_dates']}"
        )

        print(
            f"Start date         : {quality['start_date']}"
        )

        print(
            f"End date           : {quality['end_date']}"
        )

        # ----------------------------------------------------
        # 5. SAVE CLEAN DATA
        # ----------------------------------------------------

        df.to_csv(
            DATA_PATH,
            index=False
        )

        logging.info(
            "Validated climate dataset saved successfully."
        )

        # ----------------------------------------------------
        # 6. FINAL STATUS
        # ----------------------------------------------------

        print(
            "\n============================================================"
        )

        print(
            "CONTINUOUS INGESTION COMPLETED SUCCESSFULLY"
        )

        print(
            "============================================================"
        )

        print(
            f"Clean dataset saved to: {DATA_PATH}"
        )

        return df

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
            "Unexpected ingestion error."
        )

        print(
            f"\nINGESTION ERROR: {error}"
        )

        return None


# ============================================================
# MODULE EXECUTION
# ============================================================

if __name__ == "__main__":

    run_ingestion()