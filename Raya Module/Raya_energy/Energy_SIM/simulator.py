# energy_sim/models/simulator.py

from typing import Dict
from scenario import Scenario
from constants import EMISSIONS_FACTORS, DEFAULT_CAPACITY_FACTORS


class EnergySimulator:
    def __init__(self):
        self.default_cf = DEFAULT_CAPACITY_FACTORS

    def simulate(self, s: Scenario) -> Dict:
        total_demand_mwh = (s.population * s.per_capita_kwh) / 1000.0  # kWh to MWh

        production = {}
        for src, frac in s.mix.items():
            cf = (s.capacity_factors or {}).get(src, self.default_cf.get(src, 0.5))

            if s.capacity_mw and src in s.capacity_mw:
                cap_mw = s.capacity_mw[src]
                prod_mwh = cap_mw * 24 * 365 * cf / 1000.0
            else:
                prod_mwh = total_demand_mwh * frac

            production[src] = prod_mwh

        total_production = sum(production.values())
        surplus_mwh = total_production - total_demand_mwh
        deficit_mwh = max(0.0, -surplus_mwh)

        emissions_tco2 = sum(production[src] * EMISSIONS_FACTORS.get(src, 0.1) for src in production)

        return {
            "region": s.region,
            "year": s.year,
            "total_demand_MWh": round(total_demand_mwh, 2),
            "production_by_source_MWh": {k: round(v, 2) for k, v in production.items()},
            "total_production_MWh": round(total_production, 2),
            "surplus_MWh": round(surplus_mwh, 2),
            "deficit_MWh": round(deficit_mwh, 2),
            "emissions_tCO2": round(emissions_tco2, 2)
        }
