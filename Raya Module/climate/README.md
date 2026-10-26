#  Climate Intelligence System — Task 006

## Continuous Live Weather Ingestion, Multi-Variable Forecasting & Future Risk Intelligence

Task 006 extends the Climate Intelligence System into a more advanced climate intelligence pipeline.

The system combines **live weather ingestion, multi-variable climate forecasting, forecast uncertainty estimation, predictive climate-state classification, future anomaly detection, and evidence-driven future risk assessment**.

The objective is to transform historical and newly ingested climate data into structured future climate intelligence.

---

##  Task 006 Objectives

The main objectives of Task 006 are:

* Continuous live weather data ingestion
* Integration of latest weather observations
* Multi-variable climate forecasting
* Forecasting of temperature, rainfall and wind speed
* Forecast uncertainty estimation
* Predictive future climate-state classification
* Future climate anomaly detection
* Evidence-driven future climate risk assessment
* Structured output generation
* Integration with the Climate Intelligence Dashboard

---

#  System Architecture

```text
                    ┌──────────────────────────┐
                    │      Open-Meteo API      │
                    │   Live Weather Data      │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Live Data Ingestion     │
                    │ live_weather_ingestion.py│
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Climate Database      │
                    │   climate_data.csv       │
                    └────────────┬─────────────┘
                                 │
                 ┌───────────────┼────────────────┐
                 │               │                │
                 ▼               ▼                ▼
        Multi-Variable     Forecast           Climate
         Forecasting      Uncertainty         State
                 │               │                │
                 └───────────────┼────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Future Anomaly Engine  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Evidence-Driven Future   │
                    │      Risk Engine         │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │  Climate Intelligence    │
                    │       Dashboard          │
                    └──────────────────────────┘
```

---

#  Project Structure

```text
Climate Intelligence System task 06/
│
├── anomaly/
│
├── anomaly_monitoring/
│
├── baseline/
│
├── climate_state/
│
├── climate_state_forecast/
│   └── climate_state_forecast.py
│
├── configs/
│
├── dashboard/
│   ├── app.py
│   ├── charts.py
│   ├── metrics.py
│   ├── alerts.py
│   └── app_task5_backup.py
│
├── data/
│   ├── climate_data.csv
│   ├── climate_data_10year.csv
│   └── temperature_forecast.csv
│
├── evidence_risk/
│   └── evidence_risk.py
│
├── forecasting/
│
├── forecast_monitoring/
│
├── forecast_uncertainty/
│   └── forecast_uncertainty.py
│
├── future_anomaly/
│   └── future_anomaly.py
│
├── future_risk/
│
├── impact/
│
├── ingestion/
│
├── live_ingestion/
│   └── live_weather_ingestion.py
│
├── logs/
│
├── monitoring/
│
├── multivariable_forecast/
│   └── multivariable_forecast.py
│
├── notebooks/
│
├── outputs/
│   ├── actual_vs_predicted_regressors.csv
│   ├── climate_baseline.csv
│   ├── climate_anomalies.csv
│   ├── climate_state.csv
│   ├── climate_risk.csv
│   ├── climate_impact.csv
│   ├── climate_recommendations.csv
│   ├── emerging_anomalies.csv
│   ├── forecast_monitoring.csv
│   ├── future_risk_monitoring.csv
│   ├── multivariable_forecast.csv
│   ├── forecast_with_uncertainty.csv
│   ├── future_climate_state.csv
│   ├── future_anomaly.csv
│   └── evidence_based_future_risk.csv
│
├── recommendation/
│
├── risk_engine/
│
├── tests/
│
├── generate_climate_data.py
├── run_dashboard.py
├── README.md
├── requirements.txt
└── Task_05_Documentation.md
```

---

#  Module 1 — Continuous Live Weather Ingestion

### File

```text
live_ingestion/live_weather_ingestion.py
```

This module connects to the **Open-Meteo API** and fetches the latest weather observation.

The ingestion process collects:

* Maximum temperature
* Minimum temperature
* Rainfall
* Wind speed
* Observation date

The new observation is then synchronized with the existing climate database.

### Latest successful execution

```text
TASK 006 - CONTINUOUS LIVE WEATHER INGESTION

Live Observation
Date        : 2026-09-06
Temp Max    : 28.3 °C
Temp Min    : 22.4 °C
Rainfall    : 3.3 mm
Wind Speed  : 18.7 km/h

Existing Records : 4018
Updated Records  : 4019
Latest Date      : 2026-09-06

LIVE INGESTION COMPLETED SUCCESSFULLY
```

