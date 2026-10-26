import plotly.express as px
import plotly.graph_objects as go


# --------------------------------
# Temperature Trend Chart
# --------------------------------

def temperature_chart(climate_df):

    fig = px.line(
        climate_df,
        x="Date",
        y="Temp_Max",
        title="Temperature Trend"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        template="plotly_white"
    )

    return fig


# --------------------------------
# Rainfall Trend Chart
# --------------------------------

def rainfall_chart(climate_df):

    fig = px.bar(
        climate_df,
        x="Date",
        y="Rainfall",
        title="Rainfall Trend"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Rainfall (mm)",
        template="plotly_white"
    )

    return fig


# --------------------------------
# Temperature Forecast Chart
# --------------------------------

def forecast_chart(forecast_df):

    fig = px.line(
        forecast_df,
        x="ds",
        y="yhat",
        title="Temperature Forecast"
    )

    fig.update_layout(
        xaxis_title="Forecast Date",
        yaxis_title="Predicted Temperature (°C)",
        template="plotly_white"
    )

    return fig


# --------------------------------
# Forecast Confidence Interval
# --------------------------------

def confidence_interval_chart(forecast_df):

    fig = go.Figure()

    # Forecast
    fig.add_trace(
        go.Scatter(
            x=forecast_df["ds"],
            y=forecast_df["yhat"],
            mode="lines",
            name="Forecast"
        )
    )

    # Upper confidence
    if "yhat_upper" in forecast_df.columns:

        fig.add_trace(
            go.Scatter(
                x=forecast_df["ds"],
                y=forecast_df["yhat_upper"],
                mode="lines",
                name="Upper Confidence",
                line=dict(dash="dash")
            )
        )

    # Lower confidence
    if "yhat_lower" in forecast_df.columns:

        fig.add_trace(
            go.Scatter(
                x=forecast_df["ds"],
                y=forecast_df["yhat_lower"],
                mode="lines",
                name="Lower Confidence",
                line=dict(dash="dash")
            )
        )

    fig.update_layout(
        title="Forecast Confidence Interval",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        template="plotly_white"
    )

    return fig


# --------------------------------
# Actual vs Predicted Temperature
# --------------------------------

def actual_vs_predicted_chart(comparison_df):

    fig = go.Figure()

    # Actual Temperature
    fig.add_trace(
        go.Scatter(
            x=comparison_df["Date"],
            y=comparison_df["Actual_Temp"],
            mode="lines",
            name="Actual Temperature"
        )
    )

    # Predicted Temperature
    fig.add_trace(
        go.Scatter(
            x=comparison_df["Date"],
            y=comparison_df["Predicted_Temp"],
            mode="lines",
            name="Predicted Temperature"
        )
    )

    fig.update_layout(
        title="Actual vs Predicted Maximum Temperature",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig