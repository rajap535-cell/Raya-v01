from farmer_search_engine import farmer_search

print("\n=== WEATHER TESTS ===")

pkt = farmer_search(
    "Karnataka",
    "Mandya",
    "rice",
    "flowering",
    weather_event="rain",
    weather_intensity="heavy"
)

print("Rain during flowering:", pkt["weather"])
