import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "state_energy_indices.csv")

#DATA_PATH = os.path.join("RAYA Energy", "data", "state_energy_indices.csv")
OUTPUT_DIR = os.path.join("data", "visualizations")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
df = pd.read_csv(DATA_PATH)


#renewable Share per state (Bar Chart)
plt.figure(figsize=(12,6))
sns.barplot(x='state', y='renewables_share_percent', data=df.sort_values('renewables_share_percent', ascending=False))
plt.xticks(rotation=90)
plt.ylabel('Renewables Share (%)')
plt.title('Renewable Energy Share by State')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "renewables_share_by_state.png"))
plt.show()


#CO₂ Intensity Heatmap
#CO₂ intensity = CO2_emissions_MtCO2 / annual_generation_GWh

df['CO2_intensity'] = df['CO2_emissions_MtCO2'] / df['annual_generation_GWh']

plt.figure(figsize=(12,6))
sns.heatmap(df[['state', 'CO2_intensity']].set_index('state').T, annot=True, cmap='Reds')
plt.title('CO₂ Intensity per MWh by State')
plt.savefig(os.path.join(OUTPUT_DIR, "co2_intensity_heatmap.png"))
plt.show()

#Grid reliability ranking

plt.figure(figsize=(12,6))
sns.barplot(x='state', y='grid_reliability_index', data=df.sort_values('grid_reliability_index', ascending=False))
plt.xticks(rotation=90)
plt.ylabel('Grid Reliability Index')
plt.title('Grid Reliability by State')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "grid_reliability_by_state.png"))
plt.show()
