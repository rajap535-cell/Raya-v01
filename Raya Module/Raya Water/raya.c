#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* ===================== CONFIG ===================== */
#define YEAR_MIN 1925
#define YEAR_MAX 2125
#define PAST_YEAR_MAX 2025

#define DATA_DIR "data/"
#define RAINFALL_ERROR_FILE DATA_DIR "rainfall_error_validation_1925_2025.csv"
#define POPULATION_FILE     DATA_DIR "year_population_1925-2125.csv"
#define WATER_FILE          DATA_DIR "water_demand_supply_1925_2125.csv"
#define RAINFALL_FILE       DATA_DIR "climate_rainfall_factors _1925_2125.csv"
/* ================================================== */

void validate_rainfall() {
    FILE *fp = fopen(RAINFALL_ERROR_FILE, "r");
    if (fp == NULL) {
        perror("Error opening rainfall error file");
        exit(EXIT_FAILURE);
    }

    char line[200];
    fgets(line, sizeof(line), fp); // skip header

    double mae_sum = 0.0;
    double mape_sum = 0.0;
    double rmse_sum = 0.0;
    int count = 0;

    while (fgets(line, sizeof(line), fp)) {
        int Year;
        double Observed, Predicted, ErrorPct;

        if (sscanf(line, "%d,%lf,%lf,%lf", 
                   &Year, &Observed, &Predicted, &ErrorPct) != 4) {
            continue;
        }

        double abs_err = fabs(Observed - Predicted);
        double pct_err = fabs(abs_err / Observed) * 100;

        mae_sum += abs_err;
        mape_sum += pct_err;
        rmse_sum += abs_err * abs_err;

        count++;
    }

    fclose(fp);

    if (count == 0) {
        printf("Validation failed: No data found.\n");
        return;
    }

    double MAE  = mae_sum / count;
    double MAPE = mape_sum / count;
    double RMSE = sqrt(rmse_sum / count);

    FILE *out = fopen("validation_summary.csv", "w");
    if (out == NULL) {
        perror("Error writing validation_summary.csv");
        exit(EXIT_FAILURE);
    }

    fprintf(out, "Metric,Value\n");
    fprintf(out, "MAE,%.4lf\n", MAE);
    fprintf(out, "MAPE,%.4lf\n", MAPE);
    fprintf(out, "RMSE,%.4lf\n", RMSE);

    fclose(out);

    printf("Validation Complete: MAPE = %.2lf%%\n", MAPE);
}

int population(int year){
        FILE *fp = fopen("data\\year_population_1925-2125.csv", "r");
        if (fp == NULL) {
            perror("Error opening file");
            exit(EXIT_FAILURE);
        }
        else{
            char line[20];
            fgets(line, sizeof(line), fp);
            while (fgets(line, sizeof(line), fp)) {
                int Year;
                int Population;
                int found = 0;
                sscanf(line, "%d,%d", &Year, &Population);
                if (Year == year) {
                    printf("\nPopulation for: %d\n", Year);
                    printf("Population of India: %d\n\n", Population);
                    found = 1;
                    fclose(fp);
                    return 0;
                }
            }  
        }
    return 0; 
}

int waterCrisis(int demandYear){
        FILE *fp = fopen("data\\water_demand_supply_1925_2125.csv", "r");
        if (fp == NULL) {
            perror("Error opening file");
            exit(EXIT_FAILURE);
        }
        else{
            char line[200];
            fgets(line, sizeof(line), fp);
            while (fgets(line, sizeof(line), fp)) {
                int Year;
                double Total_Water_Availability_Litre,Water_Demand_Agriculture,Water_Demand_Industry,Water_Demand_Energy,Water_Demand_Domestic,Water_Demand_Other,PerCapita_Availability,PerCapita_Demand;
                char Crisis_Status[10] = " ";
                int found = 0;
                sscanf(line, "%d,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%s", &Year, &Total_Water_Availability_Litre, &Water_Demand_Agriculture, &Water_Demand_Industry, &Water_Demand_Energy, &Water_Demand_Domestic, &Water_Demand_Other, &PerCapita_Availability, &PerCapita_Demand, Crisis_Status);
                if (Year == demandYear) {
                    printf("Water Crisis details for: %d\n", Year);
                    printf("(1) Total Water Availability in Litre: %.2lf\n", Total_Water_Availability_Litre);
                    printf("(2) Water Demand for Agriculture: %.2lf\n", Water_Demand_Agriculture);
                    printf("(3) Water Demand for Industry: %.2lf\n", Water_Demand_Industry);
                    printf("(4) Water Demand for Energy: %.2lf\n", Water_Demand_Energy);
                    printf("(5) WaterDemand for Domestic: %.2lf\n", Water_Demand_Domestic);
                    printf("(6) Water Demand for Other: %.2lf\n", Water_Demand_Other);
                    printf("(7) PerCapita Water Availability: %.2lf\n", PerCapita_Availability);
                    printf("(8) PerCapita Water Demand: %.2lf\n", PerCapita_Demand);
                    printf("(9) Crisis Status: %s\n", Crisis_Status);
                    printf("General Information: Average per person per day demand for domestic use is set  for Rural Area =  55 litre  According to Ministry of Urban and Housing Affairs\n");
                    printf("Average per person per day demand for domestic use is set for Urban Area =  135 litre  According to Ministry of Urban and Housing Affairs\n\n" );
                    found = 1;
                    fclose(fp);
                    return 0;
                }
            }  
        }
    return 0; 
}

