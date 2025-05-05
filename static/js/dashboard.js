// Dashboard JavaScript for CyberShield IDS

document.addEventListener('DOMContentLoaded', function() {
    // Store alerts data
    let alertsData = [];
    
    // Mock data for demo purposes (remove in production)
    const mockTrafficData = {
        hour: generateHourlyData(),
        day: generateDailyData(),
        week: generateWeeklyData()
    };
    
    const mockThreatData = {
        labels: ['Normal Traffic', 'Port Scan', 'DDoS', 'Brute Force', 'SQL Injection'],
        values: [65, 15, 10, 5, 5]
    };
    
    // Update dashboard statistics
    function updateStats() {
        // In a real application, these would come from an API
        document.getElementById('total-traffic').textContent = randomInRange(1000, 10000);
        document.getElementById('safe-traffic').textContent = randomInRange(900, 9000);
        document.getElementById('intrusion-count').textContent = alertsData.length;
        document.getElementById('processing-speed').textContent = randomInRange(50, 200);
    }
    
    // Initialize charts
    function initCharts() {
        // Traffic Analysis Chart
        const trafficCtx = document.getElementById('traffic-chart').getContext('2d');
        const trafficChart = new Chart(trafficCtx, {
            type: 'line',
            data: {
                labels: mockTrafficData.hour.labels,
                datasets: [
                    {
                        label: 'Total Traffic',
                        data: mockTrafficData.hour.total,
                        borderColor: '#2b5fb4',
                        backgroundColor: 'rgba(43, 95, 180, 0.1)',
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: '#2b5fb4',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Intrusions',
                        data: mockTrafficData.hour.intrusions,
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: '#dc3545',
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
        
        // Threat Distribution Chart
        const threatCtx = document.getElementById('threat-distribution').getContext('2d');
        const threatChart = new Chart(threatCtx, {
            type: 'doughnut',
            data: {
                labels: mockThreatData.labels,
                datasets: [{
                    data: mockThreatData.values,
                    backgroundColor: [
                        '#28a745',
                        '#dc3545',
                        '#ffc107',
                        '#17a2b8',
                        '#6c757d'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 15,
                            padding: 15
                        }
                    }
                },
                cutout: '70%'
            }
        });
        
        // Add time period switcher for traffic chart
        const timeButtons = document.querySelectorAll('[data-time]');
        timeButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                timeButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                this.classList.add('active');
                
                // Update chart data
                const timeFrame = this.getAttribute('data-time');
                trafficChart.data.labels = mockTrafficData[timeFrame].labels;
                trafficChart.data.datasets[0].data = mockTrafficData[timeFrame].total;
                trafficChart.data.datasets[1].data = mockTrafficData[timeFrame].intrusions;
                trafficChart.update();
            });
        });
        
        return { trafficChart, threatChart };
    }
    
    // Fetch alerts from API
    function fetchAlerts() {
        fetch('/api/alerts')
            .then(response => response.json())
            .then(data => {
                alertsData = data;
                updateAlertsTable();
                updateStats();
            })
            .catch(error => {
                console.error('Error fetching alerts:', error);
            });
    }
    
    // Update alerts table
    function updateAlertsTable() {
        const tableBody = document.querySelector('#alerts-table tbody');
        
        if (alertsData.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No alerts found</td></tr>';
            return;
        }
        
        tableBody.innerHTML = '';
        
        alertsData.forEach(alert => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-id', alert.id);
            
            const confidence = alert.confidence * 100;
            const confidenceFixed = confidence.toFixed(2);
            
            tr.innerHTML = `
                <td>${alert.timestamp}</td>
                <td>${alert.source}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar bg-danger" role="progressbar" 
                             style="width: ${confidence}%">
                            ${confidenceFixed}%
                        </div>
                    </div>
                </td>
                <td><span class="badge bg-danger">Active</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary view-details">
                        <i class="fas fa-eye"></i> Details
                    </button>
                </td>
            `;
            
            tableBody.appendChild(tr);
        });
        
        // Add event listeners to view details buttons
        document.querySelectorAll('.view-details').forEach(button => {
            button.addEventListener('click', function() {
                const alertId = this.closest('tr').getAttribute('data-id');
                showAlertDetails(alertId);
            });
        });
    }
    
    // Show alert details in modal
    function showAlertDetails(alertId) {
        const alert = alertsData.find(a => a.id === alertId);
        
        if (!alert) return;
        
        // Populate modal with alert data
        document.getElementById('modal-alert-id').textContent = alert.id;
        document.getElementById('modal-alert-time').textContent = alert.timestamp;
        document.getElementById('modal-alert-source').textContent = alert.source;
        document.getElementById('modal-alert-confidence').textContent = `${(alert.confidence * 100).toFixed(2)}%`;
        
        // Populate details table
        const detailsTable = document.getElementById('alert-details-table').querySelector('tbody');
        detailsTable.innerHTML = '';
        
        Object.entries(alert.details).forEach(([key, value]) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${key}</strong></td>
                <td>${value}</td>
            `;
            detailsTable.appendChild(tr);
        });
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('alert-details-modal'));
        modal.show();
    }
    
    // Mark alert as resolved
    document.getElementById('mark-resolved').addEventListener('click', function() {
        const alertId = document.getElementById('modal-alert-id').textContent;
        
        // In a real application, this would make an API call
        // For demo purposes, just update the UI
        document.querySelector(`tr[data-id="${alertId}"] .badge`).className = 'badge bg-success';
        document.querySelector(`tr[data-id="${alertId}"] .badge`).textContent = 'Resolved';
        
        document.getElementById('modal-alert-status').className = 'badge bg-success';
        document.getElementById('modal-alert-status').textContent = 'Resolved';
        
        // Update intrusion count
        const intrusions = parseInt(document.getElementById('intrusion-count').textContent);
        document.getElementById('intrusion-count').textContent = intrusions - 1;
    });
    
    // Refresh alerts
    document.getElementById('refresh-alerts').addEventListener('click', function() {
        const icon = this.querySelector('i');
        icon.classList.add('fa-spin');
        
        fetchAlerts();
        
        setTimeout(() => {
            icon.classList.remove('fa-spin');
        }, 1000);
    });
    
    // Initialize dashboard
    if (document.querySelector('.dashboard-container')) {
        updateStats();
        const charts = initCharts();
        fetchAlerts();
        
        // Set up auto-refresh (every 30 seconds)
        setInterval(() => {
            fetchAlerts();
            updateStats();
        }, 30000);
    }
    
    // Helper functions for generating mock data
    function generateHourlyData() {
        const hours = [];
        const total = [];
        const intrusions = [];
        
        const now = new Date();
        
        for (let i = 12; i >= 0; i--) {
            const time = new Date(now);
            time.setHours(now.getHours() - i);
            hours.push(time.getHours() + ':00');
            
            const traffic = randomInRange(100, 500);
            total.push(traffic);
            
            // Intrusions are typically a small percentage of total traffic
            intrusions.push(Math.floor(traffic * randomInRange(0.01, 0.1)));
        }
        
        return { labels: hours, total, intrusions };
    }
    
    function generateDailyData() {
        const days = [];
        const total = [];
        const intrusions = [];
        
        const now = new Date();
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        
        for (let i = 6; i >= 0; i--) {
            const day = new Date(now);
            day.setDate(now.getDate() - i);
            days.push(dayNames[day.getDay()]);
            
            const traffic = randomInRange(1000, 5000);
            total.push(traffic);
            
            // Intrusions are typically a small percentage of total traffic
            intrusions.push(Math.floor(traffic * randomInRange(0.02, 0.08)));
        }
        
        return { labels: days, total, intrusions };
    }
    
    function generateWeeklyData() {
        const weeks = [];
        const total = [];
        const intrusions = [];
        
        const now = new Date();
        
        for (let i = 4; i >= 0; i--) {
            const week = new Date(now);
            week.setDate(now.getDate() - (i * 7));
            weeks.push(`Week ${i + 1}`);
            
            const traffic = randomInRange(5000, 20000);
            total.push(traffic);
            
            // Intrusions are typically a small percentage of total traffic
            intrusions.push(Math.floor(traffic * randomInRange(0.03, 0.07)));
        }
        
        return { labels: weeks, total, intrusions };
    }
    
    function randomInRange(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
});