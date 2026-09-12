/**
 * LivingAI - Agents Management JavaScript
 * =====================================
 * Agent CRUD operations, agent list management, and agent interactions
 */

// ============================================
// AGENTS INITIALIZATION
// ============================================

let agents = [];
let currentAgent = null;

function initAgents() {
    console.log('Initializing Agents Module...');
    
    // Load agents data
    loadAgents();
    
    // Initialize form handlers
    initAgentForm();
    
    // Initialize event listeners
    initEventListeners();
    
    console.log('Agents Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadAgents() {
    console.log('Loading agents...');
    
    try {
        // Show loading state
        const agentsList = document.getElementById('agents-list');
        if (agentsList) {
            agentsList.innerHTML = '<div class="loading-spinner"></div>';
        }
        
        // Fetch agents from API (or use mock data)
        agents = await fetchAgents();
        
        // Render agents
        renderAgents();
        
        // Update dashboard count
        updateDashboardAgentCount();
        
        console.log(`Loaded ${agents.length} agents`);
    } catch (error) {
        console.error('Error loading agents:', error);
        showError('Failed to load agents');
        
        // Show empty state
        const agentsList = document.getElementById('agents-list');
        if (agentsList) {
            agentsList.innerHTML = '<div class="empty-state"><i class="fa fa-robot"></i><p>No agents found</p></div>';
        }
    }
}

async function fetchAgents() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/agents');
    // return await response.json();
    
    return [
        {
            id: 'agent-001',
            name: 'Research Agent',
            type: 'research',
            description: 'Specialized in web research and data gathering',
            status: 'active',
            createdAt: '2024-01-15T10:30:00Z',
            lastUsed: '2024-01-20T14:25:00Z',
            tasksCompleted: 42,
            tools: ['web_search', 'data_analysis', 'summarization']
        },
        {
            id: 'agent-002',
            name: 'Development Agent',
            type: 'development',
            description: 'Code generation and software development assistant',
            status: 'inactive',
            createdAt: '2024-01-16T11:45:00Z',
            lastUsed: '2024-01-19T09:15:00Z',
            tasksCompleted: 28,
            tools: ['code_generation', 'debugging', 'testing']
        },
        {
            id: 'agent-003',
            name: 'Analysis Agent',
            type: 'analysis',
            description: 'Data analysis and pattern recognition specialist',
            status: 'active',
            createdAt: '2024-01-17T08:20:00Z',
            lastUsed: '2024-01-20T16:40:00Z',
            tasksCompleted: 35,
            tools: ['data_visualization', 'statistical_analysis', 'predictive_modeling']
        },
        {
            id: 'agent-004',
            name: 'Creative Agent',
            type: 'creative',
            description: 'Creative writing, brainstorming, and idea generation',
            status: 'inactive',
            createdAt: '2024-01-18T13:10:00Z',
            lastUsed: '2024-01-19T11:30:00Z',
            tasksCompleted: 19,
            tools: ['content_generation', 'brainstorming', 'story_telling']
        },
        {
            id: 'agent-005',
            name: 'General Purpose Agent',
            type: 'general',
            description: 'Versatile agent for various tasks',
            status: 'active',
            createdAt: '2024-01-14T09:00:00Z',
            lastUsed: '2024-01-20T10:05:00Z',
            tasksCompleted: 56,
            tools: ['general_knowledge', 'conversation', 'problem_solving']
        }
    ];
}

// ============================================
// RENDERING
// ============================================

