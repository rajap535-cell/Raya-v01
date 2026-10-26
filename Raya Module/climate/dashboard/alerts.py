import streamlit as st

from risk_engine.heatwave import detect_heatwaves
from risk_engine.rainfall import detect_rainfall_risk


def show_alerts(climate_df):

    st.subheader(" Climate Risk Intelligence")

    st.success(
        "Climate Monitoring System is Active."
    )

    st.info(
        "Forecast generated using Prophet Time Series Model."
    )

    heatwave_result = detect_heatwaves(
        climate_df
    )

    rainfall_result = detect_rainfall_risk(
        climate_df
    )

    if heatwave_result["Heatwave Days"] > 0:

        st.warning(
            f"🔥 Heatwave Alert: {heatwave_result['Heatwave Days']} heatwave days detected."
        )

    else:

        st.success(
            "✅ No Heatwave Risk Detected."
        )

    if rainfall_result["Heavy Rainfall"] > 0:

        st.error(
            f"🌧 Flood Alert: {rainfall_result['Heavy Rainfall']} heavy rainfall days detected."
        )

    else:

        st.success(
            "✅ No Heavy Rainfall Risk Detected."
        )