import pandas as pd

def detect_anomalies(df):

    avg_temp = df[
        "Temp_Max"
    ].mean()

    anomalies = df[
        df["Temp_Max"]
        >
        avg_temp + 5
    ]

    return anomalies