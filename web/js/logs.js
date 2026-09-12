/**
 * LivingAI - Logs Management JavaScript
 * ====================================
 * System logs viewing, filtering, and export functionality
 */

// ============================================
// LOGS INITIALIZATION
// ============================================

let logs = [];
let logLevels = ['debug', 'info', 'warning', 'error', 'critical'];
let currentLogLevel = 'all';

function initLogs() {
    console.log('Initializing Logs Module...');
    
    // Load logs data
    loadLogs();
    
    // Initialize filters
    initFilters();
    
    // Initialize event listeners
    initEventListeners();
    
    // Start auto-refresh
    startAutoRefresh();
    
    console.log('Logs Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadLogs() {
    console.log('Loading logs...');
    
    try {
        // Show loading state
        const logsContainer = document.getElementById('logs-container');
        if (logsContainer) {
            logsContainer.innerHTML = '<div class="loading-spinner"></div>';
        }
        
        // Fetch logs from API (or use mock data)
        logs = await fetchLogs();
        
        // Render logs
        renderLogs();
        renderLogStats();
        
        console.log(`Loaded ${logs.length} logs`);
    } catch (error) {
        console.error('Error loading logs:', error);
        showError('Failed to load logs');
        
        // Show empty state
        const logsContainer = document.getElementById('logs-container');
        if (logsContainer) {
            logsContainer.innerHTML = '<div class="empty-state"><i class="fa fa-file-text"></i><p>No logs found</p></div>';
        }
    }
}

async function fetchLogs() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/logs');
    // return await response.json();
    
    const now = new Date();
    const generateLog = (level, index) => ({
        id: `log-${index}`,
        timestamp: new Date(now - (index * 5 * 60000)).toISOString(), // 5 minutes apart
        level: level,
        source: ['Agent', 'Tool', 'Task', 'System', 'API'][Math.floor(Math.random() * 5)],
        message: getRandomLogMessage(level),
        details: `Additional details for ${level} log entry`,
        sessionId: `session-${Math.floor(Math.random() * 1000)}`
    });
    
    const logsData = [];
    
    // Generate logs for last 24 hours
    for (let i = 0; i < 200; i++) {
        const levels = ['debug', 'debug', 'info', 'info', 'info', 'warning', 'error'];
        const level = levels[Math.floor(Math.random() * levels.length)];
        logsData.push(generateLog(level, i));
    }
    
    // Sort by timestamp (newest first)
    logsData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    return logsData;
}

function getRandomLogMessage(level) {
    const messages = {
        debug: [
            'Initializing component',
            'Processing request',
            'Loading configuration',
            'Connecting to database',
            'Parsing response'
        ],
        info: [
            'Agent started successfully',
            'Task completed',
            'Tool executed',
            'System health check passed',
            'New session created'
        ],
        warning: [
            'High memory usage detected',
            'Slow response time',
            'Resource limit approaching',
            'Deprecated API used',
            'Configuration override'
        ],
        error: [
            'Failed to connect to database',
            'Invalid API key',
            'Task execution failed',
            'File not found',
            'Permission denied'
        ],
        critical: [
            'System crash detected',
            'Security breach attempt',
            'Critical error in main process',
            'Database corruption',
            'Memory overflow'
        ]
    };
    
    const levelMessages = messages[level] || messages.info;
    return levelMessages[Math.floor(Math.random() * levelMessages.length)];
}

// ============================================
// RENDERING
// ============================================

