import pandas as pd
import numpy as np
import os

# --- CONFIG ---
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "india_energy_data.csv")

#DATA_PATH = os.path.join("RAYA Energy", "data", "india_energy_data.csv")
#OUTPUT_PATH = os.path.join("RAYA Energy", "data", "state_energy_enhanced.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "state_energy_enhanced.csv")

YEARS = range(2015, 2026)  # 2015 to 2025

# --- STEP 1: Load Base Dataset ---
df_base = pd.read_csv(DATA_PATH)
print(f"🔹 Loaded base data: {df_base.shape[0]} states, {df_base.shape[1]} columns")

# --- STEP 2: Expand Temporally ---
expanded_rows = []

for year in YEARS:
    df_year = df_base.copy()
    df_year['year'] = year

    # --- STEP 3: Simulate Trends ---
    # Renewable growth: +5% per year for solar & wind
    df_year['solar_utility_MW'] = df_year['solar_utility_MW'] * (1 + 0.05 * (year - 2025))
    df_year['solar_rooftop_MW'] = df_year['solar_rooftop_MW'] * (1 + 0.05 * (year - 2025))
    df_year['wind_MW'] = df_year['wind_MW'] * (1 + 0.04 * (year - 2025))
    df_year['biomass_MW'] = df_year['biomass_MW'] * (1 + 0.03 * (year - 2025))

    # CO2 intensity trend: -2% per year
    df_year['CO2_emissions_MtCO2'] = df_year['CO2_emissions_MtCO2'] * (1 - 0.02 * (2025 - year))

    # Storage growth: +8% per year
    df_year['storage_capacity_MWh'] = df_year['storage_capacity_MWh'] * (1 + 0.08 * (year - 2025))

    # Derived Metrics
    df_year['CO2_per_MWh'] = df_year['CO2_emissions_MtCO2'] / df_year['annual_generation_GWh']
    df_year['renewables_to_demand_ratio'] = (df_year['solar_utility_MW'] + df_year['solar_rooftop_MW'] + 
                                             df_year['wind_MW'] + df_year['biomass_MW']) / df_year['peak_demand_MW']

    expanded_rows.append(df_year)

# --- STEP 4: Concatenate All Years ---
df_expanded = pd.concat(expanded_rows, ignore_index=True)
print(f"✅ Expanded dataset: {df_expanded.shape[0]} rows, {df_expanded.shape[1]} columns")

# --- STEP 5: Save Enhanced CSV ---
df_expanded.to_csv(OUTPUT_PATH, index=False)
print(f"📌 Enhanced data saved to: {OUTPUT_PATH}")
