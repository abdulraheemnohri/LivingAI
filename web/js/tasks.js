/**
 * LivingAI - Tasks Management JavaScript
 * =====================================
 * Task CRUD operations, priority management, and status tracking
 */

// ============================================
// TASKS INITIALIZATION
// ============================================

let tasks = [];
let currentTask = null;
let priorities = ['low', 'medium', 'high', 'critical'];
let statuses = ['pending', 'in-progress', 'completed', 'failed', 'cancelled'];

function initTasks() {
    console.log('Initializing Tasks Module...');
    
    // Load tasks data
    loadTasks();
    
    // Initialize form handlers
    initTaskForm();
    
    // Initialize event listeners
    initEventListeners();
    
    // Initialize drag and drop
    initDragAndDrop();
    
    console.log('Tasks Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadTasks() {
    console.log('Loading tasks...');
    
    try {
        // Show loading state
        const tasksContainer = document.getElementById('tasks-container');
        if (tasksContainer) {
            tasksContainer.innerHTML = '<div class="loading-spinner"></div>';
        }
        
        // Fetch tasks from API (or use mock data)
        tasks = await fetchTasks();
        
        // Render tasks
        renderTasks();
        renderTaskStats();
        
        // Update dashboard count
        updateDashboardTasksCount();
        
        console.log(`Loaded ${tasks.length} tasks`);
    } catch (error) {
        console.error('Error loading tasks:', error);
        showError('Failed to load tasks');
        
        // Show empty state
        const tasksContainer = document.getElementById('tasks-container');
        if (tasksContainer) {
            tasksContainer.innerHTML = '<div class="empty-state"><i class="fa fa-tasks"></i><p>No tasks found. Create your first task!</p></div>';
        }
    }
}

async function fetchTasks() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/tasks');
    // return await response.json();
    
    return [
        {
            id: 'task-001',
            title: 'Research Market Trends',
            description: 'Analyze current market trends for AI applications',
            agent: 'Research Agent',
            priority: 'high',
            status: 'completed',
            createdAt: '2024-01-18T10:00:00Z',
            completedAt: '2024-01-18T14:30:00Z',
            dueDate: '2024-01-18T18:00:00Z',
            progress: 100,
            tools: ['web_search', 'data_analysis'],
            result: 'Market analysis completed with 42 data points'
        },
        {
            id: 'task-002',
            title: 'Develop API Integration',
            description: 'Create API integration for external services',
            agent: 'Development Agent',
            priority: 'critical',
            status: 'in-progress',
            createdAt: '2024-01-19T09:00:00Z',
            completedAt: null,
            dueDate: '2024-01-20T17:00:00Z',
            progress: 65,
            tools: ['code_generation', 'api_integration'],
            result: null
        },
        {
            id: 'task-003',
            title: 'Data Cleaning',
            description: 'Clean and preprocess dataset for analysis',
            agent: 'Analysis Agent',
            priority: 'medium',
            status: 'pending',
            createdAt: '2024-01-19T11:00:00Z',
            completedAt: null,
            dueDate: '2024-01-21T12:00:00Z',
            progress: 0,
            tools: ['data_analysis', 'data_cleaning'],
            result: null
        },
        {
            id: 'task-004',
            title: 'Write Documentation',
            description: 'Create documentation for new features',
            agent: 'Creative Agent',
            priority: 'low',
            status: 'in-progress',
            createdAt: '2024-01-19T13:00:00Z',
            completedAt: null,
            dueDate: '2024-01-22T16:00:00Z',
            progress: 30,
            tools: ['content_generation', 'documentation'],
            result: null
        },
        {
            id: 'task-005',
            title: 'Test System Performance',
            description: 'Run performance tests on all components',
            agent: 'General Purpose Agent',
            priority: 'high',
            status: 'pending',
            createdAt: '2024-01-20T08:00:00Z',
            completedAt: null,
            dueDate: '2024-01-20T15:00:00Z',
            progress: 0,
            tools: ['testing', 'performance_analysis'],
            result: null
        },
        {
            id: 'task-006',
            title: 'Translate Documents',
            description: 'Translate technical documents to Urdu',
            agent: 'General Purpose Agent',
            priority: 'medium',
            status: 'completed',
            createdAt: '2024-01-17T14:00:00Z',
            completedAt: '2024-01-18T10:00:00Z',
            dueDate: '2024-01-19T12:00:00Z',
            progress: 100,
            tools: ['translation'],
            result: '15 documents translated successfully'
        }
    ];
}

