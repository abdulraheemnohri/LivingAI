/**
 * LivingAI - Analytics Dashboard JavaScript
 * ========================================
 * Chart.js integration for tool usage, task distribution, and performance analytics
 */

// ============================================
// ANALYTICS INITIALIZATION
// ============================================

let analyticsData = {};
let charts = {};

function initAnalytics() {
    console.log('Initializing Analytics Module...');
    
    // Load analytics data
    loadAnalyticsData();
    
    // Initialize charts
    initCharts();
    
    // Initialize date range picker
    initDateRangePicker();
    
    console.log('Analytics Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadAnalyticsData() {
    console.log('Loading analytics data...');
    
    try {
        // Show loading state
        const analyticsContainer = document.getElementById('analytics-container');
        if (analyticsContainer) {
            analyticsContainer.innerHTML = '<div class="loading-spinner"></div>';
        }
        
        // Fetch analytics from API (or use mock data)
        analyticsData = await fetchAnalyticsData();
        
        // Render analytics
        renderAnalytics();
        
        console.log('Analytics data loaded');
    } catch (error) {
        console.error('Error loading analytics:', error);
        showError('Failed to load analytics data');
        
        // Show empty state
        const analyticsContainer = document.getElementById('analytics-container');
        if (analyticsContainer) {
            analyticsContainer.innerHTML = '<div class="empty-state"><i class="fa fa-chart-line"></i><p>No analytics data available</p></div>';
        }
    }
}

async function fetchAnalyticsData() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/analytics');
    // return await response.json();
    
    return {
        // Summary stats
        summary: {
            totalAgents: 8,
            totalTools: 42,
            totalTasks: 127,
            totalMemoryEntries: 843,
            activeUsers: 1,
            systemUptime: '99.9%'
        },
        
        // Tool usage analytics
        toolUsage: {
            labels: ['Web Search', 'Code Gen', 'Data Analysis', 'Summarization', 'Translation', 'Image Gen'],
            data: [42, 87, 35, 28, 53, 64],
            backgroundColors: [
                'rgba(99, 102, 241, 0.7)',
                'rgba(139, 92, 246, 0.7)',
                'rgba(16, 185, 129, 0.7)',
                'rgba(245, 158, 11, 0.7)',
                'rgba(6, 182, 212, 0.7)',
                'rgba(239, 68, 68, 0.7)'
            ],
            borderColors: [
                'rgba(99, 102, 241, 1)',
                'rgba(139, 92, 246, 1)',
                'rgba(16, 185, 129, 1)',
                'rgba(245, 158, 11, 1)',
                'rgba(6, 182, 212, 1)',
                'rgba(239, 68, 68, 1)'
            ]
        },
        
        // Task distribution
        taskDistribution: {
            labels: ['Pending', 'In Progress', 'Completed', 'Failed', 'Cancelled'],
            data: [25, 15, 80, 5, 2],
            backgroundColors: [
                'rgba(107, 114, 128, 0.7)',
                'rgba(245, 158, 11, 0.7)',
                'rgba(16, 185, 129, 0.7)',
                'rgba(239, 68, 68, 0.7)',
                'rgba(156, 163, 175, 0.7)'
            ],
            borderColors: [
                'rgba(107, 114, 128, 1)',
                'rgba(245, 158, 11, 1)',
                'rgba(16, 185, 129, 1)',
                'rgba(239, 68, 68, 1)',
                'rgba(156, 163, 175, 1)'
            ]
        },
        
        // Performance metrics
        performance: {
            cpu: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                data: [25, 20, 45, 60, 40, 30]
            },
            memory: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                data: [30, 25, 50, 65, 45, 35]
            },
            storage: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                data: [40, 35, 55, 70, 50, 45]
            }
        },
        
        // Agent activity
        agentActivity: {
            labels: ['Research', 'Development', 'Analysis', 'Creative', 'General'],
            data: [25, 40, 30, 15, 50],
            backgroundColors: [
                'rgba(99, 102, 241, 0.7)',
                'rgba(139, 92, 246, 0.7)',
                'rgba(16, 185, 129, 0.7)',
                'rgba(245, 158, 11, 0.7)',
                'rgba(6, 182, 212, 0.7)'
            ]
        },
        
        // Daily activity
        dailyActivity: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            data: [65, 59, 80, 81, 56, 55, 40]
        }
    };
}

