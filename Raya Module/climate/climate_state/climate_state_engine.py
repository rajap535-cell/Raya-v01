import logging
from pathlib import Path

import pandas as pd


ANOMALY_PATH = Path("outputs") / "climate_anomalies.csv"
OUTPUT_PATH = Path("outputs") / "climate_state.csv"


logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def determine_climate_state(row):
    """
    Interpret temperature, rainfall and wind conditions
    together and generate a human-readable climate state.
    """

    temp_level = row["Temperature_Level"]
    rainfall_level = row["Rainfall_Level"]
    wind_level = row["Wind_Level"]

    temp_anomaly = row["Temperature_Anomaly"]
    rainfall_anomaly = row["Rainfall_Anomaly"]

    # --------------------------------------------------
    # Temperature condition
    # --------------------------------------------------

    if temp_level == "Extreme":
        if temp_anomaly > 0:
            temperature_state = "Very Hot"
        else:
            temperature_state = "Very Cold"

    elif temp_level == "Elevated":
        if temp_anomaly > 0:
            temperature_state = "Hot"
        else:
            temperature_state = "Cooler Than Normal"

    else:
        temperature_state = "Normal Temperature"

    # --------------------------------------------------
    # Rainfall condition
    # --------------------------------------------------

    if rainfall_level == "Extreme":
        if rainfall_anomaly > 0:
            rainfall_state = "Very Wet"
        else:
            rainfall_state = "Very Dry"

    elif rainfall_level == "Elevated":
        if rainfall_anomaly > 0:
            rainfall_state = "Wet"
        else:
            rainfall_state = "Dry"

    else:
        rainfall_state = "Normal Rainfall"

    # --------------------------------------------------
    # Wind condition
    # --------------------------------------------------

    if wind_level == "Extreme":
        wind_state = "Very Windy"

    elif wind_level == "Elevated":
        wind_state = "Windy"

    else:
        wind_state = "Normal Wind"

    # --------------------------------------------------
    # Combined climate state
    # --------------------------------------------------

    # Hot + Dry
    if (
        temp_anomaly >= 2
        and rainfall_anomaly < 0
    ):
        return "Hot / Dry"

    # Hot + Wet
    if (
        temp_anomaly >= 2
        and rainfall_anomaly >= 20
    ):
        return "Hot / Wet"

    # Very hot condition
    if temp_level == "Extreme" and temp_anomaly > 0:
        return "Extreme Heat"

    # Very wet condition
    if rainfall_level == "Extreme" and rainfall_anomaly > 0:
        return "Extreme Rainfall"

    # Very windy condition
    if wind_level == "Extreme":
        return "Extreme Wind"

    # Hot condition
    if temp_level == "Elevated" and temp_anomaly > 0:
        return "Hot / Above Seasonal Normal"

    # Cooler condition
    if temp_level == "Elevated" and temp_anomaly < 0:
        return "Cool / Below Seasonal Normal"

    # Wet condition
    if rainfall_level == "Elevated" and rainfall_anomaly > 0:
        return "Wet / Above Seasonal Normal"

    # Dry condition
    if rainfall_level == "Elevated" and rainfall_anomaly < 0:
        return "Dry / Below Seasonal Normal"

    # Windy condition
    if wind_level == "Elevated":
        return "Windy / Above Seasonal Normal"

    # Otherwise
    return "Normal Climate Conditions"


def generate_climate_state():

    logging.info(
        "Starting Climate State Engine."
    )

    # --------------------------------------------------
    # 1. Check anomaly file
    # --------------------------------------------------

    if not ANOMALY_PATH.exists():
        raise FileNotFoundError(
            f"Anomaly file not found: {ANOMALY_PATH}"
        )

    # --------------------------------------------------
    # 2. Load anomaly data
    # --------------------------------------------------

    df = pd.read_csv(ANOMALY_PATH)

    if df.empty:
        raise ValueError(
            "Climate anomaly dataset is empty."
        )

    # --------------------------------------------------
    # 3. Generate climate state
    # --------------------------------------------------

    df["Climate_State"] = df.apply(
        determine_climate_state,
        axis=1
    )

    # --------------------------------------------------
    # 4. Save output
    # --------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------
    # 5. Logging
    # --------------------------------------------------

    logging.info(
        "Climate State Engine completed successfully."
    )

    logging.info(
        f"Climate state records generated: {len(df)}"
    )

    # --------------------------------------------------
    # 6. Console output
    # --------------------------------------------------

    print("=" * 60)
    print("CLIMATE STATE ENGINE COMPLETED")
    print("=" * 60)

    print(f"Records Analysed : {len(df)}")

    print("\nClimate State Distribution:")
    print(
        df["Climate_State"]
        .value_counts()
    )

    print("\nSample Climate States:")

    print(
        df[
            [
                "Date",
                "Temperature_Level",
                "Rainfall_Level",
                "Wind_Level",
                "Climate_State"
            ]
        ].head(15)
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)

    return df


if __name__ == "__main__":
    generate_climate_state()