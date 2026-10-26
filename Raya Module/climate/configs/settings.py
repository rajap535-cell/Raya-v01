# ============================================
# CLIMATE INTELLIGENCE SYSTEM - SETTINGS
# ============================================

# --------------------------------------------
# Location
# --------------------------------------------

CITY = "Pune"

LATITUDE = 18.5204
LONGITUDE = 73.8567


# --------------------------------------------
# Historical Climate Dataset
# --------------------------------------------

# Final dataset: 11 years (2014-2024)
START_DATE = "2014-01-01"
END_DATE = "2024-12-31"


# --------------------------------------------
# Forecast Configuration
# --------------------------------------------

FORECAST_DAYS = 30


# --------------------------------------------
# Climate Risk Thresholds
# --------------------------------------------

HEATWAVE_THRESHOLD = 40
SEVERE_HEATWAVE_THRESHOLD = 45

HEAVY_RAINFALL_THRESHOLD = 50
EXTREME_RAINFALL_THRESHOLD = 100


# --------------------------------------------
# File Paths
# --------------------------------------------

# Final 11-year climate dataset
DATA_PATH = "data/climate_data.csv"

# Forecast output
FORECAST_PATH = "data/temperature_forecast.csv"

# System log
LOG_PATH = "logs/system.log"