/**
 * LivingAI - Tools Management JavaScript
 * =====================================
 * Tool filtering, search, category management, and tool execution
 */

// ============================================
// TOOLS INITIALIZATION
// ============================================

let tools = [];
let categories = [];
let currentCategory = 'all';

function initTools() {
    console.log('Initializing Tools Module...');
    
    // Load tools data
    loadTools();
    
    // Initialize search and filters
    initSearchAndFilters();
    
    // Initialize event listeners
    initEventListeners();
    
    console.log('Tools Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadTools() {
    console.log('Loading tools...');
    
    try {
        // Show loading state
        const toolsContainer = document.getElementById('tools-container');
        if (toolsContainer) {
            toolsContainer.innerHTML = '<div class="loading-spinner"></div>';
        }
        
        // Fetch tools from API (or use mock data)
        const data = await fetchTools();
        tools = data.tools;
        categories = data.categories;
        
        // Render tools
        renderTools();
        renderCategories();
        
        // Update dashboard count
        updateDashboardToolsCount();
        
        console.log(`Loaded ${tools.length} tools in ${categories.length} categories`);
    } catch (error) {
        console.error('Error loading tools:', error);
        showError('Failed to load tools');
        
        // Show empty state
        const toolsContainer = document.getElementById('tools-container');
        if (toolsContainer) {
            toolsContainer.innerHTML = '<div class="empty-state"><i class="fa fa-wrench"></i><p>No tools found</p></div>';
        }
    }
}

async function fetchTools() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/tools');
    // return await response.json();
    
    return {
        tools: [
            {
                id: 'tool-001',
                name: 'Web Search',
                category: 'search',
                description: 'Search the web for information and data',
                icon: 'fa-globe',
                version: '1.2.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-20T14:25:00Z',
                usageCount: 42,
                isEnabled: true,
                requiresApiKey: true,
                tags: ['search', 'web', 'information']
            },
            {
                id: 'tool-002',
                name: 'Code Generation',
                category: 'development',
                description: 'Generate code in various programming languages',
                icon: 'fa-code',
                version: '1.5.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-20T10:15:00Z',
                usageCount: 87,
                isEnabled: true,
                requiresApiKey: false,
                tags: ['code', 'development', 'programming']
            },
            {
                id: 'tool-003',
                name: 'Data Analysis',
                category: 'analysis',
                description: 'Analyze and process structured data',
                icon: 'fa-chart-bar',
                version: '1.1.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-19T16:40:00Z',
                usageCount: 35,
                isEnabled: true,
                requiresApiKey: false,
                tags: ['data', 'analysis', 'statistics']
            },
            {
                id: 'tool-004',
                name: 'Text Summarization',
                category: 'text',
                description: 'Summarize long text documents',
                icon: 'fa-file-text',
                version: '1.3.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-20T09:30:00Z',
                usageCount: 28,
                isEnabled: true,
                requiresApiKey: false,
                tags: ['text', 'summarization', 'document']
            },
            {
                id: 'tool-005',
                name: 'Image Generation',
                category: 'creative',
                description: 'Generate images from text prompts',
                icon: 'fa-paint-brush',
                version: '2.0.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-18T11:20:00Z',
                usageCount: 64,
                isEnabled: true,
                requiresApiKey: true,
                tags: ['image', 'generation', 'creative']
            },
            {
                id: 'tool-006',
                name: 'Translation',
                category: 'language',
                description: 'Translate text between multiple languages',
                icon: 'fa-language',
                version: '1.4.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-20T14:00:00Z',
                usageCount: 53,
                isEnabled: true,
                requiresApiKey: true,
                tags: ['translation', 'language', 'multilingual']
            },
            {
                id: 'tool-007',
                name: 'Database Query',
                category: 'database',
                description: 'Execute SQL queries on databases',
                icon: 'fa-database',
                version: '1.0.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-17T08:45:00Z',
                usageCount: 19,
                isEnabled: false,
                requiresApiKey: false,
                tags: ['database', 'sql', 'query']
            },
            {
                id: 'tool-008',
                name: 'API Integration',
                category: 'integration',
                description: 'Integrate with external APIs and services',
                icon: 'fa-plug',
                version: '1.2.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-19T13:25:00Z',
                usageCount: 31,
                isEnabled: true,
                requiresApiKey: true,
                tags: ['api', 'integration', 'external']
            },
            {
                id: 'tool-009',
                name: 'File Management',
                category: 'system',
                description: 'Manage files and directories',
                icon: 'fa-folder',
                version: '1.3.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-20T15:10:00Z',
                usageCount: 76,
                isEnabled: true,
                requiresApiKey: false,
                tags: ['file', 'management', 'system']
            },
            {
                id: 'tool-010',
                name: 'Math Calculator',
                category: 'utility',
                description: 'Perform complex mathematical calculations',
                icon: 'fa-calculator',
                version: '1.1.0',
                author: 'LivingAI Team',
                lastUsed: '2024-01-19T10:05:00Z',
                usageCount: 22,
                isEnabled: true,
                requiresApiKey: false,
                tags: ['math', 'calculator', 'calculations']
            }
        ],
        categories: [
            { id: 'all', name: 'All Tools', icon: 'fa-wrench' },
            { id: 'search', name: 'Search', icon: 'fa-search' },
            { id: 'development', name: 'Development', icon: 'fa-code' },
            { id: 'analysis', name: 'Analysis', icon: 'fa-chart-bar' },
            { id: 'text', name: 'Text Processing', icon: 'fa-file-text' },
            { id: 'creative', name: 'Creative', icon: 'fa-paint-brush' },
            { id: 'language', name: 'Language', icon: 'fa-language' },
            { id: 'database', name: 'Database', icon: 'fa-database' },
            { id: 'integration', name: 'Integration', icon: 'fa-plug' },
            { id: 'system', name: 'System', icon: 'fa-cogs' },
            { id: 'utility', name: 'Utility', icon: 'fa-calculator' }
        ]
    };
}

