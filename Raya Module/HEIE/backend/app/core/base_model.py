def get_base_model(age: int, gender: str):

    # Age groups
    if 13 <= age <= 18:
        sleep = (8, 10)
        steps = (8000, 12000)
        deep_work = (2, 4)
        screen = (0, 2)

    elif 18 <= age <= 30:
        sleep = (7, 9)
        steps = (6000, 10000)
        deep_work = (3, 6)
        screen = (0, 3)

    else:  # 30+
        sleep = (7, 8)
        steps = (5000, 8000)
        deep_work = (2, 5)
        screen = (0, 3)

    return {
        "sleep": sleep,
        "steps": steps,
        "deep_work": deep_work,
        "screen": screen
    }