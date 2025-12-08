# energy/energy_simulator.py
from dataclasses import dataclass, asdict
from typing import Dict
import math

EMISSIONS_FACTORS = {  # tCO2 per MWh (approx.)
    "coal": 1.0,
    "gas": 0.5,
    "oil": 0.7,
    "solar": 0.05,
    "wind": 0.02,
    "nuclear": 0.01,
    "hydro": 0.03,
    "storage_loss": 0.05
}

@dataclass
class Scenario:
    region: str
    year: int
    population: int
    per_capita_kwh: float
    mix: Dict[str, float]   # fractions sum to 1.0
    capacity_factors: Dict[str, float] = None  # optional per-source CF
    capacity_mw: Dict[str, float] = None

class EnergySimulator:
    def __init__(self):
        # default capacity_factors (simple)
        self.default_cf = {
            "solar": 0.18, "wind": 0.35, "nuclear": 0.9,
            "hydro": 0.5, "coal": 0.6, "gas": 0.5, "oil": 0.4
        }

    def simulate(self, s: Scenario) -> Dict:
        total_demand_mwh = (s.population * s.per_capita_kwh) / 1000.0  # convert kWh to MWh
        # naive production estimate: assume capacity sized to meet mix percentages via CF
        production = {}
        for src, frac in s.mix.items():
            cf = (s.capacity_factors or {}).get(src, self.default_cf.get(src, 0.5))
            # assume capacity (MW) if provided else derive capacity required to supply frac of demand
            if s.capacity_mw and src in s.capacity_mw:
                cap_mw = s.capacity_mw[src]
                prod_mwh = cap_mw * 24.0 * 365.0 * cf / 1000.0  # convert MWh/year (cap in MW simplified)
            else:
                prod_mwh = total_demand_mwh * frac
            production[src] = prod_mwh

        total_production = sum(production.values())
        surplus_mwh = total_production - total_demand_mwh
        deficit_mwh = max(0.0, -surplus_mwh)

        emissions_tco2 = 0.0
        for src, prod in production.items():
            ef = EMISSIONS_FACTORS.get(src, 0.1)
            emissions_tco2 += prod * ef

        result = {
            "region": s.region,
            "year": s.year,
            "total_demand_MWh": round(total_demand_mwh,2),
            "production_by_source_MWh": {k: round(v,2) for k,v in production.items()},
            "total_production_MWh": round(total_production,2),
            "surplus_MWh": round(surplus_mwh,2),
            "deficit_MWh": round(deficit_mwh,2),
            "emissions_tCO2": round(emissions_tco2,2)
        }
        return result

# quick CLI demo
if __name__ == "__main__":
    scen = Scenario(
        region="Testland",
        year=2040,
        population=1000000,
        per_capita_kwh=2000,
        mix={"solar":0.6, "wind":0.2, "nuclear":0.1, "hydro":0.1}
    )
    sim = EnergySimulator()
    out = sim.simulate(scen)
    import json
    print(json.dumps(out, indent=2))
