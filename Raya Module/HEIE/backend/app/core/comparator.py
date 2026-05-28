def compare_user(user, data):

    insights = []

    # Sleep
    if data["avg_sleep"] is not None:
        if data["avg_sleep"] < 6:
            insights.append("⚠️ Sleep is critically low.")
        elif data["avg_sleep"] < 7:
            insights.append("😴 Sleep can be improved.")
        else:
            insights.append("✅ Sleep looks healthy.")

    # Steps
    if data["avg_steps"] is not None:
        if data["avg_steps"] < 5000:
            insights.append("🚶 Activity level is low.")
        elif data["avg_steps"] < 8000:
            insights.append("🙂 Moderate activity detected.")
        else:
            insights.append("🔥 Excellent movement levels.")

    # Screen Time
    if data["avg_screen_time"] is not None:
        if data["avg_screen_time"] > 8:
            insights.append("📱 Excessive screen time.")
        else:
            insights.append("✅ Screen balance looks fine.")

    # Work Hours
    if data["avg_work_hours"] is not None:
        if data["avg_work_hours"] > 10:
            insights.append("💼 High workload may cause burnout.")

    # Exercise
    if data["avg_exercise"] is not None:
        if data["avg_exercise"] < 20:
            insights.append("🏃 Increase exercise levels.")

    # Water
    if data["avg_water"] is not None:
        if data["avg_water"] < 2:
            insights.append("💧 Hydration is low.")

    # Learning
    if data["avg_learning"] is not None:
        if data["avg_learning"] > 2:
            insights.append("🧠 Strong learning consistency.")

    return insights