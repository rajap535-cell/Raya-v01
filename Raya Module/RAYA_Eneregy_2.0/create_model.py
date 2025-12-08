"""
Script to create dummy ML model for testing
"""

import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import os

def create_dummy_model():
    """Create a dummy ML model for testing"""
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Create a simple RandomForest model
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    
    # Create dummy training data
    # Features: [temperature, humidity, hour, is_weekend, industrial, population, economic_growth, urbanization, gdp, tech, efficiency]
    X_train = np.random.randn(100, 11) * 10 + 25
    
    # Targets: Energy consumption between 2000-6000 MW
    y_train = np.random.randint(2000, 6000, 100)
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Save the model
    model_path = 'models/energy_predictor_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"✅ Model saved to {model_path}")
    print(f"📊 Model score: {model.score(X_train, y_train):.3f}")
    
    return model

if __name__ == '__main__':
    create_dummy_model()