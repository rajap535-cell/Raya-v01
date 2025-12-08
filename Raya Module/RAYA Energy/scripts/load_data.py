import pandas as pd
import sqlite3
import os
import glob

# --- CONFIG ---
# --- CONFIG ---
DATA_DIR = r"C:\Users\RD\OneDrive\Desktop\raya_cleaned\RAYA Energy\data"
DB_PATH = os.path.join(DATA_DIR, "state_energy.db")

# --- STEP 0: Find CSV file in data folder ---
csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV file found in {DATA_DIR} folder.")
elif len(csv_files) > 1:
    print(f"⚠ Multiple CSV files found. Using the first one: {csv_files[0]}")
CSV_PATH = csv_files[0]

# --- STEP 1: Load CSV ---
def load_csv(path=CSV_PATH):
    print(f"🔹 Loading CSV data from: {path}")
    df = pd.read_csv(path)
    print(f"✅ Loaded {len(df)} records and {len(df.columns)} columns.\n")
    print("📊 Full Data Preview (first 5 rows):")
    print(df.head(5))
    return df

# --- STEP 2: Convert to SQLite DB ---
def convert_to_sqlite(df, db_path=DB_PATH):
    print("\n🔹 Creating SQLite Database...")
    conn = sqlite3.connect(db_path)
    df.to_sql("state_energy", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Database created at {db_path}")

# --- STEP 3: Summary Metrics ---
def summary_metrics(df):
    print("\n📌 Key Metrics Summary:")
    metrics_cols = ["state", "total_installed_capacity_MW", "renewables_share_percent",
                    "CO2_emissions_MtCO2", "peak_demand_MW", "TnD_losses_percent"]
    available_cols = [c for c in metrics_cols if c in df.columns]
    print(df[available_cols].sort_values("total_installed_capacity_MW", ascending=False).head(10))

# --- MAIN ---
if __name__ == "__main__":
    df = load_csv()
    convert_to_sqlite(df)
    summary_metrics(df)
