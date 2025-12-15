# RAYA Water Module

A simple and clean implementation of India's water intelligence system for the RAYA project. This module provides:

* Year‑wise population lookup
* National water availability & demand insights
* Rainfall factors (ENSO, IOD, SST, etc.)
* Rainfall prediction error validation
* A scientific validation mode that generates **MAE, MAPE, RMSE**

This folder represents the core water‑resource engine inside **RAYA Module → RAYA Water**.

---

## Folder Structure

```
Raya Water/
│
├── assets/                # Extra references or notes
├── data/                  # All CSV datasets (population, rainfall, water demand, etc.)
│
├── raya.c                 # Main source code for the water module
├── raya.exe               # Compiled executable
│
├── test_resource_module.ps1   # Automated CI testing script
├── validation_summary.csv      # Output generated during validation mode
```

---

## How to Run the Water Module

### **1. Normal Mode (Interactive)**

This mode asks for a year between **1925–2125** and prints:

* Population
* Water demand & crisis status
* Rainfall & climate factors
* Rainfall prediction error (1925–2025 only)

Run:

```
./raya.exe
```

Then enter any year, for example:

```
Enter The Year:- 2030
```

Enter a year outside the valid range to exit.

---

## Validation Mode – Scientific Rainfall Accuracy Check

To validate the rainfall prediction model:

```
./raya.exe --validation
```

This will:

* Read **rainfall_error_validation_1925_2025.csv**
* Compute:

  * **MAE** (Mean Absolute Error)
  * **MAPE** (Mean Absolute Percentage Error)
  * **RMSE** (Root Mean Squared Error)
* Save results in **validation_summary.csv**
* Print a single clean line:

```
Validation Complete: MAPE = X%
```

This helps ensure RAYA Water module remains scientifically reliable.

---

## Automated Testing

Use the PowerShell script:

```
./test_resource_module.ps1
```

It will automatically:

* Run the program for year 2000
* Run for year 2050
* Run validation mode
* Check if `validation_summary.csv` is created
* Print **Test Passed / Test Failed** messages

This ensures contributors don't break core functionality.

---

## Data Sources Used in This Module

All CSVs inside `data/`:

* `year_population_1925-2125.csv`
* `water_demand_supply_1925_2125.csv`
* `climate_rainfall_factors_1925_2125.csv`
* `rainfall_error_validation_1925_2025.csv`

These provide the backbone for simulation & analysis.

---

