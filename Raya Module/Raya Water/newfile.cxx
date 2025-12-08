#include <stdio.h>
#include<stdlib.h>

int daysInMonth(int n){
    if( n == 2){
        return 28;
    }
    else if( n < 8){
        if(n%2 == 0){
            return 30;
        }
        else{
            return 31;
        }
    }
    else{
        if(n%2 == 0){
            return 31;
        }
        else{
            return 30;
        }
    }
}

int isLeapYear(int y){
    if(y%100 == 0){
        if( y%400 == 0){
                return 1;
        }
        else{
            return 0;
        }
    }
    else if(y%4 == 0){
            return 1;
    }
    else{
        return 0;
    }
}

int leapYear(int y1, int y2){
    int count = 0;
    for(int i = y1; i <= y2; i++){
        if(i%100 == 0){
            if( i%400 == 0){
                count = count +1;
            }
        }
        else if(i%4 == 0){
            count++;
        }
    }
    return count;
}

int numOfDays(int m1, int m2, int d1, int d2){
    int total = 0;
    if(m1 < m2){
        for(int i = m1; i <= m2; i++){
            if(i == m1){
                total = total + daysInMonth(i)-d1 +1;
            }
            else if( i == m2){
                total = total + d2;
            }
            else{
                total = total + daysInMonth(i);
            }
        }  
    }
    else if(m1 == m2){
        total = total + (d2 - d1);;
    }
    else{
        for(int i = m1; i != 12 ; i++){
            if(i == m1){
                total = total + daysInMonth(i)-d1 +1;
            }
            else{
                total = total + daysInMonth(i);
            }
        }
        for(int i = m2; i > 0; i--){
            if( i == m2){
                total = total + d2;
            }
            else{
                total = total + daysInMonth(i);
            }
        }
        total = total - 365;
    }
    return total;
}


int calculateDays(int d1, int d2, int m1, int m2, int y1, int y2){
    int total = 0;
    if( isLeapYear(y1) == 1 && m1 <= 2){
        if(isLeapYear(y2) == 1 && m2 > 2){
            total = total + numOfDays(m1, m2, d1, d2) + leapYear(y1, y2);
        }
        else{
            total = total + numOfDays(m1, m2, d1, d2) + leapYear(y1, y2) -1;
        }
    }
    else{
        if(isLeapYear(y2) == 1 && m2 > 2){
            total = total + numOfDays(m1, m2, d1, d2) + leapYear(y1, y2)-1;
        }
        else{
            total = total + numOfDays(m1, m2, d1, d2) + leapYear(y1, y2) -2;
        }
    } 
    total = total + (y2 - y1) * 365;
    return total;  
}

int waterDistributionPerCapitaForIndia(){
    double x = 3838.00;  
    // x = todays_expected_wateravailibity_in_litre_for_2025 according to ministey of water resources under Govt of india
    double y = 3507; 
    // y = expected_wateravailibility_in_litre_for_2035
    
    int d2, m2, y2;
    printf("\nEnter the current date (eg. if current date is 6th November 2025, given it as 6 11 2025 ) :- ");
    scanf("%d %d %d", &d2, &m2, &y2);
    int z = calculateDays(1, d2, 1, m2, 2025, y2);

    double expected_change_in_decade = x- y;
    // printf("%lf", expected_change_in_decade);

    double expecter_change_perYear = expected_change_in_decade / 10;
    double per_day_changes = (expecter_change_perYear)/365;
    double per_capita_availibility = (3838 - (per_day_changes * z));

    if(y2 < 2025 || y2 > 2035){
        printf("invalit input, Please input year between 2025 and 2035\n\n");
        return 0;
    }
        

    printf("Water available in India on %d/%d/%d = %.2lf", d2, m2, y2, per_capita_availibility);
    printf("litre\n");
    printf("This data is calculated on projected data by Ministry of water - Govt of India for 2035\n\n");
    return 0;
}

int population(){
    int population_year;
    long population_2025 = 1467335156;
    long population =  population_2025;
    float percentage_change[10] = {0.88, 0.87, 0.86, 0.84, 0.82, 0.78, 0.71, 0.72, 0.71, 0.71}; //yearly percentage change  given for 2026 t0 2035

    printf("which year population you want to know, Please enter the year:- ");
    scanf("%d", &population_year);

    if(population_year == 2025){
        printf("population of 2025 = %ld according to United Nation Population Devision and world Bank prediction estimates\n\n", population);
    }

    else if(population_year < 2036 && population_year > 2025){
        for(int i = 2026; i <= population_year; i++ ){
            population = population + (population_2025 * percentage_change[population_year - 2026])/100;
        }
        printf("population of %d = %ld \nAbove data is based on United Nation Population Devision and world Bank prediction estimates \n\n", population_year, population);
    }

    else{
        printf("We don't have accurate estimate data for %d , after seeing decreasing fertility trends.", population_year);
        printf("It is estimated by national and internaional organisations population of India will start to decrease from 2060.");
        printf("So, now, We can provide data here till 2060. Thank You!\n\n");
    }
    return 0;
}