// ============================================
// RENDERING
// ============================================

function renderAnalytics() {
    const analyticsContainer = document.getElementById('analytics-container');
    if (!analyticsContainer) return;
    
    analyticsContainer.innerHTML = '';
    
    // Create dashboard layout
    const dashboard = document.createElement('div');
    dashboard.className = 'analytics-dashboard';
    
    // Summary cards
    const summaryRow = createSummaryCards();
    dashboard.appendChild(summaryRow);
    
    // Charts row 1
    const chartsRow1 = document.createElement('div');
    chartsRow1.className = 'analytics-row';
    
    const toolUsageChart = createChartContainer('tool-usage-chart', 'Tool Usage', 'bar');
    const taskDistributionChart = createChartContainer('task-distribution-chart', 'Task Distribution', 'doughnut');
    
    chartsRow1.appendChild(toolUsageChart);
    chartsRow1.appendChild(taskDistributionChart);
    dashboard.appendChild(chartsRow1);
    
    // Charts row 2
    const chartsRow2 = document.createElement('div');
    chartsRow2.className = 'analytics-row';
    
    const performanceChart = createChartContainer('performance-chart', 'System Performance', 'line');
    const agentActivityChart = createChartContainer('agent-activity-chart', 'Agent Activity', 'polarArea');
    
    chartsRow2.appendChild(performanceChart);
    chartsRow2.appendChild(agentActivityChart);
    dashboard.appendChild(chartsRow2);
    
    // Charts row 3
    const chartsRow3 = document.createElement('div');
    chartsRow3.className = 'analytics-row';
    
    const dailyActivityChart = createChartContainer('daily-activity-chart', 'Daily Activity', 'line');
    
    chartsRow3.appendChild(dailyActivityChart);
    dashboard.appendChild(chartsRow3);
    
    analyticsContainer.appendChild(dashboard);
    
    // Initialize charts
    initCharts();
}

function createSummaryCards() {
    const row = document.createElement('div');
    row.className = 'analytics-row summary-row';
    
    const summary = analyticsData.summary || {};
    
    const cards = [
        { label: 'Active Agents', value: summary.totalAgents || 0, icon: 'fa-robot', color: 'primary' },
        { label: 'Available Tools', value: summary.totalTools || 0, icon: 'fa-wrench', color: 'success' },
        { label: 'Total Tasks', value: summary.totalTasks || 0, icon: 'fa-tasks', color: 'info' },
        { label: 'Memory Entries', value: summary.totalMemoryEntries || 0, icon: 'fa-database', color: 'warning' },
        { label: 'System Uptime', value: summary.systemUptime || '0%', icon: 'fa-heartbeat', color: 'danger' },
        { label: 'Active Users', value: summary.activeUsers || 0, icon: 'fa-users', color: 'secondary' }
    ];
    
    cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'analytics-summary-card';
        cardElement.innerHTML = `
            <div class="summary-icon bg-${card.color}">
                <i class="fa ${card.icon}"></i>
            </div>
            <div class="summary-content">
                <h3>${card.value}</h3>
                <p>${card.label}</p>
            </div>
        `;
        row.appendChild(cardElement);
    });
    
    return row;
}

function createChartContainer(id, title, type) {
    const container = document.createElement('div');
    container.className = `analytics-chart-container ${type}-chart`;
    
    container.innerHTML = `
        <div class="chart-header">
            <h3>${title}</h3>
            <div class="chart-controls">
                <button class="btn-icon" onclick="refreshChart('${id}')" title="Refresh">
                    <i class="fa fa-refresh"></i>
                </button>
            </div>
        </div>
        <div class="chart-canvas-container">
            <canvas id="${id}"></canvas>
        </div>
    `;
    
    return container;
}

// ============================================
// CHARTS INITIALIZATION
// ============================================

