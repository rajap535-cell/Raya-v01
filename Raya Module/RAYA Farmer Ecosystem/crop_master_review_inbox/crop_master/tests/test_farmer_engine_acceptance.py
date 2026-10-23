from farmer_search_engine import farmer_search, format_for_farmer

print("\n=== TRACK-1 ACCEPTANCE TEST ===")

pkt = farmer_search(
    state="Karnataka",
    district="Mandya",
    crop="rice",
    stage="flowering",
    weather_event="rain",
    weather_intensity="heavy"
)

# Structured output
print("\n--- PACKET ---")
print(pkt)

# Farmer formatted output
print("\n--- FARMER FORMAT ---")
print(format_for_farmer(pkt))

# Deterministic expectation:
# Input → SAME output always