function renderLogs() {
    const logsContainer = document.getElementById('logs-container');
    if (!logsContainer) return;
    
    // Filter logs by level
    let filteredLogs = currentLogLevel === 'all' 
        ? logs 
        : logs.filter(log => log.level === currentLogLevel);
    
    if (filteredLogs.length === 0) {
        logsContainer.innerHTML = '<div class="empty-state"><i class="fa fa-file-text"></i><p>No logs found for this filter</p></div>';
        return;
    }
    
    // Create logs table
    logsContainer.innerHTML = '';
    
    const logsTable = document.createElement('div');
    logsTable.className = 'logs-table';
    
    // Table header
    const tableHeader = document.createElement('div');
    tableHeader.className = 'logs-header';
    tableHeader.innerHTML = `
        <div class="log-cell timestamp">Timestamp</div>
        <div class="log-cell level">Level</div>
        <div class="log-cell source">Source</div>
        <div class="log-cell message">Message</div>
        <div class="log-cell actions">Actions</div>
    `;
    
    // Table body
    const tableBody = document.createElement('div');
    tableBody.className = 'logs-body';
    
    filteredLogs.forEach(log => {
        const logRow = createLogRow(log);
        tableBody.appendChild(logRow);
    });
    
    logsTable.appendChild(tableHeader);
    logsTable.appendChild(tableBody);
    logsContainer.appendChild(logsTable);
}

function createLogRow(log) {
    const row = document.createElement('div');
    row.className = `log-row level-${log.level}`;
    row.dataset.logId = log.id;
    
    // Format timestamp
    const timestamp = formatLogTimestamp(log.timestamp);
    
    // Level badge
    const levelBadge = getLevelBadge(log.level);
    
    row.innerHTML = `
        <div class="log-cell timestamp">${timestamp}</div>
        <div class="log-cell level">${levelBadge}</div>
        <div class="log-cell source">${log.source}</div>
        <div class="log-cell message">${log.message}</div>
        <div class="log-cell actions">
            <button class="btn-icon" onclick="viewLogDetails('${log.id}')" title="View Details">
                <i class="fa fa-eye"></i>
            </button>
            <button class="btn-icon" onclick="copyLog('${log.id}')" title="Copy">
                <i class="fa fa-copy"></i>
            </button>
        </div>
    `;
    
    return row;
}

function formatLogTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

function getLevelBadge(level) {
    const levelIcons = {
        debug: 'fa-bug',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-times-circle',
        critical: 'fa-exclamation-circle'
    };
    
    const levelColors = {
        debug: 'debug',
        info: 'info',
        warning: 'warning',
        error: 'danger',
        critical: 'critical'
    };
    
    const icon = levelIcons[level] || 'fa-circle';
    const color = levelColors[level] || 'info';
    
    return `<span class="log-level-badge ${color}"><i class="fa ${icon}"></i> ${level.toUpperCase()}</span>`;
}

function renderLogStats() {
    const statsContainer = document.getElementById('logs-stats');
    if (!statsContainer) return;
    
    const totalLogs = logs.length;
    const stats = {};
    
    logLevels.forEach(level => {
        stats[level] = logs.filter(log => log.level === level).length;
    });
    
    statsContainer.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">${totalLogs}</div>
            <div class="stat-label">Total Logs</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${stats.critical + stats.error}</div>
            <div class="stat-label">Critical/Errors</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${stats.warning}</div>
            <div class="stat-label">Warnings</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${stats.info}</div>
            <div class="stat-label">Info</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${stats.debug}</div>
            <div class="stat-label">Debug</div>
        </div>
    `;
}

// ============================================
// LOG ACTIONS
// ============================================

function viewLogDetails(logId) {
    const log = logs.find(l => l.id === logId);
    if (!log) {
        showError('Log not found');
        return;
    }
    
    showLogDetailsDialog(log);
}

function showLogDetailsDialog(log) {
    const dialog = document.createElement('div');
    dialog.className = 'modal-overlay';
    dialog.id = 'log-details-modal';
    
    const levelColors = {
        debug: 'debug',
        info: 'info',
        warning: 'warning',
        error: 'danger',
        critical: 'critical'
    };
    
    const color = levelColors[log.level] || 'info';
    
    dialog.innerHTML = `
        <div class="modal log-modal">
            <div class="modal-header">
                <h2><i class="fa fa-file-text"></i> Log Details</h2>
                <button class="modal-close" onclick="closeLogDetailsDialog()">
                    <i class="fa fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="log-detail-item">
                    <div class="detail-label">Timestamp</div>
                    <div class="detail-value">${formatLogTimestamp(log.timestamp)}</div>
                </div>
                <div class="log-detail-item">
                    <div class="detail-label">Level</div>
                    <div class="detail-value">
                        <span class="log-level-badge ${color}">
                            <i class="fa ${getLevelIcon(log.level)}"></i> ${log.level.toUpperCase()}
                        </span>
                    </div>
                </div>
                <div class="log-detail-item">
                    <div class="detail-label">Source</div>
                    <div class="detail-value">${log.source}</div>
                </div>
                <div class="log-detail-item">
                    <div class="detail-label">Session ID</div>
                    <div class="detail-value">${log.sessionId}</div>
                </div>
                <div class="log-detail-item">
                    <div class="detail-label">Message</div>
                    <div class="detail-value">${log.message}</div>
                </div>
                <div class="log-detail-item">
                    <div class="detail-label">Details</div>
                    <div class="detail-value">${log.details}</div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeLogDetailsDialog()">
                    <i class="fa fa-times"></i> Close
                </button>
                <button class="btn btn-primary" onclick="copyLogDetails('${log.id}')">
                    <i class="fa fa-copy"></i> Copy Details
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialog);
}

