import os
import sqlite3
import pandas as pd

# Make paths relative to THIS script file, not CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")  # ../data because scripts/ -> data/
DB_PATH = os.path.join(DATA_DIR, "state_energy.db")
OUTPUT_CSV = os.path.join(DATA_DIR, "state_energy_indices.csv")

# Load data
def load_data(db_path=DB_PATH):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"No database found at {db_path}. Run load_data.py first.")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM state_energy", conn)
    conn.close()
    return df

# --- STEP 2: Compute indices ---
def compute_indices(df):
    print("🔹 Computing derived indices...")

    # Example: Energy mix %
    energy_sources = ['coal_MW', 'gas_MW', 'hydro_MW', 'nuclear_MW', 'solar_utility_MW',
                      'solar_rooftop_MW', 'wind_MW', 'biomass_MW', 'other_renewables_MW']
    
    df['total_generation_MW'] = df[energy_sources].sum(axis=1)

    for source in energy_sources:
        df[f'{source}_pct'] = df[source] / df['total_generation_MW'] * 100

    # Renewable share index (example)
    renewable_cols = ['solar_utility_MW', 'solar_rooftop_MW', 'wind_MW', 'biomass_MW', 'other_renewables_MW']
    df['renewables_share_percent'] = df[renewable_cols].sum(axis=1) / df['total_generation_MW'] * 100

    # CO2 intensity per MWh
    df['CO2_intensity_kg_per_MWh'] = df['CO2_emissions_MtCO2'] * 1e6 / df['annual_generation_GWh']

    # Grid reliability index (placeholder)
    df['grid_reliability_index'] = 100 - df['TnD_losses_percent']  # simple proxy

    return df

# --- STEP 3: Save results ---
def save_results(df, output_csv=OUTPUT_CSV):
    df.to_csv(output_csv, index=False)
    print(f"✅ Computed indices saved to {output_csv}")

# --- MAIN ---
if __name__ == "__main__":
    df = load_data()
    df = compute_indices(df)
    save_results(df)

    print("\n📌 Key Metrics Preview:")
    display_cols = ['state', 'total_generation_MW', 'renewables_share_percent', 'CO2_intensity_kg_per_MWh', 'grid_reliability_index']
    print(df[display_cols].head(10))
