/**
 * LivingAI - Dashboard JavaScript
 * ==============================
 * Dashboard data loading, real-time stats, and activity feed
 */

// ============================================
// DASHBOARD INITIALIZATION
// ============================================

function initDashboard() {
    console.log('Initializing Dashboard...');
    
    // Load dashboard data
    loadDashboardData();
    
    // Initialize real-time updates
    initRealTimeUpdates();
    
    // Initialize quick actions
    initQuickActions();
    
    // Initialize activity feed
    initActivityFeed();
    
    console.log('Dashboard Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadDashboardData() {
    console.log('Loading dashboard data...');
    
    try {
        // Load all dashboard components
        await Promise.all([
            loadStats(),
            loadRecentActivity(),
            loadSystemHealth(),
            loadQuickActions()
        ]);
        
        console.log('Dashboard data loaded');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

async function loadStats() {
    // Simulate API call to get stats
    // Replace with actual API call: fetch('/api/dashboard/stats')
    
    const mockStats = {
        totalAgents: 8,
        totalTools: 42,
        totalTasks: 127,
        memoryEntries: 843
    };
    
    // Update UI
    const stats = [
        { id: 'total-agents', value: mockStats.totalAgents },
        { id: 'total-tools', value: mockStats.totalTools },
        { id: 'total-tasks', value: mockStats.totalTasks },
        { id: 'memory-entries', value: mockStats.memoryEntries }
    ];
    
    stats.forEach(stat => {
        const element = document.getElementById(stat.id);
        if (element) {
            animateNumber(element, 0, stat.value, 1000);
        }
    });
}

async function loadRecentActivity() {
    // Simulate API call
    const mockActivity = [
        { id: 1, type: 'agent_started', title: 'Agent Started', message: 'Research Agent has been started', time: '2 minutes ago', icon: 'fa-robot', status: 'success' },
        { id: 2, type: 'task_completed', title: 'Task Completed', message: 'Data analysis task finished', time: '5 minutes ago', icon: 'fa-check-circle', status: 'success' },
        { id: 3, type: 'tool_registered', title: 'New Tool', message: 'Web search tool registered', time: '10 minutes ago', icon: 'fa-wrench', status: 'info' },
        { id: 4, type: 'memory_updated', title: 'Memory Updated', message: 'New knowledge added to memory', time: '15 minutes ago', icon: 'fa-database', status: 'info' },
        { id: 5, type: 'system_alert', title: 'System Alert', message: 'High CPU usage detected', time: '20 minutes ago', icon: 'fa-exclamation-triangle', status: 'warning' }
    ];
    
    const activityFeed = document.getElementById('activity-feed');
    if (activityFeed) {
        activityFeed.innerHTML = '';
        
        mockActivity.forEach(activity => {
            const item = createActivityItem(activity);
            activityFeed.appendChild(item);
        });
    }
}

function createActivityItem(activity) {
    const item = document.createElement('div');
    item.className = 'activity-item';
    
    const statusIcons = {
        'success': 'fa-check-circle status-success',
        'info': 'fa-info-circle status-info',
        'warning': 'fa-exclamation-triangle status-warning',
        'error': 'fa-times-circle status-danger'
    };
    
    const icon = statusIcons[activity.status] || 'fa-circle status-info';
    
    item.innerHTML = `
        <i class="fa ${icon}"></i>
        <div class="activity-content">
            <p><strong>${activity.title}</strong>: ${activity.message}</p>
            <span class="activity-time">${activity.time}</span>
        </div>
    `;
    
    return item;
}

async function loadSystemHealth() {
    // Simulate API call
    const mockHealth = {
        cpu: 25,
        memory: 45,
        storage: 35,
        network: 100
    };
    
    // Update UI
    const healthItems = [
        { id: 'cpu-usage', barId: 'cpu-bar', value: mockHealth.cpu },
        { id: 'memory-usage', barId: 'memory-bar', value: mockHealth.memory },
        { id: 'storage-bar', value: mockHealth.storage }
    ];
    
    healthItems.forEach(item => {
        if (item.id) {
            const element = document.getElementById(item.id);
            if (element) element.textContent = `${item.value}%`;
        }
        if (item.barId) {
            const bar = document.getElementById(item.barId);
            if (bar) {
                bar.style.width = `${item.value}%`;
                bar.className = item.value > 80 ? 'health-progress bg-danger' : 
                               item.value > 60 ? 'health-progress bg-warning' : 'health-progress bg-success';
            }
        }
    });
}

async function loadQuickActions() {
    // Quick actions are already defined in HTML
    // Just add click handlers
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', () => {
            button.classList.add('active');
            setTimeout(() => button.classList.remove('active'), 200);
        });
    });
}

// ============================================
// REAL-TIME UPDATES
// ============================================

function initRealTimeUpdates() {
    // Update stats every 30 seconds
    setInterval(() => {
        updateStats();
    }, 30000);
    
    // Update system health every 5 seconds
    setInterval(() => {
        updateSystemHealth();
    }, 5000);
    
    // Update activity feed every 60 seconds
    setInterval(() => {
        updateActivityFeed();
    }, 60000);
}

