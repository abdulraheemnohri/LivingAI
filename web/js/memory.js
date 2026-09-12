/**
 * LivingAI - Memory Management JavaScript
 * =====================================
 * Memory search, entries management, and knowledge base operations
 */

// ============================================
// MEMORY INITIALIZATION
// ============================================

let memoryEntries = [];
let categories = ['knowledge', 'conversations', 'settings', 'cache'];
let currentCategory = 'all';

function initMemory() {
    console.log('Initializing Memory Module...');
    
    // Load memory entries
    loadMemoryEntries();
    
    // Initialize search and filters
    initSearchAndFilters();
    
    // Initialize event listeners
    initEventListeners();
    
    console.log('Memory Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadMemoryEntries() {
    console.log('Loading memory entries...');
    
    try {
        // Show loading state
        const memoryContainer = document.getElementById('memory-container');
        if (memoryContainer) {
            memoryContainer.innerHTML = '<div class="loading-spinner"></div>';
        }
        
        // Fetch memory entries from API (or use mock data)
        memoryEntries = await fetchMemoryEntries();
        
        // Render entries
        renderMemoryEntries();
        renderMemoryStats();
        renderCategories();
        
        // Update dashboard count
        updateDashboardMemoryCount();
        
        console.log(`Loaded ${memoryEntries.length} memory entries`);
    } catch (error) {
        console.error('Error loading memory entries:', error);
        showError('Failed to load memory entries');
        
        // Show empty state
        const memoryContainer = document.getElementById('memory-container');
        if (memoryContainer) {
            memoryContainer.innerHTML = '<div class="empty-state"><i class="fa fa-database"></i><p>No memory entries found</p></div>';
        }
    }
}

async function fetchMemoryEntries() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/memory');
    // return await response.json();
    
    return [
        {
            id: 'mem-001',
            title: 'AI Research Paper Summary',
            content: 'Summary of the latest AI research paper on transformer models and their applications in natural language processing.',
            category: 'knowledge',
            type: 'document',
            size: '2.5 KB',
            createdAt: '2024-01-18T10:00:00Z',
            updatedAt: '2024-01-18T10:00:00Z',
            tags: ['ai', 'research', 'nlp', 'transformers'],
            accessCount: 15,
            lastAccessed: '2024-01-20T14:30:00Z'
        },
        {
            id: 'mem-002',
            title: 'User Preferences',
            content: 'User prefers dark theme, Urdu language, and has enabled notifications for important events.',
            category: 'settings',
            type: 'configuration',
            size: '1 KB',
            createdAt: '2024-01-15T08:00:00Z',
            updatedAt: '2024-01-19T11:20:00Z',
            tags: ['preferences', 'settings', 'user'],
            accessCount: 8,
            lastAccessed: '2024-01-20T09:15:00Z'
        },
        {
            id: 'mem-003',
            title: 'Conversation: Project Planning',
            content: 'User discussion about planning the LivingAI project, including features, timeline, and resource requirements.',
            category: 'conversations',
            type: 'conversation',
            size: '4.2 KB',
            createdAt: '2024-01-19T14:00:00Z',
            updatedAt: '2024-01-19T15:30:00Z',
            tags: ['project', 'planning', 'livingai'],
            accessCount: 5,
            lastAccessed: '2024-01-20T10:00:00Z'
        },
        {
            id: 'mem-004',
            title: 'Technical Documentation',
            content: 'Complete technical documentation for the LivingAI system architecture, including component diagrams and API specifications.',
            category: 'knowledge',
            type: 'document',
            size: '8.7 KB',
            createdAt: '2024-01-16T11:00:00Z',
            updatedAt: '2024-01-18T16:45:00Z',
            tags: ['documentation', 'architecture', 'technical'],
            accessCount: 22,
            lastAccessed: '2024-01-20T13:20:00Z'
        },
        {
            id: 'mem-005',
            title: 'Cached Web Search Results',
            content: 'Cached results from web searches on AI trends, including URLs, snippets, and timestamps.',
            category: 'cache',
            type: 'cache',
            size: '3.1 KB',
            createdAt: '2024-01-20T08:00:00Z',
            updatedAt: '2024-01-20T08:00:00Z',
            tags: ['cache', 'web', 'search'],
            accessCount: 3,
            lastAccessed: '2024-01-20T12:45:00Z'
        },
        {
            id: 'mem-006',
            title: 'Machine Learning Models',
            content: 'Information about various machine learning models, their parameters, and use cases for different scenarios.',
            category: 'knowledge',
            type: 'document',
            size: '5.8 KB',
            createdAt: '2024-01-17T09:30:00Z',
            updatedAt: '2024-01-19T14:10:00Z',
            tags: ['ml', 'models', 'ai', 'knowledge'],
            accessCount: 18,
            lastAccessed: '2024-01-20T11:30:00Z'
        },
        {
            id: 'mem-007',
            title: 'API Configuration',
            content: 'Configuration details for various API integrations, including endpoints, keys, and rate limits.',
            category: 'settings',
            type: 'configuration',
            size: '1.5 KB',
            createdAt: '2024-01-18T16:00:00Z',
            updatedAt: '2024-01-19T10:30:00Z',
            tags: ['api', 'configuration', 'integration'],
            accessCount: 12,
            lastAccessed: '2024-01-20T15:00:00Z'
        },
        {
            id: 'mem-008',
            title: 'Conversation: Bug Fixes',
            content: 'User discussion about debugging and fixing issues in the LivingAI system, with solutions and workarounds.',
            category: 'conversations',
            type: 'conversation',
            size: '3.5 KB',
            createdAt: '2024-01-19T10:00:00Z',
            updatedAt: '2024-01-19T12:45:00Z',
            tags: ['bug', 'debug', 'fixes'],
            accessCount: 7,
            lastAccessed: '2024-01-20T08:30:00Z'
        }
    ];
}

