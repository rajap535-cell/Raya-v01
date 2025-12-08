"""
Indian Meteorological Department Weather Simulation Module
"""

import numpy as np
from datetime import datetime

class IMDWeather:
    """Indian Meteorological Department Weather Simulation"""
    
    def __init__(self):
        self.seasons = {
            'winter': (12, 1, 2),
            'summer': (3, 4, 5),
            'monsoon': (6, 7, 8, 9),
            'post_monsoon': (10, 11)
        }
        
        self.city_climate_data = {
            'Delhi': {
                'temp_range': (8, 45),
                'avg_temp': 32,
                'avg_humidity': 65,
                'climate_zone': 'Subtropical',
                'rainfall_mm': 800
            },
            'Mumbai': {
                'temp_range': (18, 38),
                'avg_temp': 28,
                'avg_humidity': 80,
                'climate_zone': 'Tropical',
                'rainfall_mm': 2200
            },
            'Chennai': {
                'temp_range': (20, 42),
                'avg_temp': 34,
                'avg_humidity': 70,
                'climate_zone': 'Tropical',
                'rainfall_mm': 1400
            },
            'Kolkata': {
                'temp_range': (12, 38),
                'avg_temp': 31,
                'avg_humidity': 75,
                'climate_zone': 'Tropical',
                'rainfall_mm': 1800
            },
            'Bangalore': {
                'temp_range': (15, 35),
                'avg_temp': 26,
                'avg_humidity': 60,
                'climate_zone': 'Moderate',
                'rainfall_mm': 1000
            }
        }
    
    def get_season(self):
        """Get current season based on month"""
        month = datetime.now().month
        for season, months in self.seasons.items():
            if month in months:
                return season
        return 'summer'
    
    def get_city_weather(self, city):
        """Get comprehensive weather data for Indian city"""
        if city not in self.city_climate_data:
            raise ValueError(f"Weather data not available for {city}")
        
        data = self.city_climate_data[city]
        season = self.get_season()
        hour = datetime.now().hour
        
        # Calculate temperature with realistic patterns
        base_temp = data['avg_temp']
        
        # Daily variation (cooler at night, warmer in afternoon)
        if 0 <= hour <= 6:  # Early morning
            temp_variation = -8 + hour * 0.5
        elif 7 <= hour <= 12:  # Morning to noon
            temp_variation = -4 + (hour - 7) * 1.5
        elif 13 <= hour <= 16:  # Afternoon peak
            temp_variation = 5
        elif 17 <= hour <= 21:  # Evening cooling
            temp_variation = 3 - (hour - 17) * 0.5
        else:  # Late night
            temp_variation = -5
        
        # Season adjustment
        season_adjustment = {
            'winter': -6,
            'summer': 4,
            'monsoon': 0,
            'post_monsoon': 0
        }
        
        temp = base_temp + temp_variation + season_adjustment.get(season, 0)
        
        # Random variation
        temp += np.random.uniform(-2, 2)
        temp = round(temp, 1)
        
        # Humidity calculation
        humidity = data['avg_humidity']
        
        # Humidity variations
        if season == 'monsoon':
            humidity += np.random.randint(5, 15)
        elif season == 'summer':
            humidity += np.random.randint(-5, 5)
        
        # Daily humidity pattern
        if 0 <= hour <= 6:  # Higher in early morning
            humidity += 10
        elif 13 <= hour <= 15:  # Lower in afternoon
            humidity -= 5
        
        humidity += np.random.randint(-8, 8)
        humidity = max(30, min(95, humidity))
        
        # Weather condition
        condition = self._get_condition(temp, humidity, season)
        
        return {
            'city': city,
            'temperature': temp,
            'humidity': humidity,
            'season': season,
            'condition': condition,
            'climate_zone': data['climate_zone'],
            'temp_range_min': data['temp_range'][0],
            'temp_range_max': data['temp_range'][1],
            'annual_rainfall': data['rainfall_mm'],
            'feels_like': self._calculate_feels_like(temp, humidity),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_condition(self, temp, humidity, season):
        """Determine weather condition based on parameters"""
        if season == 'monsoon':
            if humidity > 85:
                return 'Rainy'
            else:
                return 'Cloudy'
        elif temp > 38:
            return 'Hot'
        elif temp < 15:
            return 'Cold'
        elif humidity > 75:
            return 'Humid'
        elif humidity < 40:
            return 'Dry'
        elif 20 <= temp <= 30 and 50 <= humidity <= 70:
            return 'Pleasant'
        else:
            return 'Clear'
    
    def _calculate_feels_like(self, temp, humidity):
        """Calculate feels-like temperature"""
        # Simplified heat index calculation
        if temp >= 27:
            feels_like = temp + 0.1 * (humidity - 60)
        else:
            feels_like = temp
        return round(feels_like, 1)
    
    def get_city_climate_summary(self, city):
        """Get climate summary for a city"""
        if city not in self.city_climate_data:
            raise ValueError(f"Climate data not available for {city}")
        
        data = self.city_climate_data[city]
        
        return {
            'city': city,
            'climate_zone': data['climate_zone'],
            'avg_temperature': data['avg_temp'],
            'temperature_range': f"{data['temp_range'][0]}°C to {data['temp_range'][1]}°C",
            'avg_humidity': f"{data['avg_humidity']}%",
            'annual_rainfall': f"{data['rainfall_mm']} mm",
            'severe_weather_risk': self._get_severe_weather_risk(city)
        }
    
    def _get_severe_weather_risk(self, city):
        """Get severe weather risk assessment"""
        risks = {
            'Delhi': 'Heat waves in summer, fog in winter',
            'Mumbai': 'Heavy rains in monsoon, occasional cyclones',
            'Chennai': 'Heavy rains, heat waves',
            'Kolkata': 'Heavy rains, heat waves',
            'Bangalore': 'Generally mild, occasional heavy rains'
        }
        return risks.get(city, 'Moderate')