// LivingAI Web Interface - Main JavaScript

// Application State
const AppState = {
    currentSection: 'dashboard',
    theme: localStorage.getItem('theme') || 'light',
    language: localStorage.getItem('language') || 'en',
    agents: [],
    tools: [],
    tasks: [],
    memory: [],
    terminalHistory: [],
    analytics: {
        sessions: 0,
        commands: 0,
        avgResponseTime: 0,
        errorRate: 0
    },
    settings: {
        darkMode: localStorage.getItem('darkMode') === 'true' || false,
        autoUpdate: true,
        dataSync: false,
        notifications: true
    }
};

// DOM Elements
const DOM = {
    sidebar: document.getElementById('sidebar'),
    mainContent: document.getElementById('mainContent'),
    sidebarToggle: document.getElementById('sidebarToggle'),
    modalOverlay: document.getElementById('modalOverlay'),
    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modalTitle'),
    modalContent: document.getElementById('modalContent'),
    modalFooter: document.getElementById('modalFooter'),
    toastContainer: document.getElementById('toastContainer'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    terminalOutput: document.getElementById('terminalOutput'),
    terminalInput: document.getElementById('terminalInput'),
    commandSuggestions: document.getElementById('commandSuggestions')
};

// Initialize Application
function init() {
    // Set theme
    setTheme(AppState.theme);
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    loadInitialData();
    
    // Initialize sections
    initSections();
    
    // Initialize terminal
    initTerminal();
    
    // Show welcome message
    showToast('Welcome to LivingAI!', 'info');
}

// Setup Event Listeners
function setupEventListeners() {
    // Sidebar toggle
    DOM.sidebarToggle.addEventListener('click', toggleSidebar);
    
    // Navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section');
            showSection(section);
            toggleSidebar();
        });
    });
    
    // Terminal input
    DOM.terminalInput.addEventListener('input', handleTerminalInput);
    DOM.terminalInput.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp') {
            navigateTerminalHistory(-1);
        } else if (e.key === 'ArrowDown') {
            navigateTerminalHistory(1);
        }
    });
    
    // Close modal on overlay click
    DOM.modalOverlay.addEventListener('click', (e) => {
        if (e.target === DOM.modalOverlay) {
            closeModal();
        }
    });
    
    // Window resize
    window.addEventListener('resize', handleResize);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            focusSearch();
        }
        
        // Escape to close modal
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// Load Initial Data
function loadInitialData() {
    // Load from localStorage if available
    const savedAgents = localStorage.getItem('agents');
    const savedTools = localStorage.getItem('tools');
    const savedTasks = localStorage.getItem('tasks');
    const savedMemory = localStorage.getItem('memory');
    const savedTerminalHistory = localStorage.getItem('terminalHistory');
    
    if (savedAgents) AppState.agents = JSON.parse(savedAgents);
    if (savedTools) AppState.tools = JSON.parse(savedTools);
    if (savedTasks) AppState.tasks = JSON.parse(savedTasks);
    if (savedMemory) AppState.memory = JSON.parse(savedMemory);
    if (savedTerminalHistory) AppState.terminalHistory = JSON.parse(savedTerminalHistory);
    
    // Update UI with loaded data
    updateDashboard();
    updateAgentsList();
    updateToolsList();
    updateTasksList();
    updateMemoryList();
    updateTerminal();
}

// Save Data to LocalStorage
function saveData() {
    localStorage.setItem('agents', JSON.stringify(AppState.agents));
    localStorage.setItem('tools', JSON.stringify(AppState.tools));
    localStorage.setItem('tasks', JSON.stringify(AppState.tasks));
    localStorage.setItem('memory', JSON.stringify(AppState.memory));
    localStorage.setItem('terminalHistory', JSON.stringify(AppState.terminalHistory));
    localStorage.setItem('theme', AppState.theme);
    localStorage.setItem('language', AppState.language);
    localStorage.setItem('darkMode', AppState.settings.darkMode);
}

// Initialize Sections
function initSections() {
    // Hide all sections except the active one
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show the current section
    const currentSection = document.getElementById(AppState.currentSection);
    if (currentSection) {
        currentSection.classList.add('active');
    }
}

// Show Section
function showSection(sectionName) {
    AppState.currentSection = sectionName;
    
    // Update nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.parentElement.classList.remove('active');
        if (link.getAttribute('data-section') === sectionName) {
            link.parentElement.classList.add('active');
        }
    });
    
    // Update sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show the selected section
    const selectedSection = document.getElementById(sectionName);
    if (selectedSection) {
        selectedSection.classList.add('active');
    }
    
    // Scroll to top
    DOM.mainContent.scrollTop = 0;
    
    // Load section-specific data
    switch (sectionName) {
        case 'agents':
            updateAgentsList();
            break;
        case 'tools':
            updateToolsList();
            break;
        case 'tasks':
            updateTasksList();
            break;
        case 'memory':
            updateMemoryList();
            break;
        case 'terminal':
            DOM.terminalInput.focus();
            break;
        case 'analytics':
            updateAnalytics();
            break;
    }
}

// Toggle Sidebar
function toggleSidebar() {
    DOM.sidebar.classList.toggle('show');
}

// Handle Resize
function handleResize() {
    if (window.innerWidth > 1024) {
        DOM.sidebar.classList.remove('show');
    }
}