function initCharts() {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded. Analytics charts will not work.');
        showError('Chart.js library is required for analytics. Please include it in your HTML.');
        return;
    }
    
    // Destroy existing charts
    Object.values(charts).forEach(chart => {
        if (chart) {
            chart.destroy();
        }
    });
    charts = {};
    
    // Create charts
    createToolUsageChart();
    createTaskDistributionChart();
    createPerformanceChart();
    createAgentActivityChart();
    createDailyActivityChart();
}

function createToolUsageChart() {
    const ctx = document.getElementById('tool-usage-chart');
    if (!ctx) return;
    
    const data = analyticsData.toolUsage || {};
    
    charts.toolUsage = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Usage Count',
                data: data.data || [],
                backgroundColor: data.backgroundColors || [],
                borderColor: data.borderColors || [],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Usage: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function createTaskDistributionChart() {
    const ctx = document.getElementById('task-distribution-chart');
    if (!ctx) return;
    
    const data = analyticsData.taskDistribution || {};
    
    charts.taskDistribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels || [],
            datasets: [{
                data: data.data || [],
                backgroundColor: data.backgroundColors || [],
                borderColor: data.borderColors || [],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createPerformanceChart() {
    const ctx = document.getElementById('performance-chart');
    if (!ctx) return;
    
    const data = analyticsData.performance || {};
    
    charts.performance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.cpu.labels || [],
            datasets: [
                {
                    label: 'CPU Usage (%)',
                    data: data.cpu.data || [],
                    borderColor: 'rgba(99, 102, 241, 1)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Memory Usage (%)',
                    data: data.memory.data || [],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Storage Usage (%)',
                    data: data.storage.data || [],
                    borderColor: 'rgba(245, 158, 11, 1)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
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
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function createAgentActivityChart() {
    const ctx = document.getElementById('agent-activity-chart');
    if (!ctx) return;
    
    const data = analyticsData.agentActivity || {};
    
    charts.agentActivity = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: data.labels || [],
            datasets: [{
                data: data.data || [],
                backgroundColor: data.backgroundColors || [],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.r}`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function createDailyActivityChart() {
    const ctx = document.getElementById('daily-activity-chart');
    if (!ctx) return;
    
    const data = analyticsData.dailyActivity || {};
    
    charts.dailyActivity = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Tasks Completed',
                data: data.data || [],
                borderColor: 'rgba(139, 92, 246, 1)',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Tasks: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// ============================================
// DATE RANGE PICKER
// ============================================

function initDateRangePicker() {
    const dateRangeSelect = document.getElementById('analytics-date-range');
    if (!dateRangeSelect) return;
    
    dateRangeSelect.addEventListener('change', (e) => {
        const range = e.target.value;
        updateDateRange(range);
    });
}

function updateDateRange(range) {
    // Update analytics data based on date range
    // This would typically fetch new data from the API
    console.log(`Date range changed to: ${range}`);
    
    // For demo, just show a message
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Date Range Updated', `Analytics now showing data for: ${range}`, 'info');
    }
}

// ============================================
// CHART ACTIONS
// ============================================

function refreshChart(chartId) {
    // Simulate refreshing chart data
    console.log(`Refreshing chart: ${chartId}`);
    
    // For demo, just show a message
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Chart Refreshed', `Chart "${chartId}" has been refreshed`, 'success');
    }
}

function refreshAllCharts() {
    // Refresh all charts
    Object.keys(charts).forEach(chartId => {
        refreshChart(chartId);
    });
    
    // Reload analytics data
    loadAnalyticsData();
}

// ============================================
// DATA EXPORT
// ============================================

function exportAnalytics() {
    const data = JSON.stringify(analyticsData, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `livingai-analytics-${new Date().toISOString().substring(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Analytics Exported', 'Analytics data has been exported successfully', 'success');
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function showError(message) {
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Error', message, 'error');
    } else {
        console.error(message);
    }
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

window.initAnalytics = initAnalytics;
window.refreshChart = refreshChart;
window.refreshAllCharts = refreshAllCharts;
window.exportAnalytics = exportAnalytics;
window.updateDateRange = updateDateRange;
