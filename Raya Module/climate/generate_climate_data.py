import requests
import pandas as pd
from pathlib import Path


# ============================================================
# OPEN-METEO HISTORICAL CLIMATE DATA GENERATOR
# ============================================================

LATITUDE = 18.5204
LONGITUDE = 73.8567

START_DATE = "2014-01-01"
END_DATE = "2024-12-31"

OUTPUT_PATH = Path("data/climate_data_10year.csv")


print("=" * 60)
print("OPEN-METEO HISTORICAL CLIMATE DATA GENERATOR")
print("=" * 60)

print(f"\nLocation : Pune")
print(f"Latitude : {LATITUDE}")
print(f"Longitude: {LONGITUDE}")
print(f"Period   : {START_DATE} to {END_DATE}")

# ------------------------------------------------------------
# Open-Meteo API
# ------------------------------------------------------------

url = "https://archive-api.open-meteo.com/v1/archive"

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

print("\nRequesting data from Open-Meteo...")

response = requests.get(
    url,
    params=params,
    timeout=60
)

print(f"\nSTATUS: {response.status_code}")

response.raise_for_status()

data = response.json()

# ------------------------------------------------------------
# Validate API response
# ------------------------------------------------------------

if "daily" not in data:

    raise ValueError(
        "Open-Meteo response does not contain daily data."
    )

daily = data["daily"]

print("\nOpen-Meteo daily fields received:")
print(daily.keys())

# ------------------------------------------------------------
# Create DataFrame
# ------------------------------------------------------------

df = pd.DataFrame({
    "Date": daily["time"],
    "Temp_Max": daily["temperature_2m_max"],
    "Temp_Min": daily["temperature_2m_min"],
    "Rainfall": daily["rain_sum"],
    "WindSpeed": daily["wind_speed_10m_max"]
})

# ------------------------------------------------------------
# Data preprocessing
# ------------------------------------------------------------

df["Date"] = pd.to_datetime(df["Date"])

df["Temp_Max"] = pd.to_numeric(
    df["Temp_Max"],
    errors="coerce"
)

df["Temp_Min"] = pd.to_numeric(
    df["Temp_Min"],
    errors="coerce"
)

df["Rainfall"] = pd.to_numeric(
    df["Rainfall"],
    errors="coerce"
)

df["WindSpeed"] = pd.to_numeric(
    df["WindSpeed"],
    errors="coerce"
)

# Sort chronologically
df = df.sort_values(
    "Date"
).reset_index(
    drop=True
)

# ------------------------------------------------------------
# Remove completely invalid rows
# ------------------------------------------------------------

df = df.dropna(
    subset=[
        "Date",
        "Temp_Max",
        "Temp_Min"
    ]
)

# ------------------------------------------------------------
# Create output directory
# ------------------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

# ------------------------------------------------------------
# Save dataset
# ------------------------------------------------------------

df.to_csv(
    OUTPUT_PATH,
    index=False
)

# ------------------------------------------------------------
# Dataset information
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("DATASET GENERATED SUCCESSFULLY")
print("=" * 60)

print(f"\nRows       : {len(df)}")

print(
    f"Start Date : {df['Date'].min().date()}"
)

print(
    f"End Date   : {df['Date'].max().date()}"
)

print(
    f"Missing    : {df.isna().sum().sum()}"
)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head().to_string(index=False))

print("\nLast 5 rows:")
print(df.tail().to_string(index=False))

print("\nSaved to:")
print(OUTPUT_PATH)

print("\nDataset statistics:")

print(
    df[
        [
            "Temp_Max",
            "Temp_Min",
            "Rainfall",
            "WindSpeed"
        ]
    ].describe().round(2)
)

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)