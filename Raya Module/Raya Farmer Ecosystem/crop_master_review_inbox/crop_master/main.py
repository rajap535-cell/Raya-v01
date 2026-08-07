import json

from farmer_search_engine import farmer_search
from advisory_engine import build_advisory
from disease_detection_engine import detect_disease


def run_system():

    # ----------------------------------------
    # STEP 1: USER INPUT (simulate farmer)
    # ----------------------------------------
    user_input = {
        "state": "Karnataka",
        "district": "Mandya",
        "crop": "rice",
        "stage": "Flowering",
        "weather_event": "rain",
        "weather_intensity": "heavy",
        "image": "leaf.jpg"   # 👈 THIS is where image comes
    }

    # ----------------------------------------
    # STEP 2: SNAPSHOT (Track-1)
    # ----------------------------------------
    snapshot = farmer_search(
        state=user_input["state"],
        district=user_input["district"],
        crop=user_input["crop"],
        stage=user_input["stage"],
        weather_event=user_input["weather_event"],
        weather_intensity=user_input["weather_intensity"]
    )

    print("\n--- SNAPSHOT ---")
    print(snapshot)

    # ----------------------------------------
    # STEP 3: ADVISORY (Integration Layer)
    # ----------------------------------------
    advisory = build_advisory(snapshot)

    print("\n--- ADVISORY ---")
    print(advisory)

    # ----------------------------------------
    # STEP 4: DISEASE DETECTION
    # ----------------------------------------
    snapshot["image"] = user_input["image"]

    advisory = build_advisory(snapshot)

    print("\n--- FINAL UNIFIED OUTPUT ---")
    print(json.dumps(advisory, indent=4))


if __name__ == "__main__":
    run_system()