// ============================================
// RENDERING
// ============================================

function renderMemoryEntries() {
    const memoryContainer = document.getElementById('memory-container');
    if (!memoryContainer) return;
    
    // Filter by category
    let filteredEntries = currentCategory === 'all' 
        ? memoryEntries 
        : memoryEntries.filter(entry => entry.category === currentCategory);
    
    // Sort by last accessed (descending)
    filteredEntries.sort((a, b) => new Date(b.lastAccessed) - new Date(a.lastAccessed));
    
    if (filteredEntries.length === 0) {
        memoryContainer.innerHTML = '<div class="empty-state"><i class="fa fa-database"></i><p>No memory entries found in this category</p></div>';
        return;
    }
    
    // Create memory cards
    memoryContainer.innerHTML = '';
    
    filteredEntries.forEach(entry => {
        const entryCard = createMemoryCard(entry);
        memoryContainer.appendChild(entryCard);
    });
}

function createMemoryCard(entry) {
    const card = document.createElement('div');
    card.className = `memory-card category-${entry.category}`;
    card.dataset.entryId = entry.id;
    
    // Category icons
    const categoryIcons = {
        'knowledge': 'fa-book',
        'conversations': 'fa-comments',
        'settings': 'fa-cog',
        'cache': 'fa-archive'
    };
    
    // Type icons
    const typeIcons = {
        'document': 'fa-file-text',
        'conversation': 'fa-commenting',
        'configuration': 'fa-sliders',
        'cache': 'fa-database'
    };
    
    const categoryIcon = categoryIcons[entry.category] || 'fa-folder';
    const typeIcon = typeIcons[entry.type] || 'fa-file';
    
    card.innerHTML = `
        <div class="memory-header">
            <div class="memory-icon">
                <i class="fa ${typeIcon}"></i>
            </div>
            <div class="memory-info">
                <h4>${entry.title}</h4>
                <div class="memory-meta">
                    <span class="memory-category"><i class="fa ${categoryIcon}"></i> ${formatCategory(entry.category)}</span>
                    <span class="memory-size">${entry.size}</span>
                </div>
            </div>
            <div class="memory-actions">
                <button class="btn-icon" onclick="viewMemoryEntry('${entry.id}')" title="View">
                    <i class="fa fa-eye"></i>
                </button>
                <button class="btn-icon" onclick="editMemoryEntry('${entry.id}')" title="Edit">
                    <i class="fa fa-pencil"></i>
                </button>
                <button class="btn-icon" onclick="deleteMemoryEntry('${entry.id}')" title="Delete">
                    <i class="fa fa-trash"></i>
                </button>
            </div>
        </div>
        <div class="memory-body">
            <p>${truncateContent(entry.content, 150)}</p>
        </div>
        <div class="memory-footer">
            <div class="memory-tags">
                ${entry.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
            <div class="memory-stats">
                <span><i class="fa fa-clock-o"></i> ${formatDate(entry.updatedAt)}</span>
                <span><i class="fa fa-eye"></i> ${entry.accessCount}</span>
            </div>
        </div>
    `;
    
    return card;
}

