# energy_sim/utils/constants.py

EMISSIONS_FACTORS = {
    "coal": 1.0,
    "gas": 0.5,
    "oil": 0.7,
    "solar": 0.02,     # Lifecycle adjusted
    "wind": 0.01,
    "nuclear": 0.005,
    "hydro": 0.01,
    "storage_loss": 0.05
}

DEFAULT_CAPACITY_FACTORS = {
    "solar": 0.18,
    "wind": 0.35,
    "nuclear": 0.9,
    "hydro": 0.5,
    "coal": 0.6,
    "gas": 0.5,
    "oil": 0.4
}
