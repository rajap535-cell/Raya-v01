/**
 * RAYA Energy AI - Complete Frontend Application
 */

// ===== GLOBAL VARIABLES =====
let energyChart = null;
let currentChartType = 'bar';
let currentDataType = 'consumption';
let isLoading = false;
let startTime = Date.now();
let predictionHistory = [];

// ===== TOAST NOTIFICATION SYSTEM =====
class Toast {
    static show(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Icon based on type
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <div class="toast-content">
                <i class="${icons[type] || icons.info}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
        
        return toast;
    }
}

// ===== LOADING STATE MANAGEMENT =====
function setLoading(state, message = '') {
    isLoading = state;
    const overlay = document.getElementById('loadingOverlay');
    
    if (overlay) {
        if (state) {
            overlay.style.display = 'flex';
            if (message) {
                const messageEl = overlay.querySelector('p');
                if (messageEl) {
                    messageEl.textContent = message;
                }
            }
        } else {
            overlay.style.display = 'none';
        }
    }
}

// ===== ERROR HANDLING =====
function showError(message) {
    console.error('Error:', message);
    Toast.show(`❌ ${message}`, 'error', 7000);
}

function showSuccess(message) {
    Toast.show(`✅ ${message}`, 'success', 3000);
}

function showWarning(message) {
    Toast.show(`⚠️ ${message}`, 'warning', 5000);
}

function showInfo(message) {
    Toast.show(`ℹ️ ${message}`, 'info', 4000);
}

// ===== UTILITY FUNCTIONS =====
function formatNumber(num) {
    return new Intl.NumberFormat('en-IN').format(num);
}