### Updated database

```text
data/climate_data.csv
```

The climate database contains the historical climate records along with the newly ingested live observation.

---

#  Module 2 — Multi-Variable Climate Forecasting

### File

```text
multivariable_forecast/multivariable_forecast.py
```

This module performs forecasting for multiple climate variables.

The system forecasts:

* Temperature
* Rainfall
* Wind Speed

### Historical dataset

```text
Historical Records : 4018
Historical Period  : 2014-01-01 to 2024-12-31
```

### Forecast horizon

```text
30 days
```

### Forecast variables

```text
Temp_Max
Rainfall
WindSpeed
```

### Forecast summary

```text
Average Predicted Temperature : 30.37 °C
Maximum Predicted Temperature : 30.37 °C
Minimum Predicted Temperature : 30.37 °C

Average Predicted Rainfall    : 3.36 mm
Maximum Predicted Rainfall    : 3.36 mm

Average Predicted Wind Speed  : 18.25 km/h
Maximum Predicted Wind Speed  : 18.26 km/h
```

### Output

```text
outputs/multivariable_forecast.csv
```

---

#  Module 3 — Forecast Uncertainty Engine

### File

```text
forecast_uncertainty/forecast_uncertainty.py
```

Forecast values are estimates and therefore contain uncertainty.

This module calculates uncertainty ranges for:

* Temperature
* Rainfall
* Wind speed

### Uncertainty estimates

```text
Temperature : ±7.92 °C
Rainfall    : ±15.63 mm
Wind Speed  : ±11.01 km/h
```

For each forecast date, the system generates:

```text
Predicted Value
Lower Bound
Upper Bound
```

### Example

```text
Predicted_Temp_Max : 30.37
Temp_Lower         : 22.45
Temp_Upper         : 38.29
```

### Output

```text
outputs/forecast_with_uncertainty.csv
```

---

#  Module 4 — Predictive Climate State Engine

### File

```text
climate_state_forecast/climate_state_forecast.py
```

This module converts forecast information into an interpretable future climate state.

Each forecast day receives:

* Climate State
* State Severity
* Confidence Score
* State Change

### Climate state distribution

```text
Normal : 30
```

### Severity distribution

```text
LOW : 30
```

### Average confidence

```text
38.71%
```

### Example

```text
Date        : 2025-01-01
Climate State    : Normal
State Severity   : LOW
Confidence Score : 38.71%
State Change     : Initial State
```

Subsequent days were classified as:

```text
Persistent
```

### Output

```text
outputs/future_climate_state.csv
```

---

#  Module 5 — Future Anomaly Engine

### File

```text
future_anomaly/future_anomaly.py
```

This module identifies possible future climate anomalies using the predictive climate-state information.

The engine evaluates forecast conditions and assigns:

* Future anomaly status
* Anomaly signal
* Anomaly severity
* Confidence score

### Current forecast result

```text
Future Anomaly : NORMAL
Anomaly Severity : LOW
Anomaly Signal : None
```

Distribution:

```text
NORMAL : 30
LOW    : 30
None   : 30
```

### Output

```text
outputs/future_anomaly.csv
```

---

#  Module 6 — Evidence-Driven Future Risk Engine

### File

```text
evidence_risk/evidence_risk.py
```

This module converts future anomaly intelligence into an evidence-driven risk assessment.

The engine produces:

* Risk score
* Risk level
* Recommended action

### Current result

```text
Risk Level Distribution

LOW : 30
```

### Risk score

```text
Average Risk Score : 0.00
Maximum Risk Score : 0
```

### Recommended action

```text
Routine climate monitoring
```

This indicates that the current 30-day forecast does not generate a significant future climate risk according to the implemented risk logic.

### Output

```text
outputs/evidence_based_future_risk.csv
```

---

#  Generated Outputs

Task 006 generates the following important intelligence files:

| Output File                      | Purpose                                 |
| -------------------------------- | --------------------------------------- |
| `multivariable_forecast.csv`     | Multi-variable climate forecast         |
| `forecast_with_uncertainty.csv`  | Forecast values with uncertainty bounds |
| `future_climate_state.csv`       | Predictive climate-state classification |
| `future_anomaly.csv`             | Future anomaly detection                |
| `evidence_based_future_risk.csv` | Evidence-driven future risk             |
| `climate_data.csv`               | Updated climate database                |

