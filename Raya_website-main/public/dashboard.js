document.addEventListener('DOMContentLoaded', () => {
    // --- 0. SESSION CHECK ---
    if (localStorage.getItem('raya_auth') !== 'true') {
        window.location.href = 'portal_login.html';
        return;
    }

    // --- 1. SYSTEM CLOCK ---
    const timeDisplay = document.getElementById('live-time');
    function updateClock() {
        const now = new Date();
        const timeString = now.toISOString().split('T')[1].split('.')[0] + ' UTC';
        timeDisplay.textContent = timeString;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // --- 2. STATUS STRIP SIMULATION ---
    const statusMetrics = {
        demand: { el: document.getElementById('val-demand'), base: 1240, suffix: ' <small>MW</small>' },
        temp: { el: document.getElementById('val-temp'), base: 22.4, suffix: ' <small>°C</small>' },
        health: { el: document.getElementById('val-health'), base: 98.2, suffix: ' <small>%</small>' }
    };

    function updateStatusStrip() {
        // Demand fluctuation
        const dVar = (Math.random() * 40 - 20).toFixed(0);
        const demandVal = statusMetrics.demand.base + parseInt(dVar);
        statusMetrics.demand.el.innerHTML = `${demandVal.toLocaleString()}${statusMetrics.demand.suffix}`;
        
        // Temp fluctuation
        const tVar = (Math.random() * 0.4 - 0.2).toFixed(1);
        const tempVal = (statusMetrics.temp.base + parseFloat(tVar)).toFixed(1);
        statusMetrics.temp.el.innerHTML = `${tempVal}${statusMetrics.temp.suffix}`;

        // Health fluctuation (rarely drops)
        const hVar = Math.random() > 0.9 ? -(Math.random() * 0.5).toFixed(1) : (Math.random() * 0.1).toFixed(1);
        let healthVal = (statusMetrics.health.base + parseFloat(hVar)).toFixed(1);
        healthVal = Math.min(100, Math.max(95, healthVal));
        statusMetrics.health.el.innerHTML = `${healthVal}${statusMetrics.health.suffix}`;

        updateRegionGrid();
        updateSystemLog();
    }

    const logMessages = [
        "Load imbalance detected — Singapore buffer activated",
        "Prediction model updated via federated learning",
        "Tokyo peak threshold approaching — standby initiated",
        "Anomaly detection: System stable",
        "New York node synchronization optimal",
        "Renewable energy mix increased to 42%",
        "Grid frequency stabilized at 50.02 Hz",
        "Thermal deviation detected in London sector"
    ];

    function updateSystemLog() {
        const logContainer = document.getElementById('system-log');
        const now = new Date();
        const time = `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}]`;
        const msg = logMessages[Math.floor(Math.random() * logMessages.length)];
        
        const newLog = document.createElement('div');
        newLog.className = 'log-item';
        newLog.textContent = `${time} ${msg}`;
        
        logContainer.prepend(newLog);
        if (logContainer.children.length > 5) {
            logContainer.lastElementChild.remove();
        }
    }

    // --- 2.1 ALERTS & RECOMMENDATIONS ---
    const alerts = [
        { text: "NO ANOMALY DETECTED", color: "green" },
        { text: "TOKYO APPROACHING PEAK", color: "yellow" },
        { text: "UNEXPECTED SPIKE DETECTED", color: "red" }
    ];
    let currentAlertIdx = 0;

    function updateAlerts() {
        const alertEl = document.getElementById('system-alerts');
        const dot = alertEl.querySelector('.alert-dot');
        const text = alertEl.querySelector('.alert-text');
        
        currentAlertIdx = (currentAlertIdx + 1) % alerts.length;
        const alert = alerts[currentAlertIdx];
        
        dot.className = `alert-dot ${alert.color}`;
        text.textContent = alert.text;
    }
    setInterval(updateAlerts, 8000);

    const recommendations = [
        "Shift 12% load from Tokyo to Singapore in next 2 hours",
        "Peak risk expected at 18:00 — pre-distribute energy from Singapore",
        "London demand surging — activate secondary thermal buffer",
        "Grid optimization suggested: Increase renewable intake in New York"
    ];

    function updateRecommendation() {
        const recText = document.getElementById('recommendation-text');
        recText.textContent = recommendations[Math.floor(Math.random() * recommendations.length)];
    }
    setInterval(updateRecommendation, 15000);

    function updateRegionGrid() {
        const cityCards = document.querySelectorAll('.city-card');
        cityCards.forEach(card => {
            const stats = card.querySelectorAll('.stat-value');
            // Demand
            const currentDemand = parseInt(stats[0].textContent);
            const dVar = Math.floor(Math.random() * 10 - 5);
            stats[0].textContent = `${currentDemand + dVar} MW`;
            // Load
            const currentLoad = parseInt(stats[1].textContent);
            const lVar = Math.floor(Math.random() * 4 - 2);
            stats[1].textContent = `${Math.min(100, Math.max(10, currentLoad + lVar))}%`;
        });
    }

    setInterval(updateStatusStrip, 20000);

    // --- 3. ENERGY CHART (CHART.JS) ---
    const ctx = document.getElementById('energyChart').getContext('2d');
    
    const chartData = {
        current: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:59'],
            demand: [850, 720, 1100, 1450, 1380, 1200, 950],
            temp: [18, 16, 21, 26, 25, 22, 19]
        },
        '6h': {
            labels: ['T-0', 'T+1h', 'T+2h', 'T+3h', 'T+4h', 'T+5h', 'T+6h'],
            demand: [1240, 1320, 1450, 1580, 1620, 1550, 1480],
            temp: [22, 23, 24, 25, 26, 25, 24]
        },
        '24h': {
            labels: ['Morning', 'Afternoon', 'Evening', 'Night'],
            demand: [900, 1600, 1400, 800],
            temp: [18, 28, 22, 16]
        }
    };

    let energyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.current.labels,
            datasets: [
                {
                    label: 'Demand (MW)',
                    data: chartData.current.demand,
                    backgroundColor: 'rgba(6, 182, 212, 0.4)',
                    borderColor: 'rgba(6, 182, 212, 1)',
                    borderWidth: 1,
                    yAxisID: 'y',
                },
                {
                    label: 'Temperature (°C)',
                    data: chartData.current.temp,
                    type: 'line',
                    borderColor: 'rgba(255, 255, 255, 0.6)',
                    borderWidth: 2,
                    pointRadius: 3,
                    fill: false,
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#e2e8f0', font: { family: 'Inter', size: 11 } }
                }
            }
        }
    });

    // Time Intelligence Controls
    const timeBtns = document.querySelectorAll('.time-btn');
    timeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            timeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const range = btn.dataset.range;
            const newData = chartData[range];
            
            energyChart.data.labels = newData.labels;
            energyChart.data.datasets[0].data = newData.demand;
            energyChart.data.datasets[1].data = newData.temp;
            energyChart.update();

            // Add log
            const logContainer = document.getElementById('system-log');
            const now = new Date();
            const time = `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}]`;
            const newLog = document.createElement('div');
            newLog.className = 'log-item';
            newLog.textContent = `${time} Time range adjusted: ${range.toUpperCase()}`;
            logContainer.prepend(newLog);
        });
    });

    // --- 4. SIMULATION ENGINE LOGIC ---
    const predForm = document.getElementById('prediction-form');
    const predOutput = document.getElementById('prediction-output');
    const predResult = document.getElementById('pred-result');
    const predConfidence = document.getElementById('pred-confidence');
    const predRisk = document.getElementById('pred-risk');
    const predReasoning = document.getElementById('pred-reasoning');

    const regionBaselines = {
        london: 350,
        tokyo: 500,
        singapore: 200,
        'new-york': 450
    };

    predForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Show loading state
        const submitBtn = predForm.querySelector('button');
        submitBtn.textContent = 'SIMULATING SCENARIO...';
        submitBtn.disabled = true;
        predOutput.classList.add('dormant');

        setTimeout(() => {
            const region = document.getElementById('pred-region').value;
            const temp = parseFloat(document.getElementById('pred-temp').value);
            const humidity = parseFloat(document.getElementById('pred-humidity').value);
            const hour = parseInt(document.getElementById('pred-hour').value);
            const isWeekend = document.getElementById('pred-weekend').checked;

            // Decision Simulation Logic
            let demand = regionBaselines[region];
            demand += (Math.abs(20 - temp) * 8);
            demand += (humidity * 0.5);
            const hourEffect = Math.exp(-Math.pow(hour - 14, 2) / 32) * 150;
            demand += hourEffect;
            if (isWeekend) demand *= 0.85;
            demand += (Math.random() * 10 - 5);

            // Additional Simulation Metrics
            const confidence = 75 + Math.floor(Math.random() * 15);
            let risk = "LOW";
            if (demand > 600) risk = "MEDIUM";
            if (demand > 800) risk = "HIGH";

            const reasonings = [
                "Weekend load variation detected. Thermal deviation increasing demand.",
                "Peak industrial hours identified. Load balancing recommended.",
                "Weather correlation indicates slight cooling surge.",
                "Region historical data suggests stable consumption pattern."
            ];

            // Display results
            predResult.innerHTML = `${Math.round(demand)} <small>MW</small>`;
            predConfidence.textContent = `${confidence}%`;
            predRisk.textContent = risk;
            predRisk.className = `value text-${risk === 'HIGH' ? 'red' : (risk === 'MEDIUM' ? 'yellow' : 'green')}`;
            predReasoning.innerHTML = reasonings[Math.floor(Math.random() * reasonings.length)];

            predOutput.classList.remove('dormant');
            submitBtn.disabled = false;
            submitBtn.textContent = 'RUN SCENARIO';

            // Log the simulation
            const logContainer = document.getElementById('system-log');
            const now = new Date();
            const time = `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}]`;
            const newLog = document.createElement('div');
            newLog.className = 'log-item';
            newLog.textContent = `${time} Simulation model updated for ${region.toUpperCase()}`;
            logContainer.prepend(newLog);

        }, 1200);
    });

    // --- 5. LOGOUT ---
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('raya_auth');
            window.location.href = 'portal_login.html';
        });
    }
});