function closeLogDetailsDialog() {
    const dialog = document.getElementById('log-details-modal');
    if (dialog) {
        dialog.remove();
    }
}

function getLevelIcon(level) {
    const icons = {
        debug: 'fa-bug',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-times-circle',
        critical: 'fa-exclamation-circle'
    };
    return icons[level] || 'fa-circle';
}

function copyLog(logId) {
    const log = logs.find(l => l.id === logId);
    if (!log) {
        showError('Log not found');
        return;
    }
    
    const logText = formatLogForCopy(log);
    copyToClipboard(logText);
    
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Log Copied', 'Log entry has been copied to clipboard', 'success');
    }
}

function copyLogDetails(logId) {
    const log = logs.find(l => l.id === logId);
    if (!log) {
        showError('Log not found');
        return;
    }
    
    const logText = formatLogDetailsForCopy(log);
    copyToClipboard(logText);
    
    closeLogDetailsDialog();
    
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Details Copied', 'Log details have been copied to clipboard', 'success');
    }
}

function formatLogForCopy(log) {
    return `[${formatLogTimestamp(log.timestamp)}] [${log.level.toUpperCase()}] [${log.source}] ${log.message}`;
}

function formatLogDetailsForCopy(log) {
    return `Timestamp: ${formatLogTimestamp(log.timestamp)}
Level: ${log.level.toUpperCase()}
Source: ${log.source}
Session ID: ${log.sessionId}
Message: ${log.message}
Details: ${log.details}`;
}

function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}

// ============================================
// AUTO-REFRESH
// ============================================

function startAutoRefresh() {
    // Auto-refresh logs every 30 seconds
    setInterval(() => {
        refreshLogs();
    }, 30000);
}

async function refreshLogs() {
    try {
        // Fetch new logs
        const newLogs = await fetchLogs();
        
        // Check if there are new logs
        if (newLogs.length > logs.length) {
            logs = newLogs;
            renderLogs();
            renderLogStats();
            
            if (window.livingAIApp) {
                window.livingAIApp.addNotification('New Logs', `${newLogs.length - logs.length} new log entries`, 'info');
            }
        }
    } catch (error) {
        console.error('Error refreshing logs:', error);
    }
}

// ============================================
// FILTERS
// ============================================

function initFilters() {
    // Log level filter
    const levelFilter = document.getElementById('log-level-filter');
    if (levelFilter) {
        levelFilter.addEventListener('change', (e) => {
            currentLogLevel = e.target.value;
            renderLogs();
        });
    }
    
    // Search filter
    const searchInput = document.getElementById('log-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchLogs(e.target.value);
        });
    }
}

