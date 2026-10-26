import os
import pandas as pd
import numpy as np

# ============================================================
# EVIDENCE-DRIVEN FUTURE RISK ENGINE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "future_anomaly.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "evidence_based_future_risk.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading future anomaly intelligence...")

    if not os.path.exists(INPUT_FILE):

        raise FileNotFoundError(
            f"Future anomaly file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "Date",
        "Predicted_Temp_Max",
        "Predicted_Rainfall",
        "Predicted_WindSpeed",
        "Climate_State",
        "Future_Anomaly",
        "Anomaly_Signal",
        "Anomaly_Severity",
        "Confidence_Score"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df["Date"] = pd.to_datetime(df["Date"])

    return df


# ============================================================
# CALCULATE DAILY RISK SCORE
# ============================================================

def calculate_daily_risk(row):

    score = 0

    temperature = row["Predicted_Temp_Max"]
    rainfall = row["Predicted_Rainfall"]
    wind = row["Predicted_WindSpeed"]

    anomaly = row["Future_Anomaly"]
    severity = row["Anomaly_Severity"]

    confidence = row["Confidence_Score"]

    # --------------------------------------------------------
    # Temperature evidence
    # --------------------------------------------------------

    if temperature >= 40:

        score += 4

    elif temperature >= 35:

        score += 3

    elif temperature >= 32:

        score += 1

    # --------------------------------------------------------
    # Rainfall evidence
    # --------------------------------------------------------

    if rainfall >= 50:

        score += 4

    elif rainfall >= 20:

        score += 3

    elif rainfall >= 10:

        score += 2

    elif rainfall >= 5:

        score += 1

    # --------------------------------------------------------
    # Wind evidence
    # --------------------------------------------------------

    if wind >= 40:

        score += 4

    elif wind >= 30:

        score += 3

    elif wind >= 20:

        score += 1

    # --------------------------------------------------------
    # Anomaly evidence
    # --------------------------------------------------------

    if anomaly == "MULTIPLE":

        score += 3

    elif anomaly == "ANOMALY":

        score += 2

    # --------------------------------------------------------
    # Severity evidence
    # --------------------------------------------------------

    if severity == "HIGH":

        score += 3

    elif severity == "MEDIUM":

        score += 2

    # --------------------------------------------------------
    # Confidence adjustment
    # --------------------------------------------------------

    if confidence >= 70:

        score += 2

    elif confidence >= 50:

        score += 1

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    if score >= 10:

        risk_level = "CRITICAL"

    elif score >= 7:

        risk_level = "HIGH"

    elif score >= 4:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    return score, risk_level


# ============================================================
# RECOMMENDED ACTION
# ============================================================

def recommended_action(risk_level, anomaly):

    if risk_level == "CRITICAL":

        return "Immediate climate risk monitoring and emergency preparedness"

    elif risk_level == "HIGH":

        return "Increase monitoring frequency and prepare mitigation actions"

    elif risk_level == "MEDIUM":

        return "Continue active monitoring and review local conditions"

    elif anomaly != "NORMAL":

        return "Monitor developing climate anomaly"

    else:

        return "Routine climate monitoring"


# ============================================================
# RISK EVIDENCE
# ============================================================

def build_evidence(row):

    evidence = []

    temperature = row["Predicted_Temp_Max"]
    rainfall = row["Predicted_Rainfall"]
    wind = row["Predicted_WindSpeed"]

    anomaly = row["Future_Anomaly"]

    if temperature >= 35:

        evidence.append(
            f"High temperature forecast ({temperature:.2f} °C)"
        )

    if rainfall >= 10:

        evidence.append(
            f"Heavy rainfall forecast ({rainfall:.2f} mm)"
        )

    if wind >= 30:

        evidence.append(
            f"High wind forecast ({wind:.2f} km/h)"
        )

    if anomaly == "MULTIPLE":

        evidence.append(
            "Multiple future climate anomaly signals"
        )

    elif anomaly == "ANOMALY":

        evidence.append(
            "Future climate anomaly detected"
        )

    if not evidence:

        evidence.append(
            "No significant future climate anomaly detected"
        )

    return "; ".join(evidence)


# ============================================================
# MAIN ENGINE
# ============================================================

def main():

    print("=" * 60)
    print("TASK 006 - EVIDENCE-DRIVEN FUTURE RISK ENGINE")
    print("=" * 60)

    df = load_data()

    print()

    print(
        "Forecast Records :",
        len(df)
    )

    print(
        "Forecast Period  :",
        df["Date"].min().date(),
        "to",
        df["Date"].max().date()
    )

    print()

    print("Calculating evidence-based future risk...")

    # --------------------------------------------------------
    # Daily risk calculation
    # --------------------------------------------------------

    risk_results = df.apply(
        calculate_daily_risk,
        axis=1
    )

    df["Risk_Score"] = [
        result[0]
        for result in risk_results
    ]

    df["Risk_Level"] = [
        result[1]
        for result in risk_results
    ]

    # --------------------------------------------------------
    # Recommended actions
    # --------------------------------------------------------

    df["Recommended_Action"] = df.apply(
        lambda row: recommended_action(
            row["Risk_Level"],
            row["Future_Anomaly"]
        ),
        axis=1
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    df["Risk_Evidence"] = df.apply(
        build_evidence,
        axis=1
    )

    # --------------------------------------------------------
    # Risk persistence
    # --------------------------------------------------------

    df["Previous_Risk_Level"] = (
        df["Risk_Level"].shift(1)
    )

    df["Risk_Persistence"] = np.where(

        df["Previous_Risk_Level"].isna(),

        "Initial",

        np.where(

            df["Risk_Level"]
            == df["Previous_Risk_Level"],

            "Persistent",

            "Risk Change"
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()

    print(
        "Evidence-based future risk file saved successfully:"
    )

    print(OUTPUT_FILE)

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 60)
    print("EVIDENCE-DRIVEN FUTURE RISK SUMMARY")
    print("=" * 60)

    print()

    print("Risk Level Distribution:")

    print(
        df["Risk_Level"]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Average Risk Score :",
        f"{df['Risk_Score'].mean():.2f}"
    )

    print(
        "Maximum Risk Score :",
        df["Risk_Score"].max()
    )

    print()

    print("Recommended Actions:")

    print(
        df["Recommended_Action"]
        .value_counts()
        .to_string()
    )

    print()

    print("First 5 Risk Predictions:")

    print(
        df[
            [
                "Date",
                "Climate_State",
                "Future_Anomaly",
                "Anomaly_Severity",
                "Confidence_Score",
                "Risk_Score",
                "Risk_Level",
                "Recommended_Action"
            ]
        ]
        .head()
        .to_string(index=False)
    )

    print()

    print("=" * 60)
    print(
        "EVIDENCE-DRIVEN FUTURE RISK ENGINE "
        "COMPLETED SUCCESSFULLY"
    )
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()