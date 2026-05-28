import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


#  TITLE
st.title(" Kolkata Climate Intelligence Dashboard")

st.write(
    """
    This dashboard analyzes historical climate data of Kolkata
    and provides environmental insights, trends, and alerts.
    """
)


# LOAD DATASET
df = pd.read_csv("fiveyearsweatherdata.csv")


# DATE CONVERSION
df['Date time'] = pd.to_datetime(df['Date time'])


# MONTH COLUMN
df['Month'] = df['Date time'].dt.month


# DATASET PREVIEW
st.subheader(" Dataset Preview")

st.write(df.head())


# KPI METRICS
st.subheader(" Climate Metrics")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Temperature",
    round(df['Temperature'].mean(), 2)
)

col2.metric(
    "Average Humidity",
    round(df['Relative Humidity'].mean(), 2)
)

col3.metric(
    "Maximum Temperature",
    round(df['Maximum Temperature'].max(), 2)
)


# TEMPERATURE TREND
st.subheader(" Temperature Trend")

plt.figure(figsize=(12,6))

plt.plot(
    df['Date time'],
    df['Temperature']
)

plt.title("Temperature Trend")

plt.xlabel("Date")

plt.ylabel("Temperature")

st.pyplot(plt)


# HUMIDITY TREND
st.subheader(" Humidity Trend")

plt.figure(figsize=(12,6))

plt.plot(
    df['Date time'],
    df['Relative Humidity']
)

plt.title("Humidity Trend")

plt.xlabel("Date")

plt.ylabel("Humidity")

st.pyplot(plt)


# WIND SPEED ANALYSIS
st.subheader(" Wind Speed Analysis")

plt.figure(figsize=(12,6))

plt.plot(
    df['Date time'],
    df['Wind Speed']
)

plt.title("Wind Speed Trend")

plt.xlabel("Date")

plt.ylabel("Wind Speed")

st.pyplot(plt)


# CLOUD COVER ANALYSIS
st.subheader(" Cloud Cover Analysis")

plt.figure(figsize=(12,6))

plt.plot(
    df['Date time'],
    df['Cloud Cover']
)

plt.title("Cloud Cover Trend")

plt.xlabel("Date")

plt.ylabel("Cloud Cover")

st.pyplot(plt)


# PRESSURE TREND
st.subheader("Sea Level Pressure Trend")

plt.figure(figsize=(12,6))

plt.plot(
    df['Date time'],
    df['Sea Level Pressure']
)

plt.title("Sea Level Pressure Trend")

plt.xlabel("Date")

plt.ylabel("Pressure")

st.pyplot(plt)


# HEAT ALERTS
st.subheader(" Heat Alerts")

heat_alerts = df[
    df['Maximum Temperature'] > 35
]

st.write(heat_alerts)

st.write(
    "Total Heat Alert Days:",
    len(heat_alerts)
)


# HEAT ALERT GRAPH
st.subheader(" Heat Alert Graph")

plt.figure(figsize=(12,6))

plt.plot(
    df['Date time'],
    df['Maximum Temperature']
)

plt.axhline(
    y=35,
    color='red',
    linestyle='--'
)

plt.title("Heat Alert Analysis")

plt.xlabel("Date")

plt.ylabel("Maximum Temperature")

st.pyplot(plt)


# RAINY DAYS ANALYSIS
st.subheader(" Rainy Days Analysis")

rainy_days = df[
    df['Conditions'].str.contains(
        'Rain',
        case=False,
        na=False
    )
]

st.write(rainy_days.head())

st.write(
    "Total Rainy Days:",
    len(rainy_days)
)


# RAINY DAYS CLOUD COVER GRAPH

st.subheader(" Rainy Days Cloud Cover")

plt.figure(figsize=(12,6))

plt.plot(
    rainy_days['Date time'],
    rainy_days['Cloud Cover']
)

plt.title("Rainy Days Cloud Cover Analysis")

plt.xlabel("Date")

plt.ylabel("Cloud Cover")

st.pyplot(plt)


# MONTHLY TEMPERATURE ANALYSIS
st.subheader(" Monthly Temperature Analysis")

monthly_temp = df.groupby(
    'Month'
)['Temperature'].mean()

st.bar_chart(monthly_temp)


# WEATHER CONDITIONS ANALYSIS
st.subheader(" Weather Conditions Count")

weather_count = df[
    'Conditions'
].value_counts()

st.bar_chart(weather_count.head(10))


# SIDEBAR FILTERS
st.sidebar.title(" Climate Filters")

selected_month = st.sidebar.slider(
    "Select Month",
    1,
    12,
    1
)

filtered_data = df[
    df['Month'] == selected_month
]

st.sidebar.write(
    "Filtered Records:",
    len(filtered_data)
)


# FILTERED DATA
st.subheader(" Filtered Climate Data")

st.write(filtered_data.head())


# FINAL INSIGHTS
st.subheader(" Climate Insights")

st.write(
    """
    • Summer months show higher temperatures.

    • Humidity remains high during monsoon periods.

    • Rain-related conditions are associated with high cloud cover.

    • Pressure fluctuations indicate unstable weather conditions.

    • Seasonal climate behavior is clearly visible in Kolkata.
    """
)


# PROJECT CONCLUSION
st.subheader(" Conclusion")

st.write(
    """
    This Regional Climate Intelligence System analyzes
    historical climate data of Kolkata to understand
    environmental patterns and climate behavior.

    The dashboard provides insights into temperature,
    humidity, cloud cover, heat alerts, rainy conditions,
    and seasonal climate trends.
    """
)

# -----------------------------
# AI TEMPERATURE PREDICTION
# -----------------------------

st.subheader(" AI-Based Temperature Prediction")

from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import mean_absolute_error

# FEATURES

X = df[
    [
        'Relative Humidity',
        'Wind Speed',
        'Sea Level Pressure',
        'Cloud Cover'
    ]
]

# TARGET

y = df['Temperature']

# SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# MODEL

model = RandomForestRegressor()

model.fit(X_train, y_train)

# PREDICTIONS

predictions = model.predict(X_test)

# ERROR

error = mean_absolute_error(
    y_test,
    predictions
)

st.write(
    "Mean Absolute Error:",
    round(error,2)
)

# GRAPH

fig, ax = plt.subplots(figsize=(12,6))

ax.plot(
    y_test.values[:100],
    label='Actual Temperature'
)

ax.plot(
    predictions[:100],
    label='Predicted Temperature'
)

ax.legend()

ax.set_title(
    "Actual vs Predicted Temperature"
)

st.pyplot(fig)