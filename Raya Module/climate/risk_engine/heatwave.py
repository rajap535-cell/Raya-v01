from configs.settings import (
    HEATWAVE_THRESHOLD,
    SEVERE_HEATWAVE_THRESHOLD
)


def detect_heatwaves(df):

    heatwave_days = df[
        df["Temp_Max"] >= HEATWAVE_THRESHOLD
    ]

    severe_heatwave_days = df[
        df["Temp_Max"] >= SEVERE_HEATWAVE_THRESHOLD
    ]

    return {
        "Heatwave Days": len(heatwave_days),
        "Severe Heatwave Days": len(severe_heatwave_days)
    }