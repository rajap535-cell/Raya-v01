from app.core.base_model import get_base_model

def compare_user(user, analytics):

    base = get_base_model(user.age, user.gender)

    results = {}

    # ---- SLEEP ----
    sleep = analytics["avg_sleep"]
    ideal_min, ideal_max = base["sleep"]

    if sleep is None:
        results["sleep"] = "No data yet"
    elif sleep < ideal_min:
        diff = round(ideal_min - sleep, 1)
        results["sleep"] = f"Below optimal by {diff} hrs"
    elif sleep > ideal_max:
        results["sleep"] = "Above optimal (check oversleep)"
    else:
        results["sleep"] = "On track"

    # ---- STEPS ----
    steps = analytics["total_steps"]
    ideal_min, ideal_max = base["steps"]

    if steps is None:
        results["steps"] = "No data yet"
    elif steps < ideal_min:
        results["steps"] = "Low activity"
    elif steps > ideal_max:
        results["steps"] = "High activity"
    else:
        results["steps"] = "On track"

    # ---- SCREEN ----
    screen = analytics["avg_screen_time"]
    ideal_min, ideal_max = base["screen"]

    if screen is None:
        results["screen"] = "No data yet"
    elif screen > ideal_max:
        results["screen"] = "Too high"
    else:
        results["screen"] = "Balanced"

    # ---- DEEP WORK ----
    # using work_hours as proxy for now
    work = analytics.get("avg_work_hours", None)
    ideal_min, ideal_max = base["deep_work"]

    if work is None:
        results["deep_work"] = "No data yet"
    elif work < ideal_min:
        results["deep_work"] = "Needs improvement"
    else:
        results["deep_work"] = "On track"

    return results