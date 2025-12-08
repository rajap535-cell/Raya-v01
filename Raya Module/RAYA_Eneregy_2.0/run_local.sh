#!/bin/bash

# RAYA Energy AI - Local Development Runner
# Run this script to start the application locally

set -e  # Exit on error

echo "========================================"
echo "🚀 Starting RAYA Energy AI"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs models static/{css,js} templates

# Create sample data files if they don't exist
if [ ! -f "data/historical_patterns.json" ]; then
    echo '{
      "daily_pattern": {
        "00-06": 0.7,
        "06-09": 1.2,
        "09-12": 1.0,
        "12-15": 0.95,
        "15-18": 1.05,
        "18-22": 1.4,
        "22-24": 0.9
      },
      "weekly_pattern": {
        "monday": 1.05,
        "tuesday": 1.0,
        "wednesday": 1.0,
        "thursday": 1.0,
        "friday": 1.05,
        "saturday": 0.9,
        "sunday": 0.85
      },
      "seasonal_pattern": {
        "winter": 0.95,
        "summer": 1.15,
        "monsoon": 1.0,
        "post_monsoon": 1.05
      }
    }' > data/historical_patterns.json
fi

if [ ! -f "data/sample_dataset.csv" ]; then
    echo "city,date,temperature,humidity,consumption_mw
Delhi,2024-01-01,15,65,3800
Delhi,2024-01-02,16,67,3850
Mumbai,2024-01-01,28,80,3200
Mumbai,2024-01-02,29,82,3250
Chennai,2024-01-01,30,75,2800
Chennai,2024-01-02,31,77,2850" > data/sample_dataset.csv
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.sample .env
    echo "⚠️  Please update the .env file with your configuration"
fi

# Run the application
echo "========================================"
echo "📡 Starting Flask server..."
echo "🌐 Dashboard: http://localhost:5000"
echo "🔗 API: http://localhost:5000/api/health"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py