"""
RAYA ENERGY AI - FINAL INTEGRATED VERSION
Complete energy prediction system with real-time dashboard
"""

from flask import Flask, jsonify, request, render_template_string
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

app = Flask(__name__)

print("""
╔══════════════════════════════════════════════════════════╗
║   ██████╗  █████╗ ██╗   ██╗ █████╗     ███████╗███████╗  ║
║   ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗    ██╔════╝██╔════╝  ║
║   ██████╔╝███████║ ╚████╔╝ ███████║    ███████╗█████╗    ║
║   ██╔══██╗██╔══██║  ╚██╔╝  ██╔══██║    ╚════██║██╔══╝    ║
║   ██║  ██║██║  ██║   ██║   ██║  ██║    ███████║███████╗  ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚══════╝╚══════╝  ║
║                ENERGY AI - INTEGRATED v2.0               ║
╚══════════════════════════════════════════════════════════╝
""")

# ==================== DATA MODULES ====================

class IMDWeather:
    """Indian Meteorological Department Weather Simulation"""
    def __init__(self):
        self.seasons = {
            'winter': (12, 1, 2),
            'summer': (3, 4, 5),
            'monsoon': (6, 7, 8, 9),
            'post_monsoon': (10, 11)
        }
        
    def get_season(self):
        month = datetime.now().month
        for season, months in self.seasons.items():
            if month in months:
                return season
        return 'summer'
    
    def get_city_weather(self, city):
        """Get weather data for Indian city"""
        city_data = {
            'Delhi': {'temp_range': (8, 45), 'avg_temp': 32, 'avg_humidity': 65},
            'Mumbai': {'temp_range': (18, 38), 'avg_temp': 28, 'avg_humidity': 80},
            'Chennai': {'temp_range': (20, 42), 'avg_temp': 34, 'avg_humidity': 70},
            'Kolkata': {'temp_range': (12, 38), 'avg_temp': 31, 'avg_humidity': 75},
            'Bangalore': {'temp_range': (15, 35), 'avg_temp': 26, 'avg_humidity': 60}
        }
        
        if city not in city_data:
            city = 'Delhi'
        
        data = city_data[city]
        season = self.get_season()
        
        # Calculate temperature based on season and time
        hour = datetime.now().hour
        base_temp = data['avg_temp']
        
        # Daily variation
        if 2 <= hour <= 6:
            temp = base_temp - 5
        elif 13 <= hour <= 15:
            temp = base_temp + 5
        else:
            temp = base_temp
        
        # Season adjustment
        if season == 'summer':
            temp += 3
        elif season == 'winter':
            temp -= 5
        
        humidity = data['avg_humidity'] + np.random.randint(-10, 10)
        humidity = max(30, min(95, humidity))
        
        return {
            'city': city,
            'temperature': round(temp, 1),
            'humidity': humidity,
            'season': season,
            'condition': self.get_condition(temp, humidity),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_condition(self, temp, humidity):
        if humidity > 80:
            return 'Humid'
        elif temp > 38:
            return 'Hot'
        elif temp < 15:
            return 'Cold'
        elif humidity > 70:
            return 'Partly Cloudy'
        else:
            return 'Clear'

class CEAPowerData:
    """Central Electricity Authority Power Data"""
    def __init__(self):
        self.city_data = {
            'Delhi': {
                'base_consumption': 4500,
                'peak_consumption': 6500,
                'industrial_load': 0.7,
                'growth_rate': 0.05
            },
            'Mumbai': {
                'base_consumption': 3800,
                'peak_consumption': 5200,
                'industrial_load': 0.8,
                'growth_rate': 0.06
            },
            'Chennai': {
                'base_consumption': 2800,
                'peak_consumption': 3800,
                'industrial_load': 0.6,
                'growth_rate': 0.04
            },
            'Kolkata': {
                'base_consumption': 3200,
                'peak_consumption': 4500,
                'industrial_load': 0.5,
                'growth_rate': 0.03
            },
            'Bangalore': {
                'base_consumption': 3100,
                'peak_consumption': 4200,
                'industrial_load': 0.75,
                'growth_rate': 0.08
            }
        }
    
    def get_power_data(self, city):
        """Get power consumption data for city"""
        if city not in self.city_data:
            city = 'Delhi'
        
        data = self.city_data[city]
        hour = datetime.now().hour
        day_type = 'weekend' if datetime.now().weekday() >= 5 else 'weekday'
        
        # Time-based consumption
        if 6 <= hour <= 9:  # Morning peak
            multiplier = 1.2
        elif 18 <= hour <= 22:  # Evening peak
            multiplier = 1.4
        elif 0 <= hour <= 5:  # Night low
            multiplier = 0.7
        else:
            multiplier = 1.0
        
        # Weekend adjustment
        if day_type == 'weekend':
            multiplier *= 0.9
        
        consumption = data['base_consumption'] * multiplier
        consumption += np.random.randint(-100, 100)  # Random variation
        
        return {
            'city': city,
            'power_consumption_mw': int(consumption),
            'base_consumption': data['base_consumption'],
            'peak_consumption': data['peak_consumption'],
            'time_multiplier': multiplier,
            'day_type': day_type,
            'industrial_load': data['industrial_load'],
            'timestamp': datetime.now().isoformat()
        }

class EnergyPredictor:
    """AI Energy Prediction Model"""
    def __init__(self):
        self.city_factors = {
            'Delhi': {'base': 4000, 'industrial': 1.2, 'population': 1.3},
            'Mumbai': {'base': 3500, 'industrial': 1.3, 'population': 1.4},
            'Chennai': {'base': 2800, 'industrial': 1.1, 'population': 1.2},
            'Kolkata': {'base': 3200, 'industrial': 1.15, 'population': 1.25},
            'Bangalore': {'base': 3000, 'industrial': 1.25, 'population': 1.3}
        }
    
    def predict(self, city, temperature, humidity, hour, is_weekend=False):
        """Predict energy consumption using enhanced algorithm"""
        if city not in self.city_factors:
            city = 'Delhi'
        
        factors = self.city_factors[city]
        
        # Base consumption
        base = factors['base']
        
        # Temperature effect (25°C is optimal)
        temp_effect = 1 + abs(temperature - 25) * 0.02
        
        # Humidity effect (60% is optimal)
        humidity_effect = 1 + abs(humidity - 60) * 0.01
        
        # Time effect
        if 6 <= hour <= 9:  # Morning peak
            time_effect = 1.2
        elif 18 <= hour <= 22:  # Evening peak
            time_effect = 1.4
        elif 0 <= hour <= 5:  # Night
            time_effect = 0.7
        else:
            time_effect = 1.0
        
        # Weekend effect
        weekend_effect = 0.9 if is_weekend else 1.0
        
        # Industrial and population effects
        industrial_effect = factors['industrial']
        population_effect = factors['population']
        
        # Calculate final prediction
        prediction = (base * temp_effect * humidity_effect * 
                     time_effect * weekend_effect * 
                     industrial_effect * population_effect)
        
        # Add some randomness
        prediction += np.random.normal(0, 100)
        
        return max(1000, int(prediction))

# ==================== INITIALIZE MODULES ====================

imd = IMDWeather()
cea = CEAPowerData()
predictor = EnergyPredictor()

print("✅ Modules initialized successfully!")
print("🌤️ Weather: Active | ⚡ Power Data: Active | 🤖 AI: Active")

# ==================== HTML TEMPLATE ====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAYA Energy AI</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 40px 20px;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 2px solid #3b82f6;
        }
        .header h1 {
            font-size: 3.5rem;
            background: linear-gradient(45deg, #60a5fa, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #94a3b8;
            font-size: 1.2rem;
            margin-bottom: 20px;
        }
        .badges {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .badge {
            background: linear-gradient(45deg, #3b82f6, #1d4ed8);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(30, 41, 59, 0.9);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .card h2 {
            color: #60a5fa;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .city-grid {
            display: grid;
            gap: 15px;
        }
        .city-card {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #3b82f6;
        }
        .city-card.high { border-left-color: #ef4444; }
        .city-card.medium { border-left-color: #f59e0b; }
        .city-card.low { border-left-color: #10b981; }
        .city-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            color: #94a3b8;
            margin-bottom: 5px;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #475569;
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.9);
            color: white;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(45deg, #3b82f6, #1d4ed8);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }
        .result {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(21, 128, 61, 0.1));
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .chart-container {
            height: 300px;
            margin-top: 20px;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: rgba(15, 23, 42, 0.8);
            border-radius: 10px;
            margin-top: 20px;
            font-size: 0.9rem;
        }
        .live {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #10b981;
        }
        .pulse {
            width: 10px;
            height: 10px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ RAYA ENERGY AI</h1>
            <p class="subtitle">Intelligent Energy Prediction System</p>
            <div class="badges">
                <span class="badge">Real-time Data</span>
                <span class="badge">AI Predictions</span>
                <span class="badge">Indian Cities</span>
                <span class="badge">Energy Analytics</span>
            </div>
        </div>

        <div class="dashboard">
            <!-- Live Cities Card -->
            <div class="card">
                <h2>🏙️ Live City Status</h2>
                <div class="city-grid" id="cityGrid">
                    <!-- Cities will be loaded here -->
                </div>
            </div>

            <!-- Prediction Card -->
            <div class="card">
                <h2>🔮 Energy Predictor</h2>
                <div class="form-group">
                    <label for="citySelect">City</label>
                    <select id="citySelect">
                        <option value="Delhi">Delhi</option>
                        <option value="Mumbai">Mumbai</option>
                        <option value="Chennai">Chennai</option>
                        <option value="Kolkata">Kolkata</option>
                        <option value="Bangalore">Bangalore</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="tempInput">Temperature (°C)</label>
                    <input type="number" id="tempInput" value="32" min="15" max="45">
                </div>
                <div class="form-group">
                    <label for="humidityInput">Humidity (%)</label>
                    <input type="number" id="humidityInput" value="70" min="30" max="95">
                </div>
                <div class="form-group">
                    <label for="hourInput">Hour (0-23)</label>
                    <input type="number" id="hourInput" value="14" min="0" max="23">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="weekendCheck"> Weekend?
                    </label>
                </div>
                <button onclick="predictEnergy()">Predict Energy</button>
                <div id="predictionResult" class="result" style="display: none;">
                    <h3>🎯 Prediction Result</h3>
                    <div id="resultContent"></div>
                </div>
            </div>
        </div>

        <!-- Chart Card -->
        <div class="card">
            <h2>📈 Energy Consumption</h2>
            <div class="chart-container">
                <canvas id="energyChart"></canvas>
            </div>
        </div>

        <!-- Status Bar -->
        <div class="status-bar">
            <div class="live">
                <div class="pulse"></div>
                <span>Live Data Streaming • {{ season }} Season</span>
            </div>
            <div>
                <span id="lastUpdate">Last update: {{ timestamp }}</span>
            </div>
            <button onclick="refreshData()" style="width: auto; padding: 8px 16px;">🔄 Refresh</button>
        </div>
    </div>

    <script>
        // Load initial city data
        async function loadCityData() {
            try {
                const response = await fetch('/api/cities/live');
                const data = await response.json();
                
                let html = '';
                data.cities.forEach(city => {
                    const status = city.power_mw > 4500 ? 'high' : city.power_mw > 3000 ? 'medium' : 'low';
                    
                    html += `
                        <div class="city-card ${status}">
                            <h3>${city.city}</h3>
                            <div class="city-stats">
                                <div class="stat">
                                    <span>⚡ Power:</span>
                                    <strong>${city.power_mw} MW</strong>
                                </div>
                                <div class="stat">
                                    <span>🌡️ Temp:</span>
                                    <strong>${city.temperature}°C</strong>
                                </div>
                                <div class="stat">
                                    <span>💧 Humidity:</span>
                                    <strong>${city.humidity}%</strong>
                                </div>
                                <div class="stat">
                                    <span>📊 Condition:</span>
                                    <strong>${city.condition}</strong>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                document.getElementById('cityGrid').innerHTML = html;
                updateChart(data.cities);
                document.getElementById('lastUpdate').textContent = 
                    `Last update: ${new Date().toLocaleTimeString()}`;
            } catch (error) {
                console.error('Error loading city data:', error);
            }
        }

        // Update chart
        let energyChart = null;
        function updateChart(cities) {
            const ctx = document.getElementById('energyChart').getContext('2d');
            
            if (energyChart) {
                energyChart.destroy();
            }
            
            energyChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: cities.map(c => c.city),
                    datasets: [{
                        label: 'Power Consumption (MW)',
                        data: cities.map(c => c.power_mw),
                        backgroundColor: cities.map(c => 
                            c.power_mw > 4500 ? '#ef4444' : 
                            c.power_mw > 3000 ? '#f59e0b' : '#10b981'
                        ),
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1
                    }, {
                        label: 'Temperature (°C)',
                        data: cities.map(c => c.temperature),
                        type: 'line',
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderColor: '#3b82f6',
                        borderWidth: 3,
                        pointRadius: 6,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Power (MW)',
                                color: '#94a3b8'
                            },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: '#94a3b8' }
                        },
                        y1: {
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Temperature (°C)',
                                color: '#94a3b8'
                            },
                            grid: { drawOnChartArea: false },
                            ticks: { color: '#94a3b8' }
                        },
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            ticks: { color: '#94a3b8' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#94a3b8' }
                        }
                    }
                }
            });
        }

        // Make prediction
        async function predictEnergy() {
            const city = document.getElementById('citySelect').value;
            const temp = parseFloat(document.getElementById('tempInput').value);
            const humidity = parseFloat(document.getElementById('humidityInput').value);
            const hour = parseInt(document.getElementById('hourInput').value);
            const isWeekend = document.getElementById('weekendCheck').checked;
            
            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        city: city,
                        temperature: temp,
                        humidity: humidity,
                        hour: hour,
                        is_weekend: isWeekend
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('resultContent').innerHTML = `
                        <div style="margin-top: 10px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span>City:</span>
                                <strong>${result.city}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span>Temperature:</span>
                                <strong>${result.temperature}°C</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span>Humidity:</span>
                                <strong>${result.humidity}%</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span>Hour:</span>
                                <strong>${result.hour}:00</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span>Weekend:</span>
                                <strong>${result.is_weekend ? 'Yes' : 'No'}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 15px; padding-top: 15px; border-top: 2px solid rgba(34, 197, 94, 0.3);">
                                <span style="font-size: 1.2rem;">Predicted Energy:</span>
                                <strong style="font-size: 1.5rem; color: #22c55e;">
                                    ${result.prediction.toLocaleString()} MW
                                </strong>
                            </div>
                        </div>
                    `;
                    
                    document.getElementById('predictionResult').style.display = 'block';
                }
            } catch (error) {
                alert('Prediction failed: ' + error.message);
            }
        }

        // Refresh data
        function refreshData() {
            loadCityData();
        }

        // Auto-refresh every 30 seconds
        setInterval(loadCityData, 30000);
        
        // Initialize
        loadCityData();
        document.getElementById('hourInput').value = new Date().getHours();
    </script>
</body>
</html>
"""

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string(HTML_TEMPLATE, 
                                 season=imd.get_season(),
                                 timestamp=datetime.now().strftime('%H:%M:%S'))

@app.route('/api/cities/live')
def live_cities():
    """Get live data for all cities"""
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
                'timestamp': datetime.now().isoformat()
            })
    
    return jsonify({
        'cities': result,
        'total': len(result),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predict', methods=['POST'])
def predict_energy():
    """AI energy prediction API"""
    try:
        data = request.get_json()
        city = data.get('city', 'Delhi')
        temperature = float(data.get('temperature', 30))
        humidity = float(data.get('humidity', 70))
        hour = int(data.get('hour', 14))
        is_weekend = data.get('is_weekend', False)
        
        prediction = predictor.predict(city, temperature, humidity, hour, is_weekend)
        
        return jsonify({
            'success': True,
            'city': city,
            'temperature': temperature,
            'humidity': humidity,
            'hour': hour,
            'is_weekend': is_weekend,
            'prediction': prediction,
            'model': 'RAYA Energy AI v2.0',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'RAYA Energy AI',
        'version': '2.0.0',
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
    city = request.args.get('city', 'Delhi')
    temp = float(request.args.get('temp', 32))
    
    prediction = predictor.predict(city, temp, 70, 14, False)
    
    return jsonify({
        'city': city,
        'temperature': temp,
        'prediction': prediction,
        'timestamp': datetime.now().isoformat()
    })

# ==================== MAIN ====================

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 RAYA ENERGY AI - STARTING UP")
    print("="*60)
    print("📊 Services:")
    print("  • Weather Simulation: ✅ ACTIVE")
    print("  • Power Data: ✅ ACTIVE")
    print("  • AI Predictor: ✅ ACTIVE")
    print("  • Dashboard: ✅ READY")
    print("\n🌐 Endpoints:")
    print("  📍 Dashboard: http://localhost:5000")
    print("  🔗 Live Data: http://localhost:5000/api/cities/live")
    print("  🔮 Predict API: http://localhost:5000/api/predict")
    print("  ❤️  Health: http://localhost:5000/api/health")
    print("  🧪 Simple API: http://localhost:5000/api/simple?city=Delhi&temp=32")
    print("\n⚡ Starting server on port 5000...")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)