// Set Theme
function setTheme(theme) {
    AppState.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// Toggle Dark Mode
function toggleDarkMode() {
    AppState.settings.darkMode = !AppState.settings.darkMode;
    setTheme(AppState.settings.darkMode ? 'dark' : 'light');
    saveData();
    showToast(AppState.settings.darkMode ? 'Dark mode enabled' : 'Dark mode disabled', 'info');
}

// Focus Search
function focusSearch() {
    const currentSection = AppState.currentSection;
    let searchInput = null;
    
    switch (currentSection) {
        case 'agents':
            searchInput = document.getElementById('agentSearch');
            break;
        case 'tools':
            searchInput = document.getElementById('toolSearch');
            break;
        case 'tasks':
            searchInput = document.getElementById('taskSearch');
            break;
        case 'memory':
            searchInput = document.getElementById('memorySearch');
            break;
        case 'documentation':
            searchInput = document.getElementById('docSearch');
            break;
    }
    
    if (searchInput) {
        searchInput.focus();
    }
}

// Show Toast
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconMap = {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info'
    };
    
    toast.innerHTML = `
        <span class="material-icons">${iconMap[type] || 'info'}</span>
        <span>${message}</span>
    `;
    
    DOM.toastContainer.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Show Modal
function showModal(title, content, showFooter = true, confirmText = 'Confirm', cancelText = 'Cancel') {
    DOM.modalTitle.textContent = title;
    DOM.modalContent.innerHTML = content;
    
    if (showFooter) {
        DOM.modalFooter.innerHTML = `
            <button class="btn-secondary" onclick="closeModal()">${cancelText}</button>
            <button class="btn-primary" onclick="confirmModal()">${confirmText}</button>
        `;
        DOM.modalFooter.style.display = 'flex';
    } else {
        DOM.modalFooter.style.display = 'none';
    }
    
    DOM.modalOverlay.classList.add('show');
    DOM.modal.classList.add('show');
}

// Close Modal
function closeModal() {
    DOM.modalOverlay.classList.remove('show');
    DOM.modal.classList.remove('show');
}

// Confirm Modal
function confirmModal() {
    // To be overridden by specific modal handlers
    closeModal();
}

// Show Loading
function showLoading() {
    DOM.loadingOverlay.classList.add('show');
}

// Hide Loading
function hideLoading() {
    DOM.loadingOverlay.classList.remove('show');
}

// ==================== DASHBOARD ====================

// Update Dashboard
function updateDashboard() {
    // Update stats
    document.getElementById('totalAgents').textContent = AppState.agents.length;
    document.getElementById('totalTools').textContent = AppState.tools.length;
    document.getElementById('totalTasks').textContent = AppState.tasks.length;
    
    // Calculate memory usage
    const totalMemory = AppState.memory.length * 100; // Example calculation
    const memoryPercentage = Math.min(totalMemory, 100);
    document.getElementById('memoryUsage').textContent = `${memoryPercentage}%`;
    
    // Update recent activity
    updateRecentActivity();
}

// Update Recent Activity
function updateRecentActivity() {
    const activityList = document.getElementById('recentActivity');
    const activities = [];
    
    // Add recent agents
    AppState.agents.slice(-3).forEach(agent => {
        activities.push({
            icon: 'group',
            text: `Agent "${agent.name}" created`
        });
    });
    
    // Add recent tools
    AppState.tools.slice(-3).forEach(tool => {
        activities.push({
            icon: 'build',
            text: `Tool "${tool.name}" added`
        });
    });
    
    // Add recent tasks
    AppState.tasks.slice(-3).forEach(task => {
        activities.push({
            icon: 'assignment',
            text: `Task "${task.title}" ${task.status}`
        });
    });
    
    // Sort by date (if we had dates)
    activities.reverse();
    
    // Update UI
    if (activities.length === 0) {
        activityList.innerHTML = `
            <div class="activity-item">
                <span class="material-icons">history</span>
                <span>No recent activity</span>
            </div>
        `;
    } else {
        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <span class="material-icons">${activity.icon}</span>
                <span>${activity.text}</span>
            </div>
        `).join('');
    }
}

// ==================== AGENTS ====================

// Create Agent
function createAgent() {
    showModal(
        'Create New Agent',
        `
            <div class="form-group">
                <label for="agentName">Agent Name</label>
                <input type="text" id="agentName" placeholder="Enter agent name">
            </div>
            <div class="form-group">
                <label for="agentType">Agent Type</label>
                <select id="agentType">
                    <option value="general">General</option>
                    <option value="specialized">Specialized</option>
                    <option value="system">System</option>
                </select>
            </div>
            <div class="form-group">
                <label for="agentDescription">Description</label>
                <textarea id="agentDescription" placeholder="Describe the agent's purpose"></textarea>
            </div>
        `,
        true,
        'Create',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        const name = document.getElementById('agentName').value;
        const type = document.getElementById('agentType').value;
        const description = document.getElementById('agentDescription').value;
        
        if (!name) {
            showToast('Please enter an agent name', 'error');
            return;
        }
        
        const newAgent = {
            id: Date.now().toString(),
            name,
            type,
            description,
            status: 'active',
            createdAt: new Date().toISOString()
        };
        
        AppState.agents.push(newAgent);
        saveData();
        updateAgentsList();
        updateDashboard();
        closeModal();
        showToast(`Agent "${name}" created successfully!`, 'success');
    };
}

// Update Agents List
function updateAgentsList() {
    const agentsGrid = document.getElementById('agentsGrid');
    const filteredAgents = filterAgents();
    
    if (filteredAgents.length === 0) {
        agentsGrid.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">group_off</span>
                <h3>No agents available</h3>
                <p>Create your first agent to get started</p>
                <button class="btn-primary" onclick="createAgent()">
                    <span class="material-icons">add</span>
                    <span>Create Agent</span>
                </button>
            </div>
        `;
    } else {
        agentsGrid.innerHTML = filteredAgents.map(agent => `
            <div class="agent-card">
                <div class="agent-header">
                    <div class="agent-icon">
                        <span class="material-icons">group</span>
                    </div>
                    <div class="agent-info">
                        <h4>${agent.name}</h4>
                        <span class="agent-type">${agent.type}</span>
                    </div>
                </div>
                <div class="agent-description">
                    <p>${agent.description || 'No description'}</p>
                </div>
                <div class="agent-status">
                    <span class="status-badge ${agent.status}">${agent.status}</span>
                </div>
                <div class="agent-actions">
                    <button class="action-btn" onclick="startAgent('${agent.id}')" title="Start">
                        <span class="material-icons">play_arrow</span>
                    </button>
                    <button class="action-btn" onclick="stopAgent('${agent.id}')" title="Stop">
                        <span class="material-icons">stop</span>
                    </button>
                    <button class="action-btn" onclick="editAgent('${agent.id}')" title="Edit">
                        <span class="material-icons">edit</span>
                    </button>
                    <button class="action-btn" onclick="deleteAgent('${agent.id}')" title="Delete">
                        <span class="material-icons">delete</span>
                    </button>
                </div>
            </div>
        `).join('');
    }
}

// Filter Agents
function filterAgents(filter = 'all') {
    const searchTerm = document.getElementById('agentSearch')?.value?.toLowerCase() || '';
    
    return AppState.agents.filter(agent => {
        const matchesSearch = agent.name.toLowerCase().includes(searchTerm) ||
                            agent.description?.toLowerCase().includes(searchTerm);
        
        if (filter === 'all') return matchesSearch;
        if (filter === 'active') return matchesSearch && agent.status === 'active';
        if (filter === 'inactive') return matchesSearch && agent.status === 'inactive';
        if (filter === 'system') return matchesSearch && agent.type === 'system';
        if (filter === 'custom') return matchesSearch && agent.type !== 'system';
        
        return matchesSearch;
    });
}

// Start Agent
function startAgent(agentId) {
    const agent = AppState.agents.find(a => a.id === agentId);
    if (agent) {
        agent.status = 'active';
        saveData();
        updateAgentsList();
        showToast(`Agent "${agent.name}" started`, 'success');
    }
}

// Stop Agent
function stopAgent(agentId) {
    const agent = AppState.agents.find(a => a.id === agentId);
    if (agent) {
        agent.status = 'inactive';
        saveData();
        updateAgentsList();
        showToast(`Agent "${agent.name}" stopped`, 'success');
    }
}

// Edit Agent
function editAgent(agentId) {
    const agent = AppState.agents.find(a => a.id === agentId);
    if (!agent) return;
    
    showModal(
        `Edit Agent: ${agent.name}`,
        `
            <div class="form-group">
                <label for="editAgentName">Agent Name</label>
                <input type="text" id="editAgentName" value="${agent.name}">
            </div>
            <div class="form-group">
                <label for="editAgentType">Agent Type</label>
                <select id="editAgentType">
                    <option value="general" ${agent.type === 'general' ? 'selected' : ''}>General</option>
                    <option value="specialized" ${agent.type === 'specialized' ? 'selected' : ''}>Specialized</option>
                    <option value="system" ${agent.type === 'system' ? 'selected' : ''}>System</option>
                </select>
            </div>
            <div class="form-group">
                <label for="editAgentDescription">Description</label>
                <textarea id="editAgentDescription">${agent.description || ''}</textarea>
            </div>
            <div class="form-group">
                <label for="editAgentStatus">Status</label>
                <select id="editAgentStatus">
                    <option value="active" ${agent.status === 'active' ? 'selected' : ''}>Active</option>
                    <option value="inactive" ${agent.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                </select>
            </div>
        `,
        true,
        'Save',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        const name = document.getElementById('editAgentName').value;
        const type = document.getElementById('editAgentType').value;
        const description = document.getElementById('editAgentDescription').value;
        const status = document.getElementById('editAgentStatus').value;
        
        if (!name) {
            showToast('Please enter an agent name', 'error');
            return;
        }
        
        agent.name = name;
        agent.type = type;
        agent.description = description;
        agent.status = status;
        
        saveData();
        updateAgentsList();
        closeModal();
        showToast(`Agent "${name}" updated successfully!`, 'success');
    };
}

// Delete Agent
function deleteAgent(agentId) {
    const agent = AppState.agents.find(a => a.id === agentId);
    if (!agent) return;
    
    showModal(
        'Delete Agent',
        `Are you sure you want to delete agent "${agent.name}"? This action cannot be undone.`,
        true,
        'Delete',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        AppState.agents = AppState.agents.filter(a => a.id !== agentId);
        saveData();
        updateAgentsList();
        updateDashboard();
        closeModal();
        showToast(`Agent "${agent.name}" deleted`, 'success');
    };
}

// ==================== TOOLS ====================

// Create Tool
function createTool() {
    showModal(
        'Create New Tool',
        `
            <div class="form-group">
                <label for="toolName">Tool Name</label>
                <input type="text" id="toolName" placeholder="Enter tool name">
            </div>
            <div class="form-group">
                <label for="toolCategory">Category</label>
                <select id="toolCategory">
                    <option value="ai">AI</option>
                    <option value="data">Data</option>
                    <option value="automation">Automation</option>
                    <option value="utility">Utility</option>
                </select>
            </div>
            <div class="form-group">
                <label for="toolDescription">Description</label>
                <textarea id="toolDescription" placeholder="Describe what the tool does"></textarea>
            </div>
            <div class="form-group">
                <label for="toolVersion">Version</label>
                <input type="text" id="toolVersion" value="1.0.0">
            </div>
        `,
        true,
        'Create',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        const name = document.getElementById('toolName').value;
        const category = document.getElementById('toolCategory').value;
        const description = document.getElementById('toolDescription').value;
        const version = document.getElementById('toolVersion').value;
        
        if (!name) {
            showToast('Please enter a tool name', 'error');
            return;
        }
        
        const newTool = {
            id: Date.now().toString(),
            name,
            category,
            description,
            version,
            enabled: true,
            createdAt: new Date().toISOString()
        };
        
        AppState.tools.push(newTool);
        saveData();
        updateToolsList();
        updateDashboard();
        closeModal();
        showToast(`Tool "${name}" created successfully!`, 'success');
    };
}

// Update Tools List
function updateToolsList() {
    const toolsGrid = document.getElementById('toolsGrid');
    const filteredTools = filterTools();
    
    if (filteredTools.length === 0) {
        toolsGrid.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">build</span>
                <h3>No tools available</h3>
                <p>Add tools to enhance your LivingAI experience</p>
                <button class="btn-primary" onclick="createTool()">
                    <span class="material-icons">add</span>
                    <span>Add Tool</span>
                </button>
            </div>
        `;
    } else {
        toolsGrid.innerHTML = filteredTools.map(tool => `
            <div class="tool-card">
                <div class="tool-header">
                    <div class="tool-icon">
                        <span class="material-icons">build</span>
                    </div>
                    <div class="tool-info">
                        <h4>${tool.name}</h4>
                        <span class="tool-category">${tool.category}</span>
                    </div>
                </div>
                <div class="tool-description">
                    <p>${tool.description || 'No description'}</p>
                </div>
                <div class="tool-meta">
                    <span class="tool-version">v${tool.version}</span>
                    <span class="tool-status">${tool.enabled ? 'Enabled' : 'Disabled'}</span>
                </div>
                <div class="tool-actions">
                    <button class="action-btn" onclick="toggleTool('${tool.id}')" title="Toggle">
                        <span class="material-icons">${tool.enabled ? 'toggle_on' : 'toggle_off'}</span>
                    </button>
                    <button class="action-btn" onclick="editTool('${tool.id}')" title="Edit">
                        <span class="material-icons">edit</span>
                    </button>
                    <button class="action-btn" onclick="deleteTool('${tool.id}')" title="Delete">
                        <span class="material-icons">delete</span>
                    </button>
                </div>
            </div>
        `).join('');
    }
}

// Filter Tools
function filterTools(filter = 'all') {
    const searchTerm = document.getElementById('toolSearch')?.value?.toLowerCase() || '';
    
    return AppState.tools.filter(tool => {
        const matchesSearch = tool.name.toLowerCase().includes(searchTerm) ||
                            tool.description?.toLowerCase().includes(searchTerm) ||
                            tool.category.toLowerCase().includes(searchTerm);
        
        if (filter === 'all') return matchesSearch;
        if (filter === tool.category) return matchesSearch;
        
        return matchesSearch;
    });
}

// Toggle Tool
function toggleTool(toolId) {
    const tool = AppState.tools.find(t => t.id === toolId);
    if (tool) {
        tool.enabled = !tool.enabled;
        saveData();
        updateToolsList();
        showToast(`Tool "${tool.name}" ${tool.enabled ? 'enabled' : 'disabled'}`, 'success');
    }
}

// Edit Tool
function editTool(toolId) {
    const tool = AppState.tools.find(t => t.id === toolId);
    if (!tool) return;
    
    showModal(
        `Edit Tool: ${tool.name}`,
        `
            <div class="form-group">
                <label for="editToolName">Tool Name</label>
                <input type="text" id="editToolName" value="${tool.name}">
            </div>
            <div class="form-group">
                <label for="editToolCategory">Category</label>
                <select id="editToolCategory">
                    <option value="ai" ${tool.category === 'ai' ? 'selected' : ''}>AI</option>
                    <option value="data" ${tool.category === 'data' ? 'selected' : ''}>Data</option>
                    <option value="automation" ${tool.category === 'automation' ? 'selected' : ''}>Automation</option>
                    <option value="utility" ${tool.category === 'utility' ? 'selected' : ''}>Utility</option>
                </select>
            </div>
            <div class="form-group">
                <label for="editToolDescription">Description</label>
                <textarea id="editToolDescription">${tool.description || ''}</textarea>
            </div>
            <div class="form-group">
                <label for="editToolVersion">Version</label>
                <input type="text" id="editToolVersion" value="${tool.version}">
            </div>
            <div class="form-group">
                <label for="editToolEnabled">Enabled</label>
                <select id="editToolEnabled">
                    <option value="true" ${tool.enabled ? 'selected' : ''}>Enabled</option>
                    <option value="false" ${!tool.enabled ? 'selected' : ''}>Disabled</option>
                </select>
            </div>
        `,
        true,
        'Save',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        const name = document.getElementById('editToolName').value;
        const category = document.getElementById('editToolCategory').value;
        const description = document.getElementById('editToolDescription').value;
        const version = document.getElementById('editToolVersion').value;
        const enabled = document.getElementById('editToolEnabled').value === 'true';
        
        if (!name) {
            showToast('Please enter a tool name', 'error');
            return;
        }
        
        tool.name = name;
        tool.category = category;
        tool.description = description;
        tool.version = version;
        tool.enabled = enabled;
        
        saveData();
        updateToolsList();
        closeModal();
        showToast(`Tool "${name}" updated successfully!`, 'success');
    };
}

// Delete Tool
function deleteTool(toolId) {
    const tool = AppState.tools.find(t => t.id === toolId);
    if (!tool) return;
    
    showModal(
        'Delete Tool',
        `Are you sure you want to delete tool "${tool.name}"? This action cannot be undone.`,
        true,
        'Delete',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        AppState.tools = AppState.tools.filter(t => t.id !== toolId);
        saveData();
        updateToolsList();
        updateDashboard();
        closeModal();
        showToast(`Tool "${tool.name}" deleted`, 'success');
    };
}

// ==================== TASKS ====================

// Create Task
function createTask() {
    showModal(
        'Create New Task',
        `
            <div class="form-group">
                <label for="taskTitle">Title</label>
                <input type="text" id="taskTitle" placeholder="Enter task title">
            </div>
            <div class="form-group">
                <label for="taskDescription">Description</label>
                <textarea id="taskDescription" placeholder="Describe the task"></textarea>
            </div>
            <div class="form-group">
                <label for="taskPriority">Priority</label>
                <select id="taskPriority">
                    <option value="low">Low</option>
                    <option value="medium" selected>Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                </select>
            </div>
            <div class="form-group">
                <label for="taskDeadline">Deadline</label>
                <input type="datetime-local" id="taskDeadline">
            </div>
        `,
        true,
        'Create',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        const title = document.getElementById('taskTitle').value;
        const description = document.getElementById('taskDescription').value;
        const priority = document.getElementById('taskPriority').value;
        const deadline = document.getElementById('taskDeadline').value;
        
        if (!title) {
            showToast('Please enter a task title', 'error');
            return;
        }
        
        const newTask = {
            id: Date.now().toString(),
            title,
            description,
            priority,
            deadline: deadline || null,
            status: 'pending',
            createdAt: new Date().toISOString()
        };
        
        AppState.tasks.push(newTask);
        saveData();
        updateTasksList();
        updateDashboard();
        closeModal();
        showToast(`Task "${title}" created successfully!`, 'success');
    };
}

// Update Tasks List
function updateTasksList() {
    const tasksList = document.getElementById('tasksList');
    const filteredTasks = filterTasks();
    
    // Update stats
    const totalTasks = filteredTasks.length;
    const completedTasks = filteredTasks.filter(t => t.status === 'completed').length;
    const pendingTasks = filteredTasks.filter(t => t.status === 'pending').length;
    const failedTasks = filteredTasks.filter(t => t.status === 'failed').length;
    
    document.getElementById('totalTasksCount').textContent = totalTasks;
    document.getElementById('completedTasksCount').textContent = completedTasks;
    document.getElementById('pendingTasksCount').textContent = pendingTasks;
    document.getElementById('failedTasksCount').textContent = failedTasks;
    
    if (filteredTasks.length === 0) {
        tasksList.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">assignment_late</span>
                <h3>No tasks available</h3>
                <p>Create your first task to get started</p>
                <button class="btn-primary" onclick="createTask()">
                    <span class="material-icons">add</span>
                    <span>Create Task</span>
                </button>
            </div>
        `;
    } else {
        tasksList.innerHTML = filteredTasks.map(task => `
            <div class="task-card">
                <div class="task-header">
                    <div class="task-priority ${task.priority}">
                        <span>${task.priority}</span>
                    </div>
                    <div class="task-info">
                        <h4>${task.title}</h4>
                        <p>${task.description || 'No description'}</p>
                    </div>
                </div>
                <div class="task-meta">
                    <span class="task-deadline">${task.deadline ? new Date(task.deadline).toLocaleDateString() : 'No deadline'}</span>
                    <span class="task-status ${task.status}">${task.status}</span>
                </div>
                <div class="task-actions">
                    <button class="action-btn" onclick="startTask('${task.id}')" title="Start">
                        <span class="material-icons">play_arrow</span>
                    </button>
                    <button class="action-btn" onclick="editTask('${task.id}')" title="Edit">
                        <span class="material-icons">edit</span>
                    </button>
                    <button class="action-btn" onclick="deleteTask('${task.id}')" title="Delete">
                        <span class="material-icons">delete</span>
                    </button>
                </div>
            </div>
        `).join('');
    }
}

// Filter Tasks
function filterTasks() {
    const searchTerm = document.getElementById('taskSearch')?.value?.toLowerCase() || '';
    
    return AppState.tasks.filter(task => {
        const matchesSearch = task.title.toLowerCase().includes(searchTerm) ||
                            task.description?.toLowerCase().includes(searchTerm) ||
                            task.priority.toLowerCase().includes(searchTerm) ||
                            task.status.toLowerCase().includes(searchTerm);
        
        return matchesSearch;
    });
}

// Start Task
function startTask(taskId) {
    const task = AppState.tasks.find(t => t.id === taskId);
    if (task) {
        task.status = 'in_progress';
        saveData();
        updateTasksList();
        showToast(`Task "${task.title}" started`, 'success');
    }
}

// Edit Task
function editTask(taskId) {
    const task = AppState.tasks.find(t => t.id === taskId);
    if (!task) return;
    
    showModal(
        `Edit Task: ${task.title}`,
        `
            <div class="form-group">
                <label for="editTaskTitle">Title</label>
                <input type="text" id="editTaskTitle" value="${task.title}">
            </div>
            <div class="form-group">
                <label for="editTaskDescription">Description</label>
                <textarea id="editTaskDescription">${task.description || ''}</textarea>
            </div>
            <div class="form-group">
                <label for="editTaskPriority">Priority</label>
                <select id="editTaskPriority">
                    <option value="low" ${task.priority === 'low' ? 'selected' : ''}>Low</option>
                    <option value="medium" ${task.priority === 'medium' ? 'selected' : ''}>Medium</option>
                    <option value="high" ${task.priority === 'high' ? 'selected' : ''}>High</option>
                    <option value="urgent" ${task.priority === 'urgent' ? 'selected' : ''}>Urgent</option>
                </select>
            </div>
            <div class="form-group">
                <label for="editTaskStatus">Status</label>
                <select id="editTaskStatus">
                    <option value="pending" ${task.status === 'pending' ? 'selected' : ''}>Pending</option>
                    <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                    <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>Completed</option>
                    <option value="failed" ${task.status === 'failed' ? 'selected' : ''}>Failed</option>
                </select>
            </div>
        `,
        true,
        'Save',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        const title = document.getElementById('editTaskTitle').value;
        const description = document.getElementById('editTaskDescription').value;
        const priority = document.getElementById('editTaskPriority').value;
        const status = document.getElementById('editTaskStatus').value;
        
        if (!title) {
            showToast('Please enter a task title', 'error');
            return;
        }
        
        task.title = title;
        task.description = description;
        task.priority = priority;
        task.status = status;
        
        saveData();
        updateTasksList();
        closeModal();
        showToast(`Task "${title}" updated successfully!`, 'success');
    };
}

// Delete Task
function deleteTask(taskId) {
    const task = AppState.tasks.find(t => t.id === taskId);
    if (!task) return;
    
    showModal(
        'Delete Task',
        `Are you sure you want to delete task "${task.title}"? This action cannot be undone.`,
        true,
        'Delete',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        AppState.tasks = AppState.tasks.filter(t => t.id !== taskId);
        saveData();
        updateTasksList();
        updateDashboard();
        closeModal();
        showToast(`Task "${task.title}" deleted`, 'success');
    };
}

// ==================== MEMORY ====================

// Update Memory List
function updateMemoryList() {
    const memoryList = document.getElementById('memoryList');
    const filteredMemory = filterMemory();
    
    // Update memory stats
    const memoryPercentage = Math.min(filteredMemory.length * 10, 100);
    document.getElementById('memoryFill').style.width = `${memoryPercentage}%`;
    document.getElementById('memoryPercentage').textContent = `${memoryPercentage}%`;
    document.getElementById('memoryEntries').textContent = `${filteredMemory.length} entries`;
    
    if (filteredMemory.length === 0) {
        memoryList.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">memory</span>
                <h3>No memory entries</h3>
                <p>Memory will be stored here automatically</p>
            </div>
        `;
    } else {
        memoryList.innerHTML = filteredMemory.map(memory => `
            <div class="memory-card">
                <div class="memory-header">
                    <div class="memory-icon">
                        <span class="material-icons">memory</span>
                    </div>
                    <div class="memory-info">
                        <h4>${memory.type || 'Unknown'}</h4>
                        <span class="memory-timestamp">${new Date(memory.timestamp).toLocaleString()}</span>
                    </div>
                </div>
                <div class="memory-content">
                    <p>${memory.content || 'No content'}</p>
                </div>
                <div class="memory-actions">
                    <button class="action-btn" onclick="editMemory('${memory.id}')" title="Edit">
                        <span class="material-icons">edit</span>
                    </button>
                    <button class="action-btn" onclick="deleteMemory('${memory.id}')" title="Delete">
                        <span class="material-icons">delete</span>
                    </button>
                </div>
            </div>
        `).join('');
    }
}

// Filter Memory
function filterMemory(filter = 'all') {
    const searchTerm = document.getElementById('memorySearch')?.value?.toLowerCase() || '';
    
    return AppState.memory.filter(memory => {
        const matchesSearch = memory.type?.toLowerCase().includes(searchTerm) ||
                            memory.content?.toLowerCase().includes(searchTerm);
        
        if (filter === 'all') return matchesSearch;
        if (filter === memory.type) return matchesSearch;
        
        return matchesSearch;
    });
}

// Backup Memory
function backupMemory() {
    showToast('Memory backup initiated', 'info');
    // In a real app, this would call an API to backup memory
    setTimeout(() => {
        showToast('Memory backup completed successfully!', 'success');
    }, 2000);
}

// Clear Memory
function clearMemory() {
    showModal(
        'Clear Memory',
        'Are you sure you want to clear all memory? This action cannot be undone.',
        true,
        'Clear All',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        AppState.memory = [];
        saveData();
        updateMemoryList();
        closeModal();
        showToast('All memory cleared', 'success');
    };
}

// Add Memory
function addMemory() {
    showModal(
        'Add Memory Entry',
        `
            <div class="form-group">
                <label for="memoryType">Type</label>
                <select id="memoryType">
                    <option value="conversation">Conversation</option>
                    <option value="knowledge">Knowledge</option>
                    <option value="preference">Preference</option>
                    <option value="context">Context</option>
                </select>
            </div>
            <div class="form-group">
                <label for="memoryContent">Content</label>
                <textarea id="memoryContent" placeholder="Enter memory content"></textarea>
            </div>
        `,
        true,
        'Add',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        const type = document.getElementById('memoryType').value;
        const content = document.getElementById('memoryContent').value;
        
        if (!content) {
            showToast('Please enter memory content', 'error');
            return;
        }
        
        const newMemory = {
            id: Date.now().toString(),
            type,
            content,
            timestamp: new Date().toISOString()
        };
        
        AppState.memory.push(newMemory);
        saveData();
        updateMemoryList();
        closeModal();
        showToast('Memory entry added successfully!', 'success');
    };
}

// Edit Memory
function editMemory(memoryId) {
    const memory = AppState.memory.find(m => m.id === memoryId);
    if (!memory) return;
    
    showModal(
        `Edit Memory: ${memory.type}`,
        `
            <div class="form-group">
                <label for="editMemoryType">Type</label>
                <select id="editMemoryType">
                    <option value="conversation" ${memory.type === 'conversation' ? 'selected' : ''}>Conversation</option>
                    <option value="knowledge" ${memory.type === 'knowledge' ? 'selected' : ''}>Knowledge</option>
                    <option value="preference" ${memory.type === 'preference' ? 'selected' : ''}>Preference</option>
                    <option value="context" ${memory.type === 'context' ? 'selected' : ''}>Context</option>
                </select>
            </div>
            <div class="form-group">
                <label for="editMemoryContent">Content</label>
                <textarea id="editMemoryContent">${memory.content || ''}</textarea>
            </div>
        `,
        true,
        'Save',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        const type = document.getElementById('editMemoryType').value;
        const content = document.getElementById('editMemoryContent').value;
        
        if (!content) {
            showToast('Please enter memory content', 'error');
            return;
        }
        
        memory.type = type;
        memory.content = content;
        memory.timestamp = new Date().toISOString();
        
        saveData();
        updateMemoryList();
        closeModal();
        showToast('Memory entry updated successfully!', 'success');
    };
}

// Delete Memory
function deleteMemory(memoryId) {
    const memory = AppState.memory.find(m => m.id === memoryId);
    if (!memory) return;
    
    showModal(
        'Delete Memory',
        `Are you sure you want to delete this memory entry? This action cannot be undone.`,
        true,
        'Delete',
        'Cancel'
    );
    
    // Override confirm function
    window.confirmModal = function() {
        AppState.memory = AppState.memory.filter(m => m.id !== memoryId);
        saveData();
        updateMemoryList();
        closeModal();
        showToast('Memory entry deleted', 'success');
    };
}

// ==================== TERMINAL ====================

// Initialize Terminal
function initTerminal() {
    // Add welcome message
    addTerminalOutput('LivingAI Terminal v1.0.0', 'system');
    addTerminalOutput('Type "help" for available commands', 'system');
    
    // Focus input
    DOM.terminalInput.focus();
}

// Handle Terminal Input
function handleTerminalInput(e) {
    if (e.key === 'Enter') {
        executeCommand();
    }
}

// Execute Command
function executeCommand() {
    const input = DOM.terminalInput.value.trim();
    if (!input) return;
    
    // Add command to history
    AppState.terminalHistory.push(input);
    saveData();
    
    // Add to output
    addTerminalOutput(`livingai@terminal:~$ ${input}`, 'input');
    
    // Process command
    processCommand(input);
    
    // Clear input
    DOM.terminalInput.value = '';
    
    // Hide suggestions
    DOM.commandSuggestions.classList.remove('show');
}

// Process Command
function processCommand(command) {
    const parts = command.split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);
    
    switch (cmd) {
        case 'help':
            showHelp();
            break;
        case 'clear':
            clearTerminal();
            break;
        case 'list':
            listItems(args);
            break;
        case 'create':
            createItem(args);
            break;
        case 'delete':
            deleteItem(args);
            break;
        case 'start':
            startItem(args);
            break;
        case 'stop':
            stopItem(args);
            break;
        case 'status':
            showStatus(args);
            break;
        case 'version':
            showVersion();
            break;
        case 'exit':
        case 'quit':
            addTerminalOutput('Goodbye!', 'system');
            break;
        default:
            addTerminalOutput(`Command not found: ${command}`, 'error');
            addTerminalOutput('Type "help" for available commands', 'system');
    }
}

// Add Terminal Output
function addTerminalOutput(text, type = 'output') {
    const outputDiv = document.createElement('div');
    outputDiv.className = `terminal-line ${type}`;
    outputDiv.textContent = text;
    DOM.terminalOutput.appendChild(outputDiv);
    
    // Scroll to bottom
    DOM.terminalOutput.scrollTop = DOM.terminalOutput.scrollHeight;
}

// Clear Terminal
function clearTerminal() {
    DOM.terminalOutput.innerHTML = '';
    addTerminalOutput('Terminal cleared', 'system');
}

// Show Help
function showHelp() {
    addTerminalOutput('Available Commands:', 'header');
    addTerminalOutput('  help                    Show this help message', 'output');
    addTerminalOutput('  clear                   Clear the terminal', 'output');
    addTerminalOutput('  list agents|tools|tasks List items', 'output');
    addTerminalOutput('  create agent|tool|task  Create a new item', 'output');
    addTerminalOutput('  delete agent|tool|task  Delete an item', 'output');
    addTerminalOutput('  start agent|task       Start an item', 'output');
    addTerminalOutput('  stop agent|task        Stop an item', 'output');
    addTerminalOutput('  status                  Show system status', 'output');
    addTerminalOutput('  version                 Show version information', 'output');
    addTerminalOutput('  exit, quit              Exit the terminal', 'output');
}

// List Items
function listItems(args) {
    if (args.length === 0) {
        addTerminalOutput('Usage: list agents|tools|tasks', 'error');
        return;
    }
    
    const type = args[0].toLowerCase();
    
    switch (type) {
        case 'agents':
            addTerminalOutput(`Agents (${AppState.agents.length}):`, 'header');
            AppState.agents.forEach(agent => {
                addTerminalOutput(`  - ${agent.name} [${agent.status}]`, 'output');
            });
            break;
        case 'tools':
            addTerminalOutput(`Tools (${AppState.tools.length}):`, 'header');
            AppState.tools.forEach(tool => {
                addTerminalOutput(`  - ${tool.name} [${tool.category}]`, 'output');
            });
            break;
        case 'tasks':
            addTerminalOutput(`Tasks (${AppState.tasks.length}):`, 'header');
            AppState.tasks.forEach(task => {
                addTerminalOutput(`  - ${task.title} [${task.status}]`, 'output');
            });
            break;
        default:
            addTerminalOutput(`Unknown type: ${type}`, 'error');
            addTerminalOutput('Usage: list agents|tools|tasks', 'error');
    }
}

// Create Item
function createItem(args) {
    if (args.length === 0) {
        addTerminalOutput('Usage: create agent|tool|task [name]', 'error');
        return;
    }
    
    const type = args[0].toLowerCase();
    const name = args.slice(1).join(' ');
    
    if (!name) {
        addTerminalOutput(`Please provide a name for the ${type}`, 'error');
        return;
    }
    
    switch (type) {
        case 'agent':
            const newAgent = {
                id: Date.now().toString(),
                name,
                type: 'general',
                status: 'inactive',
                createdAt: new Date().toISOString()
            };
            AppState.agents.push(newAgent);
            saveData();
            addTerminalOutput(`Agent "${name}" created`, 'success');
            break;
        case 'tool':
            const newTool = {
                id: Date.now().toString(),
                name,
                category: 'utility',
                enabled: true,
                createdAt: new Date().toISOString()
            };
            AppState.tools.push(newTool);
            saveData();
            addTerminalOutput(`Tool "${name}" created`, 'success');
            break;
        case 'task':
            const newTask = {
                id: Date.now().toString(),
                title: name,
                status: 'pending',
                priority: 'medium',
                createdAt: new Date().toISOString()
            };
            AppState.tasks.push(newTask);
            saveData();
            addTerminalOutput(`Task "${name}" created`, 'success');
            break;
        default:
            addTerminalOutput(`Unknown type: ${type}`, 'error');
            addTerminalOutput('Usage: create agent|tool|task [name]', 'error');
    }
}

// Delete Item
function deleteItem(args) {
    if (args.length < 2) {
        addTerminalOutput('Usage: delete agent|tool|task [id|name]', 'error');
        return;
    }
    
    const type = args[0].toLowerCase();
    const identifier = args.slice(1).join(' ');
    
    switch (type) {
        case 'agent':
            const agentIndex = AppState.agents.findIndex(a => a.id === identifier || a.name === identifier);
            if (agentIndex !== -1) {
                const agentName = AppState.agents[agentIndex].name;
                AppState.agents.splice(agentIndex, 1);
                saveData();
                addTerminalOutput(`Agent "${agentName}" deleted`, 'success');
            } else {
                addTerminalOutput(`Agent not found: ${identifier}`, 'error');
            }
            break;
        case 'tool':
            const toolIndex = AppState.tools.findIndex(t => t.id === identifier || t.name === identifier);
            if (toolIndex !== -1) {
                const toolName = AppState.tools[toolIndex].name;
                AppState.tools.splice(toolIndex, 1);
                saveData();
                addTerminalOutput(`Tool "${toolName}" deleted`, 'success');
            } else {
                addTerminalOutput(`Tool not found: ${identifier}`, 'error');
            }
            break;
        case 'task':
            const taskIndex = AppState.tasks.findIndex(t => t.id === identifier || t.title === identifier);
            if (taskIndex !== -1) {
                const taskTitle = AppState.tasks[taskIndex].title;
                AppState.tasks.splice(taskIndex, 1);
                saveData();
                addTerminalOutput(`Task "${taskTitle}" deleted`, 'success');
            } else {
                addTerminalOutput(`Task not found: ${identifier}`, 'error');
            }
            break;
        default:
            addTerminalOutput(`Unknown type: ${type}`, 'error');
            addTerminalOutput('Usage: delete agent|tool|task [id|name]', 'error');
    }
}

// Start Item
function startItem(args) {
    if (args.length < 2) {
        addTerminalOutput('Usage: start agent|task [id|name]', 'error');
        return;
    }
    
    const type = args[0].toLowerCase();
    const identifier = args.slice(1).join(' ');
    
    switch (type) {
        case 'agent':
            const agent = AppState.agents.find(a => a.id === identifier || a.name === identifier);
            if (agent) {
                agent.status = 'active';
                saveData();
                addTerminalOutput(`Agent "${agent.name}" started`, 'success');
            } else {
                addTerminalOutput(`Agent not found: ${identifier}`, 'error');
            }
            break;
        case 'task':
            const task = AppState.tasks.find(t => t.id === identifier || t.title === identifier);
            if (task) {
                task.status = 'in_progress';
                saveData();
                addTerminalOutput(`Task "${task.title}" started`, 'success');
            } else {
                addTerminalOutput(`Task not found: ${identifier}`, 'error');
            }
            break;
        default:
            addTerminalOutput(`Unknown type: ${type}`, 'error');
            addTerminalOutput('Usage: start agent|task [id|name]', 'error');
    }
}

// Stop Item
function stopItem(args) {
    if (args.length < 2) {
        addTerminalOutput('Usage: stop agent|task [id|name]', 'error');
        return;
    }
    
    const type = args[0].toLowerCase();
    const identifier = args.slice(1).join(' ');
    
    switch (type) {
        case 'agent':
            const agent = AppState.agents.find(a => a.id === identifier || a.name === identifier);
            if (agent) {
                agent.status = 'inactive';
                saveData();
                addTerminalOutput(`Agent "${agent.name}" stopped`, 'success');
            } else {
                addTerminalOutput(`Agent not found: ${identifier}`, 'error');
            }
            break;
        case 'task':
            const task = AppState.tasks.find(t => t.id === identifier || t.title === identifier);
            if (task) {
                task.status = 'pending';
                saveData();
                addTerminalOutput(`Task "${task.title}" stopped`, 'success');
            } else {
                addTerminalOutput(`Task not found: ${identifier}`, 'error');
            }
            break;
        default:
            addTerminalOutput(`Unknown type: ${type}`, 'error');
            addTerminalOutput('Usage: stop agent|task [id|name]', 'error');
    }
}

// Show Status
function showStatus() {
    addTerminalOutput('System Status:', 'header');
    addTerminalOutput(`  Agents: ${AppState.agents.length} (${AppState.agents.filter(a => a.status === 'active').length} active)`, 'output');
    addTerminalOutput(`  Tools: ${AppState.tools.length} (${AppState.tools.filter(t => t.enabled).length} enabled)`, 'output');
    addTerminalOutput(`  Tasks: ${AppState.tasks.length} (${AppState.tasks.filter(t => t.status === 'completed').length} completed)`, 'output');
    addTerminalOutput(`  Memory: ${AppState.memory.length} entries`, 'output');
}

// Show Version
function showVersion() {
    addTerminalOutput('LivingAI Terminal v1.0.0', 'header');
    addTerminalOutput('Build: 2026-09-12', 'output');
    addTerminalOutput('Developer: Abdulraheem Nohari', 'output');
}

// Navigate Terminal History
function navigateTerminalHistory(direction) {
    // Not implemented - would need to track current position in history
}

// Toggle Terminal Theme
function toggleTerminalTheme() {
    // Not implemented - would toggle between light/dark terminal themes
    showToast('Terminal theme toggled', 'info');
}

// Use Suggestion
function useSuggestion(command) {
    DOM.terminalInput.value = command;
    DOM.commandSuggestions.classList.remove('show');
    DOM.terminalInput.focus();
}

// Update Terminal
function updateTerminal() {
    // Update terminal output with current state
    // This would be called when data changes
}

// ==================== ANALYTICS ====================

// Update Analytics
function updateAnalytics() {
    // This would typically fetch analytics data from a server
    // For demo purposes, we'll use mock data
    
    const dateRange = document.getElementById('dateRange').value;
    
    // Mock analytics data
    AppState.analytics = {
        sessions: Math.floor(Math.random() * 1000) + 500,
        commands: Math.floor(Math.random() * 5000) + 2000,
        avgResponseTime: Math.floor(Math.random() * 500) + 100,
        errorRate: Math.floor(Math.random() * 10)
    };
    
    // Update UI
    document.getElementById('totalSessions').textContent = AppState.analytics.sessions.toLocaleString();
    document.getElementById('totalCommands').textContent = AppState.analytics.commands.toLocaleString();
    document.getElementById('avgResponseTime').textContent = `${AppState.analytics.avgResponseTime}ms`;
    document.getElementById('errorRate').textContent = `${AppState.analytics.errorRate}%`;
    
    // Update chart
    updateAnalyticsChart();
}

// Update Analytics Chart
function updateAnalyticsChart() {
    const ctx = document.getElementById('usageChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (window.analyticsChart) {
        window.analyticsChart.destroy();
    }
    
    // Create new chart
    window.analyticsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Sessions',
                data: Array.from({length: 12}, () => Math.floor(Math.random() * 1000) + 100),
                borderColor: 'var(--color-primary)',
                backgroundColor: 'rgba(98, 0, 238, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Commands',
                data: Array.from({length: 12}, () => Math.floor(Math.random() * 5000) + 500),
                borderColor: 'var(--color-secondary)',
                backgroundColor: 'rgba(3, 218, 198, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Show Analytics Tab
function showAnalyticsTab(tab) {
    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.analytics-tab');
    tabs.forEach(tabElement => {
        tabElement.classList.remove('active');
    });
    
    // Add active class to selected tab
    const selectedTab = document.querySelector(`[onclick="showAnalyticsTab('${tab}')"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Update content based on tab
    const content = document.getElementById('analyticsContent');
    
    switch (tab) {
        case 'overview':
            content.innerHTML = `
                <div class="analytics-overview">
                    <div class="chart-container">
                        <canvas id="usageChart"></canvas>
                    </div>
                    <div class="analytics-stats">
                        <div class="analytics-stat">
                            <span class="stat-value" id="totalSessions">${AppState.analytics.sessions.toLocaleString()}</span>
                            <span class="stat-label">Total Sessions</span>
                        </div>
                        <div class="analytics-stat">
                            <span class="stat-value" id="totalCommands">${AppState.analytics.commands.toLocaleString()}</span>
                            <span class="stat-label">Total Commands</span>
                        </div>
                        <div class="analytics-stat">
                            <span class="stat-value" id="avgResponseTime">${AppState.analytics.avgResponseTime}ms</span>
                            <span class="stat-label">Avg Response Time</span>
                        </div>
                        <div class="analytics-stat">
                            <span class="stat-value" id="errorRate">${AppState.analytics.errorRate}%</span>
                            <span class="stat-label">Error Rate</span>
                        </div>
                    </div>
                </div>
            `;
            updateAnalyticsChart();
            break;
        case 'usage':
            content.innerHTML = `
                <div class="usage-analytics">
                    <h3>Usage Analytics</h3>
                    <p>Detailed usage statistics and trends.</p>
                    <div class="chart-container">
                        <canvas id="usageChart"></canvas>
                    </div>
                </div>
            `;
            updateAnalyticsChart();
            break;
        case 'performance':
            content.innerHTML = `
                <div class="performance-analytics">
                    <h3>Performance Analytics</h3>
                    <p>System performance metrics and optimization suggestions.</p>
                    <div class="performance-metrics">
                        <div class="metric-card">
                            <h4>Response Time</h4>
                            <p>Average: ${AppState.analytics.avgResponseTime}ms</p>
                        </div>
                        <div class="metric-card">
                            <h4>Error Rate</h4>
                            <p>${AppState.analytics.errorRate}%</p>
                        </div>
                        <div class="metric-card">
                            <h4>Success Rate</h4>
                            <p>${100 - AppState.analytics.errorRate}%</p>
                        </div>
                    </div>
                </div>
            `;
            break;
        case 'logs':
            content.innerHTML = `
                <div class="logs-analytics">
                    <h3>System Logs</h3>
                    <p>View and filter system logs.</p>
                    <div class="logs-list">
                        <div class="log-entry">
                            <span class="log-timestamp">2026-09-12 10:00:00</span>
                            <span class="log-level info">INFO</span>
                            <span class="log-message">Application started</span>
                        </div>
                        <div class="log-entry">
                            <span class="log-timestamp">2026-09-12 10:00:01</span>
                            <span class="log-level success">SUCCESS</span>
                            <span class="log-message">All systems operational</span>
                        </div>
                        <div class="log-entry">
                            <span class="log-timestamp">2026-09-12 10:05:00</span>
                            <span class="log-level warning">WARNING</span>
                            <span class="log-message">High memory usage detected</span>
                        </div>
                    </div>
                </div>
            `;
            break;
    }
}

// Export Analytics
function exportAnalytics() {
    showToast('Analytics export initiated', 'info');
    
    // In a real app, this would generate and download a report
    setTimeout(() => {
        showToast('Analytics report generated successfully!', 'success');
    }, 2000);
}

// ==================== DOCUMENTATION ====================

// Show Documentation Category
function showDocCategory(category) {
    const content = document.getElementById('docContent');
    
    const documentation = {
        'getting-started': {
            title: 'Getting Started',
            content: `
                <h3>Getting Started with LivingAI</h3>
                <p>Welcome to LivingAI! This guide will help you get started with the platform.</p>
                
                <h4>Installation</h4>
                <p>To install LivingAI, follow these steps:</p>
                <ol>
                    <li>Download the latest version from GitHub</li>
                    <li>Install the required dependencies</li>
                    <li>Configure the application</li>
                    <li>Start the service</li>
                </ol>
                
                <h4>First Steps</h4>
                <p>Once installed, you can:</p>
                <ul>
                    <li>Create your first agent</li>
                    <li>Add tools to your collection</li>
                    <li>Set up tasks</li>
                    <li>Explore the terminal</li>
                </ul>
            `
        },
        'agents': {
            title: 'Agents',
            content: `
                <h3>Working with Agents</h3>
                <p>Agents are the core components of LivingAI that perform intelligent tasks.</p>
                
                <h4>Creating Agents</h4>
                <p>To create a new agent:</p>
                <ol>
                    <li>Click the "Create Agent" button</li>
                    <li>Provide a name and description</li>
                    <li>Select the agent type</li>
                    <li>Configure agent settings</li>
                    <li>Start the agent</li>
                </ol>
                
                <h4>Agent Types</h4>
                <ul>
                    <li><strong>General:</strong> Multi-purpose agents for various tasks</li>
                    <li><strong>Specialized:</strong> Agents designed for specific domains</li>
                    <li><strong>System:</strong> Built-in agents for system operations</li>
                </ul>
            `
        },
        'tools': {
            title: 'Tools',
            content: `
                <h3>Using Tools</h3>
                <p>Tools extend the capabilities of LivingAI by providing specialized functions.</p>
                
                <h4>Tool Categories</h4>
                <ul>
                    <li><strong>AI:</strong> Artificial intelligence and machine learning tools</li>
                    <li><strong>Data:</strong> Data processing and analysis tools</li>
                    <li><strong>Automation:</strong> Workflow automation tools</li>
                    <li><strong>Utility:</strong> General utility tools</li>
                </ul>
                
                <h4>Adding Tools</h4>
                <p>To add a new tool:</p>
                <ol>
                    <li>Click the "Create Tool" button</li>
                    <li>Provide tool details</li>
                    <li>Configure tool settings</li>
                    <li>Enable the tool</li>
                </ol>
            `
        },
        'tasks': {
            title: 'Tasks',
            content: `
                <h3>Managing Tasks</h3>
                <p>Tasks allow you to organize and track work that needs to be done.</p>
                
                <h4>Creating Tasks</h4>
                <p>To create a new task:</p>
                <ol>
                    <li>Click the "Create Task" button</li>
                    <li>Provide a title and description</li>
                    <li>Set priority and deadline</li>
                    <li>Assign the task to an agent</li>
                </ol>
                
                <h4>Task Priorities</h4>
                <ul>
                    <li><strong>Low:</strong> Non-urgent tasks</li>
                    <li><strong>Medium:</strong> Standard priority tasks</li>
                    <li><strong>High:</strong> Important tasks</li>
                    <li><strong>Urgent:</strong> Critical tasks requiring immediate attention</li>
                </ul>
            `
        },
        'memory': {
            title: 'Memory',
            content: `
                <h3>Understanding Memory</h3>
                <p>Memory allows LivingAI to remember and recall information across sessions.</p>
                
                <h4>Memory Types</h4>
                <ul>
                    <li><strong>Conversation:</strong> Chat and interaction history</li>
                    <li><strong>Knowledge:</strong> Learned information and facts</li>
                    <li><strong>Preference:</strong> User preferences and settings</li>
                    <li><strong>Context:</strong> Session context and state</li>
                </ul>
                
                <h4>Memory Management</h4>
                <p>You can:</p>
                <ul>
                    <li>View memory entries</li>
                    <li>Search through memory</li>
                    <li>Backup memory data</li>
                    <li>Clear memory when needed</li>
                </ul>
            `
        },
        'api': {
            title: 'API Reference',
            content: `
                <h3>LivingAI API Reference</h3>
                <p>Interact with LivingAI programmatically using our REST API.</p>
                
                <h4>Base URL</h4>
                <p><code>https://api.livingai.com/v1</code></p>
                
                <h4>Authentication</h4>
                <p>All API requests require authentication using an API key.</p>
                <p><code>Authorization: Bearer YOUR_API_KEY</code></p>
                
                <h4>Endpoints</h4>
                <table>
                    <tr>
                        <th>Method</th>
                        <th>Endpoint</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>GET</td>
                        <td>/agents</td>
                        <td>List all agents</td>
                    </tr>
                    <tr>
                        <td>POST</td>
                        <td>/agents</td>
                        <td>Create a new agent</td>
                    </tr>
                    <tr>
                        <td>GET</td>
                        <td>/tools</td>
                        <td>List all tools</td>
                    </tr>
                    <tr>
                        <td>POST</td>
                        <td>/tasks</td>
                        <td>Create a new task</td>
                    </tr>
                </table>
            `
        }
    };
    
    const doc = documentation[category] || documentation['getting-started'];
    content.innerHTML = `
        <div class="doc-article">
            ${doc.content}
        </div>
    `;
}

// ==================== SETTINGS ====================

// Show Settings Tab
function showSettingsTab(tab) {
    // Hide all settings sections
    const sections = document.querySelectorAll('.settings-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.settings-tab');
    tabs.forEach(tabElement => {
        tabElement.classList.remove('active');
    });
    
    // Show selected section
    const selectedSection = document.getElementById(`${tab}Settings`);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
    
    // Add active class to selected tab
    const selectedTab = document.querySelector(`[onclick="showSettingsTab('${tab}')"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
}

// Toggle Dark Mode
function toggleDarkModeSetting() {
    AppState.settings.darkMode = !AppState.settings.darkMode;
    setTheme(AppState.settings.darkMode ? 'dark' : 'light');
    saveData();
}

// Change Language
function changeLanguage() {
    const language = document.getElementById('languageSelect').value;
    AppState.language = language;
    saveData();
    showToast(`Language changed to ${language}`, 'info');
}

// Toggle Auto Update
function toggleAutoUpdate() {
    AppState.settings.autoUpdate = !AppState.settings.autoUpdate;
    saveData();
}

// Toggle Data Sync
function toggleDataSync() {
    AppState.settings.dataSync = !AppState.settings.dataSync;
    saveData();
}

// Save Settings
function saveSettings() {
    saveData();
    showToast('Settings saved successfully!', 'success');
}

// ==================== ABOUT ====================

// Show Privacy Policy
function showPrivacyPolicy() {
    showModal(
        'Privacy Policy',
        `
            <div class="policy-content">
                <h4>Privacy Policy</h4>
                <p>This Privacy Policy describes how LivingAI collects, uses, and discloses your information.</p>
                
                <h4>Information We Collect</h4>
                <p>We may collect information you provide directly to us, such as when you create an account, use our services, or communicate with us.</p>
                
                <h4>How We Use Your Information</h4>
                <p>We use the information we collect to provide, maintain, and improve our services, and to respond to your requests.</p>
                
                <h4>Information Sharing</h4>
                <p>We do not share your personal information with third parties except as described in this policy.</p>
                
                <h4>Security</h4>
                <p>We take reasonable measures to help protect your personal information from loss, theft, misuse, and unauthorized access.</p>
                
                <p><em>Last updated: September 12, 2026</em></p>
            </div>
        `,
        false
    );
}

// Show Terms of Service
function showTermsOfService() {
    showModal(
        'Terms of Service',
        `
            <div class="policy-content">
                <h4>Terms of Service</h4>
                <p>These Terms of Service govern your use of LivingAI services.</p>
                
                <h4>Acceptance of Terms</h4>
                <p>By using LivingAI, you agree to be bound by these Terms of Service.</p>
                
                <h4>Description of Service</h4>
                <p>LivingAI provides an intelligent assistant platform with various features and tools.</p>
                
                <h4>User Responsibilities</h4>
                <p>You are responsible for maintaining the confidentiality of your account and for all activities that occur under your account.</p>
                
                <h4>Termination</h4>
                <p>We may terminate or suspend your account at any time for any reason.</p>
                
                <h4>Disclaimer</h4>
                <p>The services are provided "as is" without warranty of any kind.</p>
                
                <p><em>Last updated: September 12, 2026</em></p>
            </div>
        `,
        false
    );
}

// Show License
function showLicense() {
    showModal(
        'Open Source License',
        `
            <div class="policy-content">
                <h4>MIT License</h4>
                <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>
                
                <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>
                
                <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>
            </div>
        `,
        false
    );
}

// ==================== UTILITY FUNCTIONS ====================

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format time
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// ==================== INITIALIZATION ====================

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

// Export functions for global access
window.createAgent = createAgent;
window.createTool = createTool;
window.createTask = createTask;
window.filterAgents = filterAgents;
window.filterTools = filterTools;
window.filterMemory = filterMemory;
window.updateAgentsList = updateAgentsList;
window.updateToolsList = updateToolsList;
window.updateTasksList = updateTasksList;
window.updateMemoryList = updateMemoryList;
window.showSection = showSection;
window.toggleDarkMode = toggleDarkMode;
window.toggleSidebar = toggleSidebar;
window.closeModal = closeModal;
window.showToast = showToast;
window.showAnalyticsTab = showAnalyticsTab;
window.updateAnalytics = updateAnalytics;
window.showSettingsTab = showSettingsTab;
window.showDocCategory = showDocCategory;
window.showPrivacyPolicy = showPrivacyPolicy;
window.showTermsOfService = showTermsOfService;
window.showLicense = showLicense;
window.handleTerminalInput = handleTerminalInput;
window.executeCommand = executeCommand;
window.clearTerminal = clearTerminal;
window.useSuggestion = useSuggestion;
