"""
RAYA ENERGY AI - PRODUCTION READY VERSION
Complete energy prediction system with modular architecture
"""

from flask import Flask, jsonify, request, render_template
import numpy as np
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler

# Import modular components
from modules.imd import IMDWeather
from modules.cea import CEAPowerData
from modules.predictor import EnergyPredictor
from utils.validators import validate_prediction_input

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'raya-energy-ai-secret-key-v1')

# Setup logging
os.makedirs('logs', exist_ok=True)
handler = RotatingFileHandler('logs/raya_energy.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Initialize modules
try:
    imd = IMDWeather()
    cea = CEAPowerData()
    predictor = EnergyPredictor()
    app.logger.info("✅ All modules initialized successfully")
except Exception as e:
    app.logger.error(f"❌ Module initialization failed: {str(e)}")
    raise

print("""
╔══════════════════════════════════════════════════════════╗
║   ██████╗  █████╗ ██╗   ██╗ █████╗     ███████╗███████╗  ║
║   ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗    ██╔════╝██╔════╝  ║
║   ██████╔╝███████║ ╚████╔╝ ███████║    ███████╗█████╗    ║
║   ██╔══██╗██╔══██║  ╚██╔╝  ██╔══██║    ╚════██║██╔══╝    ║
║   ██║  ██║██║  ██║   ██║   ██║  ██║    ███████║███████╗  ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚══════╝╚══════╝  ║
║                ENERGY AI - PRODUCTION v1.0               ║
╚══════════════════════════════════════════════════════════╝
""")

print(f"📊 Model Version: {predictor.version}")
print(f"📅 Last Updated: {predictor.last_updated}")
print(f"📈 Reliability Score: {predictor.reliability_score}%")

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard"""
    try:
        season = imd.get_season()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template('index.html', 
                             season=season,
                             timestamp=timestamp,
                             model_version=predictor.version,
                             reliability_score=predictor.reliability_score)
    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
        return "Service temporarily unavailable", 503

@app.route('/api/cities/live')
def live_cities():
    """Get live data for all cities"""
    try:
        cities = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore']
        result = []
        
        for city in cities:
            weather = imd.get_city_weather(city)
            power = cea.get_power_data(city)
            
            if weather and power:
                result.append({
                    'city': city,
                    'temperature': weather['temperature'],
                    'humidity': weather['humidity'],
                    'condition': weather['condition'],
                    'power_mw': power['power_consumption_mw'],
                    'base_consumption': power['base_consumption'],
                    'peak_consumption': power['peak_consumption'],
                    'timestamp': datetime.now().isoformat()
                })
        
        response = {
            'success': True,
            'cities': result,
            'total': len(result),
            'timestamp': datetime.now().isoformat(),
            'season': imd.get_season()
        }
        
        app.logger.info(f"Live data fetched: {len(result)} cities")
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Live cities error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch live data',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/predict', methods=['POST'])
def predict_energy():
    """AI energy prediction API"""
    try:
        data = request.get_json()
        
        # Validate input
        validation_result = validate_prediction_input(data)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': validation_result['error'],
                'timestamp': datetime.now().isoformat()
            }), 400
        
        city = data.get('city', 'Delhi')
        temperature = float(data.get('temperature', 30))
        humidity = float(data.get('humidity', 70))
        hour = int(data.get('hour', 14))
        is_weekend = data.get('is_weekend', False)
        
        # Get prediction
        prediction = predictor.predict(city, temperature, humidity, hour, is_weekend)
        
        # Get confidence score
        confidence = predictor.get_confidence_score(city, temperature, humidity, hour)
        
        response = {
            'success': True,
            'city': city,
            'temperature': temperature,
            'humidity': humidity,
            'hour': hour,
            'is_weekend': is_weekend,
            'prediction': prediction,
            'confidence': confidence,
            'model': predictor.version,
            'model_updated': predictor.last_updated,
            'reliability': predictor.reliability_score,
            'timestamp': datetime.now().isoformat()
        }
        
        app.logger.info(f"Prediction made for {city}: {prediction} MW")
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Prediction failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    status = 'healthy'
    try:
        # Test all modules
        imd.get_city_weather('Delhi')
        cea.get_power_data('Delhi')
        predictor.predict('Delhi', 30, 70, 14, False)
    except Exception as e:
        status = 'unhealthy'
        app.logger.error(f"Health check failed: {str(e)}")
    
    return jsonify({
        'status': status,
        'service': 'RAYA Energy AI',
        'version': '1.0.0',
        'model_version': predictor.version,
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'dashboard': '/',
            'live_data': '/api/cities/live',
            'predict': '/api/predict',
            'health': '/api/health'
        }
    })

@app.route('/api/simple')
def simple_api():
    """Simple prediction API"""
    try:
        city = request.args.get('city', 'Delhi')
        temp = float(request.args.get('temp', 32))
        
        prediction = predictor.predict(city, temp, 70, 14, False)
        confidence = predictor.get_confidence_score(city, temp, 70, 14)
        
        return jsonify({
            'city': city,
            'temperature': temp,
            'prediction': prediction,
            'confidence': confidence,
            'model': predictor.version,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f"Server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 RAYA ENERGY AI - PRODUCTION SERVER")
    print("="*60)
    print("📊 System Status:")
    print(f"  • Weather Module: ✅ ACTIVE")
    print(f"  • Power Data: ✅ ACTIVE")
    print(f"  • AI Predictor: ✅ ACTIVE (v{predictor.version})")
    print(f"  • Dashboard: ✅ READY")
    print("\n🌐 Endpoints:")
    print("  📍 Dashboard: http://localhost:5000")
    print("  🔗 Live Data: http://localhost:5000/api/cities/live")
    print("  🔮 Predict API: http://localhost:5000/api/predict")
    print("  ❤️  Health: http://localhost:5000/api/health")
    print("  🧪 Simple API: http://localhost:5000/api/simple?city=Delhi&temp=32")
    print("\n📈 Model Info:")
    print(f"  • Version: {predictor.version}")
    print(f"  • Last Updated: {predictor.last_updated}")
    print(f"  • Reliability: {predictor.reliability_score}%")
    print("\n⚡ Starting production server on port 5000...")
    print("="*60)
    
    # Run with production settings
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )