/**
 * LivingAI - About Page JavaScript
 * ==============================
 * About page with system information, credits, and contact details
 */

// ============================================
// ABOUT INITIALIZATION
// ============================================

let systemInfo = {};

function initAbout() {
    console.log('Initializing About Module...');
    
    // Load system information
    loadSystemInfo();
    
    // Initialize event listeners
    initEventListeners();
    
    // Render about page
    renderAboutPage();
    
    console.log('About Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadSystemInfo() {
    console.log('Loading system information...');
    
    try {
        systemInfo = await fetchSystemInfo();
        console.log('System information loaded');
    } catch (error) {
        console.error('Error loading system info:', error);
        // Use default values
        systemInfo = getDefaultSystemInfo();
    }
}

async function fetchSystemInfo() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/system/info');
    // return await response.json();
    
    return {
        version: '1.0.0',
        build: '20240120.1',
        environment: 'production',
        platform: 'Android',
        architecture: 'ARM64',
        nodeVersion: '16.20.1',
        pythonVersion: '3.11.4',
        dependencies: {
            backend: 42,
            frontend: 15,
            total: 57
        },
        memory: {
            total: '2.5 GB',
            used: '1.2 GB',
            available: '1.3 GB'
        },
        storage: {
            total: '128 GB',
            used: '45 GB',
            available: '83 GB'
        },
        uptime: '24 days, 3 hours, 15 minutes',
        lastUpdate: '2024-01-20T16:30:00Z',
        features: [
            'AI Agents',
            'Tool Integration',
            'Task Management',
            'Memory System',
            'Terminal Interface',
            'Analytics Dashboard',
            'Multi-language Support',
            'Offline Mode',
            'Custom Tools',
            'Web Interface',
            'Android App',
            'API Access'
        ]
    };
}

function getDefaultSystemInfo() {
    return {
        version: '1.0.0',
        build: '20240120.1',
        environment: 'development',
        platform: 'Unknown',
        architecture: 'Unknown',
        dependencies: {
            backend: 0,
            frontend: 0,
            total: 0
        },
        memory: {
            total: 'Unknown',
            used: 'Unknown',
            available: 'Unknown'
        },
        storage: {
            total: 'Unknown',
            used: 'Unknown',
            available: 'Unknown'
        },
        uptime: 'Unknown',
        lastUpdate: 'Unknown',
        features: []
    };
}

// ============================================
// RENDERING
// ============================================

function renderAboutPage() {
    const aboutContainer = document.getElementById('about-container');
    if (!aboutContainer) return;
    
    aboutContainer.innerHTML = '';
    
    // System Information Section
    const systemInfoSection = createSystemInfoSection();
    aboutContainer.appendChild(systemInfoSection);
    
    // Features Section
    const featuresSection = createFeaturesSection();
    aboutContainer.appendChild(featuresSection);
    
    // Team Section
    const teamSection = createTeamSection();
    aboutContainer.appendChild(teamSection);
    
    // Credits Section
    const creditsSection = createCreditsSection();
    aboutContainer.appendChild(creditsSection);
    
    // Contact Section
    const contactSection = createContactSection();
    aboutContainer.appendChild(contactSection);
    
    // License Section
    const licenseSection = createLicenseSection();
    aboutContainer.appendChild(licenseSection);
}

