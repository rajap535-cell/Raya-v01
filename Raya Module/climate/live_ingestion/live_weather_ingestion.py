#live_weather_ingestion.py
import os
import requests
import pandas as pd


# ============================================================
# CONTINUOUS LIVE WEATHER INGESTION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "climate_data.csv")

# Pune, Maharashtra
LATITUDE = 18.5204
LONGITUDE = 73.8567

API_URL = "https://api.open-meteo.com/v1/forecast"


# ============================================================
# FETCH LIVE WEATHER
# ============================================================

def fetch_live_weather():

    print("=" * 60)
    print("TASK 006 - CONTINUOUS LIVE WEATHER INGESTION")
    print("=" * 60)

    print("\nFetching latest weather observations from Open-Meteo...")

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "rain_sum",
            "wind_speed_10m_max"
        ]),
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm"
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# CONVERT LIVE DATA
# ============================================================

def convert_to_dataframe(weather_data):

    daily = weather_data["daily"]

    df = pd.DataFrame({
        "Date": daily["time"],
        "Temp_Max": daily["temperature_2m_max"],
        "Temp_Min": daily["temperature_2m_min"],
        "Rainfall": daily["rain_sum"],
        "WindSpeed": daily["wind_speed_10m_max"]
    })

    return df


# ============================================================
# LOAD EXISTING DATA
# ============================================================

def load_existing_data():

    if not os.path.exists(DATA_FILE):

        print("\nClimate dataset not found.")

        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    # Ensure original column format
    df = df.rename(columns={
        "date": "Date",
        "temp_max": "Temp_Max",
        "temp_min": "Temp_Min",
        "rainfall": "Rainfall",
        "wind_speed": "WindSpeed"
    })

    return df


# ============================================================
# SYNCHRONIZE HISTORICAL + LIVE DATA
# ============================================================

def synchronize_dataset(existing_df, live_df):

    if existing_df.empty:

        combined_df = live_df.copy()

    else:

        combined_df = pd.concat(
            [existing_df, live_df],
            ignore_index=True
        )

    combined_df["Date"] = pd.to_datetime(
        combined_df["Date"],
        errors="coerce"
    )

    combined_df = combined_df.dropna(
        subset=["Date"]
    )

    # Replace existing observation if same date arrives again
    combined_df = combined_df.drop_duplicates(
        subset=["Date"],
        keep="last"
    )

    combined_df = combined_df.sort_values(
        "Date"
    )

    combined_df["Date"] = combined_df[
        "Date"
    ].dt.strftime("%Y-%m-%d")

    return combined_df


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        os.makedirs(
            DATA_DIR,
            exist_ok=True
        )

        weather_data = fetch_live_weather()

        live_df = convert_to_dataframe(
            weather_data
        )

        print("\nLive Observation")
        print("----------------")

        print(
            "Date        :",
            live_df.iloc[0]["Date"]
        )

        print(
            "Temp Max    :",
            live_df.iloc[0]["Temp_Max"],
            "°C"
        )

        print(
            "Temp Min    :",
            live_df.iloc[0]["Temp_Min"],
            "°C"
        )

        print(
            "Rainfall    :",
            live_df.iloc[0]["Rainfall"],
            "mm"
        )

        print(
            "Wind Speed  :",
            live_df.iloc[0]["WindSpeed"],
            "km/h"
        )

        existing_df = load_existing_data()

        print(
            "\nExisting Records :",
            len(existing_df)
        )

        combined_df = synchronize_dataset(
            existing_df,
            live_df
        )

        combined_df.to_csv(
            DATA_FILE,
            index=False
        )

        print(
            "Updated Records  :",
            len(combined_df)
        )

        print(
            "Latest Date      :",
            combined_df["Date"].max()
        )

        print("\n" + "=" * 60)
        print(
            "LIVE INGESTION COMPLETED SUCCESSFULLY"
        )
        print("=" * 60)

        print(
            f"\nClimate database updated:\n{DATA_FILE}"
        )

    except Exception as e:

        print(
            "\nERROR:",
            str(e)
        )


if __name__ == "__main__":
    main()