function renderAgents() {
    const agentsList = document.getElementById('agents-list');
    if (!agentsList) return;
    
    if (agents.length === 0) {
        agentsList.innerHTML = '<div class="empty-state"><i class="fa fa-robot"></i><p>No agents found. Create your first agent!</p></div>';
        return;
    }
    
    // Group by type for grid display
    const groupedAgents = {};
    agents.forEach(agent => {
        if (!groupedAgents[agent.type]) {
            groupedAgents[agent.type] = [];
        }
        groupedAgents[agent.type].push(agent);
    });
    
    // Create agent cards
    agentsList.innerHTML = '';
    
    Object.entries(groupedAgents).forEach(([type, typeAgents]) => {
        const typeSection = document.createElement('div');
        typeSection.className = 'agent-type-section';
        
        const typeHeader = document.createElement('div');
        typeHeader.className = 'agent-type-header';
        typeHeader.innerHTML = `
            <h3><i class="fa fa-${getAgentTypeIcon(type)}"></i> ${formatAgentType(type)}</h3>
            <span class="agent-count">${typeAgents.length} agents</span>
        `;
        
        const agentsGrid = document.createElement('div');
        agentsGrid.className = 'agents-grid';
        
        typeAgents.forEach(agent => {
            const agentCard = createAgentCard(agent);
            agentsGrid.appendChild(agentCard);
        });
        
        typeSection.appendChild(typeHeader);
        typeSection.appendChild(agentsGrid);
        agentsList.appendChild(typeSection);
    });
}