// ============================================
// RENDERING
// ============================================

function renderTools() {
    const toolsContainer = document.getElementById('tools-container');
    if (!toolsContainer) return;
    
    // Filter tools by category
    let filteredTools = currentCategory === 'all' 
        ? tools 
        : tools.filter(tool => tool.category === currentCategory);
    
    // Sort by usage count (descending)
    filteredTools.sort((a, b) => b.usageCount - a.usageCount);
    
    if (filteredTools.length === 0) {
        toolsContainer.innerHTML = '<div class="empty-state"><i class="fa fa-wrench"></i><p>No tools found in this category</p></div>';
        return;
    }
    
    // Create tool cards
    toolsContainer.innerHTML = '';
    
    filteredTools.forEach(tool => {
        const toolCard = createToolCard(tool);
        toolsContainer.appendChild(toolCard);
    });
}

function createToolCard(tool) {
    const card = document.createElement('div');
    card.className = `tool-card ${tool.isEnabled ? '' : 'disabled'}`;
    card.dataset.toolId = tool.id;
    
    const statusBadge = tool.isEnabled 
        ? '<span class="tool-status enabled"><i class="fa fa-check-circle"></i> Enabled</span>'
        : '<span class="tool-status disabled"><i class="fa fa-times-circle"></i> Disabled</span>';
    
    const apiKeyBadge = tool.requiresApiKey 
        ? '<span class="tool-badge api-key"><i class="fa fa-key"></i> API Key Required</span>'
        : '';
    
    card.innerHTML = `
        <div class="tool-header">
            <div class="tool-icon">
                <i class="fa ${tool.icon}"></i>
            </div>
            <div class="tool-info">
                <h4>${tool.name}</h4>
                <span class="tool-version">v${tool.version}</span>
                ${apiKeyBadge}
            </div>
            <div class="tool-actions">
                ${statusBadge}
                <button class="btn-icon" onclick="executeTool('${tool.id}')" title="Execute">
                    <i class="fa fa-play"></i>
                </button>
            </div>
        </div>
        <div class="tool-body">
            <p>${tool.description}</p>
        </div>
        <div class="tool-footer">
            <div class="tool-meta">
                <span><i class="fa fa-user"></i> ${tool.author}</span>
                <span><i class="fa fa-clock-o"></i> Used ${formatLastUsed(tool.lastUsed)}</span>
                <span><i class="fa fa-chart-line"></i> ${tool.usageCount} times</span>
            </div>
            <div class="tool-tags">
                ${tool.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        </div>
    `;
    
    return card;
}

function renderCategories() {
    const categoriesContainer = document.getElementById('tool-categories');
    if (!categoriesContainer) return;
    
    categoriesContainer.innerHTML = '';
    
    categories.forEach(category => {
        const categoryItem = document.createElement('div');
        categoryItem.className = `category-item ${currentCategory === category.id ? 'active' : ''}`;
        categoryItem.onclick = () => selectCategory(category.id);
        
        categoryItem.innerHTML = `
            <i class="fa ${category.icon}"></i>
            <span>${category.name}</span>
            <span class="category-count">${getCategoryToolCount(category.id)}</span>
        `;
        
        categoriesContainer.appendChild(categoryItem);
    });
}