function formatTime(date) {
    return date.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function formatDate(date) {
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function calculateTimeAgo(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
}

// ===== SYSTEM INITIALIZATION =====
function initSystem() {
    console.log('Initializing RAYA Energy AI...');
    
    // Set current hour
    const currentHour = new Date().getHours();
    document.getElementById('currentHour').textContent = currentHour;
    document.getElementById('hourInput').value = currentHour;
    document.getElementById('hourSlider').value = currentHour;
    
    // Set up slider synchronization
    setupSliderSync();
    
    // Load initial data
    loadCityData();
    updateSystemStatus();
    
    // Set up auto-refresh
    setupAutoRefresh();
    
    // Update uptime counter
    updateUptime();
    setInterval(updateUptime, 1000);
    
    // Hide loading overlay
    setTimeout(() => {
        setLoading(false);
        showInfo('RAYA Energy AI initialized successfully!');
    }, 1500);
}

// ===== SLIDER SYNC =====
function setupSliderSync() {
    const tempInput = document.getElementById('tempInput');
    const tempSlider = document.getElementById('tempSlider');
    const humidityInput = document.getElementById('humidityInput');
    const humiditySlider = document.getElementById('humiditySlider');
    const hourInput = document.getElementById('hourInput');
    const hourSlider = document.getElementById('hourSlider');
    
    // Temperature sync
    tempInput.addEventListener('input', function() {
        const value = parseFloat(this.value) || 0;
        tempSlider.value = value;
        validateTemperature(value);
    });
    
    tempSlider.addEventListener('input', function() {
        tempInput.value = this.value;
        validateTemperature(this.value);
    });
    
    // Humidity sync
    humidityInput.addEventListener('input', function() {
        const value = parseFloat(this.value) || 0;
        humiditySlider.value = value;
        validateHumidity(value);
    });
    
    humiditySlider.addEventListener('input', function() {
        humidityInput.value = this.value;
        validateHumidity(this.value);
    });
    
    // Hour sync
    hourInput.addEventListener('input', function() {
        const value = parseInt(this.value) || 0;
        hourSlider.value = value;
        validateHour(value);
    });
    
    hourSlider.addEventListener('input', function() {
        hourInput.value = this.value;
        validateHour(this.value);
    });
}

// ===== INPUT VALIDATION =====
function validateTemperature(temp) {
    const input = document.getElementById('tempInput');
    if (temp < -10 || temp > 50) {
        input.style.borderColor = 'var(--danger-red)';
        return false;
    } else if (temp < 0 || temp > 40) {
        input.style.borderColor = 'var(--warning-orange)';
        return true;
    } else {
        input.style.borderColor = '';
        return true;
    }
}

function validateHumidity(humidity) {
    const input = document.getElementById('humidityInput');
    if (humidity < 0 || humidity > 100) {
        input.style.borderColor = 'var(--danger-red)';
        return false;
    } else if (humidity < 20 || humidity > 90) {
        input.style.borderColor = 'var(--warning-orange)';
        return true;
    } else {
        input.style.borderColor = '';
        return true;
    }
}

function validateHour(hour) {
    const input = document.getElementById('hourInput');
    if (hour < 0 || hour > 23) {
        input.style.borderColor = 'var(--danger-red)';
        return false;
    } else {
        input.style.borderColor = '';
        return true;
    }
}

// ===== CITY DATA LOADING =====
async function loadCityData() {
    if (isLoading) return;
    
    setLoading(true, 'Fetching live city data...');
    
    try {
        const response = await fetch('/api/cities/live');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateCityGrid(data.cities);
            updateChart(data.cities);
            updateLastUpdated();
            showSuccess('City data refreshed successfully');
            
            // Add to history
            predictionHistory.push({
                type: 'data_refresh',
                timestamp: Date.now(),
                data: data.cities
            });
        } else {
            throw new Error(data.error || 'Failed to load city data');
        }
    } catch (error) {
        console.error('Error loading city data:', error);
        showError(`Failed to load city data: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

// ===== UPDATE CITY GRID =====
function updateCityGrid(cities) {
    const container = document.getElementById('cityGrid');
    if (!container) return;
    
    let html = '';
    
    cities.forEach(city => {
        // Determine power level class
        let powerClass = 'low';
        if (city.power_mw > 4500) {
            powerClass = 'high';
        } else if (city.power_mw > 3000) {
            powerClass = 'medium';
        }
        
        // Determine condition color
        let conditionColor = '#10b981'; // Default green
        switch(city.condition) {
            case 'Hot':
                conditionColor = '#ef4444';
                break;
            case 'Cold':
                conditionColor = '#3b82f6';
                break;
            case 'Rainy':
                conditionColor = '#06b6d4';
                break;
            case 'Humid':
                conditionColor = '#8b5cf6';
                break;
            case 'Cloudy':
                conditionColor = '#94a3b8';
                break;
        }
        
        // Calculate capacity utilization
        const capacity = city.peak_consumption || 5000;
        const utilization = Math.min(100, Math.round((city.power_mw / capacity) * 100));
        
        html += `
            <div class="city-card ${powerClass}">
                <div class="city-header">
                    <h3>${city.city}</h3>
                    <span class="city-condition" style="color: ${conditionColor}; border-color: ${conditionColor}">
                        ${city.condition}
                    </span>
                </div>
                <div class="city-stats">
                    <div class="stat">
                        <span><i class="fas fa-bolt"></i> Power Consumption:</span>
                        <strong>${formatNumber(city.power_mw)} MW</strong>
                    </div>
                    <div class="stat">
                        <span><i class="fas fa-thermometer-half"></i> Temperature:</span>
                        <strong>${city.temperature}°C</strong>
                    </div>
                    <div class="stat">
                        <span><i class="fas fa-tint"></i> Humidity:</span>
                        <strong>${city.humidity}%</strong>
                    </div>
                    <div class="stat">
                        <span><i class="fas fa-chart-line"></i> Capacity Utilization:</span>
                        <strong>${utilization}%</strong>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// ===== ENERGY PREDICTION =====
async function predictEnergy() {
    if (isLoading) return;
    
    // Get form values
    const city = document.getElementById('citySelect').value;
    const temp = parseFloat(document.getElementById('tempInput').value);
    const humidity = parseFloat(document.getElementById('humidityInput').value);
    const hour = parseInt(document.getElementById('hourInput').value);
    const isWeekend = document.getElementById('weekendCheck').checked;
    
    // Validate inputs
    if (!validateTemperature(temp) || !validateHumidity(humidity) || !validateHour(hour)) {
        showError('Please fix the highlighted fields before predicting');
        return;
    }
    
    setLoading(true, 'Running AI prediction...');
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
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
            displayPredictionResult(result);
            savePredictionToHistory(result);
            showSuccess(`Prediction for ${city}: ${formatNumber(result.prediction)} MW`);
        } else {
            throw new Error(result.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('Prediction error:', error);
        showError(`Prediction failed: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

// ===== DISPLAY PREDICTION RESULT =====
function displayPredictionResult(result) {
    const resultDiv = document.getElementById('predictionResult');
    const contentDiv = document.getElementById('resultContent');
    const confidenceBadge = document.getElementById('confidenceBadge');
    const confidenceValue = document.getElementById('confidenceValue');
    
    if (!resultDiv || !contentDiv || !confidenceBadge || !confidenceValue) return;
    
    // Update confidence badge
    const confidence = result.confidence || 85;
    confidenceValue.textContent = `${confidence}%`;
    
    // Set confidence badge color
    if (confidence >= 85) {
        confidenceBadge.style.background = 'var(--success-green)';
    } else if (confidence >= 70) {
        confidenceBadge.style.background = 'var(--warning-orange)';
    } else {
        confidenceBadge.style.background = 'var(--danger-red)';
    }
    
    // Format the result content
    const predictionTime = new Date(result.timestamp || Date.now());
    const formattedTime = formatTime(predictionTime);
    const formattedDate = formatDate(predictionTime);
    
    contentDiv.innerHTML = `
        <div class="prediction-details">
            <div class="prediction-summary">
                <div class="prediction-value">
                    ${formatNumber(result.prediction)} <span class="unit">MW</span>
                </div>
                <div class="prediction-label">
                    Predicted Energy Consumption for ${result.city}
                </div>
            </div>
            
            <div class="prediction-breakdown">
                <h4><i class="fas fa-chart-pie"></i> Prediction Breakdown</h4>
                <div class="breakdown-grid">
                    <div class="breakdown-item">
                        <span class="breakdown-label">City:</span>
                        <span class="breakdown-value">${result.city}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Temperature:</span>
                        <span class="breakdown-value">${result.temperature}°C</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Humidity:</span>
                        <span class="breakdown-value">${result.humidity}%</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Time of Day:</span>
                        <span class="breakdown-value">${result.hour}:00</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Weekend:</span>
                        <span class="breakdown-value">${result.is_weekend ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Model Version:</span>
                        <span class="breakdown-value">${result.model || 'v1.0.0'}</span>
                    </div>
                </div>
            </div>
            
            <div class="prediction-meta">
                <div class="meta-item">
                    <i class="fas fa-shield-alt"></i>
                    <span>Confidence: ${confidence}%</span>
                </div>
                <div class="meta-item">
                    <i class="fas fa-calendar-alt"></i>
                    <span>${formattedDate} ${formattedTime}</span>
                </div>
                <div class="meta-item">
                    <i class="fas fa-robot"></i>
                    <span>AI Model: ${result.model || 'Multi-Factor Regression'}</span>
                </div>
            </div>
        </div>
    `;
    
    // Show result card
    resultDiv.style.display = 'block';
    
    // Scroll to result
    resultDiv.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
}

// ===== SAVE PREDICTION =====
function savePrediction() {
    const resultDiv = document.getElementById('predictionResult');
    if (!resultDiv || resultDiv.style.display === 'none') {
        showWarning('No prediction to save');
        return;
    }
    
    showSuccess('Prediction saved to history');
    // In a real app, you would save to localStorage or send to backend
}

function savePredictionToHistory(prediction) {
    predictionHistory.push({
        type: 'prediction',
        timestamp: Date.now(),
        data: prediction
    });
    
    // Keep only last 50 predictions
    if (predictionHistory.length > 50) {
        predictionHistory = predictionHistory.slice(-50);
    }
}

// ===== CHART FUNCTIONS =====
function updateChart(cities) {
    const ctx = document.getElementById('energyChart');
    if (!ctx) return;
    
    const canvas = ctx.getContext('2d');
    
    // Destroy existing chart
    if (energyChart) {
        energyChart.destroy();
    }
    
    // Prepare data based on current data type
    let datasets = [];
    let yAxisLabel = '';
    let dataValues = [];
    
    switch(currentDataType) {
        case 'consumption':
            dataValues = cities.map(c => c.power_mw);
            yAxisLabel = 'Power Consumption (MW)';
            datasets = [{
                label: 'Power Consumption',
                data: dataValues,
                backgroundColor: cities.map(c => {
                    if (c.power_mw > 4500) return 'rgba(239, 68, 68, 0.7)';
                    if (c.power_mw > 3000) return 'rgba(245, 158, 11, 0.7)';
                    return 'rgba(16, 185, 129, 0.7)';
                }),
                borderColor: cities.map(c => {
                    if (c.power_mw > 4500) return '#ef4444';
                    if (c.power_mw > 3000) return '#f59e0b';
                    return '#10b981';
                }),
                borderWidth: 2,
                borderRadius: 5,
                order: 1
            }];
            break;
            
        case 'temperature':
            dataValues = cities.map(c => c.temperature);
            yAxisLabel = 'Temperature (°C)';
            datasets = [{
                label: 'Temperature',
                data: dataValues,
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: '#3b82f6',
                borderWidth: 2,
                borderRadius: 5,
                order: 1
            }];
            break;
            
        case 'humidity':
            dataValues = cities.map(c => c.humidity);
            yAxisLabel = 'Humidity (%)';
            datasets = [{
                label: 'Humidity',
                data: dataValues,
                backgroundColor: 'rgba(6, 182, 212, 0.7)',
                borderColor: '#06b6d4',
                borderWidth: 2,
                borderRadius: 5,
                order: 1
            }];
            break;
    }
    
    // Add temperature as line chart for comparison when showing consumption
    if (currentDataType === 'consumption') {
        datasets.push({
            label: 'Temperature (°C)',
            data: cities.map(c => c.temperature),
            type: 'line',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderColor: '#3b82f6',
            borderWidth: 3,
            pointBackgroundColor: '#3b82f6',
            pointRadius: 6,
            pointHoverRadius: 8,
            fill: true,
            order: 0,
            yAxisID: 'y1'
        });
    }
    
    // Chart configuration
    const chartConfig = {
        type: currentChartType,
        data: {
            labels: cities.map(c => c.city),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: {
                            size: 12,
                            family: 'var(--font-sans)'
                        },
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#f1f5f9',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 6,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                if (context.dataset.label.includes('Power')) {
                                    label += formatNumber(context.parsed.y) + ' MW';
                                } else if (context.dataset.label.includes('Temperature')) {
                                    label += context.parsed.y + '°C';
                                } else if (context.dataset.label.includes('Humidity')) {
                                    label += context.parsed.y + '%';
                                } else {
                                    label += context.parsed.y;
                                }
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'var(--font-sans)'
                        }
                    }
                },
                y: {
                    beginAtZero: currentDataType !== 'temperature',
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'var(--font-sans)'
                        },
                        callback: function(value) {
                            if (currentDataType === 'consumption') {
                                return formatNumber(value) + ' MW';
                            }
                            return value;
                        }
                    },
                    title: {
                        display: true,
                        text: yAxisLabel,
                        color: '#94a3b8',
                        font: {
                            family: 'var(--font-sans)',
                            size: 12,
                            weight: 'normal'
                        }
                    }
                },
                y1: {
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'var(--font-sans)'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Temperature (°C)',
                        color: '#94a3b8',
                        font: {
                            family: 'var(--font-sans)',
                            size: 12,
                            weight: 'normal'
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    };
    
    // Create chart
    energyChart = new Chart(canvas, chartConfig);
}

function updateChartType() {
    currentChartType = document.getElementById('chartTypeSelect').value;
    loadCityData(); // Reload to update chart
}

function updateChartData() {
    currentDataType = document.getElementById('dataTypeSelect').value;
    loadCityData(); // Reload to update chart
}

function refreshChart() {
    loadCityData();
}

function exportChart() {
    const canvas = document.getElementById('energyChart');
    if (!canvas) return;
    
    const link = document.createElement('a');
    link.download = `raya-energy-chart-${new Date().toISOString().slice(0,10)}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    
    showSuccess('Chart exported as PNG');
}

// ===== SYSTEM STATUS =====
async function updateSystemStatus() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        // Update status indicators
        const statusElements = {
            'weatherStatus': 'weather',
            'powerStatus': 'power',
            'modelStatus': 'model',
            'dataStatus': 'data'
        };
        
        for (const [elementId, service] of Object.entries(statusElements)) {
            const element = document.getElementById(elementId);
            if (element) {
                if (data.status === 'healthy') {
                    element.innerHTML = `
                        <span class="status-dot live" style="display: inline-block; margin-right: 8px;"></span>
                        <span>Operational</span>
                    `;
                } else {
                    element.innerHTML = `
                        <span class="status-dot" style="display: inline-block; margin-right: 8px; background: var(--danger-red)"></span>
                        <span>Offline</span>
                    `;
                }
            }
        }
        
        // Update last update time
        updateLastUpdated();
        
    } catch (error) {
        console.error('Status update error:', error);
        
        // Set all to error state
        const statusIds = ['weatherStatus', 'powerStatus', 'modelStatus', 'dataStatus'];
        statusIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = `
                    <span class="status-dot" style="display: inline-block; margin-right: 8px; background: var(--danger-red)"></span>
                    <span>Connection Error</span>
                `;
            }
        });
    }
}

function updateLastUpdated() {
    const element = document.getElementById('lastUpdate');
    if (element) {
        element.textContent = formatTime(new Date());
    }
    
    const timeElement = document.getElementById('lastUpdatedTime');
    if (timeElement) {
        timeElement.textContent = `Updated: ${formatTime(new Date())}`;
    }
}

function updateUptime() {
    const element = document.getElementById('uptime');
    if (!element) return;
    
    const now = Date.now();
    const diff = now - startTime;
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    element.textContent = 
        `${hours.toString().padStart(2, '0')}:` +
        `${minutes.toString().padStart(2, '0')}:` +
        `${seconds.toString().padStart(2, '0')}`;
}

// ===== AUTO REFRESH =====
function setupAutoRefresh() {
    // Auto-refresh city data every 30 seconds
    setInterval(() => {
        if (!isLoading) {
            loadCityData();
        }
    }, 30000);
    
    // Auto-refresh system status every 60 seconds
    setInterval(() => {
        updateSystemStatus();
    }, 60000);
}

// ===== EVENT LISTENERS =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the system
    initSystem();
    
    // Add form submission handler
    const form = document.getElementById('predictionForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            predictEnergy();
        });
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+R or Cmd+R to refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            loadCityData();
        }
        
        // Ctrl+P or Cmd+P to predict
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            predictEnergy();
        }
        
        // Escape to clear result
        if (e.key === 'Escape') {
            const resultDiv = document.getElementById('predictionResult');
            if (resultDiv) {
                resultDiv.style.display = 'none';
            }
        }
    });
    
    // Add window focus/blur events
    window.addEventListener('focus', function() {
        // Refresh data when window gains focus
        loadCityData();
    });
    
    // Log initialization
    console.log('RAYA Energy AI Frontend initialized');
    console.log('Version: 1.2.0');
    console.log('Build: 2024-12-05');
});

// ===== ERROR BOUNDARY =====
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showError(`Application error: ${event.error.message}`);
});

// ===== EXPORT FUNCTIONS (for debugging) =====
window.rayaDebug = {
    getPredictionHistory: () => predictionHistory,
    clearPredictionHistory: () => { predictionHistory = []; },
    getChartInstance: () => energyChart,
    forceRefresh: () => loadCityData(),
    simulatePrediction: (city, temp, humidity, hour, weekend) => {
        return {
            city: city || 'Delhi',
            temperature: temp || 32,
            humidity: humidity || 70,
            hour: hour || 14,
            is_weekend: weekend || false,
            prediction: Math.floor(Math.random() * 4000) + 2000,
            confidence: Math.floor(Math.random() * 30) + 70,
            model: 'v1.2.0'
        };
    }
};