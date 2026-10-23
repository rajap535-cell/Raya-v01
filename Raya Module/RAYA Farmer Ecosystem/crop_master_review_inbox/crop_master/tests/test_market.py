from farmer_search_engine import farmer_search

print("\n=== MARKET TESTS ===")

pkt = farmer_search("Karnataka", "Mandya", "rice", "flowering")
print("Market:", pkt["market"])
