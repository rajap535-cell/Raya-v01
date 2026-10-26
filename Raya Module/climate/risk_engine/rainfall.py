from configs.settings import (
    HEAVY_RAINFALL_THRESHOLD,
    EXTREME_RAINFALL_THRESHOLD
)


def detect_rainfall_risk(df):

    heavy_rainfall = df[
        df["Rainfall"] >= HEAVY_RAINFALL_THRESHOLD
    ]

    extreme_rainfall = df[
        df["Rainfall"] >= EXTREME_RAINFALL_THRESHOLD
    ]

    return {
        "Heavy Rainfall": len(heavy_rainfall),
        "Extreme Rainfall": len(extreme_rainfall)
    }