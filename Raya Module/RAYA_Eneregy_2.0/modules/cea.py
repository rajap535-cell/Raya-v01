"""
Central Electricity Authority Power Data Module
"""

import numpy as np
from datetime import datetime

class CEAPowerData:
    """Central Electricity Authority Power Data Simulation"""
    
    def __init__(self):
        # Historical and projected data for Indian cities
        self.city_power_data = {
            'Delhi': {
                'base_consumption': 4500,
                'peak_consumption': 6500,
                'off_peak_consumption': 2800,
                'industrial_load': 0.7,
                'residential_load': 0.25,
                'commercial_load': 0.05,
                'growth_rate': 0.05,
                'capacity_mw': 8500,
                'renewable_share': 0.15,
                'peak_hours': [18, 19, 20, 21],
                'demand_supply_gap': 200
            },
            'Mumbai': {
                'base_consumption': 3800,
                'peak_consumption': 5200,
                'off_peak_consumption': 2500,
                'industrial_load': 0.8,
                'residential_load': 0.15,
                'commercial_load': 0.05,
                'growth_rate': 0.06,
                'capacity_mw': 7000,
                'renewable_share': 0.12,
                'peak_hours': [19, 20, 21, 22],
                'demand_supply_gap': 150
            },
            'Chennai': {
                'base_consumption': 2800,
                'peak_consumption': 3800,
                'off_peak_consumption': 1800,
                'industrial_load': 0.6,
                'residential_load': 0.35,
                'commercial_load': 0.05,
                'growth_rate': 0.04,
                'capacity_mw': 4500,
                'renewable_share': 0.10,
                'peak_hours': [18, 19, 20],
                'demand_supply_gap': 100
            },
            'Kolkata': {
                'base_consumption': 3200,
                'peak_consumption': 4500,
                'off_peak_consumption': 2000,
                'industrial_load': 0.5,
                'residential_load': 0.40,
                'commercial_load': 0.10,
                'growth_rate': 0.03,
                'capacity_mw': 5000,
                'renewable_share': 0.08,
                'peak_hours': [18, 19, 20, 21],
                'demand_supply_gap': 120
            },
            'Bangalore': {
                'base_consumption': 3100,
                'peak_consumption': 4200,
                'off_peak_consumption': 1900,
                'industrial_load': 0.75,
                'residential_load': 0.20,
                'commercial_load': 0.05,
                'growth_rate': 0.08,
                'capacity_mw': 5500,
                'renewable_share': 0.20,
                'peak_hours': [18, 19, 20, 21],
                'demand_supply_gap': 80
            }
        }
        
        # Power grid status codes
        self.grid_status = {
            'normal': '🟢 Normal',
            'alert': '🟡 Alert - High Demand',
            'critical': '🔴 Critical - Load Shedding Possible',
            'emergency': '🟣 Emergency - Load Shedding Active'
        }
    
    def get_power_data(self, city):
        """Get comprehensive power consumption data for city"""
        if city not in self.city_power_data:
            raise ValueError(f"Power data not available for {city}")
        
        data = self.city_power_data[city]
        hour = datetime.now().hour
        day_type = 'weekend' if datetime.now().weekday() >= 5 else 'weekday'
        month = datetime.now().month
        
        # Calculate time-based consumption multiplier
        time_multiplier = self._calculate_time_multiplier(hour, data['peak_hours'])
        
        # Day type adjustment
        if day_type == 'weekend':
            time_multiplier *= 0.85  # Reduced commercial/industrial activity
            residential_multiplier = 1.1  # Increased residential usage
            time_multiplier = (time_multiplier + residential_multiplier) / 2
        
        # Month adjustment (seasonal variation)
        month_adjustment = self._get_month_adjustment(month)
        time_multiplier *= month_adjustment
        
        # Calculate consumption
        base = data['base_consumption']
        consumption = base * time_multiplier
        
        # Add growth factor
        years_since_base = (datetime.now().year - 2023)  # Assuming base year 2023
        growth_factor = (1 + data['growth_rate']) ** years_since_base
        consumption *= growth_factor
        
        # Add random variation (±5%)
        random_variation = np.random.uniform(0.95, 1.05)
        consumption *= random_variation
        
        # Ensure within limits
        consumption = max(data['off_peak_consumption'] * 0.9, 
                         min(consumption, data['peak_consumption'] * 1.1))
        
        # Calculate demand-supply gap
        current_gap = self._calculate_current_gap(consumption, data['capacity_mw'])
        
        # Get grid status
        grid_status = self._get_grid_status(consumption, data['capacity_mw'])
        
        # Calculate load distribution
        load_distribution = self._calculate_load_distribution(data, hour, day_type)
        
        return {
            'city': city,
            'power_consumption_mw': int(consumption),
            'base_consumption': data['base_consumption'],
            'peak_consumption': data['peak_consumption'],
            'off_peak_consumption': data['off_peak_consumption'],
            'capacity_mw': data['capacity_mw'],
            'time_multiplier': round(time_multiplier, 2),
            'day_type': day_type,
            'hour': hour,
            'grid_status': grid_status,
            'grid_status_code': self._get_grid_status_code(grid_status),
            'demand_supply_gap_mw': int(current_gap),
            'load_distribution': load_distribution,
            'renewable_share': data['renewable_share'],
            'growth_rate': data['growth_rate'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_time_multiplier(self, hour, peak_hours):
        """Calculate time-based consumption multiplier"""
        if hour in peak_hours:
            return 1.4  # Peak hours
        elif 6 <= hour <= 9:  # Morning peak
            return 1.2
        elif 10 <= hour <= 16:  # Daytime
            return 1.0
        elif 22 <= hour <= 23 or 0 <= hour <= 5:  # Night
            return 0.7
        else:  # Evening shoulder
            return 1.1
    
    def _get_month_adjustment(self, month):
        """Get monthly adjustment factor"""
        # Summer months have higher AC usage
        if month in [3, 4, 5, 6]:  # March to June
            return 1.15
        elif month in [12, 1, 2]:  # December to February
            return 0.95  # Lower cooling/heating needs in moderate winters
        else:
            return 1.0
    
    def _calculate_current_gap(self, consumption, capacity):
        """Calculate current demand-supply gap"""
        gap = consumption - capacity * 0.9  # Assume 90% of capacity is available
        return max(0, gap)  # Only show positive gaps
    
    def _get_grid_status(self, consumption, capacity):
        """Determine current grid status"""
        utilization = consumption / capacity
        
        if utilization > 0.95:
            return self.grid_status['emergency']
        elif utilization > 0.85:
            return self.grid_status['critical']
        elif utilization > 0.75:
            return self.grid_status['alert']
        else:
            return self.grid_status['normal']
    
    def _get_grid_status_code(self, status):
        """Get grid status code"""
        for code, text in self.grid_status.items():
            if text == status:
                return code
        return 'normal'
    
    def _calculate_load_distribution(self, data, hour, day_type):
        """Calculate current load distribution"""
        base_distribution = {
            'industrial': data['industrial_load'],
            'residential': data['residential_load'],
            'commercial': data['commercial_load']
        }
        
        # Adjust based on time of day
        if day_type == 'weekend':
            base_distribution['industrial'] *= 0.3
            base_distribution['commercial'] *= 0.5
            base_distribution['residential'] = 1 - (base_distribution['industrial'] + base_distribution['commercial'])
        elif 9 <= hour <= 17:  # Business hours
            base_distribution['commercial'] *= 1.2
            base_distribution['industrial'] *= 0.9
        elif 18 <= hour <= 22:  # Evening residential peak
            base_distribution['residential'] *= 1.3
            base_distribution['commercial'] *= 0.7
        
        # Normalize
        total = sum(base_distribution.values())
        normalized = {k: round(v/total, 3) for k, v in base_distribution.items()}
        
        return normalized
    
    def get_city_power_profile(self, city):
        """Get complete power profile for a city"""
        if city not in self.city_power_data:
            raise ValueError(f"Power profile not available for {city}")
        
        data = self.city_power_data[city]
        
        return {
            'city': city,
            'base_load_mw': data['base_consumption'],
            'peak_load_mw': data['peak_consumption'],
            'capacity_mw': data['capacity_mw'],
            'growth_rate': data['growth_rate'],
            'renewable_share': data['renewable_share'],
            'load_distribution': {
                'industrial': data['industrial_load'],
                'residential': data['residential_load'],
                'commercial': data['commercial_load']
            },
            'peak_hours': data['peak_hours'],
            'avg_demand_supply_gap': data['demand_supply_gap'],
            'energy_mix': self._get_energy_mix(city)
        }
    
    def _get_energy_mix(self, city):
        """Get energy mix for the city"""
        mixes = {
            'Delhi': {'thermal': 0.60, 'renewable': 0.15, 'hydro': 0.10, 'nuclear': 0.10, 'import': 0.05},
            'Mumbai': {'thermal': 0.55, 'renewable': 0.12, 'hydro': 0.20, 'nuclear': 0.10, 'import': 0.03},
            'Chennai': {'thermal': 0.65, 'renewable': 0.10, 'hydro': 0.15, 'nuclear': 0.08, 'import': 0.02},
            'Kolkata': {'thermal': 0.70, 'renewable': 0.08, 'hydro': 0.12, 'nuclear': 0.08, 'import': 0.02},
            'Bangalore': {'thermal': 0.50, 'renewable': 0.20, 'hydro': 0.20, 'nuclear': 0.05, 'import': 0.05}
        }
        return mixes.get(city, {'thermal': 0.60, 'renewable': 0.15, 'hydro': 0.15, 'nuclear': 0.08, 'import': 0.02})