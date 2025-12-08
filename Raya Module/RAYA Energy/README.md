1️⃣ Energy Mix %

We compute the share of each generation source in the total installed capacity or annual generation.

Formula example:

coal_percent
=
coal_MW
total_installed_capacity_MW
×
100
coal_percent=
total_installed_capacity_MW
coal_MW
	​

×100

Similarly for solar, wind, hydro, gas, biomass, nuclear.

Why: Understand how dependent a state is on fossil vs renewable energy.

2️⃣ CO₂ Intensity per MWh
CO2_intensity
=
CO2_emissions_MtCO2
×
10
6
annual_generation_GWh
×
1000
 tCO2/MWh
CO2_intensity=
annual_generation_GWh×1000
CO2_emissions_MtCO2×10
6
	​

 tCO2/MWh

Converts MtCO₂ → tCO₂, GWh → MWh.

Gives emissions per unit of electricity, a standard sustainability metric.

Why: Compare carbon efficiency between states.

3️⃣ Renewable Share Index
renewables_share_percent
=
sum of renewable capacity (MW)
total_installed_capacity_MW
×
100
renewables_share_percent=
total_installed_capacity_MW
sum of renewable capacity (MW)
	​

×100

Include solar (utility + rooftop), wind, biomass, other renewables.

Already in CSV as a placeholder, but this script can recalc it dynamically if real data is updated.

Why: Quickly identify how green a state’s electricity grid is.

4️⃣ Grid Reliability Index

You can define a composite index based on:

T&D losses (%)

Peak demand vs generation

Microgrid coverage

Example formula:

grid_reliability=100−TnD_losses_percent+0.1×microgrid_projects_count−0.01×(peak_demand - total_installed_capacity)


Scaled so higher = more reliable

Can be refined as you collect actual outage & performance data