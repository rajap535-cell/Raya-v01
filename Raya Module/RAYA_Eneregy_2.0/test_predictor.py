"""
Test suite for Energy Predictor Module
"""

import pytest
import numpy as np
from modules.predictor import EnergyPredictor

class TestEnergyPredictor:
    """Test cases for EnergyPredictor class"""
    
    @pytest.fixture
    def predictor(self):
        """Create EnergyPredictor instance"""
        return EnergyPredictor()
    
    def test_model_metadata(self, predictor):
        """Test model metadata fields"""
        assert hasattr(predictor, 'version')
        assert hasattr(predictor, 'last_updated')
        assert hasattr(predictor, 'reliability_score')
        assert hasattr(predictor, 'training_date')
        assert hasattr(predictor, 'model_type')
        assert hasattr(predictor, 'author')
        
        assert isinstance(predictor.version, str)
        assert isinstance(predictor.last_updated, str)
        assert isinstance(predictor.reliability_score, (int, float))
        assert predictor.reliability_score > 0
    
    def test_predict_valid_city(self, predictor):
        """Test prediction for valid city"""
        prediction = predictor.predict('Delhi', 32, 70, 14, False)
        
        assert isinstance(prediction, int)
        assert 1000 <= prediction <= 10000
        
        # Test with weekend
        prediction_weekend = predictor.predict('Delhi', 32, 70, 14, True)
        assert isinstance(prediction_weekend, int)
    
    def test_predict_invalid_city(self, predictor):
        """Test prediction for invalid city raises error"""
        with pytest.raises(ValueError):
            predictor.predict('InvalidCity', 32, 70, 14, False)
    
    def test_get_confidence_score(self, predictor):
        """Test confidence score calculation"""
        confidence = predictor.get_confidence_score('Delhi', 32, 70, 14)
        
        assert isinstance(confidence, (int, float))
        assert 50 <= confidence <= 100
        
        # Test with extreme temperatures (should have lower confidence)
        confidence_extreme = predictor.get_confidence_score('Delhi', 45, 70, 14)
        assert confidence_extreme <= confidence
        
        # Test with optimal conditions (should have higher confidence)
        confidence_optimal = predictor.get_confidence_score('Delhi', 25, 60, 14)
        assert confidence_optimal >= confidence
    
    def test_get_model_info(self, predictor):
        """Test model info retrieval"""
        info = predictor.get_model_info()
        
        assert 'version' in info
        assert 'last_updated' in info
        assert 'reliability_score' in info
        assert 'training_date' in info
        assert 'model_type' in info
        assert 'author' in info
        assert 'performance_metrics' in info
        assert 'supported_cities' in info
        assert 'coefficients' in info
        assert 'has_ml_model' in info
        assert 'timestamp' in info
        
        assert isinstance(info['supported_cities'], list)
        assert len(info['supported_cities']) == 5
        assert 'Delhi' in info['supported_cities']
    
    def test_predict_with_breakdown(self, predictor):
        """Test prediction with breakdown"""
        result = predictor.predict_with_breakdown('Mumbai', 28, 75, 10, False)
        
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'city' in result
        assert 'temperature' in result
        assert 'humidity' in result
        assert 'hour' in result
        assert 'is_weekend' in result
        assert 'breakdown' in result
        assert 'model_info' in result
        
        assert isinstance(result['prediction'], int)
        assert isinstance(result['confidence'], (int, float))
        assert isinstance(result['breakdown'], dict)
        assert isinstance(result['model_info'], dict)
    
    def test_calculate_time_effect(self, predictor):
        """Test time effect calculation"""
        # Test morning peak
        assert predictor._calculate_time_effect(8) == 1.2
        
        # Test evening peak
        assert predictor._calculate_time_effect(19) == 1.4
        
        # Test night
        assert predictor._calculate_time_effect(3) == 0.7
        
        # Test daytime
        assert predictor._calculate_time_effect(14) == 1.0
    
    def test_historical_patterns_loading(self, predictor):
        """Test historical patterns loading"""
        assert 'daily_pattern' in predictor.historical_patterns
        assert 'weekly_pattern' in predictor.historical_patterns
        assert 'seasonal_pattern' in predictor.historical_patterns
        
        assert isinstance(predictor.historical_patterns['daily_pattern'], dict)
        assert isinstance(predictor.historical_patterns['weekly_pattern'], dict)
        assert isinstance(predictor.historical_patterns['seasonal_pattern'], dict)
    
    def test_coefficients_structure(self, predictor):
        """Test model coefficients structure"""
        assert isinstance(predictor.coefficients, dict)
        
        required_coeffs = [
            'temperature', 'humidity', 'time_peak_morning',
            'time_peak_evening', 'time_night', 'weekend',
            'industrial_base', 'population_base', 'random_variation'
        ]
        
        for coeff in required_coeffs:
            assert coeff in predictor.coefficients
            assert isinstance(predictor.coefficients[coeff], (int, float))