async function updateStats() {
    // Simulate real-time updates
    const mockUpdates = {
        totalAgents: Math.floor(Math.random() * 5) + 5,
        totalTools: Math.floor(Math.random() * 20) + 30,
        totalTasks: Math.floor(Math.random() * 50) + 100,
        memoryEntries: Math.floor(Math.random() * 500) + 600
    };
    
    const elements = [
        { id: 'total-agents', value: mockUpdates.totalAgents },
        { id: 'total-tools', value: mockUpdates.totalTools },
        { id: 'total-tasks', value: mockUpdates.totalTasks },
        { id: 'memory-entries', value: mockUpdates.memoryEntries }
    ];
    
    elements.forEach(el => {
        const element = document.getElementById(el.id);
        if (element) {
            animateNumber(element, parseInt(element.textContent) || 0, el.value, 500);
        }
    });
}

async function updateSystemHealth() {
    const mockHealth = {
        cpu: Math.floor(Math.random() * 30) + 10,
        memory: Math.floor(Math.random() * 40) + 20,
        storage: Math.floor(Math.random() * 60) + 10
    };
    
    // CPU
    const cpuUsage = document.getElementById('cpu-usage');
    const cpuBar = document.getElementById('cpu-bar');
    if (cpuUsage) cpuUsage.textContent = `${mockHealth.cpu}%`;
    if (cpuBar) {
        cpuBar.style.width = `${mockHealth.cpu}%`;
        cpuBar.className = mockHealth.cpu > 80 ? 'health-progress bg-danger' : 
                          mockHealth.cpu > 60 ? 'health-progress bg-warning' : 'health-progress bg-success';
    }
    
    // Memory
    const memoryUsage = document.getElementById('memory-usage');
    const memoryBar = document.getElementById('memory-bar');
    if (memoryUsage) memoryUsage.textContent = `${mockHealth.memory}%`;
    if (memoryBar) {
        memoryBar.style.width = `${mockHealth.memory}%`;
        memoryBar.className = mockHealth.memory > 80 ? 'health-progress bg-danger' : 
                              mockHealth.memory > 60 ? 'health-progress bg-warning' : 'health-progress bg-success';
    }
    
    // Storage
    const storageBar = document.getElementById('storage-bar');
    if (storageBar) {
        storageBar.style.width = `${mockHealth.storage}%`;
        storageBar.className = mockHealth.storage > 80 ? 'health-progress bg-danger' : 
                              mockHealth.storage > 60 ? 'health-progress bg-warning' : 'health-progress bg-success';
    }
}

async function updateActivityFeed() {
    // Add a new random activity item
    const activityFeed = document.getElementById('activity-feed');
    if (activityFeed) {
        const activities = [
            { type: 'agent_started', title: 'Agent Started', message: 'New agent initialized', time: 'Just now', status: 'success' },
            { type: 'task_completed', title: 'Task Completed', message: 'Background task finished', time: 'Just now', status: 'success' },
            { type: 'tool_registered', title: 'New Tool', message: 'Additional tool added', time: 'Just now', status: 'info' },
            { type: 'memory_updated', title: 'Memory Updated', message: 'Knowledge base updated', time: 'Just now', status: 'info' },
            { type: 'system_alert', title: 'System Alert', message: 'Resource usage normal', time: 'Just now', status: 'warning' }
        ];
        
        const randomActivity = activities[Math.floor(Math.random() * activities.length)];
        const item = createActivityItem(randomActivity);
        activityFeed.insertBefore(item, activityFeed.firstChild);
        
        // Keep only last 10 items
        while (activityFeed.children.length > 10) {
            activityFeed.removeChild(activityFeed.lastChild);
        }
    }
}

// ============================================
// QUICK ACTIONS
// ============================================

function initQuickActions() {
    // All quick actions are handled in app.js
    // This function is for future expansion
}

// ============================================
// ACTIVITY FEED
// ============================================

function initActivityFeed() {
    // Auto-scroll to bottom if new items are added
    const activityFeed = document.getElementById('activity-feed');
    if (activityFeed) {
        const observer = new MutationObserver(() => {
            activityFeed.scrollTop = activityFeed.scrollHeight;
        });
        
        observer.observe(activityFeed, { childList: true });
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function animateNumber(element, start, end, duration) {
    const range = end - start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    const timer = setInterval(() => {
        start += increment;
        element.textContent = start;
        if ((increment > 0 && start >= end) || (increment < 0 && start <= end)) {
            clearInterval(timer);
            element.textContent = end;
        }
    }, stepTime);
}

function showError(message) {
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Error', message, 'error');
    } else {
        console.error(message);
    }
}

// ============================================
// API FUNCTIONS (Replace with actual API calls)
// ============================================

async function fetchDashboardStats() {
    // Simulate API call
    return {
        totalAgents: 8,
        totalTools: 42,
        totalTasks: 127,
        memoryEntries: 843
    };
}

async function fetchRecentActivity() {
    // Simulate API call
    return [
        { id: 1, type: 'agent_started', title: 'Agent Started', message: 'Research Agent has been started', time: '2 minutes ago', status: 'success' },
        { id: 2, type: 'task_completed', title: 'Task Completed', message: 'Data analysis task finished', time: '5 minutes ago', status: 'success' }
    ];
}

async function fetchSystemHealth() {
    // Simulate API call
    return {
        cpu: 25,
        memory: 45,
        storage: 35,
        network: 100
    };
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

// Make functions globally available
window.initDashboard = initDashboard;
window.loadDashboardData = loadDashboardData;
