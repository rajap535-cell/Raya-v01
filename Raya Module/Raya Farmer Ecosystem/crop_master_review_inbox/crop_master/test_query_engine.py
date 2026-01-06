from query_engine import rain_risk, diseases_at_stage, harvest_risk


print("\n🌧️ TEST 1: Rice + Flowering + Rain\n")
print(rain_risk("rice", "Flowering"))


print("\n🦠 TEST 2: Rice + Vegetative + Disease\n")
print(diseases_at_stage("rice", "Vegetative"))


print("\n🌾 TEST 3: Rice + Early Harvest\n")
print(harvest_risk("rice", "early"))