function getCategoryToolCount(categoryId) {
    if (categoryId === 'all') return tools.length;
    return tools.filter(tool => tool.category === categoryId).length;
}

function formatLastUsed(dateString) {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days} days ago`;
    if (hours > 0) return `${hours} hours ago`;
    if (minutes > 0) return `${minutes} minutes ago`;
    return 'Just now';
}

// ============================================
// CATEGORY SELECTION
// ============================================

function selectCategory(categoryId) {
    currentCategory = categoryId;
    renderCategories();
    renderTools();
}

// ============================================
// SEARCH AND FILTERS
// ============================================

function initSearchAndFilters() {
    // Search input
    const searchInput = document.getElementById('tool-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchTools(e.target.value);
        });
    }
    
    // Sort options
    const sortSelect = document.getElementById('tool-sort');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            sortTools(e.target.value);
        });
    }
}

function searchTools(query) {
    if (!query) {
        renderTools();
        return;
    }
    
    const filteredTools = tools.filter(tool => 
        tool.name.toLowerCase().includes(query.toLowerCase()) ||
        tool.description.toLowerCase().includes(query.toLowerCase()) ||
        tool.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
    );
    
    const toolsContainer = document.getElementById('tools-container');
    if (!toolsContainer) return;
    
    if (filteredTools.length === 0) {
        toolsContainer.innerHTML = '<div class="empty-state"><i class="fa fa-search"></i><p>No tools found matching your search</p></div>';
        return;
    }
    
    toolsContainer.innerHTML = '';
    
    const resultsHeader = document.createElement('div');
    resultsHeader.className = 'search-results-header';
    resultsHeader.innerHTML = `<h3>Search Results (${filteredTools.length})</h3>`;
    
    const toolsGrid = document.createElement('div');
    toolsGrid.className = 'tools-grid';
    
    filteredTools.forEach(tool => {
        const toolCard = createToolCard(tool);
        toolsGrid.appendChild(toolCard);
    });
    
    toolsContainer.appendChild(resultsHeader);
    toolsContainer.appendChild(toolsGrid);
}

function sortTools(sortBy) {
    const toolsContainer = document.getElementById('tools-container');
    if (!toolsContainer) return;
    
    let filteredTools = currentCategory === 'all' 
        ? [...tools] 
        : tools.filter(tool => tool.category === currentCategory);
    
    switch (sortBy) {
        case 'name-asc':
            filteredTools.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'name-desc':
            filteredTools.sort((a, b) => b.name.localeCompare(a.name));
            break;
        case 'usage-asc':
            filteredTools.sort((a, b) => a.usageCount - b.usageCount);
            break;
        case 'usage-desc':
            filteredTools.sort((a, b) => b.usageCount - a.usageCount);
            break;
        case 'recent':
            filteredTools.sort((a, b) => new Date(b.lastUsed) - new Date(a.lastUsed));
            break;
        default:
            filteredTools.sort((a, b) => b.usageCount - a.usageCount);
    }
    
    toolsContainer.innerHTML = '';
    
    filteredTools.forEach(tool => {
        const toolCard = createToolCard(tool);
        toolsContainer.appendChild(toolCard);
    });
}

// ============================================
// TOOL ACTIONS
// ============================================

function executeTool(toolId) {
    console.log(`Executing tool: ${toolId}`);
    
    const tool = tools.find(t => t.id === toolId);
    if (!tool) {
        showError('Tool not found');
        return;
    }
    
    if (!tool.isEnabled) {
        showError('This tool is currently disabled');
        return;
    }
    
    // Show execution dialog
    showToolExecutionDialog(tool);
}

function showToolExecutionDialog(tool) {
    const dialog = document.createElement('div');
    dialog.className = 'modal-overlay';
    dialog.id = 'tool-execution-modal';
    
    dialog.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h2><i class="fa ${tool.icon}"></i> ${tool.name}</h2>
                <button class="modal-close" onclick="closeToolExecutionDialog()">
                    <i class="fa fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <p>${tool.description}</p>
                <div class="form-group">
                    <label>Input Prompt</label>
                    <textarea id="tool-input" rows="4" placeholder="Enter your input here..."></textarea>
                </div>
                ${tool.requiresApiKey ? `
                    <div class="form-group">
                        <label>API Key (Required)</label>
                        <input type="password" id="tool-api-key" placeholder="Enter API key...">
                    </div>
                ` : ''}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeToolExecutionDialog()">
                    <i class="fa fa-times"></i> Cancel
                </button>
                <button class="btn btn-primary" onclick="confirmToolExecution('${tool.id}')">
                    <i class="fa fa-play"></i> Execute
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialog);
    
    // Focus on input
    const input = document.getElementById('tool-input');
    if (input) input.focus();
}

function closeToolExecutionDialog() {
    const dialog = document.getElementById('tool-execution-modal');
    if (dialog) {
        dialog.remove();
    }
}

async function confirmToolExecution(toolId) {
    const input = document.getElementById('tool-input');
    const apiKeyInput = document.getElementById('tool-api-key');
    
    const tool = tools.find(t => t.id === toolId);
    if (!tool) {
        showError('Tool not found');
        return;
    }
    
    if (tool.requiresApiKey && !apiKeyInput.value) {
        showError('API key is required for this tool');
        return;
    }
    
    const prompt = input.value;
    if (!prompt) {
        showError('Please enter an input prompt');
        return;
    }
    
    try {
        // Show loading
        const executeBtn = document.querySelector('.modal-footer .btn-primary');
        if (executeBtn) {
            executeBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Executing...';
            executeBtn.disabled = true;
        }
        
        // Simulate tool execution
        await executeToolWithInput(toolId, prompt, apiKeyInput.value);
        
        // Close dialog
        closeToolExecutionDialog();
        
        // Show success
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Tool Executed', `Tool "${tool.name}" has been executed`, 'success');
        }
        
        // Update usage count
        tool.usageCount++;
        tool.lastUsed = new Date().toISOString();
        renderTools();
        
    } catch (error) {
        console.error('Error executing tool:', error);
        showError('Failed to execute tool');
        
        const executeBtn = document.querySelector('.modal-footer .btn-primary');
        if (executeBtn) {
            executeBtn.innerHTML = '<i class="fa fa-play"></i> Execute';
            executeBtn.disabled = false;
        }
    }
}

async function executeToolWithInput(toolId, input, apiKey) {
    // Simulate API call
    // Replace with: await fetch('/api/tools/execute', { method: 'POST', body: JSON.stringify({ toolId, input, apiKey }) })
    
    // Simulate execution delay
    return new Promise((resolve) => {
        setTimeout(() => {
            console.log(`Tool ${toolId} executed with input: ${input}`);
            resolve({ success: true, result: `Tool execution completed for: ${input}` });
        }, 1500);
    });
}

// ============================================
// TOOL MANAGEMENT
// ============================================

async function toggleToolStatus(toolId) {
    const tool = tools.find(t => t.id === toolId);
    if (!tool) {
        showError('Tool not found');
        return;
    }
    
    try {
        tool.isEnabled = !tool.isEnabled;
        await saveTool(tool);
        renderTools();
        
        const status = tool.isEnabled ? 'enabled' : 'disabled';
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Tool Updated', `Tool "${tool.name}" has been ${status}`, 'success');
        }
    } catch (error) {
        console.error('Error toggling tool status:', error);
        showError('Failed to update tool');
    }
}

async function saveTool(tool) {
    // Simulate API call
    // Replace with: await fetch('/api/tools', { method: 'POST', body: JSON.stringify(tool) })
    
    // For demo, save to localStorage
    const existingTools = JSON.parse(localStorage.getItem('livingai-tools') || '[]');
    const updatedTools = existingTools.filter(t => t.id !== tool.id);
    updatedTools.push(tool);
    localStorage.setItem('livingai-tools', JSON.stringify(updatedTools));
    
    return tool;
}

// ============================================
// DASHBOARD INTEGRATION
// ============================================

function updateDashboardToolsCount() {
    const dashboardToolsCount = document.getElementById('total-tools');
    if (dashboardToolsCount) {
        dashboardToolsCount.textContent = tools.length;
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    // Category selection
    const categoryItems = document.querySelectorAll('.category-item');
    categoryItems.forEach(item => {
        item.addEventListener('click', () => {
            const categoryId = item.dataset.categoryId;
            if (categoryId) {
                selectCategory(categoryId);
            }
        });
    });
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

window.initTools = initTools;
window.executeTool = executeTool;
window.confirmToolExecution = confirmToolExecution;
window.closeToolExecutionDialog = closeToolExecutionDialog;
window.toggleToolStatus = toggleToolStatus;
window.selectCategory = selectCategory;
