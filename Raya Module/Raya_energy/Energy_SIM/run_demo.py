# energy_sim/run_demo.py

from scenario import Scenario
from simulator import EnergySimulator 
import json

def main():
    scen = Scenario(
        region="Testland",
        year=2040,
        population=1_000_000,
        per_capita_kwh=2000,
        mix={"solar": 0.6, "wind": 0.2, "nuclear": 0.1, "hydro": 0.1}
    )

    sim = EnergySimulator()
    result = sim.simulate(scen)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
