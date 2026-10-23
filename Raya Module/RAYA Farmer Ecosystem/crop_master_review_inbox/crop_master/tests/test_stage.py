from farmer_search_engine import farmer_search

print("\n=== STAGE SNAPSHOT TESTS ===")

pkt = farmer_search("Karnataka", "Mandya", "rice", "flowering")
print("Stage snapshot:", pkt["stage_snapshot"])
