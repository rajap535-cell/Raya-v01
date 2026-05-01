from app.core.base_model import BASE_MODELS
from app.core.adaptive_model import GOAL_PRESETS

def get_age_group(age):
    if age <= 18:
        return "13-18"
    elif age <= 30:
        return "18-30"
    else:
        return "30+"

def build_model(age, goal):
    base = BASE_MODELS[get_age_group(age)].copy()
    adaptive = GOAL_PRESETS.get(goal, {})

    # merge adaptive into base
    for key, value in adaptive.items():
        base[key] = value

    return base

def calculate_gap(model, reality):
    gaps = {}

    for key in model:
        if key in reality:
            min_val, max_val = model[key]
            actual = reality[key]

            if actual < min_val:
                gaps[key] = f"below by {round(min_val - actual, 2)}"
            elif actual > max_val:
                gaps[key] = f"above by {round(actual - max_val, 2)}"
            else:
                gaps[key] = "optimal"

    return gaps


def generate_coach_response(gaps):
    messages = []

    for key, status in gaps.items():
        if status == "optimal":
            messages.append(f"{key}: You're on track. Keep it consistent.")
        elif "below" in status:
            messages.append(f"{key}: You're improving. Let's optimize this area.")
        else:
            messages.append(f"{key}: Slightly high. Let's bring it into balance.")

    return messages