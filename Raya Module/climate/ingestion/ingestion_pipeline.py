import logging
from pathlib import Path

from configs.settings import DATA_PATH
from ingestion.weather_api import fetch_historical_climate_data
from ingestion.validators import validate_data


# -------------------------------------------------
# Logging Configuration
# -------------------------------------------------

logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_ingestion():
    """
    Complete climate data ingestion pipeline.

    Flow:
    Open-Meteo API
        ↓
    Fetch climate data
        ↓
    Validate data
        ↓
    Save validated data
        ↓
    Return DataFrame
    """

    try:

        logging.info(
            "Starting Climate Data Ingestion Pipeline."
        )

        # -----------------------------------------
        # Step 1: Fetch data from Open-Meteo
        # -----------------------------------------

        df = fetch_historical_climate_data()

        logging.info(
            f"Fetched {len(df)} climate records from Open-Meteo."
        )

        # -----------------------------------------
        # Step 2: Validate data
        # -----------------------------------------

        validate_data(df)

        logging.info(
            "Climate data validation completed successfully."
        )

        # -----------------------------------------
        # Step 3: Create data directory
        # -----------------------------------------

        data_path = Path(DATA_PATH)

        data_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # -----------------------------------------
        # Step 4: Save validated data
        # -----------------------------------------

        df.to_csv(
            data_path,
            index=False
        )

        logging.info(
            f"Climate dataset saved successfully to {DATA_PATH}"
        )

        print("=" * 60)
        print("CLIMATE DATA INGESTION SUCCESSFUL")
        print("=" * 60)

        print(f"Rows       : {len(df)}")
        print(f"Start Date : {df['Date'].min().date()}")
        print(f"End Date   : {df['Date'].max().date()}")
        print(
            f"Missing    : {df.isna().sum().sum()}"
        )

        print("\nSaved to:")
        print(DATA_PATH)

        return df

    # ---------------------------------------------
    # API / Request / Network error
    # ---------------------------------------------

    except Exception as e:

        logging.error(
            f"Climate Data Ingestion Failed: {e}"
        )

        print(
            "Climate Data Ingestion Failed."
        )

        print(
            f"Error: {e}"
        )

        raise