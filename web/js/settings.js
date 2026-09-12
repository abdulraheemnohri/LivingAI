/**
 * LivingAI - Settings Management JavaScript
 * ========================================
 * User and security settings persistence, theme management, and preferences
 */

// ============================================
// SETTINGS INITIALIZATION
// ============================================

let settings = {
    // User settings
    user: {
        name: 'Abdulraheem Nohari',
        email: '',
        language: 'en',
        timezone: 'Asia/Karachi'
    },
    // Appearance settings
    appearance: {
        theme: 'dark',
        fontSize: 'medium',
        accentColor: 'primary'
    },
    // Notification settings
    notifications: {
        enabled: true,
        sound: true,
        desktop: true,
        email: false
    },
    // Security settings
    security: {
        lockScreen: false,
        lockTimeout: 30,
        biometricAuth: false,
        twoFactorAuth: false
    },
    // System settings
    system: {
        autoUpdate: true,
        analytics: false,
        errorReporting: true,
        offlineMode: false
    },
    // AI settings
    ai: {
        defaultAgent: 'General Purpose Agent',
        autoStartAgents: true,
        maxConcurrentTasks: 5,
        memoryLimit: '100 MB'
    }
};

function initSettings() {
    console.log('Initializing Settings Module...');
    
    // Load settings from storage
    loadSettings();
    
    // Initialize form handlers
    initSettingsForm();
    
    // Initialize event listeners
    initEventListeners();
    
    // Render settings
    renderSettings();
    
    console.log('Settings Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadSettings() {
    console.log('Loading settings...');
    
    try {
        // Load from localStorage
        const savedSettings = localStorage.getItem('livingai-settings');
        if (savedSettings) {
            settings = { ...settings, ...JSON.parse(savedSettings) };
        }
        
        // Apply settings
        applySettings();
        
        console.log('Settings loaded');
    } catch (error) {
        console.error('Error loading settings:', error);
        showError('Failed to load settings');
    }
}

function applySettings() {
    // Apply theme
    if (settings.appearance.theme) {
        if (window.livingAIApp) {
            window.livingAIApp.setTheme(settings.appearance.theme);
        }
    }
    
    // Apply language
    if (settings.user.language && window.livingAIApp) {
        window.livingAIApp.setLanguage(settings.user.language);
    }
}

// ============================================
// RENDERING
// ============================================

function renderSettings() {
    renderProfileSettings();
    renderAppearanceSettings();
    renderNotificationSettings();
    renderSecuritySettings();
    renderSystemSettings();
    renderAISettings();
}

function renderProfileSettings() {
    const profileSection = document.getElementById('profile-settings');
    if (!profileSection) return;
    
    profileSection.innerHTML = `
        <div class="settings-section">
            <h3><i class="fa fa-user"></i> User Profile</h3>
            <div class="settings-grid">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="setting-user-name" value="${settings.user.name || ''}" placeholder="Enter your name">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="setting-user-email" value="${settings.user.email || ''}" placeholder="Enter your email">
                </div>
                <div class="form-group">
                    <label>Language</label>
                    <select id="setting-user-language">
                        <option value="en" ${settings.user.language === 'en' ? 'selected' : ''}>English</option>
                        <option value="ur" ${settings.user.language === 'ur' ? 'selected' : ''}>اردو (Urdu)</option>
                        <option value="es" ${settings.user.language === 'es' ? 'selected' : ''}>Español</option>
                        <option value="fr" ${settings.user.language === 'fr' ? 'selected' : ''}>Français</option>
                        <option value="ar" ${settings.user.language === 'ar' ? 'selected' : ''}>العربية</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Timezone</label>
                    <select id="setting-user-timezone">
                        <option value="Asia/Karachi" ${settings.user.timezone === 'Asia/Karachi' ? 'selected' : ''}>Asia/Karachi (UTC+5)</option>
                        <option value="UTC" ${settings.user.timezone === 'UTC' ? 'selected' : ''}>UTC</option>
                        <option value="America/New_York" ${settings.user.timezone === 'America/New_York' ? 'selected' : ''}>America/New York (UTC-5)</option>
                        <option value="Europe/London" ${settings.user.timezone === 'Europe/London' ? 'selected' : ''}>Europe/London (UTC+0)</option>
                        <option value="Asia/Tokyo" ${settings.user.timezone === 'Asia/Tokyo' ? 'selected' : ''}>Asia/Tokyo (UTC+9)</option>
                    </select>
                </div>
            </div>
        </div>
    `;
}

function renderAppearanceSettings() {
    const appearanceSection = document.getElementById('appearance-settings');
    if (!appearanceSection) return;
    
    appearanceSection.innerHTML = `
        <div class="settings-section">
            <h3><i class="fa fa-paint-brush"></i> Appearance</h3>
            <div class="settings-grid">
                <div class="form-group">
                    <label>Theme</label>
                    <select id="setting-appearance-theme">
                        <option value="dark" ${settings.appearance.theme === 'dark' ? 'selected' : ''}>Dark</option>
                        <option value="light" ${settings.appearance.theme === 'light' ? 'selected' : ''}>Light</option>
                        <option value="system" ${settings.appearance.theme === 'system' ? 'selected' : ''}>System</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Font Size</label>
                    <select id="setting-appearance-font-size">
                        <option value="small" ${settings.appearance.fontSize === 'small' ? 'selected' : ''}>Small</option>
                        <option value="medium" ${settings.appearance.fontSize === 'medium' ? 'selected' : ''}>Medium</option>
                        <option value="large" ${settings.appearance.fontSize === 'large' ? 'selected' : ''}>Large</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Accent Color</label>
                    <select id="setting-appearance-accent-color">
                        <option value="primary" ${settings.appearance.accentColor === 'primary' ? 'selected' : ''}>Primary (Purple)</option>
                        <option value="blue" ${settings.appearance.accentColor === 'blue' ? 'selected' : ''}>Blue</option>
                        <option value="green" ${settings.appearance.accentColor === 'green' ? 'selected' : ''}>Green</option>
                        <option value="orange" ${settings.appearance.accentColor === 'orange' ? 'selected' : ''}>Orange</option>
                        <option value="red" ${settings.appearance.accentColor === 'red' ? 'selected' : ''}>Red</option>
                    </select>
                </div>
            </div>
        </div>
    `;
}

function renderNotificationSettings() {
    const notificationSection = document.getElementById('notification-settings');
    if (!notificationSection) return;
    
    notificationSection.innerHTML = `
        <div class="settings-section">
            <h3><i class="fa fa-bell"></i> Notifications</h3>
            <div class="settings-grid">
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-notifications-enabled" ${settings.notifications.enabled ? 'checked' : ''}>
                        <span>Enable Notifications</span>
                    </label>
                    <p class="setting-description">Receive notifications for system events and updates</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-notifications-sound" ${settings.notifications.sound ? 'checked' : ''}>
                        <span>Sound</span>
                    </label>
                    <p class="setting-description">Play sound for notifications</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-notifications-desktop" ${settings.notifications.desktop ? 'checked' : ''}>
                        <span>Desktop Notifications</span>
                    </label>
                    <p class="setting-description">Show desktop notifications when app is in background</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-notifications-email" ${settings.notifications.email ? 'checked' : ''}>
                        <span>Email Notifications</span>
                    </label>
                    <p class="setting-description">Send notifications to your email</p>
                </div>
            </div>
        </div>
    `;
}

function renderSecuritySettings() {
    const securitySection = document.getElementById('security-settings');
    if (!securitySection) return;
    
    securitySection.innerHTML = `
        <div class="settings-section">
            <h3><i class="fa fa-lock"></i> Security</h3>
            <div class="settings-grid">
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-security-lock-screen" ${settings.security.lockScreen ? 'checked' : ''}>
                        <span>Lock Screen</span>
                    </label>
                    <p class="setting-description">Enable lock screen when app is inactive</p>
                </div>
                <div class="form-group">
                    <label>Lock Timeout (minutes)</label>
                    <input type="number" id="setting-security-lock-timeout" value="${settings.security.lockTimeout}" min="1" max="60">
                    <p class="setting-description">Time before lock screen activates</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-security-biometric-auth" ${settings.security.biometricAuth ? 'checked' : ''}>
                        <span>Biometric Authentication</span>
                    </label>
                    <p class="setting-description">Use fingerprint or face recognition to unlock</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-security-two-factor-auth" ${settings.security.twoFactorAuth ? 'checked' : ''}>
                        <span>Two-Factor Authentication</span>
                    </label>
                    <p class="setting-description">Require second factor for authentication</p>
                </div>
            </div>
        </div>
    `;
}

function renderSystemSettings() {
    const systemSection = document.getElementById('system-settings');
    if (!systemSection) return;
    
    systemSection.innerHTML = `
        <div class="settings-section">
            <h3><i class="fa fa-cogs"></i> System</h3>
            <div class="settings-grid">
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-system-auto-update" ${settings.system.autoUpdate ? 'checked' : ''}>
                        <span>Auto Update</span>
                    </label>
                    <p class="setting-description">Automatically check for and install updates</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-system-analytics" ${settings.system.analytics ? 'checked' : ''}>
                        <span>Usage Analytics</span>
                    </label>
                    <p class="setting-description">Help improve LivingAI by sending anonymous usage data</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-system-error-reporting" ${settings.system.errorReporting ? 'checked' : ''}>
                        <span>Error Reporting</span>
                    </label>
                    <p class="setting-description">Automatically report errors to help fix bugs</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-system-offline-mode" ${settings.system.offlineMode ? 'checked' : ''}>
                        <span>Offline Mode</span>
                    </label>
                    <p class="setting-description">Enable offline functionality with cached data</p>
                </div>
            </div>
        </div>
    `;
}

function renderAISettings() {
    const aiSection = document.getElementById('ai-settings');
    if (!aiSection) return;
    
    // Get available agents for dropdown
    const agents = window.agents || [];
    const agentOptions = agents.map(agent => 
        `<option value="${agent.name}" ${settings.ai.defaultAgent === agent.name ? 'selected' : ''}>${agent.name}</option>`
    ).join('');
    
    aiSection.innerHTML = `
        <div class="settings-section">
            <h3><i class="fa fa-robot"></i> AI Settings</h3>
            <div class="settings-grid">
                <div class="form-group">
                    <label>Default Agent</label>
                    <select id="setting-ai-default-agent">
                        <option value="General Purpose Agent" ${settings.ai.defaultAgent === 'General Purpose Agent' ? 'selected' : ''}>General Purpose Agent</option>
                        ${agentOptions}
                    </select>
                    <p class="setting-description">Default agent for new tasks</p>
                </div>
                <div class="form-group checkbox-group">
                    <label>
                        <input type="checkbox" id="setting-ai-auto-start-agents" ${settings.ai.autoStartAgents ? 'checked' : ''}>
                        <span>Auto Start Agents</span>
                    </label>
                    <p class="setting-description">Automatically start agents when needed</p>
                </div>
                <div class="form-group">
                    <label>Max Concurrent Tasks</label>
                    <input type="number" id="setting-ai-max-concurrent-tasks" value="${settings.ai.maxConcurrentTasks}" min="1" max="20">
                    <p class="setting-description">Maximum number of tasks that can run simultaneously</p>
                </div>
                <div class="form-group">
                    <label>Memory Limit</label>
                    <select id="setting-ai-memory-limit">
                        <option value="50 MB" ${settings.ai.memoryLimit === '50 MB' ? 'selected' : ''}>50 MB</option>
                        <option value="100 MB" ${settings.ai.memoryLimit === '100 MB' ? 'selected' : ''}>100 MB</option>
                        <option value="250 MB" ${settings.ai.memoryLimit === '250 MB' ? 'selected' : ''}>250 MB</option>
                        <option value="500 MB" ${settings.ai.memoryLimit === '500 MB' ? 'selected' : ''}>500 MB</option>
                        <option value="1 GB" ${settings.ai.memoryLimit === '1 GB' ? 'selected' : ''}>1 GB</option>
                        <option value="Unlimited" ${settings.ai.memoryLimit === 'Unlimited' ? 'selected' : ''}>Unlimited</option>
                    </select>
                    <p class="setting-description">Maximum memory usage for AI operations</p>
                </div>
            </div>
        </div>
    `;
}

// ============================================
// FORM HANDLERS
// ============================================

function initSettingsForm() {
    const settingsForm = document.getElementById('settings-form');
    if (!settingsForm) return;
    
    settingsForm.addEventListener('submit', handleSettingsFormSubmit);
}

function handleSettingsFormSubmit(e) {
    e.preventDefault();
    
    // Collect all settings from form
    const newSettings = {
        user: {
            name: document.getElementById('setting-user-name').value,
            email: document.getElementById('setting-user-email').value,
            language: document.getElementById('setting-user-language').value,
            timezone: document.getElementById('setting-user-timezone').value
        },
        appearance: {
            theme: document.getElementById('setting-appearance-theme').value,
            fontSize: document.getElementById('setting-appearance-font-size').value,
            accentColor: document.getElementById('setting-appearance-accent-color').value
        },
        notifications: {
            enabled: document.getElementById('setting-notifications-enabled').checked,
            sound: document.getElementById('setting-notifications-sound').checked,
            desktop: document.getElementById('setting-notifications-desktop').checked,
            email: document.getElementById('setting-notifications-email').checked
        },
        security: {
            lockScreen: document.getElementById('setting-security-lock-screen').checked,
            lockTimeout: parseInt(document.getElementById('setting-security-lock-timeout').value) || 30,
            biometricAuth: document.getElementById('setting-security-biometric-auth').checked,
            twoFactorAuth: document.getElementById('setting-security-two-factor-auth').checked
        },
        system: {
            autoUpdate: document.getElementById('setting-system-auto-update').checked,
            analytics: document.getElementById('setting-system-analytics').checked,
            errorReporting: document.getElementById('setting-system-error-reporting').checked,
            offlineMode: document.getElementById('setting-system-offline-mode').checked
        },
        ai: {
            defaultAgent: document.getElementById('setting-ai-default-agent').value,
            autoStartAgents: document.getElementById('setting-ai-auto-start-agents').checked,
            maxConcurrentTasks: parseInt(document.getElementById('setting-ai-max-concurrent-tasks').value) || 5,
            memoryLimit: document.getElementById('setting-ai-memory-limit').value
        }
    };
    
    // Update settings
    settings = newSettings;
    
    // Save settings
    saveSettings();
    
    // Apply settings
    applySettings();
    
    // Show success message
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Settings Saved', 'Your settings have been saved successfully', 'success');
    }
}

