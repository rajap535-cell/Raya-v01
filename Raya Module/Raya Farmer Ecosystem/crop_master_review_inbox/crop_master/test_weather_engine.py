from weather_engine import assess_weather_event


print("\n🌦️ WEATHER TEST — Rice | Flowering | Heavy Rain\n")

result = assess_weather_event(
    crop="rice",
    stage="Flowering",
    event_type="rain",
    intensity="heavy"
)

print(result)
