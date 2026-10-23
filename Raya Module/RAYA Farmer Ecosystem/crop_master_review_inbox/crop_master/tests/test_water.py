from farmer_search_engine import farmer_search

print("\n=== WATER TESTS ===")

pkt = farmer_search("Karnataka", "Mandya", "rice", "flowering")
print("Water:", pkt["water"])
