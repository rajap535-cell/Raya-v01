import pandas as pd
import os

# Paths
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENHANCED_DATA_PATH = os.path.join(BASE_DIR, "data", "state_energy_enhanced.csv")
INDICES_DATA_PATH = os.path.join(BASE_DIR, "data", "state_energy_indices.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "state_energy_intelligence.csv")

# Load datasets
print("🔹 Loading enhanced data...")
df_enh = pd.read_csv(ENHANCED_DATA_PATH)
print(f"✅ Enhanced data: {df_enh.shape[0]} rows, {df_enh.shape[1]} columns")

print("🔹 Loading computed indices...")
df_idx = pd.read_csv(INDICES_DATA_PATH)
print(f"✅ Indices data: {df_idx.shape[0]} rows, {df_idx.shape[1]} columns")

# Merge datasets on state
print("🔹 Merging datasets...")
df = df_enh.merge(df_idx, on="state", how="left")
print(f"✅ Merged dataset: {df.shape[0]} rows, {df.shape[1]} columns")
print("🔹 Columns after merge:")
print(df.columns.tolist())

# Helper to find the correct column even if suffix added
def get_column(df, base_name):
    for col in df.columns:
        if base_name in col:
            return col
    raise KeyError(f"Column '{base_name}' not found in DataFrame!")

# Identify columns dynamically
renewables_col = get_column(df, "renewables_share_percent")
co2_col = get_column(df, "CO2_emissions_MtCO2")
generation_col = get_column(df, "annual_generation_GWh")
grid_col = get_column(df, "grid_reliability_index")

# Compute intelligence metrics
df['renewable_share_ratio'] = df[renewables_col] / 100
df['CO2_efficiency_score'] = 1 / (df[co2_col] / df[generation_col])
# Normalize CO2 efficiency score to 0-100
df['CO2_efficiency_score'] = df['CO2_efficiency_score'] / df['CO2_efficiency_score'].max() * 100

# Energy Sustainability Score (ESS)
df['ESS'] = df['renewable_share_ratio'] * 100 * 0.4 + df['CO2_efficiency_score'] * 0.4 + df[grid_col] * 0.2

# Save intelligence-enhanced dataset
df.to_csv(OUTPUT_PATH, index=False)
print(f"✅ Intelligence-enhanced data saved to: {OUTPUT_PATH}")

# Quick preview
print("📌 Sample of ESS and key metrics:")
print(df[['state', renewables_col, co2_col, grid_col, 'ESS']].head())
