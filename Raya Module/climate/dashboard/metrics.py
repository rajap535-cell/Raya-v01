import streamlit as st

from risk_engine.heatwave import (
    detect_heatwaves
)


def display_metrics(climate_df, forecast_df):

    avg_temp = round(
        climate_df["Temp_Max"].mean(),
        2
    )

    total_rainfall = round(
        climate_df["Rainfall"].sum(),
        2
    )

    avg_wind = round(
        climate_df["WindSpeed"].mean(),
        2
    )

    heatwave_result = detect_heatwaves(
        climate_df
    )

    heatwave_days = heatwave_result[
        "Heatwave Days"
    ]

    predicted_temp = round(
        forecast_df["yhat"].iloc[-1],
        2
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            " Average Temperature",
            f"{avg_temp} °C"
        )

    with col2:
        st.metric(
            " Total Rainfall",
            f"{total_rainfall} mm"
        )

    with col3:
        st.metric(
            " Average Wind Speed",
            f"{avg_wind} km/h"
        )

    col4, col5 = st.columns(2)

    with col4:
        st.metric(
            " Heatwave Days",
            heatwave_days
        )

    with col5:
        st.metric(
            " Predicted Temperature",
            f"{predicted_temp} °C"
        )