async function saveSettings() {
    try {
        // Save to localStorage
        localStorage.setItem('livingai-settings', JSON.stringify(settings));
        
        // Simulate API call for server-side settings
        // Replace with: await fetch('/api/settings', { method: 'POST', body: JSON.stringify(settings) })
        
        console.log('Settings saved');
    } catch (error) {
        console.error('Error saving settings:', error);
        showError('Failed to save settings');
    }
}

// ============================================
// SETTINGS ACTIONS
// ============================================

function resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to default?')) {
        return;
    }
    
    // Reset to default settings
    settings = {
        user: {
            name: 'Abdulraheem Nohari',
            email: '',
            language: 'en',
            timezone: 'Asia/Karachi'
        },
        appearance: {
            theme: 'dark',
            fontSize: 'medium',
            accentColor: 'primary'
        },
        notifications: {
            enabled: true,
            sound: true,
            desktop: true,
            email: false
        },
        security: {
            lockScreen: false,
            lockTimeout: 30,
            biometricAuth: false,
            twoFactorAuth: false
        },
        system: {
            autoUpdate: true,
            analytics: false,
            errorReporting: true,
            offlineMode: false
        },
        ai: {
            defaultAgent: 'General Purpose Agent',
            autoStartAgents: true,
            maxConcurrentTasks: 5,
            memoryLimit: '100 MB'
        }
    };
    
    // Save and apply
    saveSettings();
    applySettings();
    renderSettings();
    
    // Show success message
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Settings Reset', 'All settings have been reset to default', 'success');
    }
}

function exportSettings() {
    const data = JSON.stringify(settings, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `livingai-settings-${new Date().toISOString().substring(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Settings Exported', 'Settings have been exported successfully', 'success');
    }
}

function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const importedSettings = JSON.parse(event.target.result);
                settings = { ...settings, ...importedSettings };
                
                saveSettings();
                applySettings();
                renderSettings();
                
                if (window.livingAIApp) {
                    window.livingAIApp.addNotification('Settings Imported', 'Settings have been imported successfully', 'success');
                }
            } catch (error) {
                console.error('Error importing settings:', error);
                showError('Failed to import settings. Invalid file format.');
            }
        };
        
        reader.readAsText(file);
    };
    
    input.click();
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    // Reset button
    const resetBtn = document.getElementById('reset-settings-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetSettings);
    }
    
    // Export button
    const exportBtn = document.getElementById('export-settings-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportSettings);
    }
    
    // Import button
    const importBtn = document.getElementById('import-settings-btn');
    if (importBtn) {
        importBtn.addEventListener('click', importSettings);
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

window.initSettings = initSettings;
window.resetSettings = resetSettings;
window.exportSettings = exportSettings;
window.importSettings = importSettings;
