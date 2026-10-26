import logging
from pathlib import Path

import pandas as pd


IMPACT_PATH = Path("outputs") / "climate_impact.csv"
OUTPUT_PATH = Path("outputs") / "climate_recommendations.csv"


logging.basicConfig(
    filename="logs/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def generate_recommendation(row):
    """
    Generate a rule-based action recommendation
    from climate risk and impact assessment.
    """

    recommendations = []
    priorities = []

    climate_state = str(row["Climate_State"])

    agriculture = row["Agriculture_Impact"]
    water = row["Water_Stress_Impact"]
    heat = row["Human_Heat_Stress_Impact"]
    infrastructure = row["Infrastructure_Impact"]
    overall_risk = row["Overall_Risk"]

    # --------------------------------------------------
    # Agriculture
    # --------------------------------------------------

    if agriculture == "High":
        recommendations.append(
            "Prioritize crop monitoring and irrigation management."
        )
        priorities.append(3)

    elif agriculture == "Moderate":
        recommendations.append(
            "Monitor crop conditions and maintain adequate irrigation."
        )
        priorities.append(2)

    # --------------------------------------------------
    # Water
    # --------------------------------------------------

    if water == "High":
        recommendations.append(
            "Prioritize water conservation and monitor water availability."
        )
        priorities.append(3)

    elif water == "Moderate":
        recommendations.append(
            "Monitor water availability and irrigation requirements."
        )
        priorities.append(2)

    # --------------------------------------------------
    # Human heat stress
    # --------------------------------------------------

    if heat == "High":
        recommendations.append(
            "Issue heat-stress precautions and reduce prolonged heat exposure."
        )
        priorities.append(3)

    elif heat == "Moderate":
        recommendations.append(
            "Monitor heat conditions and provide basic heat-safety guidance."
        )
        priorities.append(2)

    # --------------------------------------------------
    # Infrastructure
    # --------------------------------------------------

    if infrastructure == "High":
        recommendations.append(
            "Inspect vulnerable infrastructure and prepare for weather-related disruption."
        )
        priorities.append(3)

    elif infrastructure == "Moderate":
        recommendations.append(
            "Monitor vulnerable infrastructure and weather-related conditions."
        )
        priorities.append(2)

    # --------------------------------------------------
    # Climate-state specific recommendations
    # --------------------------------------------------

    if "Hot / Dry" in climate_state:
        recommendations.append(
            "Increase water-use monitoring because hot and dry conditions may increase water stress."
        )
        priorities.append(3)

    if "Extreme Heat" in climate_state:
        recommendations.append(
            "Activate enhanced heat-risk monitoring and protective measures."
        )
        priorities.append(3)

    if "Extreme Rainfall" in climate_state:
        recommendations.append(
            "Monitor flooding, drainage and waterlogging conditions."
        )
        priorities.append(3)

    if "Windy" in climate_state:
        recommendations.append(
            "Monitor wind-sensitive infrastructure and outdoor activities."
        )
        priorities.append(2)

    if "Wet" in climate_state:
        recommendations.append(
            "Monitor waterlogging and excess-moisture conditions."
        )
        priorities.append(2)

    # --------------------------------------------------
    # Overall risk
    # --------------------------------------------------

    if overall_risk == "High":
        priorities.append(3)

    elif overall_risk == "Moderate":
        priorities.append(2)

    else:
        priorities.append(1)

    # --------------------------------------------------
    # Default recommendation
    # --------------------------------------------------

    if not recommendations:
        recommendations.append(
            "Continue routine climate monitoring."
        )

    # Remove duplicate recommendations
    recommendations = list(
        dict.fromkeys(recommendations)
    )

    # --------------------------------------------------
    # Priority
    # --------------------------------------------------

    max_priority = max(priorities)

    if max_priority >= 3:
        priority = "HIGH"

    elif max_priority == 2:
        priority = "MODERATE"

    else:
        priority = "LOW"

    # --------------------------------------------------
    # Final recommendation
    # --------------------------------------------------

    recommendation = " ".join(
        recommendations
    )

    return pd.Series({
        "Recommendation": recommendation,
        "Priority": priority
    })


def generate_recommendations():

    logging.info(
        "Starting Climate Recommendation Engine."
    )

    # --------------------------------------------------
    # 1. Check input
    # --------------------------------------------------

    if not IMPACT_PATH.exists():
        raise FileNotFoundError(
            f"Impact file not found: {IMPACT_PATH}"
        )

    # --------------------------------------------------
    # 2. Load impact data
    # --------------------------------------------------

    df = pd.read_csv(
        IMPACT_PATH
    )

    if df.empty:
        raise ValueError(
            "Climate impact dataset is empty."
        )

    # --------------------------------------------------
    # 3. Generate recommendations
    # --------------------------------------------------

    recommendation_df = df.apply(
        generate_recommendation,
        axis=1
    )

    df = pd.concat(
        [df, recommendation_df],
        axis=1
    )

    # --------------------------------------------------
    # 4. Select output columns
    # --------------------------------------------------

    output_columns = [
        "Date",
        "Climate_State",

        "Overall_Risk",
        "Overall_Impact",

        "Agriculture_Impact",
        "Water_Stress_Impact",
        "Human_Heat_Stress_Impact",
        "Infrastructure_Impact",

        "Recommendation",
        "Priority"
    ]

    df = df[
        output_columns
    ]

    # --------------------------------------------------
    # 5. Save output
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
    # 6. Logging
    # --------------------------------------------------

    logging.info(
        "Climate Recommendation Engine completed."
    )

    logging.info(
        f"Recommendation records generated: {len(df)}"
    )

    # --------------------------------------------------
    # 7. Console output
    # --------------------------------------------------

    print("=" * 60)
    print("CLIMATE RECOMMENDATION ENGINE COMPLETED")
    print("=" * 60)

    print(
        f"Records Analysed : {len(df)}"
    )

    print("\nPriority Distribution:")

    print(
        df["Priority"]
        .value_counts()
    )

    print("\nSample Recommendations:")

    print(
        df[
            [
                "Date",
                "Climate_State",
                "Overall_Risk",
                "Overall_Impact",
                "Recommendation",
                "Priority"
            ]
        ].head(10)
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)

    return df


if __name__ == "__main__":
    generate_recommendations()