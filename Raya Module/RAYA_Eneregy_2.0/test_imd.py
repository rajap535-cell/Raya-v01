"""
Test suite for IMD Weather Module
"""

import pytest
from modules.imd import IMDWeather
from datetime import datetime

class TestIMDWeather:
    """Test cases for IMDWeather class"""
    
    @pytest.fixture
    def imd(self):
        """Create IMDWeather instance"""
        return IMDWeather()
    
    def test_get_season(self, imd):
        """Test season detection"""
        season = imd.get_season()
        assert season in ['winter', 'summer', 'monsoon', 'post_monsoon']
    
    def test_get_city_weather_valid_city(self, imd):
        """Test weather data for valid city"""
        weather = imd.get_city_weather('Delhi')
        
        assert 'city' in weather
        assert 'temperature' in weather
        assert 'humidity' in weather
        assert 'condition' in weather
        assert 'season' in weather
        assert 'timestamp' in weather
        
        assert weather['city'] == 'Delhi'
        assert isinstance(weather['temperature'], (int, float))
        assert 0 <= weather['humidity'] <= 100
        assert weather['condition'] in ['Hot', 'Cold', 'Rainy', 'Humid', 'Clear', 'Cloudy', 'Pleasant', 'Dry']
    
    def test_get_city_weather_invalid_city(self, imd):
        """Test weather data for invalid city raises error"""
        with pytest.raises(ValueError):
            imd.get_city_weather('InvalidCity')
    
    def test_get_city_climate_summary(self, imd):
        """Test climate summary for city"""
        summary = imd.get_city_climate_summary('Mumbai')
        
        assert 'city' in summary
        assert 'climate_zone' in summary
        assert 'avg_temperature' in summary
        assert 'temperature_range' in summary
        assert 'avg_humidity' in summary
        assert 'annual_rainfall' in summary
        assert 'severe_weather_risk' in summary
        
        assert summary['city'] == 'Mumbai'
        assert summary['climate_zone'] == 'Tropical'
    
    def test_calculate_feels_like(self, imd):
        """Test feels-like temperature calculation"""
        # Test normal temperature
        feels_like = imd._calculate_feels_like(25, 60)
        assert isinstance(feels_like, (int, float))
        
        # Test hot temperature with high humidity
        feels_like_hot = imd._calculate_feels_like(35, 80)
        assert feels_like_hot > 35  # Should feel hotter
        
        # Test cool temperature
        feels_like_cool = imd._calculate_feels_like(20, 50)
        assert feels_like_cool == 20  # Should feel same
    
    def test_get_condition(self, imd):
        """Test weather condition determination"""
        # Test monsoon condition
        assert imd._get_condition(30, 90, 'monsoon') == 'Rainy'
        assert imd._get_condition(30, 80, 'monsoon') == 'Cloudy'
        
        # Test hot condition
        assert imd._get_condition(40, 50, 'summer') == 'Hot'
        
        # Test cold condition
        assert imd._get_condition(10, 60, 'winter') == 'Cold'
        
        # Test humid condition
        assert imd._get_condition(30, 80, 'summer') == 'Humid'
        
        # Test dry condition
        assert imd._get_condition(30, 30, 'summer') == 'Dry'
        
        # Test pleasant condition
        assert imd._get_condition(25, 60, 'winter') == 'Pleasant'