import logging
from pathlib import Path

import pandas as pd


RISK_PATH = Path("outputs") / "climate_risk.csv"
OUTPUT_PATH = Path("outputs") / "climate_impact.csv"


logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def assess_impact(row):
    """
    Assess potential climate impacts from the
    combined climate state and risk levels.
    """

    climate_state = str(row["Climate_State"])

    temperature_risk = row["Temperature_Risk"]
    rainfall_risk = row["Rainfall_Risk"]
    wind_risk = row["Wind_Risk"]
    overall_risk = row["Overall_Risk"]

    # --------------------------------------------------
    # Agriculture Impact
    # --------------------------------------------------

    agriculture_score = 1

    if temperature_risk == "Moderate":
        agriculture_score = max(
            agriculture_score, 2
        )

    if temperature_risk == "High":
        agriculture_score = max(
            agriculture_score, 3
        )

    if rainfall_risk == "Moderate":
        agriculture_score = max(
            agriculture_score, 2
        )

    if rainfall_risk == "High":
        agriculture_score = max(
            agriculture_score, 3
        )

    if "Dry" in climate_state:
        agriculture_score = max(
            agriculture_score, 2
        )

    if "Extreme Heat" in climate_state:
        agriculture_score = max(
            agriculture_score, 3
        )

    # --------------------------------------------------
    # Water Stress Impact
    # --------------------------------------------------

    water_score = 1

    if rainfall_risk == "Moderate":
        water_score = max(
            water_score, 2
        )

    if rainfall_risk == "High":
        water_score = max(
            water_score, 3
        )

    if "Dry" in climate_state:
        water_score = max(
            water_score, 2
        )

    if "Hot / Dry" in climate_state:
        water_score = max(
            water_score, 3
        )

    if "Extreme Heat" in climate_state:
        water_score = max(
            water_score, 3
        )

    # --------------------------------------------------
    # Human Heat Stress Impact
    # --------------------------------------------------

    heat_score = 1

    if temperature_risk == "Moderate":
        heat_score = max(
            heat_score, 2
        )

    if temperature_risk == "High":
        heat_score = max(
            heat_score, 3
        )

    if "Hot" in climate_state:
        heat_score = max(
            heat_score, 2
        )

    if "Extreme Heat" in climate_state:
        heat_score = max(
            heat_score, 3
        )

    # --------------------------------------------------
    # Infrastructure Impact
    # --------------------------------------------------

    infrastructure_score = 1

    if rainfall_risk == "Moderate":
        infrastructure_score = max(
            infrastructure_score, 2
        )

    if rainfall_risk == "High":
        infrastructure_score = max(
            infrastructure_score, 3
        )

    if wind_risk == "Moderate":
        infrastructure_score = max(
            infrastructure_score, 2
        )

    if wind_risk == "High":
        infrastructure_score = max(
            infrastructure_score, 3
        )

    # --------------------------------------------------
    # Convert scores to impact levels
    # --------------------------------------------------

    def level(score):

        if score >= 3:
            return "High"

        if score == 2:
            return "Moderate"

        return "Low"

    return pd.Series({
        "Agriculture_Impact": level(
            agriculture_score
        ),
        "Water_Stress_Impact": level(
            water_score
        ),
        "Human_Heat_Stress_Impact": level(
            heat_score
        ),
        "Infrastructure_Impact": level(
            infrastructure_score
        ),
        "Overall_Impact": level(
            max(
                agriculture_score,
                water_score,
                heat_score,
                infrastructure_score
            )
        )
    })


def generate_impact_assessment():

    logging.info(
        "Starting Climate Impact Assessment Engine."
    )

    # --------------------------------------------------
    # 1. Check input
    # --------------------------------------------------

    if not RISK_PATH.exists():

        raise FileNotFoundError(
            f"Risk file not found: {RISK_PATH}"
        )

    # --------------------------------------------------
    # 2. Load risk data
    # --------------------------------------------------

    df = pd.read_csv(
        RISK_PATH
    )

    if df.empty:

        raise ValueError(
            "Climate risk dataset is empty."
        )

    # --------------------------------------------------
    # 3. Generate impact assessment
    # --------------------------------------------------

    impact_df = df.apply(
        assess_impact,
        axis=1
    )

    df = pd.concat(
        [df, impact_df],
        axis=1
    )

    # --------------------------------------------------
    # 4. Save selected output
    # --------------------------------------------------

    output_columns = [
        "Date",
        "Climate_State",

        "Temperature_Risk",
        "Rainfall_Risk",
        "Wind_Risk",
        "Overall_Risk",

        "Agriculture_Impact",
        "Water_Stress_Impact",
        "Human_Heat_Stress_Impact",
        "Infrastructure_Impact",
        "Overall_Impact"
    ]

    df = df[
        output_columns
    ]

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
        "Climate Impact Assessment completed."
    )

    logging.info(
        f"Impact records generated: {len(df)}"
    )

    # --------------------------------------------------
    # 6. Console output
    # --------------------------------------------------

    print("=" * 60)
    print("CLIMATE IMPACT ASSESSMENT COMPLETED")
    print("=" * 60)

    print(
        f"Records Analysed : {len(df)}"
    )

    print("\nOverall Impact Distribution:")

    print(
        df["Overall_Impact"]
        .value_counts()
    )

    print("\nAgriculture Impact:")

    print(
        df["Agriculture_Impact"]
        .value_counts()
    )

    print("\nWater Stress Impact:")

    print(
        df["Water_Stress_Impact"]
        .value_counts()
    )

    print("\nHuman Heat Stress Impact:")

    print(
        df["Human_Heat_Stress_Impact"]
        .value_counts()
    )

    print("\nInfrastructure Impact:")

    print(
        df["Infrastructure_Impact"]
        .value_counts()
    )

    print("\nSample Impact Records:")

    print(
        df[
            [
                "Date",
                "Climate_State",
                "Overall_Risk",
                "Agriculture_Impact",
                "Water_Stress_Impact",
                "Human_Heat_Stress_Impact",
                "Infrastructure_Impact",
                "Overall_Impact"
            ]
        ].head(10)
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)

    return df


if __name__ == "__main__":
    generate_impact_assessment()