// ============================================
// RENDERING
// ============================================

function renderTasks() {
    const tasksContainer = document.getElementById('tasks-container');
    if (!tasksContainer) return;
    
    if (tasks.length === 0) {
        tasksContainer.innerHTML = '<div class="empty-state"><i class="fa fa-tasks"></i><p>No tasks found. Create your first task!</p></div>';
        return;
    }
    
    // Group tasks by status
    const groupedTasks = {};
    statuses.forEach(status => {
        groupedTasks[status] = tasks.filter(task => task.status === status);
    });
    
    // Create kanban-style board
    tasksContainer.innerHTML = '';
    
    const board = document.createElement('div');
    board.className = 'tasks-kanban-board';
    
    Object.entries(groupedTasks).forEach(([status, statusTasks]) => {
        const statusColumn = createStatusColumn(status, statusTasks);
        board.appendChild(statusColumn);
    });
    
    tasksContainer.appendChild(board);
}

function createStatusColumn(status, tasksInStatus) {
    const column = document.createElement('div');
    column.className = `tasks-column status-${status}`;
    column.dataset.status = status;
    
    const columnHeader = document.createElement('div');
    columnHeader.className = 'tasks-column-header';
    
    const statusIcons = {
        'pending': 'fa-clock-o',
        'in-progress': 'fa-spinner fa-pulse',
        'completed': 'fa-check-circle',
        'failed': 'fa-times-circle',
        'cancelled': 'fa-ban'
    };
    
    const statusNames = {
        'pending': 'Pending',
        'in-progress': 'In Progress',
        'completed': 'Completed',
        'failed': 'Failed',
        'cancelled': 'Cancelled'
    };
    
    columnHeader.innerHTML = `
        <div class="column-title">
            <i class="fa ${statusIcons[status] || 'fa-tasks'}"></i>
            <h3>${statusNames[status] || status}</h3>
            <span class="task-count">${tasksInStatus.length}</span>
        </div>
        <button class="btn-icon add-task-btn" onclick="showCreateTaskForm('${status}')" title="Add Task">
            <i class="fa fa-plus"></i>
        </button>
    `;
    
    const columnBody = document.createElement('div');
    columnBody.className = 'tasks-column-body';
    
    tasksInStatus.forEach(task => {
        const taskCard = createTaskCard(task);
        columnBody.appendChild(taskCard);
    });
    
    column.appendChild(columnHeader);
    column.appendChild(columnBody);
    
    return column;
}

function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = `task-card priority-${task.priority}`;
    card.dataset.taskId = task.id;
    card.draggable = true;
    
    // Priority indicator
    const priorityIcons = {
        'low': 'fa-arrow-down',
        'medium': 'fa-minus',
        'high': 'fa-arrow-up',
        'critical': 'fa-exclamation'
    };
    
    const priorityNames = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        'critical': 'Critical'
    };
    
    // Progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'task-progress-bar';
    const progressFill = document.createElement('div');
    progressFill.className = 'task-progress-fill';
    progressFill.style.width = `${task.progress}%`;
    progressBar.appendChild(progressFill);
    
    // Due date display
    const dueDateDisplay = getDueDateDisplay(task.dueDate);
    
    card.innerHTML = `
        <div class="task-header">
            <div class="task-priority">
                <i class="fa ${priorityIcons[task.priority]}"></i>
                <span>${priorityNames[task.priority]}</span>
            </div>
            <div class="task-actions">
                <button class="btn-icon" onclick="editTask('${task.id}')" title="Edit">
                    <i class="fa fa-pencil"></i>
                </button>
                <button class="btn-icon" onclick="deleteTask('${task.id}')" title="Delete">
                    <i class="fa fa-trash"></i>
                </button>
            </div>
        </div>
        <div class="task-body">
            <h4>${task.title}</h4>
            <p>${task.description}</p>
        </div>
        <div class="task-footer">
            <div class="task-meta">
                <span class="task-agent"><i class="fa fa-robot"></i> ${task.agent}</span>
                <span class="task-due"><i class="fa fa-calendar"></i> ${dueDateDisplay}</span>
            </div>
            ${task.progress > 0 ? progressBar.outerHTML : ''}
        </div>
    `;
    
    // Add drag and drop attributes
    card.ondragstart = (e) => {
        e.dataTransfer.setData('text/plain', task.id);
        card.classList.add('dragging');
    };
    
    card.ondragend = () => {
        card.classList.remove('dragging');
    };
    
    return card;
}