Existing Task 005 outputs are also retained for continuity.

---

#  Climate Intelligence Dashboard

The project includes a Streamlit dashboard.

### Dashboard file

```text
dashboard/app.py
```

The dashboard is designed to provide a centralized view of climate intelligence.

### Dashboard features

* Current climate information
* Historical climate metrics
* Temperature trend
* Rainfall trend
* Temperature forecasting
* Forecast confidence interval
* Actual vs predicted temperature
* Forecast data
* Climate risk information
* Project summary

---

#  Technology Stack

The project uses:

* **Python**
* **Pandas**
* **NumPy**
* **Prophet**
* **Scikit-learn**
* **Streamlit**
* **Plotly**
* **Requests**
* **Open-Meteo API**

---

#  Installation

Clone or download the project and open the project directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

#  Requirements

The main dependencies are:

```text
pandas
numpy
prophet
streamlit
plotly
scikit-learn
requests
```

---

#  Running the Live Ingestion

From the project root:

```powershell
python .\live_ingestion\live_weather_ingestion.py
```

The module fetches the latest weather information and updates:

```text
data/climate_data.csv
```

---

#  Running Multi-Variable Forecasting

```powershell
python .\multivariable_forecast\multivariable_forecast.py
```

Output:

```text
outputs/multivariable_forecast.csv
```

---

#  Running Forecast Uncertainty

```powershell
python .\forecast_uncertainty\forecast_uncertainty.py
```

Output:

```text
outputs/forecast_with_uncertainty.csv
```

---

#  Running Predictive Climate State

```powershell
python .\climate_state_forecast\climate_state_forecast.py
```

Output:

```text
outputs/future_climate_state.csv
```

---

#  Running Future Anomaly Detection

```powershell
python .\future_anomaly\future_anomaly.py
```

Output:

```text
outputs/future_anomaly.csv
```

---

#  Running Evidence-Driven Future Risk

```powershell
python .\evidence_risk\evidence_risk.py
```

Output:

```text
outputs/evidence_based_future_risk.csv
```

---

#  Running the Dashboard

From the project root:

```powershell
streamlit run .\dashboard\app.py
```

The dashboard will open in the browser.

Default local address:

```text
http://localhost:8501
```

---

#  Task 006 End-to-End Pipeline

The complete Task 006 intelligence flow is:

```text
Open-Meteo API
      ↓
Live Weather Ingestion
      ↓
Climate Database
      ↓
Multi-Variable Forecasting
      ↓
Forecast Uncertainty
      ↓
Predictive Climate State
      ↓
Future Anomaly Detection
      ↓
Evidence-Driven Future Risk
      ↓
Climate Intelligence Dashboard
```

---

#  Task 006 Completion Status

| Module                             | Status        |
| ---------------------------------- | ------------- |
| Continuous Live Weather Ingestion  |  Completed   |
| Multi-Variable Forecasting         |  Completed   |
| Forecast Uncertainty Engine        |  Completed   |
| Predictive Climate State Engine    |  Completed   |
| Future Anomaly Engine              |  Completed   |
| Evidence-Driven Future Risk Engine |  Completed   |
| Output Generation                  |  Completed   |
| Dashboard Integration              |  Implemented |

---

#  Project Significance

Task 006 advances the Climate Intelligence System from historical analysis and monitoring toward **future-oriented climate intelligence**.

The system is capable of combining:

```text
Live Observations
+
Historical Climate Data
+
Multi-Variable Forecasts
+
Uncertainty Information
+
Climate State Classification
+
Future Anomaly Detection
+
Evidence-Based Risk Assessment
```

This creates a structured foundation for future development of more advanced climate intelligence capabilities.

---

#  Future Development

Potential future enhancements include:

* More continuous live weather ingestion
* Additional climate variables
* Improved multi-variable forecasting
* Advanced uncertainty modelling
* Evidence-weighted risk scoring
* Longer forecasting horizons
* Automated alert generation
* Real-time dashboard updates
* More advanced climate-risk intelligence
* Integration of additional weather and climate data sources

---

#  Project

**Climate Intelligence System — Task 006**

Developed as part of the RAYA Climate Intelligence work.

**Focus:** Live Climate Monitoring, Multi-Variable Forecasting, Uncertainty Analysis, Future Climate States, Anomaly Detection and Evidence-Driven Future Risk Intelligence.