int waterCrisis(){
    int demandYear;
    double waterDemandForAgri = 611000000000000;
    double waterDemandForIndustries = 67000000000000;
    double waterDemandForEnergy = 33000000000000;
    double waterDemandForDomestic = 73000000000000;
    double waterDemandForOtherUses = 70000000000000;

    long population= 1467335156;
    float percentage_change[11] = {0.88, 0.87, 0.86, 0.84, 0.82, 0.78, 0.71, 0.72, 0.71, 0.71};
    
    double waterAvailability = 3838 * population;
    double perCapitaWaterAvailibility;


    printf("Enter the Year for which you want to know water crisis details :- ");
    scanf("%d", &demandYear);

    int waterDemandPerCapita_Rural2025 = 55;  //It is set by Ministry of Urban and Housing Affairs
    int waterDemandPerCapita_Urban2025 = 135; // It is set by Ministry of JalShakti

    if(demandYear <2025 || demandYear > 2035){
        printf("Please give year between 2025 to 2035. For now, We don't have data beyond it. We will make it available very soon. Thank You!");
    }
    else{
        for(int i = 2026; i <= demandYear; i++ ){

        waterDemandForAgri = waterDemandForAgri + waterDemandForAgri * 0.92 / 100; 
        waterDemandForIndustries = waterDemandForIndustries + waterDemandForIndustries * 1.92 / 100;
        waterDemandForEnergy = waterDemandForEnergy + waterDemandForEnergy * 6.58 / 100;
        waterDemandForDomestic = waterDemandForDomestic + waterDemandForDomestic * 1.056 / 100;
        waterDemandForOtherUses = waterDemandForOtherUses + waterDemandForOtherUses * 1.34 /100;
        waterAvailability = waterAvailability - waterAvailability * 0.91/100;
        population = population + (population * percentage_change[demandYear - 2026])/100;
     }
    }
    
    double totalDemand = waterDemandForAgri + waterDemandForIndustries + waterDemandForEnergy + waterDemandForDomestic + waterDemandForOtherUses;
    double perCapitaWaterAvailibilityDomestic = waterAvailability / population - (totalDemand - waterDemandForDomestic) / (365 * population);

    printf("Per capita water availability for Domestic Use for %d = %.2lf litre\n", demandYear, perCapitaWaterAvailibilityDomestic);
    printf("Water Demand for Domestic Use for %d = %.2lf litre\n", demandYear, (waterDemandForDomestic/365)/population);

    if(perCapitaWaterAvailibilityDomestic < (waterDemandForDomestic/365)/population){
        printf("Water Crisis! We even donot have sufficient water for domestic use. Please, start water harvesting method and other methods to tackle water crisis. \nAnd Also donot waste water! Please, save water, save life!\n\n");
    }
    else{
        printf("Presently, we have sufficient water for domectic use but we should cautions about future. So, please don't waste water! and start to save water!\nNote: This is average data. Water availability can be vary region to region.\n\n");
    }

    printf("Per capita total water availability (including for industries, agriculture, energy generation, domestic use etc.) for %d = %.2lf litre\n", demandYear, waterAvailability / population);
    printf("Per capita total water Demand (including for industries, agriculture, energy generation, domestic use etc.) %d = %.2lf litre\n", demandYear, (totalDemand / 365)/ population);

    if((totalDemand / 365)/ population >  waterAvailability){
        printf("Water Crisis!  Urgent Action Needed. Please, Don't waste water! and start to save water!\n\n");
    }
    else{
        printf("Presently, we have sufficient water but we should cautions about future.So, please don't waste water! and start to save water!\nNote: This is average data. Water availability can be vary region to region.\n\n");
    }

    printf("Average per person per day demand for domestic use is set  for Rural Area =  %d litre  According to Ministry of Urban and Housing Affairs\n",waterDemandPerCapita_Rural2025);
    printf("Average per person per day demand for domestic use is set for Urban Area =  %d litre  According to Ministry of Urban and Housing Affairs\n\n",waterDemandPerCapita_Urban2025 );

    return 0;
}

void rainfall_for_year(){
    FILE *fp = fopen("RAI_tagged_crisis_surplus.csv", "r");
    if (fp == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }
    char line[256];
    fgets(line, sizeof(line), fp); 
    int x;
    printf("Enter the Year : ");
    scanf("%d", &x);

    while (fgets(line, sizeof(line), fp)) {
        int year;
        double ENSO, IOD, SST_IO, DeltaT, AOD, Cyclones, LandUse, FiveYear_MA, RAI;
        char tag[10];

        sscanf(line, "%d,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%s", &year, &ENSO, &IOD, &SST_IO, &DeltaT, &AOD, &Cyclones, &LandUse, &RAI, &FiveYear_MA, tag);
        if((year == (x -2024)) && (x < 2125) && (x > 2024)){
            printf("Rainfall data with data of various factors that affect rainfall for %d\n(1) ENSO(El Niño-Southern Oscillation):- %.2lf\n(2) IOD(Indian Ocean Dipole: temperature difference between western and eastern Indian Ocean):-%.2lf\n(3) SST_IO( Indian Ocean Sea Surface Temperature Anomaly):-%.2lf\n(4) ΔT(Average Temperature Anomaly of India):- %.2lf\n(5) AOD(Aerosol Optical Depth (air pollution)):- %.2lf\n(6) Number of Tropical Cyclones that hit or influenced India:- %.2lf\n(7) Increase in irrigation / urban area index:- %.2lf\n(8) Five Year Moving Average:- %.2lf\nCrisis Condition:-%s\n", year+2024, ENSO, IOD, SST_IO, DeltaT, AOD, Cyclones, LandUse, FiveYear_MA, tag);
            // RAI holds rainfall for this year
            printf("For Year %d:-\nAll-India average rainfall = %.2lf mm\n", year+2024, RAI);

            fclose(fp);
            return;
        }
    }
    printf("Invalid Input:- Please enter year between 2025 to 2124.");

    fclose(fp);
}

int resourceDistribution(){
    waterDistributionPerCapitaForIndia();
    population();
    waterCrisis();
    rainfall_for_year();

    return 0;
}

int main(){
    resourceDistribution();
    return 0;
}