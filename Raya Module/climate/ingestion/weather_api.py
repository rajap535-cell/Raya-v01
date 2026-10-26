import logging
import requests
import pandas as pd

from configs.settings import (
    LATITUDE,
    LONGITUDE,
    START_DATE,
    END_DATE
)


OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_historical_climate_data():
    """
    Fetch historical daily climate data from Open-Meteo.
    """

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "rain_sum",
            "wind_speed_10m_max"
        ],
        "timezone": "Asia/Kolkata"
    }

    try:
        logging.info("Requesting climate data from Open-Meteo.")

        response = requests.get(
            OPEN_METEO_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if "daily" not in data:
            raise ValueError(
                "Daily climate data not found in Open-Meteo response."
            )

        daily = data["daily"]

        df = pd.DataFrame({
            "Date": daily["time"],
            "Temp_Max": daily["temperature_2m_max"],
            "Temp_Min": daily["temperature_2m_min"],
            "Rainfall": daily["rain_sum"],
            "WindSpeed": daily["wind_speed_10m_max"]
        })

        df["Date"] = pd.to_datetime(df["Date"])

        logging.info(
            f"Open-Meteo data fetched successfully. Rows: {len(df)}"
        )

        return df

    except requests.RequestException as e:

        logging.error(
            f"Open-Meteo API request failed: {e}"
        )

        raise

    except Exception as e:

        logging.error(
            f"Climate data fetching failed: {e}"
        )

        raise