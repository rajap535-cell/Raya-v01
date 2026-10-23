from farmer_search_engine import farmer_search

print("\n=== DISEASE TESTS ===")

pkt = farmer_search("Karnataka", "Mandya", "rice", "flowering")
print("Diseases:", pkt["diseases"])