function truncateContent(content, length) {
    if (content.length <= length) return content;
    return content.substring(0, length) + '...';
}

function formatCategory(category) {
    const categoryNames = {
        'knowledge': 'Knowledge',
        'conversations': 'Conversations',
        'settings': 'Settings',
        'cache': 'Cache'
    };
    return categoryNames[category] || category;
}

function formatDate(dateString) {
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

function renderMemoryStats() {
    const statsContainer = document.getElementById('memory-stats');
    if (!statsContainer) return;
    
    const totalEntries = memoryEntries.length;
    const totalSize = memoryEntries.reduce((sum, entry) => {
        // Parse size (e.g., "2.5 KB" -> 2.5)
        const size = parseFloat(entry.size);
        return sum + (isNaN(size) ? 0 : size);
    }, 0);
    
    const mostAccessed = memoryEntries.reduce((max, entry) => 
        entry.accessCount > max.accessCount ? entry : max, 
        memoryEntries[0] || {}
    );
    
    const recentlyUpdated = memoryEntries.reduce((recent, entry) => 
        new Date(entry.updatedAt) > new Date(recent.updatedAt) ? entry : recent,
        memoryEntries[0] || {}
    );
    
    statsContainer.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">${totalEntries}</div>
            <div class="stat-label">Total Entries</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${totalSize.toFixed(1)} KB</div>
            <div class="stat-label">Total Size</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${mostAccessed.accessCount || 0}</div>
            <div class="stat-label">Most Accessed</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${recentlyUpdated.title ? recentlyUpdated.title.substring(0, 20) + '...' : 'None'}</div>
            <div class="stat-label">Recently Updated</div>
        </div>
    `;
}

function renderCategories() {
    const categoriesContainer = document.getElementById('memory-categories');
    if (!categoriesContainer) return;
    
    categoriesContainer.innerHTML = '';
    
    categories.forEach(category => {
        const categoryItem = document.createElement('div');
        categoryItem.className = `category-item ${currentCategory === category ? 'active' : ''}`;
        categoryItem.onclick = () => selectCategory(category);
        
        const categoryIcons = {
            'all': 'fa-database',
            'knowledge': 'fa-book',
            'conversations': 'fa-comments',
            'settings': 'fa-cog',
            'cache': 'fa-archive'
        };
        
        const categoryNames = {
            'all': 'All Entries',
            'knowledge': 'Knowledge',
            'conversations': 'Conversations',
            'settings': 'Settings',
            'cache': 'Cache'
        };
        
        categoryItem.innerHTML = `
            <i class="fa ${categoryIcons[category] || 'fa-folder'}"></i>
            <span>${categoryNames[category] || category}</span>
            <span class="category-count">${getCategoryCount(category)}</span>
        `;
        
        categoriesContainer.appendChild(categoryItem);
    });
}

function getCategoryCount(category) {
    if (category === 'all') return memoryEntries.length;
    return memoryEntries.filter(entry => entry.category === category).length;
}

// ============================================
// CATEGORY SELECTION
// ============================================

function selectCategory(category) {
    currentCategory = category;
    renderCategories();
    renderMemoryEntries();
}

// ============================================
// MEMORY ACTIONS
// ============================================

function viewMemoryEntry(entryId) {
    const entry = memoryEntries.find(e => e.id === entryId);
    if (!entry) {
        showError('Memory entry not found');
        return;
    }
    
    // Increment access count
    entry.accessCount++;
    entry.lastAccessed = new Date().toISOString();
    
    // Show view dialog
    showMemoryEntryDialog(entry, true);
}

function editMemoryEntry(entryId) {
    const entry = memoryEntries.find(e => e.id === entryId);
    if (!entry) {
        showError('Memory entry not found');
        return;
    }
    
    // Show edit dialog
    showMemoryEntryDialog(entry, false);
}

async function deleteMemoryEntry(entryId) {
    if (!confirm('Are you sure you want to delete this memory entry?')) {
        return;
    }
    
    try {
        const entry = memoryEntries.find(e => e.id === entryId);
        if (!entry) {
            showError('Memory entry not found');
            return;
        }
        
        // Remove from list
        memoryEntries = memoryEntries.filter(e => e.id !== entryId);
        
        // Delete from storage (or API)
        await deleteMemoryEntryFromStorage(entryId);
        
        // Update UI
        renderMemoryEntries();
        renderMemoryStats();
        updateDashboardMemoryCount();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Entry Deleted', `Memory entry "${entry.title}" has been deleted`, 'success');
        }
    } catch (error) {
        console.error('Error deleting memory entry:', error);
        showError('Failed to delete memory entry');
    }
}

function showMemoryEntryDialog(entry, isViewOnly) {
    const dialog = document.createElement('div');
    dialog.className = 'modal-overlay';
    dialog.id = 'memory-entry-modal';
    
    const categoryIcons = {
        'knowledge': 'fa-book',
        'conversations': 'fa-comments',
        'settings': 'fa-cog',
        'cache': 'fa-archive'
    };
    
    const typeIcons = {
        'document': 'fa-file-text',
        'conversation': 'fa-commenting',
        'configuration': 'fa-sliders',
        'cache': 'fa-database'
    };
    
    const categoryIcon = categoryIcons[entry.category] || 'fa-folder';
    const typeIcon = typeIcons[entry.type] || 'fa-file';
    
    dialog.innerHTML = `
        <div class="modal memory-modal">
            <div class="modal-header">
                <h2><i class="fa ${typeIcon}"></i> ${entry.title}</h2>
                <button class="modal-close" onclick="closeMemoryEntryDialog()">
                    <i class="fa fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="memory-entry-meta">
                    <div class="meta-item">
                        <i class="fa fa-folder"></i>
                        <span>Category: ${formatCategory(entry.category)}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fa fa-file"></i>
                        <span>Type: ${entry.type}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fa fa-tags"></i>
                        <span>Tags: ${entry.tags.join(', ')}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fa fa-clock-o"></i>
                        <span>Created: ${formatDateTime(entry.createdAt)}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fa fa-refresh"></i>
                        <span>Updated: ${formatDateTime(entry.updatedAt)}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fa fa-eye"></i>
                        <span>Accessed: ${entry.accessCount} times</span>
                    </div>
                </div>
                <div class="memory-entry-content">
                    <h3>Content</h3>
                    <div class="content-display">${entry.content}</div>
                </div>
            </div>
            ${isViewOnly ? '' : `
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeMemoryEntryDialog()">
                        <i class="fa fa-times"></i> Cancel
                    </button>
                    <button class="btn btn-primary" onclick="saveMemoryEntry('${entry.id}')">
                        <i class="fa fa-save"></i> Save Changes
                    </button>
                </div>
            `}
        </div>
    `;
    
    document.body.appendChild(dialog);
    
    // Make content editable if not view-only
    if (!isViewOnly) {
        const contentDisplay = dialog.querySelector('.content-display');
        if (contentDisplay) {
            contentDisplay.contentEditable = true;
            contentDisplay.classList.add('editable');
            contentDisplay.focus();
        }
    }
}

function closeMemoryEntryDialog() {
    const dialog = document.getElementById('memory-entry-modal');
    if (dialog) {
        dialog.remove();
    }
}

async function saveMemoryEntry(entryId) {
    const dialog = document.getElementById('memory-entry-modal');
    if (!dialog) return;
    
    const contentDisplay = dialog.querySelector('.content-display');
    if (!contentDisplay) return;
    
    const newContent = contentDisplay.textContent;
    
    try {
        const entry = memoryEntries.find(e => e.id === entryId);
        if (!entry) {
            showError('Memory entry not found');
            return;
        }
        
        // Update entry
        entry.content = newContent;
        entry.updatedAt = new Date().toISOString();
        
        // Save changes
        await saveMemoryEntryToStorage(entry);
        
        // Close dialog
        closeMemoryEntryDialog();
        
        // Update UI
        renderMemoryEntries();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Entry Updated', `Memory entry "${entry.title}" has been updated`, 'success');
        }
    } catch (error) {
        console.error('Error saving memory entry:', error);
        showError('Failed to save memory entry');
    }
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// ============================================
// SEARCH AND FILTERS
// ============================================

function initSearchAndFilters() {
    // Search input
    const searchInput = document.getElementById('memory-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchMemoryEntries(e.target.value);
        });
    }
    
    // Sort options
    const sortSelect = document.getElementById('memory-sort');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            sortMemoryEntries(e.target.value);
        });
    }
}

function searchMemoryEntries(query) {
    if (!query) {
        renderMemoryEntries();
        return;
    }
    
    const filteredEntries = memoryEntries.filter(entry => 
        entry.title.toLowerCase().includes(query.toLowerCase()) ||
        entry.content.toLowerCase().includes(query.toLowerCase()) ||
        entry.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
    );
    
    renderFilteredEntries(filteredEntries, `Search: "${query}"`);
}

function sortMemoryEntries(sortBy) {
    const memoryContainer = document.getElementById('memory-container');
    if (!memoryContainer) return;
    
    let filteredEntries = currentCategory === 'all' 
        ? [...memoryEntries] 
        : memoryEntries.filter(entry => entry.category === currentCategory);
    
    switch (sortBy) {
        case 'title-asc':
            filteredEntries.sort((a, b) => a.title.localeCompare(b.title));
            break;
        case 'title-desc':
            filteredEntries.sort((a, b) => b.title.localeCompare(a.title));
            break;
        case 'date-asc':
            filteredEntries.sort((a, b) => new Date(a.updatedAt) - new Date(b.updatedAt));
            break;
        case 'date-desc':
            filteredEntries.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
            break;
        case 'access-asc':
            filteredEntries.sort((a, b) => a.accessCount - b.accessCount);
            break;
        case 'access-desc':
            filteredEntries.sort((a, b) => b.accessCount - a.accessCount);
            break;
        default:
            filteredEntries.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
    }
    
    memoryContainer.innerHTML = '';
    
    filteredEntries.forEach(entry => {
        const entryCard = createMemoryCard(entry);
        memoryContainer.appendChild(entryCard);
    });
}

function renderFilteredEntries(filteredEntries, title) {
    const memoryContainer = document.getElementById('memory-container');
    if (!memoryContainer) return;
    
    if (filteredEntries.length === 0) {
        memoryContainer.innerHTML = '<div class="empty-state"><i class="fa fa-search"></i><p>No memory entries found matching your search</p></div>';
        return;
    }
    
    memoryContainer.innerHTML = '';
    
    const header = document.createElement('div');
    header.className = 'filtered-entries-header';
    header.innerHTML = `<h3>${title} (${filteredEntries.length} entries)</h3>`;
    
    const list = document.createElement('div');
    list.className = 'filtered-entries-list';
    
    filteredEntries.forEach(entry => {
        const entryCard = createMemoryCard(entry);
        entryCard.style.marginBottom = '10px';
        list.appendChild(entryCard);
    });
    
    memoryContainer.appendChild(header);
    memoryContainer.appendChild(list);
}

// ============================================
// STORAGE OPERATIONS
// ============================================

async function saveMemoryEntryToStorage(entry) {
    // Simulate API call
    // Replace with: await fetch('/api/memory', { method: 'POST', body: JSON.stringify(entry) })
    
    // For demo, save to localStorage
    const existingEntries = JSON.parse(localStorage.getItem('livingai-memory') || '[]');
    const updatedEntries = existingEntries.filter(e => e.id !== entry.id);
    updatedEntries.push(entry);
    localStorage.setItem('livingai-memory', JSON.stringify(updatedEntries));
    
    return entry;
}

async function deleteMemoryEntryFromStorage(entryId) {
    // Simulate API call
    // Replace with: await fetch(`/api/memory/${entryId}`, { method: 'DELETE' })
    
    // For demo, remove from localStorage
    const existingEntries = JSON.parse(localStorage.getItem('livingai-memory') || '[]');
    const updatedEntries = existingEntries.filter(e => e.id !== entryId);
    localStorage.setItem('livingai-memory', JSON.stringify(updatedEntries));
    
    return true;
}

// ============================================
// DASHBOARD INTEGRATION
// ============================================

function updateDashboardMemoryCount() {
    const dashboardMemoryCount = document.getElementById('memory-entries');
    if (dashboardMemoryCount) {
        dashboardMemoryCount.textContent = memoryEntries.length;
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
            const category = item.dataset.categoryId;
            if (category) {
                selectCategory(category);
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

window.initMemory = initMemory;
window.viewMemoryEntry = viewMemoryEntry;
window.editMemoryEntry = editMemoryEntry;
window.deleteMemoryEntry = deleteMemoryEntry;
window.closeMemoryEntryDialog = closeMemoryEntryDialog;
window.saveMemoryEntry = saveMemoryEntry;
window.selectCategory = selectCategory;
