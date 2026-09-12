/**
 * LivingAI - Main Application JavaScript
 * =================================
 * Core application initialization, routing, and theme management
 */

// ============================================
// APPLICATION INITIALIZATION
// ============================================

class LivingAIApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.isSidebarCollapsed = true;
        this.isMobileMenuOpen = false;
        this.theme = localStorage.getItem('livingai-theme') || 'dark';
        this.language = localStorage.getItem('livingai-language') || 'en';
        
        // Initialize all components
        this.init();
    }

    init() {
        console.log('Initializing LivingAI Application...');
        
        // Set theme
        this.setTheme(this.theme);
        
        // Initialize components
        this.initSidebar();
        this.initTopBar();
        this.initRouting();
        this.initTimeDisplay();
        this.initSystemStats();
        this.initNotifications();
        this.initLoadingScreen();
        
        // Load initial data
        this.loadInitialData();
        
        // Hide loading screen and show main content
        setTimeout(() => {
            this.hideLoadingScreen();
        }, 1500);
        
        console.log('LivingAI Application Initialized');
    }

    // ============================================
    // THEME MANAGEMENT
    // ============================================

    setTheme(theme) {
        this.theme = theme;
        localStorage.setItem('livingai-theme', theme);
        
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
            document.body.classList.remove('light-theme');
        } else {
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
        }
        
        // Update theme toggle button
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.innerHTML = theme === 'dark' ? '<i class="fa fa-sun-o"></i>' : '<i class="fa fa-moon-o"></i>';
        }
    }

    toggleTheme() {
        this.setTheme(this.theme === 'dark' ? 'light' : 'dark');
    }

    // ============================================
    // SIDEBAR MANAGEMENT
    // ============================================

    initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
        
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
        
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => this.toggleMobileMenu());
        }
        
        // Menu item click handlers
        const menuItems = document.querySelectorAll('.menu-items a[data-page]');
        menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.getAttribute('data-page');
                this.navigateTo(page);
                
                // Close mobile menu if open
                if (this.isMobileMenuOpen) {
                    this.closeMobileMenu();
                }
            });
        });
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        this.isSidebarCollapsed = !this.isSidebarCollapsed;
        
        if (this.isSidebarCollapsed) {
            sidebar.classList.add('collapsed');
            sidebar.classList.remove('expanded');
        } else {
            sidebar.classList.remove('collapsed');
            sidebar.classList.add('expanded');
        }
        
        localStorage.setItem('livingai-sidebar-collapsed', this.isSidebarCollapsed);
    }

    toggleMobileMenu() {
        this.isMobileMenuOpen = !this.isMobileMenuOpen;
        
        if (this.isMobileMenuOpen) {
            this.openMobileMenu();
        } else {
            this.closeMobileMenu();
        }
    }

    openMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.add('mobile-open');
        document.body.classList.add('mobile-menu-open');
    }

    closeMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.remove('mobile-open');
        document.body.classList.remove('mobile-menu-open');
        this.isMobileMenuOpen = false;
    }

    // ============================================
    // TOP BAR MANAGEMENT
    // ============================================

    initTopBar() {
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Notifications toggle
        const notificationsToggle = document.getElementById('notifications-toggle');
        if (notificationsToggle) {
            notificationsToggle.addEventListener('click', () => this.toggleNotifications());
        }
    }

    toggleNotifications() {
        const notificationsPanel = document.getElementById('notifications-panel');
        if (notificationsPanel) {
            notificationsPanel.classList.toggle('show');
        }
    }

    // ============================================
    // ROUTING & NAVIGATION
    // ============================================

    initRouting() {
        // Handle hash-based navigation
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.substring(1);
            if (hash) {
                this.navigateTo(hash);
            }
        });
        
        // Handle initial hash
        const initialHash = window.location.hash.substring(1);
        if (initialHash) {
            this.navigateTo(initialHash);
        }
        
        // Handle back/forward navigation
        window.addEventListener('popstate', () => {
            const hash = window.location.hash.substring(1);
            if (hash) {
                this.navigateTo(hash);
            } else {
                this.navigateTo('dashboard');
            }
        });
    }

    navigateTo(page) {
        // Check if page exists
        const pageElement = document.getElementById(page);
        if (!pageElement) {
            console.warn(`Page "${page}" not found`);
            return;
        }
        
        // Update current page
        this.currentPage = page;
        window.location.hash = page;
        
        // Update UI
        this.updateActivePage();
        this.updateBreadcrumb();
        
        // Load page-specific data
        this.loadPageData(page);
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    updateActivePage() {
        // Hide all pages
        const pages = document.querySelectorAll('.page');
        pages.forEach(page => page.classList.remove('active'));
        
        // Show current page
        const currentPage = document.getElementById(this.currentPage);
        if (currentPage) {
            currentPage.classList.add('active');
        }
        
        // Update menu active state
        const menuItems = document.querySelectorAll('.menu-items li');
        menuItems.forEach(item => {
            const link = item.querySelector('a');
            if (link && link.getAttribute('data-page') === this.currentPage) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    updateBreadcrumb() {
        const breadcrumb = document.getElementById('current-page');
        if (breadcrumb) {
            const pageNames = {
                'dashboard': 'Dashboard',
                'agents': 'Agents',
                'tools': 'Tools',
                'tasks': 'Tasks',
                'memory': 'Memory',
                'settings': 'Settings',
                'terminal': 'Terminal',
                'logs': 'Logs',
                'analytics': 'Analytics',
                'documentation': 'Documentation',
                'about': 'About'
            };
            breadcrumb.textContent = pageNames[this.currentPage] || this.currentPage;
        }
    }

    loadPageData(page) {
        console.log(`Loading data for page: ${page}`);
        
        // Page-specific initialization
        switch (page) {
            case 'dashboard':
                if (typeof initDashboard === 'function') initDashboard();
                break;
            case 'agents':
                if (typeof initAgents === 'function') initAgents();
                break;
            case 'tools':
                if (typeof initTools === 'function') initTools();
                break;
            case 'tasks':
                if (typeof initTasks === 'function') initTasks();
                break;
            case 'memory':
                if (typeof initMemory === 'function') initMemory();
                break;
            case 'settings':
                if (typeof initSettings === 'function') initSettings();
                break;
            case 'terminal':
                if (typeof initTerminal === 'function') initTerminal();
                break;
            case 'logs':
                if (typeof initLogs === 'function') initLogs();
                break;
            case 'analytics':
                if (typeof initAnalytics === 'function') initAnalytics();
                break;
        }
    }

    // ============================================
    // TIME DISPLAY
    // ============================================

    initTimeDisplay() {
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);
    }

    updateTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            timeElement.textContent = `${hours}:${minutes}:${seconds}`;
        }
    }

    // ============================================
    // SYSTEM STATS
    // ============================================

    initSystemStats() {
        // Simulate system stats (replace with real API calls)
        this.updateSystemStats();
        setInterval(() => this.updateSystemStats(), 5000);
    }

    updateSystemStats() {
        // CPU Usage
        const cpuUsage = Math.floor(Math.random() * 30) + 10;
        const cpuElement = document.getElementById('cpu-usage');
        const cpuBar = document.getElementById('cpu-bar');
        if (cpuElement) cpuElement.textContent = `${cpuUsage}%`;
        if (cpuBar) cpuBar.style.width = `${cpuUsage}%`;
        
        // Memory Usage
        const memoryUsage = Math.floor(Math.random() * 40) + 20;
        const memoryElement = document.getElementById('memory-usage');
        const memoryBar = document.getElementById('memory-bar');
        if (memoryElement) memoryElement.textContent = `${memoryUsage}%`;
        if (memoryBar) memoryBar.style.width = `${memoryUsage}%`;
        
        // Storage Usage
        const storageUsage = Math.floor(Math.random() * 60) + 10;
        const storageBar = document.getElementById('storage-bar');
        if (storageBar) storageBar.style.width = `${storageUsage}%`;
    }

    // ============================================
    // NOTIFICATIONS
    // ============================================

    initNotifications() {
        // Load notifications from storage
        this.notifications = JSON.parse(localStorage.getItem('livingai-notifications') || '[]');
        this.updateNotificationCount();
    }

    addNotification(title, message, type = 'info') {
        const notification = {
            id: Date.now(),
            title,
            message,
            type,
            time: new Date().toISOString(),
            read: false
        };
        
        this.notifications.unshift(notification);
        localStorage.setItem('livingai-notifications', JSON.stringify(this.notifications));
        this.updateNotificationCount();
        this.showNotificationToast(notification);
    }

    updateNotificationCount() {
        const countElement = document.getElementById('notification-count');
        if (countElement) {
            const unreadCount = this.notifications.filter(n => !n.read).length;
            countElement.textContent = unreadCount;
            countElement.style.display = unreadCount > 0 ? 'inline' : 'none';
        }
    }

    showNotificationToast(notification) {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${notification.type}`;
        toast.innerHTML = `
            <i class="fa fa-${this.getNotificationIcon(notification.type)}"></i>
            <div class="toast-content">
                <h4>${notification.title}</h4>
                <p>${notification.message}</p>
            </div>
            <button class="toast-close" onclick="this.closeToast()"><i class="fa fa-times"></i></button>
        `;
        
        toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'times-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'bell';
    }

    // ============================================
    // LOADING SCREEN
    // ============================================

    initLoadingScreen() {
        // Animate loading bar
        const loadingBar = document.querySelector('.loading-progress');
        if (loadingBar) {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                }
                loadingBar.style.width = `${progress}%`;
            }, 300);
        }
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        const mainContainer = document.getElementById('main-container');
        
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        }
        
        if (mainContainer) {
            mainContainer.style.display = 'block';
        }
    }

    // ============================================
    // DATA LOADING
    // ============================================

    loadInitialData() {
        console.log('Loading initial data...');
        
        // Load agents count
        this.loadAgentsCount();
        
        // Load tools count
        this.loadToolsCount();
        
        // Load tasks count
        this.loadTasksCount();
        
        // Load memory entries count
        this.loadMemoryCount();
    }

    loadAgentsCount() {
        // Simulate API call (replace with real API)
        setTimeout(() => {
            const count = Math.floor(Math.random() * 10) + 3;
            const element = document.getElementById('total-agents');
            if (element) {
                this.animateNumber(element, 0, count, 1000);
            }
        }, 500);
    }

    loadToolsCount() {
        // Simulate API call
        setTimeout(() => {
            const count = Math.floor(Math.random() * 50) + 20;
            const element = document.getElementById('total-tools');
            if (element) {
                this.animateNumber(element, 0, count, 1000);
            }
        }, 700);
    }

    loadTasksCount() {
        // Simulate API call
        setTimeout(() => {
            const count = Math.floor(Math.random() * 100) + 50;
            const element = document.getElementById('total-tasks');
            if (element) {
                this.animateNumber(element, 0, count, 1000);
            }
        }, 900);
    }

    loadMemoryCount() {
        // Simulate API call
        setTimeout(() => {
            const count = Math.floor(Math.random() * 1000) + 500;
            const element = document.getElementById('memory-entries');
            if (element) {
                this.animateNumber(element, 0, count, 1000);
            }
        }, 1100);
    }

    animateNumber(element, start, end, duration) {
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

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================

    showLoading() {
        const loadingOverlay = document.getElementById('loading-overlay') || this.createLoadingOverlay();
        loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
        return overlay;
    }

    // ============================================
    // URDU LANGUAGE SUPPORT
    // ============================================

    setLanguage(lang) {
        this.language = lang;
        localStorage.setItem('livingai-language', lang);
        this.updateUILanguage();
    }

    updateUILanguage() {
        // This would update all UI text based on language
        // Implementation depends on your i18n strategy
        console.log(`Language set to: ${this.language}`);
    }
}

// ============================================
// GLOBAL FUNCTIONS
// ============================================

// Initialize application when DOM is ready
let livingAIApp;

document.addEventListener('DOMContentLoaded', () => {
    livingAIApp = new LivingAIApp();
});

// Global navigation functions (called from HTML onclick)
function startAgent() {
    if (livingAIApp) {
        livingAIApp.navigateTo('agents');
        livingAIApp.addNotification('Agent Started', 'New AI agent has been started successfully', 'success');
    }
}

function runTask() {
    if (livingAIApp) {
        livingAIApp.navigateTo('tasks');
        livingAIApp.addNotification('Task Created', 'New task has been added to the queue', 'info');
    }
}

function openTerminal() {
    if (livingAIApp) {
        livingAIApp.navigateTo('terminal');
    }
}

function clearMemory() {
    if (livingAIApp) {
        livingAIApp.showLoading();
        setTimeout(() => {
            livingAIApp.hideLoading();
            livingAIApp.addNotification('Cache Cleared', 'System cache has been cleared', 'success');
        }, 1000);
    }
}

// Make app globally accessible
window.LivingAIApp = LivingAIApp;
window.livingAIApp = livingAIApp;
