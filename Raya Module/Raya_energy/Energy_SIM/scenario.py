# energy_sim/models/scenario.py

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Scenario:
    region: str
    year: int
    population: int
    per_capita_kwh: float
    mix: Dict[str, float]  # e.g. {"solar": 0.5, "coal": 0.5}
    capacity_factors: Optional[Dict[str, float]] = None
    capacity_mw: Optional[Dict[str, float]] = None

#✅ Ready for Next Step?

#Let me know if you want to now:

#Add a new feature (e.g. cost, storage, variability)?

#Create a UI or API?

#Add support for multiple scenarios or CSV input?

#Or just ask about how to improve the code architecture.