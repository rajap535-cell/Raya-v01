# Rainfall Prediction Evaluation Report

**Data source:** /data/rainfall_error_validation_1925_2025.csv`

## Overall Metrics

- MAE (mm): 21.6255

- MAPE (%): 1.7807

- RMSE (mm): 26.8718


## Decade-wise Summary

|   Decade |   Count |   MAE_mm |   MAPE_pct |   RMSE_mm |
|---------:|--------:|---------:|-----------:|----------:|
|     1920 |       5 |   22.486 |  0.018713  |   27.5737 |
|     1930 |      10 |   19.155 |  0.0149089 |   24.1423 |
|     1940 |      10 |   17.998 |  0.0146003 |   28.6139 |
|     1950 |      10 |   19.227 |  0.0162509 |   22.2508 |
|     1960 |      10 |   25.189 |  0.0200234 |   27.791  |
|     1970 |      10 |   19.338 |  0.0152058 |   24.2508 |
|     1980 |      10 |   23.982 |  0.0205577 |   29.3565 |
|     1990 |      10 |   22.378 |  0.0183762 |   28.9367 |
|     2000 |      10 |   25.205 |  0.0199678 |   30.49   |
|     2010 |      10 |   22.544 |  0.0197024 |   26.5776 |
|     2020 |       6 |   20.265 |  0.0181601 |   23.1198 |

## Observations & Notes

- Median absolute error: 17.560 mm

- Maximum absolute error: 69.480 mm (Year 1998, Observed=1257.33, Predicted=1187.85)

- Percentage of years with MAPE ≤ 10%: 100.00%


## Recommended Next Steps

- Investigate years with highest absolute errors for data issues or anomalous weather patterns.

- Consider additional metrics (bias, R²) and error decomposition by season if seasonal data is available.

- Visual inspection of residuals for heteroscedasticity.
