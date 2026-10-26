import os
import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

ROOT_DIR = Path(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Climate Mission Control",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# FILE PATHS
# ============================================================

DATA_PATH = ROOT_DIR / "data" / "climate_data.csv"

MULTIVARIABLE_PATH = (
    ROOT_DIR / "outputs" / "multivariable_forecast.csv"
)

UNCERTAINTY_PATH = (
    ROOT_DIR / "outputs" / "forecast_with_uncertainty.csv"
)

STATE_PATH = (
    ROOT_DIR / "outputs" / "future_climate_state.csv"
)

ANOMALY_PATH = (
    ROOT_DIR / "outputs" / "future_anomaly.csv"
)

RISK_PATH = (
    ROOT_DIR / "outputs" / "evidence_based_future_risk.csv"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def load_csv(path):

    if not path.exists():

        st.error(
            f"Required file not found: {path}"
        )

        return None

    try:

        return pd.read_csv(path)

    except Exception as e:

        st.error(
            f"Unable to load file: {path}\n\n{e}"
        )

        return None


# ============================================================
# LOAD DATA
# ============================================================

climate_df = load_csv(DATA_PATH)

forecast_df = load_csv(MULTIVARIABLE_PATH)

uncertainty_df = load_csv(UNCERTAINTY_PATH)

state_df = load_csv(STATE_PATH)

anomaly_df = load_csv(ANOMALY_PATH)

risk_df = load_csv(RISK_PATH)


# ============================================================
# STOP IF REQUIRED DATA IS MISSING
# ============================================================

required_data = [
    climate_df,
    forecast_df,
    uncertainty_df,
    state_df,
    anomaly_df,
    risk_df
]

if any(df is None for df in required_data):

    st.stop()


# ============================================================
# CLEAN CLIMATE DATA
# ============================================================

# Task 006 live ingestion may create lowercase live columns:
# date, temp_max, temp_min, rainfall, wind_speed
#
# Historical dataset uses:
# Date, Temp_Max, Temp_Min, Rainfall, WindSpeed
#
# We normalize both into one common structure.

if "date" in climate_df.columns:

    live_columns = [
        "date",
        "temp_max",
        "temp_min",
        "rainfall",
        "wind_speed"
    ]

    if all(col in climate_df.columns for col in live_columns):

        live_df = climate_df[live_columns].copy()

        live_df.columns = [
            "Date",
            "Temp_Max",
            "Temp_Min",
            "Rainfall",
            "WindSpeed"
        ]

        # Historical rows
        historical_df = climate_df[
            [
                "Date",
                "Temp_Max",
                "Temp_Min",
                "Rainfall",
                "WindSpeed"
            ]
        ].copy()

        # Remove rows where historical Date is missing
        historical_df = historical_df[
            historical_df["Date"].notna()
        ]

        # Keep valid live rows
        live_df = live_df[
            live_df["Date"].notna()
        ]

        # Combine historical and live observations
        climate_df = pd.concat(
            [
                historical_df,
                live_df
            ],
            ignore_index=True
        )

else:

    climate_df = climate_df[
        [
            "Date",
            "Temp_Max",
            "Temp_Min",
            "Rainfall",
            "WindSpeed"
        ]
    ].copy()


# ============================================================
# DATE CONVERSION
# ============================================================

climate_df["Date"] = pd.to_datetime(
    climate_df["Date"],
    errors="coerce"
)

forecast_df["Date"] = pd.to_datetime(
    forecast_df["Date"],
    errors="coerce"
)

uncertainty_df["Date"] = pd.to_datetime(
    uncertainty_df["Date"],
    errors="coerce"
)

state_df["Date"] = pd.to_datetime(
    state_df["Date"],
    errors="coerce"
)

anomaly_df["Date"] = pd.to_datetime(
    anomaly_df["Date"],
    errors="coerce"
)

risk_df["Date"] = pd.to_datetime(
    risk_df["Date"],
    errors="coerce"
)


# ============================================================
# NUMERIC CONVERSION
# ============================================================

climate_numeric_columns = [
    "Temp_Max",
    "Temp_Min",
    "Rainfall",
    "WindSpeed"
]

for column in climate_numeric_columns:

    climate_df[column] = pd.to_numeric(
        climate_df[column],
        errors="coerce"
    )


# Remove invalid climate rows
climate_df = climate_df[
    climate_df["Date"].notna()
].copy()

climate_df = climate_df.sort_values(
    "Date"
).reset_index(drop=True)


# ============================================================
# TITLE
# ============================================================

st.title(
    "🌍 Climate Intelligence Mission Control"
)

st.write(
    " Live Climate Monitoring, "
    "Multi-Variable Forecasting and Future Risk Intelligence"
)

st.success(
    " Intelligence System is Active"
)


# ============================================================
# CURRENT CLIMATE INTELLIGENCE
# ============================================================

st.subheader(
    " Current Climate Intelligence"
)


# Get latest valid row
valid_latest = climate_df.dropna(
    subset=[
        "Date",
        "Temp_Max",
        "Rainfall",
        "WindSpeed"
    ]
)

if not valid_latest.empty:

    latest = valid_latest.iloc[-1]

    latest_date = latest["Date"]

    latest_temp = latest["Temp_Max"]

    latest_rainfall = latest["Rainfall"]

    latest_wind = latest["WindSpeed"]

else:

    latest = None

    latest_date = None

    latest_temp = None

    latest_rainfall = None

    latest_wind = None


avg_temp = climate_df["Temp_Max"].mean()


col1, col2, col3, col4 = st.columns(4)


with col1:

    if pd.notna(latest_temp):

        st.metric(
            "Latest Temperature",
            f"{latest_temp:.2f} °C"
        )

    else:

        st.metric(
            "Latest Temperature",
            "N/A"
        )


with col2:

    if pd.notna(latest_rainfall):

        st.metric(
            "Latest Rainfall",
            f"{latest_rainfall:.2f} mm"
        )

    else:

        st.metric(
            "Latest Rainfall",
            "N/A"
        )


with col3:

    if pd.notna(latest_wind):

        st.metric(
            "Latest Wind Speed",
            f"{latest_wind:.2f} km/h"
        )

    else:

        st.metric(
            "Latest Wind Speed",
            "N/A"
        )


with col4:

    st.metric(
        "Historical Avg Temperature",
        f"{avg_temp:.2f} °C"
    )


# ============================================================
# LATEST LIVE OBSERVATION
# ============================================================

st.subheader(
    " Latest Live Climate Observation"
)


if latest is not None:

    live_col1, live_col2, live_col3, live_col4 = st.columns(4)

    with live_col1:

        st.info(
            f"Date\n\n"
            f"**{latest_date.strftime('%Y-%m-%d')}**"
        )

    with live_col2:

        st.info(
            f"Temperature\n\n"
            f"**{latest_temp:.2f} °C**"
        )

    with live_col3:

        st.info(
            f"Rainfall\n\n"
            f"**{latest_rainfall:.2f} mm**"
        )

    with live_col4:

        st.info(
            f"Wind Speed\n\n"
            f"**{latest_wind:.2f} km/h**"
        )

else:

    st.warning(
        "No valid live climate observation available."
    )


# ============================================================
# HISTORICAL TEMPERATURE TREND
# ============================================================

st.subheader(
    " Historical Temperature Trend"
)

temperature_df = climate_df.dropna(
    subset=["Date", "Temp_Max"]
)

fig_temp = px.line(
    temperature_df,
    x="Date",
    y="Temp_Max",
    title="Historical Maximum Temperature"
)

fig_temp.update_layout(
    xaxis_title="Date",
    yaxis_title="Temperature (°C)"
)

st.plotly_chart(
    fig_temp,
    width="stretch"
)


# ============================================================
# HISTORICAL RAINFALL TREND
# ============================================================

st.subheader(
    " Historical Rainfall Trend"
)

rainfall_df = climate_df.dropna(
    subset=["Date", "Rainfall"]
)

fig_rain = px.line(
    rainfall_df,
    x="Date",
    y="Rainfall",
    title="Historical Rainfall"
)

fig_rain.update_layout(
    xaxis_title="Date",
    yaxis_title="Rainfall (mm)"
)

st.plotly_chart(
    fig_rain,
    width="stretch"
)


# ============================================================
# MULTI-VARIABLE TEMPERATURE FORECAST
# ============================================================

st.subheader(
    " 30-Day Multi-Variable Forecast"
)

forecast_display = forecast_df.dropna(
    subset=["Date"]
).copy()


fig_forecast_temp = px.line(
    forecast_display,
    x="Date",
    y="Predicted_Temp_Max",
    title="Predicted Maximum Temperature"
)

fig_forecast_temp.update_layout(
    xaxis_title="Forecast Date",
    yaxis_title="Temperature (°C)"
)

st.plotly_chart(
    fig_forecast_temp,
    width="stretch"
)


# ============================================================
# RAINFALL FORECAST
# ============================================================

st.subheader(
    " Predicted Rainfall"
)

fig_forecast_rain = px.line(
    forecast_display,
    x="Date",
    y="Predicted_Rainfall",
    title="Predicted Rainfall"
)

fig_forecast_rain.update_layout(
    xaxis_title="Forecast Date",
    yaxis_title="Rainfall (mm)"
)

st.plotly_chart(
    fig_forecast_rain,
    width="stretch"
)


# ============================================================
# WIND FORECAST
# ============================================================

st.subheader(
    " Predicted Wind Speed"
)

fig_forecast_wind = px.line(
    forecast_display,
    x="Date",
    y="Predicted_WindSpeed",
    title="Predicted Wind Speed"
)

fig_forecast_wind.update_layout(
    xaxis_title="Forecast Date",
    yaxis_title="Wind Speed (km/h)"
)

st.plotly_chart(
    fig_forecast_wind,
    width="stretch"
)


# ============================================================
# FORECAST UNCERTAINTY
# ============================================================

st.subheader(
    " Forecast Uncertainty"
)

fig_uncertainty = px.line(
    uncertainty_df,
    x="Date",
    y=[
        "Temp_Lower",
        "Predicted_Temp_Max",
        "Temp_Upper"
    ],
    title="Temperature Forecast with Uncertainty Range"
)

fig_uncertainty.update_layout(
    xaxis_title="Forecast Date",
    yaxis_title="Temperature (°C)"
)

st.plotly_chart(
    fig_uncertainty,
    width="stretch"
)


# ============================================================
# UNCERTAINTY SUMMARY
# ============================================================

st.subheader(
    " Uncertainty Estimates"
)

u1, u2, u3 = st.columns(3)


temp_uncertainty = (
    uncertainty_df["Predicted_Temp_Max"]
    - uncertainty_df["Temp_Lower"]
).mean()


rain_uncertainty = (
    uncertainty_df["Rainfall_Upper"]
    - uncertainty_df["Predicted_Rainfall"]
).mean()


wind_uncertainty = (
    uncertainty_df["WindSpeed_Upper"]
    - uncertainty_df["Predicted_WindSpeed"]
).mean()


with u1:

    st.metric(
        "Temperature Uncertainty",
        f"±{temp_uncertainty:.2f} °C"
    )


with u2:

    st.metric(
        "Rainfall Uncertainty",
        f"±{rain_uncertainty:.2f} mm"
    )


with u3:

    st.metric(
        "Wind Uncertainty",
        f"±{wind_uncertainty:.2f} km/h"
    )


# ============================================================
# FUTURE CLIMATE STATE
# ============================================================

st.subheader(
    " Predictive Climate State"
)

state_counts = (
    state_df["Climate_State"]
    .value_counts()
    .reset_index()
)

state_counts.columns = [
    "Climate_State",
    "Days"
]


fig_state = px.bar(
    state_counts,
    x="Climate_State",
    y="Days",
    title="Future Climate State Distribution"
)

st.plotly_chart(
    fig_state,
    width="stretch"
)


state_col1, state_col2 = st.columns(2)


dominant_state = (
    state_df["Climate_State"]
    .mode()
    .iloc[0]
)


avg_confidence = (
    state_df["Confidence_Score"]
    .mean()
)


with state_col1:

    st.metric(
        "Dominant Future Climate State",
        dominant_state
    )


with state_col2:

    st.metric(
        "Average Confidence",
        f"{avg_confidence:.2f}%"
    )


# ============================================================
# FUTURE ANOMALY
# ============================================================

st.subheader(
    " Future Anomaly Intelligence"
)

anomaly_counts = (
    anomaly_df["Future_Anomaly"]
    .value_counts()
    .reset_index()
)

anomaly_counts.columns = [
    "Future_Anomaly",
    "Days"
]


fig_anomaly = px.bar(
    anomaly_counts,
    x="Future_Anomaly",
    y="Days",
    title="Future Anomaly Distribution"
)

st.plotly_chart(
    fig_anomaly,
    width="stretch"
)


normal_days = (
    anomaly_df["Future_Anomaly"]
    .eq("NORMAL")
    .sum()
)


anomaly_days = (
    len(anomaly_df)
    - normal_days
)


a1, a2 = st.columns(2)


with a1:

    st.metric(
        "Normal Forecast Days",
        normal_days
    )


with a2:

    st.metric(
        "Anomalous Forecast Days",
        anomaly_days
    )


# ============================================================
# EVIDENCE-DRIVEN FUTURE RISK
# ============================================================

st.subheader(
    " Evidence-Driven Future Risk"
)

risk_counts = (
    risk_df["Risk_Level"]
    .value_counts()
    .reset_index()
)

risk_counts.columns = [
    "Risk_Level",
    "Days"
]


fig_risk = px.bar(
    risk_counts,
    x="Risk_Level",
    y="Days",
    title="Future Risk Level Distribution"
)

st.plotly_chart(
    fig_risk,
    width="stretch"
)


risk_col1, risk_col2, risk_col3 = st.columns(3)


dominant_risk = (
    risk_df["Risk_Level"]
    .mode()
    .iloc[0]
)


average_risk = (
    risk_df["Risk_Score"]
    .mean()
)


maximum_risk = (
    risk_df["Risk_Score"]
    .max()
)


with risk_col1:

    st.metric(
        "Dominant Risk Level",
        dominant_risk
    )


with risk_col2:

    st.metric(
        "Average Risk Score",
        f"{average_risk:.2f}"
    )


with risk_col3:

    st.metric(
        "Maximum Risk Score",
        f"{maximum_risk:.2f}"
    )


# ============================================================
# RECOMMENDED ACTIONS
# ============================================================

st.subheader(
    " Recommended Actions"
)

actions = (
    risk_df["Recommended_Action"]
    .value_counts()
    .reset_index()
)

actions.columns = [
    "Recommended_Action",
    "Days"
]


st.dataframe(
    actions,
    width="stretch"
)


# ============================================================
# FUTURE RISK TABLE
# ============================================================

st.subheader(
    " Future Risk Intelligence"
)

risk_columns = [
    "Date",
    "Climate_State",
    "Future_Anomaly",
    "Anomaly_Severity",
    "Confidence_Score",
    "Risk_Score",
    "Risk_Level",
    "Recommended_Action"
]

risk_display = risk_df[
    risk_columns
].copy()


st.dataframe(
    risk_display,
    width="stretch"
)


# ============================================================
# FORECAST TABLE
# ============================================================

st.subheader(
    " 30-Day Forecast Data"
)

st.dataframe(
    forecast_df,
    width="stretch"
)


# ============================================================
# SYSTEM STATUS
# ============================================================

st.subheader(
    " Task 006 System Status"
)

status_col1, status_col2, status_col3 = st.columns(3)


with status_col1:

    st.success(
        "Live Ingestion\n\nACTIVE"
    )


with status_col2:

    st.success(
        "Forecast Intelligence\n\nACTIVE"
    )


with status_col3:

    st.success(
        "Future Risk Engine\n\nACTIVE"
    )


# ============================================================
# PROJECT SUMMARY
# ============================================================

st.subheader(
    " Task 006 Summary"
)

st.markdown(
"""
### Climate Intelligence System — Task 006

Task 006 extends the Climate Intelligence System from historical
monitoring into predictive and future-oriented climate intelligence.

### Completed Intelligence Modules

✅ Continuous Live Weather Ingestion

✅ Multi-Variable Climate Forecasting

✅ Forecast Uncertainty Engine

✅ Predictive Climate State Engine

✅ Future Anomaly Engine

✅ Evidence-Driven Future Risk Engine

### Technology Stack

- Python
- Pandas
- NumPy
- Prophet
- Streamlit
- Plotly
- Scikit-learn

### Intelligence Flow

Live Observation → Forecast → Uncertainty → Climate State
→ Future Anomaly → Evidence-Driven Risk → Recommended Action
"""
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "RAYA Climate Intelligence System "
)