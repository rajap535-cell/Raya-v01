import os
import sys
from pathlib import Path

# --------------------------------
# Project Root Path
# --------------------------------

ROOT_DIR = Path(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# --------------------------------
# Imports
# --------------------------------

import streamlit as st
import pandas as pd

from configs.settings import (
    DATA_PATH,
    FORECAST_PATH
)

from dashboard.charts import (
    temperature_chart,
    rainfall_chart,
    forecast_chart,
    confidence_interval_chart,
    actual_vs_predicted_chart
)

from dashboard.metrics import (
    display_metrics
)

from dashboard.alerts import (
    show_alerts
)


# --------------------------------
# Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Climate Intelligence Dashboard",
    layout="wide"
)


# --------------------------------
# Absolute Paths
# --------------------------------

climate_path = ROOT_DIR / DATA_PATH
forecast_path = ROOT_DIR / FORECAST_PATH
comparison_path = ROOT_DIR / "outputs" / "actual_vs_predicted_regressors.csv"


# --------------------------------
# Load Climate Data
# --------------------------------

climate_df = pd.read_csv(
    climate_path
)


# --------------------------------
# Load Forecast Data
# --------------------------------

forecast_df = pd.read_csv(
    forecast_path
)


# --------------------------------
# Load Actual vs Predicted Data
# --------------------------------

comparison_df = None

if comparison_path.exists():

    comparison_df = pd.read_csv(
        comparison_path
    )

    comparison_df["Date"] = pd.to_datetime(
        comparison_df["Date"],
        errors="coerce"
    )

else:

    st.warning(
        "Actual vs Predicted comparison file not found."
    )


# --------------------------------
# Title
# --------------------------------

st.title(
    "🌍 Climate Intelligence Dashboard"
)

st.write(
    "Real-Time Climate Monitoring and Temperature Forecasting System"
)


# --------------------------------
# Metrics
# --------------------------------

display_metrics(
    climate_df,
    forecast_df
)


# --------------------------------
# Climate Risk Alerts
# --------------------------------

show_alerts(
    climate_df
)


# --------------------------------
# Temperature Trend
# --------------------------------

st.subheader(
    "🌡 Temperature Trend"
)

st.plotly_chart(
    temperature_chart(climate_df),
    width="stretch"
)


# --------------------------------
# Rainfall Trend
# --------------------------------

st.subheader(
    "🌧 Rainfall Trend"
)

st.plotly_chart(
    rainfall_chart(climate_df),
    width="stretch"
)


# --------------------------------
# Temperature Forecast
# --------------------------------

st.subheader(
    "📈 Temperature Forecast"
)

st.plotly_chart(
    forecast_chart(forecast_df),
    width="stretch"
)


# --------------------------------
# Forecast Confidence Interval
# --------------------------------

st.subheader(
    "📊 Forecast Confidence Interval"
)

st.plotly_chart(
    confidence_interval_chart(forecast_df),
    width="stretch"
)


# --------------------------------
# Actual vs Predicted Temperature
# --------------------------------

st.subheader(
    "🎯 Actual vs Predicted Maximum Temperature"
)

if comparison_df is not None:

    st.plotly_chart(
        actual_vs_predicted_chart(
            comparison_df
        ),
        width="stretch"
    )

else:

    st.info(
        "Actual vs Predicted comparison data is not available."
    )


# --------------------------------
# Forecast Data
# --------------------------------

st.subheader(
    "📋 Forecast Data"
)

st.dataframe(
    forecast_df.tail(15),
    width="stretch"
)


# --------------------------------
# Project Summary
# --------------------------------

st.subheader(
    "📄 Project Summary"
)

st.success(
"""
### Climate Intelligence System

This dashboard provides an end-to-end climate monitoring and temperature forecasting solution.

### Key Features

✅ Climate Data Analysis

✅ Temperature Trend Visualization

✅ Rainfall Trend Analysis

✅ Prophet-based Temperature Forecasting

✅ Actual vs Predicted Temperature Comparison

✅ Forecast Confidence Interval

✅ Climate Risk Monitoring

✅ Interactive Forecast Dashboard

### Technology Stack

• Python

• Streamlit

• Prophet

• Pandas

• Plotly

• Scikit-learn
"""
)