function searchLogs(query) {
    if (!query) {
        renderLogs();
        return;
    }
    
    const filteredLogs = logs.filter(log => 
        log.message.toLowerCase().includes(query.toLowerCase()) ||
        log.source.toLowerCase().includes(query.toLowerCase()) ||
        log.sessionId.toLowerCase().includes(query.toLowerCase())
    );
    
    const logsContainer = document.getElementById('logs-container');
    if (!logsContainer) return;
    
    if (filteredLogs.length === 0) {
        logsContainer.innerHTML = '<div class="empty-state"><i class="fa fa-search"></i><p>No logs found matching your search</p></div>';
        return;
    }
    
    logsContainer.innerHTML = '';
    
    const header = document.createElement('div');
    header.className = 'filtered-logs-header';
    header.innerHTML = `<h3>Search Results (${filteredLogs.length} logs)</h3>`;
    
    const table = document.createElement('div');
    table.className = 'logs-table';
    
    const tableHeader = document.createElement('div');
    tableHeader.className = 'logs-header';
    tableHeader.innerHTML = `
        <div class="log-cell timestamp">Timestamp</div>
        <div class="log-cell level">Level</div>
        <div class="log-cell source">Source</div>
        <div class="log-cell message">Message</div>
        <div class="log-cell actions">Actions</div>
    `;
    
    const tableBody = document.createElement('div');
    tableBody.className = 'logs-body';
    
    filteredLogs.forEach(log => {
        const logRow = createLogRow(log);
        tableBody.appendChild(logRow);
    });
    
    table.appendChild(tableHeader);
    table.appendChild(tableBody);
    
    logsContainer.appendChild(header);
    logsContainer.appendChild(table);
}

// ============================================
// LOG EXPORT
// ============================================

function exportLogs() {
    const data = JSON.stringify(logs, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `livingai-logs-${new Date().toISOString().substring(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Logs Exported', 'Logs have been exported successfully', 'success');
    }
}

function exportFilteredLogs() {
    const filteredLogs = currentLogLevel === 'all' 
        ? logs 
        : logs.filter(log => log.level === currentLogLevel);
    
    const data = JSON.stringify(filteredLogs, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `livingai-logs-${currentLogLevel}-${new Date().toISOString().substring(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Filtered Logs Exported', `Filtered logs (${currentLogLevel}) have been exported`, 'success');
    }
}

// ============================================
// LOG CLEARING
// ============================================

function clearLogs() {
    if (!confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
        return;
    }
    
    try {
        // Simulate API call to clear logs
        // Replace with: await fetch('/api/logs', { method: 'DELETE' })
        
        logs = [];
        renderLogs();
        renderLogStats();
        
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Logs Cleared', 'All logs have been cleared', 'success');
        }
    } catch (error) {
        console.error('Error clearing logs:', error);
        showError('Failed to clear logs');
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    // Export buttons
    const exportAllBtn = document.getElementById('export-all-logs-btn');
    if (exportAllBtn) {
        exportAllBtn.addEventListener('click', exportLogs);
    }
    
    const exportFilteredBtn = document.getElementById('export-filtered-logs-btn');
    if (exportFilteredBtn) {
        exportFilteredBtn.addEventListener('click', exportFilteredLogs);
    }
    
    // Clear button
    const clearBtn = document.getElementById('clear-logs-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearLogs);
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

window.initLogs = initLogs;
window.viewLogDetails = viewLogDetails;
window.closeLogDetailsDialog = closeLogDetailsDialog;
window.copyLog = copyLog;
window.copyLogDetails = copyLogDetails;
window.refreshLogs = refreshLogs;
window.exportLogs = exportLogs;
window.exportFilteredLogs = exportFilteredLogs;
window.clearLogs = clearLogs;
