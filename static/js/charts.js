// Load Airline Performance Chart
fetch('/api/airline-performance')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('airlineChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.Airline),
                datasets: [
                    {
                        label: 'Avg Satisfaction',
                        data: data.map(d => d.Avg_Satisfaction),
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Avg Delay (min)',
                        data: data.map(d => d.Avg_Delay),
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Satisfaction Score'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Delay (minutes)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    });

// Flight Status Distribution
fetch('/api/kpi-data')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('statusChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['On-Time', 'Delayed', 'Cancelled'],
                datasets: [{
                    data: [
                        data.on_time_rate,
                        100 - data.on_time_rate - data.cancellation_rate,
                        data.cancellation_rate
                    ],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(255, 99, 132, 0.7)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    });

// Delay Distribution Chart
fetch('/api/delay-distribution')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('delayChart').getContext('2d');
        
        // Group delays into bins
        const bins = [0, 15, 30, 45, 60, 90, 120, 180];
        const binLabels = ['0-15', '15-30', '30-45', '45-60', '60-90', '90-120', '120-180'];
        const binCounts = new Array(binLabels.length).fill(0);
        
        data.delay_minutes.forEach((delay, idx) => {
            const count = data.count[idx];
            for (let i = 0; i < bins.length - 1; i++) {
                if (delay >= bins[i] && delay < bins[i + 1]) {
                    binCounts[i] += count;
                    break;
                }
            }
        });
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: binLabels,
                datasets: [{
                    label: 'Number of Flights',
                    data: binCounts,
                    backgroundColor: 'rgba(255, 159, 64, 0.7)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Flights'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Delay Duration (minutes)'
                        }
                    }
                }
            }
        });
    });

// Popular Routes Chart
fetch('/api/route-analysis')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('routeChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.Route),
                datasets: [{
                    label: 'Number of Flights',
                    data: data.map(d => d.Flight_ID),
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Flights'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Error loading route chart:', error);
    });

// Time Series Chart
fetch('/api/time-series')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('timeSeriesChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.Date),
                datasets: [
                    {
                        label: 'Daily Flights',
                        data: data.map(d => d.Flight_ID),
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Avg Satisfaction',
                        data: data.map(d => d.Flight_Satisfaction_Score),
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderWidth: 2,
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        },
                        ticks: {
                            maxTicksLimit: 15
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Number of Flights'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Satisfaction Score'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    });