function createAgentCard(agent) {
    const card = document.createElement('div');
    card.className = `agent-card status-${agent.status}`;
    card.dataset.agentId = agent.id;
    
    const statusIcon = agent.status === 'active' ? 'fa-circle' : 'fa-circle-o';
    const statusText = agent.status === 'active' ? 'Active' : 'Inactive';
    
    card.innerHTML = `
        <div class="agent-header">
            <div class="agent-icon">
                <i class="fa fa-${getAgentTypeIcon(agent.type)}"></i>
            </div>
            <div class="agent-info">
                <h4>${agent.name}</h4>
                <span class="agent-type">${formatAgentType(agent.type)}</span>
            </div>
            <div class="agent-status">
                <i class="fa ${statusIcon}"></i>
                <span>${statusText}</span>
            </div>
        </div>
        <div class="agent-body">
            <p>${agent.description}</p>
        </div>
        <div class="agent-footer">
            <div class="agent-stats">
                <span><i class="fa fa-tasks"></i> ${agent.tasksCompleted} tasks</span>
                <span><i class="fa fa-wrench"></i> ${agent.tools.length} tools</span>
            </div>
            <div class="agent-actions">
                <button class="btn-icon" onclick="startAgent('${agent.id}')" title="Start">
                    <i class="fa fa-play"></i>
                </button>
                <button class="btn-icon" onclick="editAgent('${agent.id}')" title="Edit">
                    <i class="fa fa-pencil"></i>
                </button>
                <button class="btn-icon" onclick="deleteAgent('${agent.id}')" title="Delete">
                    <i class="fa fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    return card;
}

function getAgentTypeIcon(type) {
    const icons = {
        'research': 'search',
        'development': 'code',
        'analysis': 'chart-line',
        'creative': 'paint-brush',
        'general': 'robot'
    };
    return icons[type] || 'robot';
}

function formatAgentType(type) {
    const types = {
        'research': 'Research',
        'development': 'Development',
        'analysis': 'Analysis',
        'creative': 'Creative',
        'general': 'General Purpose'
    };
    return types[type] || type;
}

// ============================================
// FORM HANDLERS
// ============================================

function initAgentForm() {
    const agentForm = document.getElementById('agent-form');
    if (!agentForm) return;
    
    agentForm.addEventListener('submit', handleAgentFormSubmit);
    
    // Reset form on page navigation
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.attributeName === 'class') {
                const isActive = agentForm.closest('.page').classList.contains('active');
                if (isActive) {
                    resetAgentForm();
                }
            }
        });
    });
    
    observer.observe(agentForm.closest('.page'), { attributes: true });
}

function handleAgentFormSubmit(e) {
    e.preventDefault();
    
    const nameInput = document.getElementById('agent-name');
    const typeInput = document.getElementById('agent-type');
    
    const name = nameInput.value.trim();
    const type = typeInput.value;
    
    if (!name || !type) {
        showError('Please fill in all required fields');
        return;
    }
    
    // Create new agent
    const newAgent = {
        id: `agent-${Date.now()}`,
        name,
        type,
        description: '',
        status: 'inactive',
        createdAt: new Date().toISOString(),
        lastUsed: null,
        tasksCompleted: 0,
        tools: []
    };
    
    // Add to agents list
    agents.push(newAgent);
    
    // Save to storage (or API)
    saveAgent(newAgent).then(() => {
        // Update UI
        renderAgents();
        resetAgentForm();
        updateDashboardAgentCount();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Agent Created', `New agent "${name}" has been created`, 'success');
        }
    }).catch(error => {
        console.error('Error saving agent:', error);
        showError('Failed to create agent');
        
        // Remove from local list
        agents = agents.filter(a => a.id !== newAgent.id);
    });
}

function resetAgentForm() {
    const nameInput = document.getElementById('agent-name');
    const typeInput = document.getElementById('agent-type');
    
    if (nameInput) nameInput.value = '';
    if (typeInput) typeInput.value = '';
}

// ============================================
// AGENT ACTIONS
// ============================================

async function startAgent(agentId) {
    console.log(`Starting agent: ${agentId}`);
    
    try {
        // Find agent
        const agent = agents.find(a => a.id === agentId);
        if (!agent) {
            showError('Agent not found');
            return;
        }
        
        // Update status
        agent.status = 'active';
        agent.lastUsed = new Date().toISOString();
        
        // Save changes
        await saveAgent(agent);
        
        // Update UI
        renderAgents();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Agent Started', `Agent "${agent.name}" is now active`, 'success');
        }
    } catch (error) {
        console.error('Error starting agent:', error);
        showError('Failed to start agent');
    }
}

function editAgent(agentId) {
    console.log(`Editing agent: ${agentId}`);
    
    const agent = agents.find(a => a.id === agentId);
    if (!agent) {
        showError('Agent not found');
        return;
    }
    
    currentAgent = agent;
    
    // Pre-fill form
    const nameInput = document.getElementById('agent-name');
    const typeInput = document.getElementById('agent-type');
    
    if (nameInput) nameInput.value = agent.name;
    if (typeInput) typeInput.value = agent.type;
    
    // Scroll to form
    const form = document.getElementById('agent-form');
    if (form) {
        form.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Update submit handler to update instead of create
    const agentForm = document.getElementById('agent-form');
    if (agentForm) {
        agentForm.onsubmit = function(e) {
            e.preventDefault();
            updateAgent(agentId);
        };
    }
}

async function updateAgent(agentId) {
    const nameInput = document.getElementById('agent-name');
    const typeInput = document.getElementById('agent-type');
    
    const name = nameInput.value.trim();
    const type = typeInput.value;
    
    if (!name || !type) {
        showError('Please fill in all required fields');
        return;
    }
    
    try {
        const agent = agents.find(a => a.id === agentId);
        if (!agent) {
            showError('Agent not found');
            return;
        }
        
        // Update agent
        agent.name = name;
        agent.type = type;
        
        // Save changes
        await saveAgent(agent);
        
        // Update UI
        renderAgents();
        resetAgentForm();
        currentAgent = null;
        
        // Reset form handler
        const agentForm = document.getElementById('agent-form');
        if (agentForm) {
            agentForm.onsubmit = handleAgentFormSubmit;
        }
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Agent Updated', `Agent "${name}" has been updated`, 'success');
        }
    } catch (error) {
        console.error('Error updating agent:', error);
        showError('Failed to update agent');
    }
}

async function deleteAgent(agentId) {
    if (!confirm('Are you sure you want to delete this agent?')) {
        return;
    }
    
    try {
        // Find and remove agent
        const agent = agents.find(a => a.id === agentId);
        if (!agent) {
            showError('Agent not found');
            return;
        }
        
        agents = agents.filter(a => a.id !== agentId);
        
        // Delete from storage (or API)
        await deleteAgentFromStorage(agentId);
        
        // Update UI
        renderAgents();
        updateDashboardAgentCount();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Agent Deleted', `Agent "${agent.name}" has been deleted`, 'success');
        }
    } catch (error) {
        console.error('Error deleting agent:', error);
        showError('Failed to delete agent');
    }
}

// ============================================
// STORAGE OPERATIONS (Replace with API calls)
// ============================================

async function saveAgent(agent) {
    // Simulate API call
    // Replace with: await fetch('/api/agents', { method: 'POST', body: JSON.stringify(agent) })
    
    // For demo, save to localStorage
    const existingAgents = JSON.parse(localStorage.getItem('livingai-agents') || '[]');
    const updatedAgents = existingAgents.filter(a => a.id !== agent.id);
    updatedAgents.push(agent);
    localStorage.setItem('livingai-agents', JSON.stringify(updatedAgents));
    
    return agent;
}

async function deleteAgentFromStorage(agentId) {
    // Simulate API call
    // Replace with: await fetch(`/api/agents/${agentId}`, { method: 'DELETE' })
    
    // For demo, remove from localStorage
    const existingAgents = JSON.parse(localStorage.getItem('livingai-agents') || '[]');
    const updatedAgents = existingAgents.filter(a => a.id !== agentId);
    localStorage.setItem('livingai-agents', JSON.stringify(updatedAgents));
    
    return true;
}

// ============================================
// DASHBOARD INTEGRATION
// ============================================

function updateDashboardAgentCount() {
    const dashboardAgentCount = document.getElementById('total-agents');
    if (dashboardAgentCount) {
        const activeCount = agents.filter(a => a.status === 'active').length;
        dashboardAgentCount.textContent = activeCount;
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    // Agent type filter
    const typeFilter = document.getElementById('agent-type-filter');
    if (typeFilter) {
        typeFilter.addEventListener('change', (e) => {
            filterAgentsByType(e.target.value);
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('agent-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchAgents(e.target.value);
        });
    }
}

function filterAgentsByType(type) {
    if (type === 'all') {
        renderAgents();
        return;
    }
    
    const filteredAgents = agents.filter(a => a.type === type);
    
    const agentsList = document.getElementById('agents-list');
    if (!agentsList) return;
    
    if (filteredAgents.length === 0) {
        agentsList.innerHTML = '<div class="empty-state"><i class="fa fa-robot"></i><p>No agents of this type found</p></div>';
        return;
    }
    
    agentsList.innerHTML = '';
    
    const typeSection = document.createElement('div');
    typeSection.className = 'agent-type-section';
    
    const typeHeader = document.createElement('div');
    typeHeader.className = 'agent-type-header';
    typeHeader.innerHTML = `
        <h3><i class="fa fa-${getAgentTypeIcon(type)}"></i> ${formatAgentType(type)}</h3>
        <span class="agent-count">${filteredAgents.length} agents</span>
    `;
    
    const agentsGrid = document.createElement('div');
    agentsGrid.className = 'agents-grid';
    
    filteredAgents.forEach(agent => {
        const agentCard = createAgentCard(agent);
        agentsGrid.appendChild(agentCard);
    });
    
    typeSection.appendChild(typeHeader);
    typeSection.appendChild(agentsGrid);
    agentsList.appendChild(typeSection);
}

function searchAgents(query) {
    if (!query) {
        renderAgents();
        return;
    }
    
    const filteredAgents = agents.filter(a => 
        a.name.toLowerCase().includes(query.toLowerCase()) ||
        a.description.toLowerCase().includes(query.toLowerCase())
    );
    
    const agentsList = document.getElementById('agents-list');
    if (!agentsList) return;
    
    if (filteredAgents.length === 0) {
        agentsList.innerHTML = '<div class="empty-state"><i class="fa fa-search"></i><p>No agents found matching your search</p></div>';
        return;
    }
    
    agentsList.innerHTML = '';
    
    const resultsHeader = document.createElement('div');
    resultsHeader.className = 'search-results-header';
    resultsHeader.innerHTML = `<h3>Search Results (${filteredAgents.length})</h3>`;
    
    const agentsGrid = document.createElement('div');
    agentsGrid.className = 'agents-grid';
    
    filteredAgents.forEach(agent => {
        const agentCard = createAgentCard(agent);
        agentsGrid.appendChild(agentCard);
    });
    
    agentsList.appendChild(resultsHeader);
    agentsList.appendChild(agentsGrid);
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

window.initAgents = initAgents;
window.startAgent = startAgent;
window.editAgent = editAgent;
window.deleteAgent = deleteAgent;
window.updateAgent = updateAgent;
