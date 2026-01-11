from weather_engine import assess_weather_event


print("\n==============================")
print("🌧️ TEST 1: Rainfall Impact")
print("Rice | Flowering | Heavy Rain")
print("==============================\n")

print(
    assess_weather_event(
        crop="rice",
        stage="Flowering",
        event_type="rain",
        intensity="heavy"
    )
)


print("\n==============================")
print("🌡️ TEST 2: Temperature Impact (Heat)")
print("Rice | Flowering | High Temperature")
print("==============================\n")

print(
    assess_weather_event(
        crop="rice",
        stage="Flowering",
        event_type="temperature",
        intensity="high"
    )
)


print("\n==============================")
print("🌡️ TEST 3: Temperature Impact (Cold)")
print("Rice | Tillering | Low Temperature")
print("==============================\n")

print(
    assess_weather_event(
        crop="rice",
        stage="Tillering",
        event_type="temperature",
        intensity="low"
    )
)


print("\n==============================")
print("💧 TEST 4: Humidity Impact")
print("Rice | Vegetative | High Humidity")
print("==============================\n")

print(
    assess_weather_event(
        crop="rice",
        stage="Vegetative",
        event_type="humidity",
        intensity="high"
    )
)


print("\n==============================")
print("🌬️ TEST 5: Wind Impact")
print("Rice | Flowering | Strong Wind")
print("==============================\n")

print(
    assess_weather_event(
        crop="rice",
        stage="Flowering",
        event_type="wind",
        intensity="strong"
    )
)