void rainfall_for_year(int year){
    FILE *fp = fopen("data\\climate_rainfall_factors _1925_2125.csv", "r");
    if (fp == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }
    else{
        char line[350];
        fgets(line, sizeof(line), fp);
        while (fgets(line, sizeof(line), fp)) {
            int Year;
            double ENSO, IOD, SST_IO, DeltaT, AOD, Cyclones, LandUse, FiveYear_MA, Rainfall;
            char Crisis_Status[10];
            int found = 0;
            sscanf(line, "%d,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%s", &Year, &Rainfall, &ENSO, &IOD, &SST_IO, &DeltaT, &AOD, &Cyclones, &LandUse, &FiveYear_MA, Crisis_Status);
            if (Year == year) {
                printf("Rainfall and factors for %d:\n", Year);
                printf("All-India average rainfall: %.2lf mm\n", Rainfall);
                printf("Factors:\n");
                printf("(1) ENSO (El Nino-Southern Oscillation): %.2lf\n", ENSO);
                printf("(2) IOD (Indian Ocean Dipole): %.2lf\n", IOD);
                printf("(3) SST_IO (Sea Surface Temp Anomaly): %.2lf\n", SST_IO);
                printf("(4) DeltaT (Avg Temp Anomaly): %.2lf\n", DeltaT);
                printf("(5) AOD (Aerosol Optical Depth): %.2lf\n", AOD);
                printf("(6) Cyclones: %.2lf\n", Cyclones);
                printf("(7) LandUse index: %.2lf\n", LandUse);
                printf("(8) 5-Year Moving Avg: %.2lf\n", FiveYear_MA);
                printf("*Crisis Condition: %s\n", Crisis_Status);
                found = 1;
                fclose(fp);
                return;
            }
        }  
        fclose(fp);
        return; 
    }
}

void rainfall_error(int year){
    if(year >= 1925 && year <= 2025){
        FILE *fp = fopen("data\\rainfall_error_validation_1925_2025.csv", "r");
        if (fp == NULL) {
            perror("Error opening file");
            exit(EXIT_FAILURE);
        }
        else{
            char line[100];
            fgets(line, sizeof(line), fp);
            while (fgets(line, sizeof(line), fp)) {
                int Year;
                double Observed_Rainfall_mm,Predicted_Rainfall_mm,Error_pct;
                char Crisis_Status[10];
                int found = 0;
                sscanf(line, "%d,%lf,%lf,%lf", &Year, &Observed_Rainfall_mm, &Predicted_Rainfall_mm, &Error_pct);
                if (Year == year) {
                    printf("Error or difference between Actual Rainfall and Predicted Rainfall for %d:\n", Year);
                    printf("Factors:\n");
                    printf("(1) Observed or Actual Rainfall: %.2lf\n", Observed_Rainfall_mm);
                    printf("(2) Pridicted Rainfall: %.2lf\n", Predicted_Rainfall_mm);
                    printf("(3) Error or difference between Actual Rainfall and Predicted Rainfall: %.2lf\n", Error_pct);
                    found = 1;
                    fclose(fp);
                    return;
                }
            }  
        }
        fclose(fp);
        return; 
    }
    else{
        printf("We can calculate Error or difference between Actual Rainfall and Predicted Rainfall for past years only.\n");
        printf("For future years we could only get predicted data.");
        printf("\nSo, If You want to get Error or difference between Actual Rainfall and Predicted Rainfall, Please, give year between 1925 to 2025.\nThank You!\n");
    }
}

int runWaterResourceModule(){
    int year;
    printf("\nEnter the Year between 1925 and 2125.\n");
    printf("For Exit Enter any Year beyond above range!\n");
    printf("Enter The Year:- ");
    scanf("%d", &year);
    while(year >= 1925 && year <= 2125){
        population(year);
        waterCrisis(year);
        rainfall_for_year(year);
        rainfall_error(year);
        printf("\nEnter the Year between 1925 and 2125.\n");
        printf("For Exit Enter any Year beyond above range!\n");
        printf("Enter The Year:- ");
        scanf("%d", &year);
    }
    if(!(year >= 1925 && year <= 2125)){
        printf("You have given Input beyond given range, Thank You to visit!");
        return 0;
    }
    return 0;
}

int main(int argc, char *argv[]){
    if (argc > 1 && strcmp(argv[1], "--validation") == 0) {
        validate_rainfall();
        return 0; 
    }

    runWaterResourceModule();
    return 0;
}