function createSystemInfoSection() {
    const section = document.createElement('div');
    section.className = 'about-section';
    
    const info = systemInfo;
    
    section.innerHTML = `
        <div class="section-header">
            <h2><i class="fa fa-info-circle"></i> System Information</h2>
            <p>LivingAI Local AI Operating System</p>
        </div>
        <div class="section-content">
            <div class="info-grid">
                <div class="info-card">
                    <div class="info-icon bg-primary">
                        <i class="fa fa-code"></i>
                    </div>
                    <div class="info-content">
                        <h4>Version</h4>
                        <p>${info.version}</p>
                        <p class="info-subtitle">Build: ${info.build}</p>
                    </div>
                </div>
                <div class="info-card">
                    <div class="info-icon bg-success">
                        <i class="fa fa-server"></i>
                    </div>
                    <div class="info-content">
                        <h4>Environment</h4>
                        <p>${info.environment}</p>
                        <p class="info-subtitle">${info.platform} (${info.architecture})</p>
                    </div>
                </div>
                <div class="info-card">
                    <div class="info-icon bg-info">
                        <i class="fa fa-clock-o"></i>
                    </div>
                    <div class="info-content">
                        <h4>Uptime</h4>
                        <p>${info.uptime}</p>
                        <p class="info-subtitle">Last Update: ${formatDate(info.lastUpdate)}</p>
                    </div>
                </div>
                <div class="info-card">
                    <div class="info-icon bg-warning">
                        <i class="fa fa-package"></i>
                    </div>
                    <div class="info-content">
                        <h4>Dependencies</h4>
                        <p>${info.dependencies.total} Total</p>
                        <p class="info-subtitle">Backend: ${info.dependencies.backend}, Frontend: ${info.dependencies.frontend}</p>
                    </div>
                </div>
            </div>
            
            <div class="info-details">
                <div class="detail-row">
                    <div class="detail-item">
                        <span class="detail-label">Memory Usage</span>
                        <span class="detail-value">${info.memory.used} / ${info.memory.total}</span>
                        <div class="detail-bar">
                            <div class="detail-progress" style="width: ${calculatePercentage(info.memory.used, info.memory.total)}%"></div>
                        </div>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Storage Usage</span>
                        <span class="detail-value">${info.storage.used} / ${info.storage.total}</span>
                        <div class="detail-bar">
                            <div class="detail-progress" style="width: ${calculatePercentage(info.storage.used, info.storage.total)}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return section;
}

function calculatePercentage(used, total) {
    // Extract numeric values
    const usedValue = extractNumericValue(used);
    const totalValue = extractNumericValue(total);
    
    if (totalValue === 0) return 0;
    
    return Math.min(100, Math.round((usedValue / totalValue) * 100));
}

function extractNumericValue(text) {
    if (!text) return 0;
    
    // Extract number from text like "1.2 GB" or "45 GB"
    const match = text.match(/([\d.]+)/);
    if (match) {
        return parseFloat(match[1]);
    }
    
    return 0;
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    return date.toLocaleString();
}

function createFeaturesSection() {
    const section = document.createElement('div');
    section.className = 'about-section';
    
    const features = systemInfo.features || [];
    
    section.innerHTML = `
        <div class="section-header">
            <h2><i class="fa fa-star"></i> Features</h2>
            <p>What LivingAI can do for you</p>
        </div>
        <div class="section-content">
            <div class="features-grid">
                ${features.map(feature => `
                    <div class="feature-card">
                        <i class="fa fa-check-circle"></i>
                        <span>${feature}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    return section;
}

function createTeamSection() {
    const section = document.createElement('div');
    section.className = 'about-section';
    
    section.innerHTML = `
        <div class="section-header">
            <h2><i class="fa fa-users"></i> Team</h2>
            <p>Meet the people behind LivingAI</p>
        </div>
        <div class="section-content">
            <div class="team-grid">
                <div class="team-member">
                    <div class="member-avatar">
                        <i class="fa fa-user-circle"></i>
                    </div>
                    <div class="member-info">
                        <h4>Abdulraheem Nohari</h4>
                        <p>Founder & Lead Developer</p>
                        <p class="member-description">Visionary behind LivingAI with expertise in AI, Android development, and system architecture.</p>
                    </div>
                </div>
                <div class="team-member">
                    <div class="member-avatar">
                        <i class="fa fa-users"></i>
                    </div>
                    <div class="member-info">
                        <h4>Contributors</h4>
                        <p>Open Source Community</p>
                        <p class="member-description">A growing community of developers, testers, and enthusiasts contributing to LivingAI.</p>
                    </div>
                </div>
            </div>
            
            <div class="team-stats">
                <div class="stat-item">
                    <div class="stat-value">1</div>
                    <div class="stat-label">Core Developer</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">10+</div>
                    <div class="stat-label">Contributors</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">100+</div>
                    <div class="stat-label">Stars on GitHub</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">1000+</div>
                    <div class="stat-label">Users</div>
                </div>
            </div>
        </div>
    `;
    
    return section;
}

function createCreditsSection() {
    const section = document.createElement('div');
    section.className = 'about-section';
    
    section.innerHTML = `
        <div class="section-header">
            <h2><i class="fa fa-heart"></i> Credits</h2>
            <p>Acknowledgements and Special Thanks</p>
        </div>
        <div class="section-content">
            <div class="credits-grid">
                <div class="credit-card">
                    <div class="credit-icon bg-primary">
                        <i class="fa fa-github"></i>
                    </div>
                    <div class="credit-content">
                        <h4>GitHub</h4>
                        <p>For hosting our open source project and providing powerful development tools.</p>
                    </div>
                </div>
                <div class="credit-card">
                    <div class="credit-icon bg-success">
                        <i class="fa fa-open-source"></i>
                    </div>
                    <div class="credit-content">
                        <h4>Open Source Community</h4>
                        <p>For the amazing open source libraries and frameworks that power LivingAI.</p>
                    </div>
                </div>
                <div class="credit-card">
                    <div class="credit-icon bg-info">
                        <i class="fa fa-font-awesome"></i>
                    </div>
                    <div class="credit-content">
                        <h4>Font Awesome</h4>
                        <p>For the beautiful icons used throughout the application.</p>
                    </div>
                </div>
                <div class="credit-card">
                    <div class="credit-icon bg-warning">
                        <i class="fa fa-chart-line"></i>
                    </div>
                    <div class="credit-content">
                        <h4>Chart.js</h4>
                        <p>For the powerful and flexible charting library used in analytics.</p>
                    </div>
                </div>
                <div class="credit-card">
                    <div class="credit-icon bg-danger">
                        <i class="fa fa-python"></i>
                    </div>
                    <div class="credit-content">
                        <h4>Python Software Foundation</h4>
                        <p>For the Python programming language that powers our backend.</p>
                    </div>
                </div>
                <div class="credit-card">
                    <div class="credit-icon bg-secondary">
                        <i class="fa fa-android"></i>
                    </div>
                    <div class="credit-content">
                        <h4>Android</h4>
                        <p>For the Android platform that hosts our mobile application.</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return section;
}

function createContactSection() {
    const section = document.createElement('div');
    section.className = 'about-section';
    
    section.innerHTML = `
        <div class="section-header">
            <h2><i class="fa fa-envelope"></i> Contact</h2>
            <p>Get in touch with us</p>
        </div>
        <div class="section-content">
            <div class="contact-grid">
                <div class="contact-card">
                    <div class="contact-icon bg-primary">
                        <i class="fa fa-github"></i>
                    </div>
                    <div class="contact-content">
                        <h4>GitHub</h4>
                        <p>View source code, report issues, and contribute</p>
                        <a href="https://github.com/abdulraheemnohri/LivingAI" target="_blank" class="contact-link">
                            <i class="fa fa-external-link"></i> github.com/abdulraheemnohri/LivingAI
                        </a>
                    </div>
                </div>
                <div class="contact-card">
                    <div class="contact-icon bg-success">
                        <i class="fa fa-discord"></i>
                    </div>
                    <div class="contact-content">
                        <h4>Discord</h4>
                        <p>Join our community for discussions and support</p>
                        <a href="https://discord.gg/livingai" target="_blank" class="contact-link">
                            <i class="fa fa-external-link"></i> discord.gg/livingai
                        </a>
                    </div>
                </div>
                <div class="contact-card">
                    <div class="contact-icon bg-info">
                        <i class="fa fa-twitter"></i>
                    </div>
                    <div class="contact-content">
                        <h4>Twitter</h4>
                        <p>Follow us for updates and announcements</p>
                        <a href="https://twitter.com/LivingAI" target="_blank" class="contact-link">
                            <i class="fa fa-external-link"></i> @LivingAI
                        </a>
                    </div>
                </div>
                <div class="contact-card">
                    <div class="contact-icon bg-warning">
                        <i class="fa fa-envelope"></i>
                    </div>
                    <div class="contact-content">
                        <h4>Email</h4>
                        <p>For business inquiries and support</p>
                        <a href="mailto:contact@livingai.dev" class="contact-link">
                            <i class="fa fa-external-link"></i> contact@livingai.dev
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return section;
}

function createLicenseSection() {
    const section = document.createElement('div');
    section.className = 'about-section';
    
    section.innerHTML = `
        <div class="section-header">
            <h2><i class="fa fa-file-text"></i> License</h2>
            <p>Legal information and permissions</p>
        </div>
        <div class="section-content">
            <div class="license-card">
                <div class="license-header">
                    <h3>MIT License</h3>
                    <p>Copyright (c) 2024 Abdulraheem Nohari</p>
                </div>
                <div class="license-body">
                    <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>
                    
                    <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>
                    
                    <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>
                </div>
                <div class="license-footer">
                    <a href="https://opensource.org/licenses/MIT" target="_blank" class="license-link">
                        <i class="fa fa-external-link"></i> View Full License
                    </a>
                </div>
            </div>
        </div>
    `;
    
    return section;
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    // Check for updates button
    const checkUpdatesBtn = document.getElementById('check-updates-btn');
    if (checkUpdatesBtn) {
        checkUpdatesBtn.addEventListener('click', checkForUpdates);
    }
    
    // System info refresh button
    const refreshBtn = document.getElementById('refresh-system-info-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshSystemInfo);
    }
}

async function checkForUpdates() {
    try {
        // Simulate update check
        const hasUpdate = await checkUpdates();
        
        if (hasUpdate) {
            if (window.livingAIApp) {
                window.livingAIApp.addNotification('Update Available', 'A new version of LivingAI is available', 'info');
            }
        } else {
            if (window.livingAIApp) {
                window.livingAIApp.addNotification('Up to Date', 'You are using the latest version of LivingAI', 'success');
            }
        }
    } catch (error) {
        console.error('Error checking for updates:', error);
        showError('Failed to check for updates');
    }
}

async function checkUpdates() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/system/updates');
    // return (await response.json()).hasUpdate;
    
    // For demo, return false (no update)
    return false;
}

async function refreshSystemInfo() {
    try {
        // Reload system info
        await loadSystemInfo();
        renderAboutPage();
        
        if (window.livingAIApp) {
            window.livingAIApp.addNotification('System Info Refreshed', 'System information has been updated', 'success');
        }
    } catch (error) {
        console.error('Error refreshing system info:', error);
        showError('Failed to refresh system information');
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

window.initAbout = initAbout;
window.checkForUpdates = checkForUpdates;
window.refreshSystemInfo = refreshSystemInfo;
