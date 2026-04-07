"""
RAYA Phase-2 — FINAL INTEGRATION LAYER

Purpose:
End-to-end farmer advisory system

Flow:
Farmer Input → Snapshot → Advisory → Disease Detection → Final Output
"""

from farmer_search_engine import farmer_search
from advisory_engine import build_advisory
from disease_detection_engine import detect_disease


def run_farmer_advisory(
    state: str,
    district: str,
    crop: str,
    stage: str,
    image: str | None = None,
    weather_event: str | None = None,
    weather_intensity: str | None = None
):
    # ------------------------------------------------------
    # STEP 1: SNAPSHOT (Track-1)
    # ------------------------------------------------------
    snapshot = farmer_search(
        state=state,
        district=district,
        crop=crop,
        stage=stage,
        weather_event=weather_event,
        weather_intensity=weather_intensity
    )

    if snapshot.get("error"):
        return snapshot

    # ------------------------------------------------------
    # STEP 2: ADVISORY (Aggregation Layer)
    # ------------------------------------------------------
    advisory = build_advisory(snapshot)

    if advisory.get("status") == "error":
        return advisory

    # ------------------------------------------------------
    # STEP 3: DISEASE DETECTION (OPTIONAL)
    # ------------------------------------------------------
    disease_output = None

    if image:
        disease_output = detect_disease({
            "crop": crop,
            "stage": stage,
            "image": image
        })

    # ------------------------------------------------------
    # STEP 4: FINAL RESPONSE
    # ------------------------------------------------------
    final_output = {
        "status": "success",
        "location": advisory.get("location"),
        "crop": advisory.get("crop"),
        "stage": advisory.get("stage"),

        # Snapshot
        "snapshot": advisory.get("snapshot"),

        # Advisory
        "advisory": advisory.get("advisory"),
        "alerts": advisory.get("alerts"),
        "schedule": advisory.get("schedule"),
    }

    if disease_output:
        final_output["disease_detection"] = disease_output.get("disease_detection")

    return final_output


# ----------------------------------------------------------
# TEST HARNESS
# ----------------------------------------------------------
if __name__ == "__main__":

    result = run_farmer_advisory(
        state="Karnataka",
        district="Mandya",
        crop="rice",
        stage="Flowering",
        image="leaf.jpg",
        weather_event="rain",
        weather_intensity="heavy"
    )

    print("\n--- FINAL FARMER OUTPUT ---")
    print(result)