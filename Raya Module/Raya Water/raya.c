#include <stdio.h>
#include<stdlib.h>


int population(int year){
    if(year > 1900 && year <= 2100){
            FILE *fp = fopen("year_population.csv", "r");
            if (fp == NULL) {
                perror("Error opening file");
                exit(EXIT_FAILURE);
            }
            else{
                char line[200];
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
        }
        return 0; 
}

int waterCrisis(int demandYear){
        if(demandYear > 1900 && demandYear <= 2100){
            FILE *fp = fopen("water_demand_supply.csv", "r");
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
                    int found = 0;
                    sscanf(line, "%d,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%s", &Year, &Total_Water_Availability_Litre, &Water_Demand_Agriculture, &Water_Demand_Industry, &Water_Demand_Energy, &Water_Demand_Domestic, &Water_Demand_Other, &PerCapita_Availability, &PerCapita_Demand);
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
                        printf("General Information: Average per person per day demand for domestic use is set  for Rural Area =  55 litre  According to Ministry of Urban and Housing Affairs\n");
                        printf("Average per person per day demand for domestic use is set for Urban Area =  135 litre  According to Ministry of Urban and Housing Affairs\n\n" );
                        found = 1;
                        fclose(fp);
                        return 0;
                    }
                }  
            }
        }
        return 0; 
}

void rainfall_for_year(int year){
    if(year > 1900 && year <= 2100){
        FILE *fp = fopen("climate_rainfall_factors.csv", "r");
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
                char Crisis_Status[20];
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
        }
        fclose(fp);
        return; 
    }
}

int resourceDistribution(){
    int year;
    printf("\nEnter the Year between 1901 and 2125.\n");
    printf("For Exit Enter any Year beyond above range!\n");
    printf("Enter The Year:- ");
    scanf("%d", &year);
    while(year > 1900 && year <= 2100){
        population(year);
        waterCrisis(year);
        rainfall_for_year(year);
        printf("\nEnter the Year between 1901 and 2100.\n");
        printf("For Exit Enter any Year beyond above range!\n");
        printf("Enter The Year:- ");
        scanf("%d", &year);
    }
    if(!(year > 1900 && year <= 2100)){
        printf("You given Input beyond given range, Thank You to visit!");
        return 0;
    }
    return 0;
}

int main(){
    resourceDistribution();
    return 0;
}