function getDueDateDisplay(dueDateString) {
    if (!dueDateString) return 'No due date';
    
    const dueDate = new Date(dueDateString);
    const now = new Date();
    const diff = dueDate - now;
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days < 0) {
        return `Overdue (${Math.abs(days)} days ago)`;
    } else if (days === 0) {
        return 'Due today';
    } else if (days === 1) {
        return 'Due tomorrow';
    } else {
        return `Due in ${days} days`;
    }
}

function renderTaskStats() {
    const statsContainer = document.getElementById('task-stats');
    if (!statsContainer) return;
    
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(t => t.status === 'completed').length;
    const inProgressTasks = tasks.filter(t => t.status === 'in-progress').length;
    const pendingTasks = tasks.filter(t => t.status === 'pending').length;
    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    statsContainer.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">${totalTasks}</div>
            <div class="stat-label">Total Tasks</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${completedTasks}</div>
            <div class="stat-label">Completed</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${inProgressTasks}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${pendingTasks}</div>
            <div class="stat-label">Pending</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${completionRate}%</div>
            <div class="stat-label">Completion Rate</div>
        </div>
    `;
}

// ============================================
// FORM HANDLERS
// ============================================

function initTaskForm() {
    // Form submission
    const taskForm = document.getElementById('task-form');
    if (!taskForm) return;
    
    taskForm.addEventListener('submit', handleTaskFormSubmit);
}

function showCreateTaskForm(status = 'pending') {
    const formContainer = document.getElementById('task-form-container');
    if (!formContainer) return;
    
    // Reset form
    resetTaskForm();
    
    // Set default status
    const statusSelect = document.getElementById('task-status');
    if (statusSelect) {
        statusSelect.value = status;
    }
    
    // Show form
    formContainer.style.display = 'block';
    
    // Scroll to form
    formContainer.scrollIntoView({ behavior: 'smooth' });
}

function hideTaskForm() {
    const formContainer = document.getElementById('task-form-container');
    if (formContainer) {
        formContainer.style.display = 'none';
    }
    resetTaskForm();
    currentTask = null;
}

function handleTaskFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const taskData = Object.fromEntries(formData.entries());
    
    // Validate
    if (!taskData.title) {
        showError('Please enter a task title');
        return;
    }
    
    if (currentTask) {
        // Update existing task
        updateTask(currentTask.id, taskData);
    } else {
        // Create new task
        createTask(taskData);
    }
}

function resetTaskForm() {
    const form = document.getElementById('task-form');
    if (form) {
        form.reset();
    }
}

// ============================================
// TASK ACTIONS
// ============================================

function editTask(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) {
        showError('Task not found');
        return;
    }
    
    currentTask = task;
    
    // Pre-fill form
    const form = document.getElementById('task-form');
    if (form) {
        form.elements['task-title'].value = task.title;
        form.elements['task-description'].value = task.description;
        form.elements['task-agent'].value = task.agent;
        form.elements['task-priority'].value = task.priority;
        form.elements['task-status'].value = task.status;
        form.elements['task-due-date'].value = task.dueDate ? task.dueDate.substring(0, 16) : '';
    }
    
    // Show form
    const formContainer = document.getElementById('task-form-container');
    if (formContainer) {
        formContainer.style.display = 'block';
        formContainer.scrollIntoView({ behavior: 'smooth' });
    }
}

async function createTask(taskData) {
    try {
        const newTask = {
            id: `task-${Date.now()}`,
            title: taskData['task-title'],
            description: taskData['task-description'] || '',
            agent: taskData['task-agent'] || 'General Purpose Agent',
            priority: taskData['task-priority'] || 'medium',
            status: taskData['task-status'] || 'pending',
            createdAt: new Date().toISOString(),
            completedAt: null,
            dueDate: taskData['task-due-date'] || null,
            progress: 0,
            tools: [],
            result: null
        };
        
        // Add to tasks list
        tasks.push(newTask);
        
        // Save to storage (or API)
        await saveTask(newTask);
        
        // Update UI
        renderTasks();
        renderTaskStats();
        hideTaskForm();
        updateDashboardTasksCount();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Task Created', `New task "${newTask.title}" has been created`, 'success');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showError('Failed to create task');
    }
}

async function updateTask(taskId, taskData) {
    try {
        const task = tasks.find(t => t.id === taskId);
        if (!task) {
            showError('Task not found');
            return;
        }
        
        // Update task
        task.title = taskData['task-title'];
        task.description = taskData['task-description'] || '';
        task.agent = taskData['task-agent'] || task.agent;
        task.priority = taskData['task-priority'] || task.priority;
        task.status = taskData['task-status'] || task.status;
        task.dueDate = taskData['task-due-date'] || task.dueDate;
        
        // If status changed to completed
        if (task.status === 'completed' && !task.completedAt) {
            task.completedAt = new Date().toISOString();
            task.progress = 100;
        }
        
        // Save changes
        await saveTask(task);
        
        // Update UI
        renderTasks();
        renderTaskStats();
        hideTaskForm();
        currentTask = null;
        updateDashboardTasksCount();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Task Updated', `Task "${task.title}" has been updated`, 'success');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showError('Failed to update task');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const task = tasks.find(t => t.id === taskId);
        if (!task) {
            showError('Task not found');
            return;
        }
        
        // Remove from list
        tasks = tasks.filter(t => t.id !== taskId);
        
        // Delete from storage (or API)
        await deleteTaskFromStorage(taskId);
        
        // Update UI
        renderTasks();
        renderTaskStats();
        updateDashboardTasksCount();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Task Deleted', `Task "${task.title}" has been deleted`, 'success');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showError('Failed to delete task');
    }
}

// ============================================
// DRAG AND DROP
// ============================================

function initDragAndDrop() {
    const columns = document.querySelectorAll('.tasks-column');
    
    columns.forEach(column => {
        column.addEventListener('dragover', (e) => {
            e.preventDefault();
            column.classList.add('drag-over');
        });
        
        column.addEventListener('dragleave', () => {
            column.classList.remove('drag-over');
        });
        
        column.addEventListener('drop', (e) => {
            e.preventDefault();
            column.classList.remove('drag-over');
            
            const taskId = e.dataTransfer.getData('text/plain');
            const newStatus = column.dataset.status;
            
            updateTaskStatus(taskId, newStatus);
        });
    });
}

async function updateTaskStatus(taskId, newStatus) {
    try {
        const task = tasks.find(t => t.id === taskId);
        if (!task) {
            showError('Task not found');
            return;
        }
        
        // Update status
        task.status = newStatus;
        
        // If moved to completed
        if (newStatus === 'completed' && !task.completedAt) {
            task.completedAt = new Date().toISOString();
            task.progress = 100;
        }
        
        // Save changes
        await saveTask(task);
        
        // Update UI
        renderTasks();
        renderTaskStats();
        updateDashboardTasksCount();
        
        // Show success message
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('Task Updated', `Task "${task.title}" status changed to ${newStatus}`, 'success');
        }
    } catch (error) {
        console.error('Error updating task status:', error);
        showError('Failed to update task status');
    }
}

// ============================================
// STORAGE OPERATIONS
// ============================================

async function saveTask(task) {
    // Simulate API call
    // Replace with: await fetch('/api/tasks', { method: 'POST', body: JSON.stringify(task) })
    
    // For demo, save to localStorage
    const existingTasks = JSON.parse(localStorage.getItem('livingai-tasks') || '[]');
    const updatedTasks = existingTasks.filter(t => t.id !== task.id);
    updatedTasks.push(task);
    localStorage.setItem('livingai-tasks', JSON.stringify(updatedTasks));
    
    return task;
}

async function deleteTaskFromStorage(taskId) {
    // Simulate API call
    // Replace with: await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' })
    
    // For demo, remove from localStorage
    const existingTasks = JSON.parse(localStorage.getItem('livingai-tasks') || '[]');
    const updatedTasks = existingTasks.filter(t => t.id !== taskId);
    localStorage.setItem('livingai-tasks', JSON.stringify(updatedTasks));
    
    return true;
}

// ============================================
// DASHBOARD INTEGRATION
// ============================================

function updateDashboardTasksCount() {
    const dashboardTasksCount = document.getElementById('total-tasks');
    if (dashboardTasksCount) {
        const completedCount = tasks.filter(t => t.status === 'completed').length;
        dashboardTasksCount.textContent = completedCount;
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    // Filter by status
    const statusFilter = document.getElementById('task-status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', (e) => {
            filterTasksByStatus(e.target.value);
        });
    }
    
    // Filter by priority
    const priorityFilter = document.getElementById('task-priority-filter');
    if (priorityFilter) {
        priorityFilter.addEventListener('change', (e) => {
            filterTasksByPriority(e.target.value);
        });
    }
    
    // Search
    const searchInput = document.getElementById('task-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchTasks(e.target.value);
        });
    }
}

function filterTasksByStatus(status) {
    if (status === 'all') {
        renderTasks();
        return;
    }
    
    const filteredTasks = tasks.filter(t => t.status === status);
    renderFilteredTasks(filteredTasks, `Status: ${status}`);
}

function filterTasksByPriority(priority) {
    if (priority === 'all') {
        renderTasks();
        return;
    }
    
    const filteredTasks = tasks.filter(t => t.priority === priority);
    renderFilteredTasks(filteredTasks, `Priority: ${priority}`);
}

function searchTasks(query) {
    if (!query) {
        renderTasks();
        return;
    }
    
    const filteredTasks = tasks.filter(t => 
        t.title.toLowerCase().includes(query.toLowerCase()) ||
        t.description.toLowerCase().includes(query.toLowerCase()) ||
        t.agent.toLowerCase().includes(query.toLowerCase())
    );
    
    renderFilteredTasks(filteredTasks, `Search: "${query}"`);
}

function renderFilteredTasks(filteredTasks, title) {
    const tasksContainer = document.getElementById('tasks-container');
    if (!tasksContainer) return;
    
    if (filteredTasks.length === 0) {
        tasksContainer.innerHTML = '<div class="empty-state"><i class="fa fa-search"></i><p>No tasks found matching your criteria</p></div>';
        return;
    }
    
    tasksContainer.innerHTML = '';
    
    const header = document.createElement('div');
    header.className = 'filtered-tasks-header';
    header.innerHTML = `<h3>${title} (${filteredTasks.length} tasks)</h3>`;
    
    const list = document.createElement('div');
    list.className = 'filtered-tasks-list';
    
    filteredTasks.forEach(task => {
        const taskCard = createTaskCard(task);
        taskCard.style.marginBottom = '10px';
        list.appendChild(taskCard);
    });
    
    tasksContainer.appendChild(header);
    tasksContainer.appendChild(list);
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

window.initTasks = initTasks;
window.showCreateTaskForm = showCreateTaskForm;
window.hideTaskForm = hideTaskForm;
window.editTask = editTask;
window.deleteTask = deleteTask;
window.updateTaskStatus = updateTaskStatus;
