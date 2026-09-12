package com.livingai.app.utils

/**
 * Constants for the LivingAI application
 */
object Constants {

    // App constants
    const val APP_NAME = "LivingAI"
    const val APP_VERSION = "1.0.0"
    const val APP_BUILD = "20240120.1"
    const val APP_PACKAGE = "com.livingai.app"

    // API constants
    const val BASE_API_URL = "https://api.livingai.local/v1/"
    const val API_TIMEOUT = 30L // seconds
    const val API_RETRY_COUNT = 3
    const val API_RETRY_DELAY = 1000L // milliseconds

    // Database constants
    const val DATABASE_NAME = "livingai.db"
    const val DATABASE_VERSION = 1
    const val DATABASE_MAX_SIZE = 100L // MB

    // Agent constants
    const val AGENT_STATUS_ACTIVE = "active"
    const val AGENT_STATUS_INACTIVE = "inactive"
    const val AGENT_STATUS_PAUSED = "paused"
    const val AGENT_STATUS_ERROR = "error"

    // Task constants
    const val TASK_STATUS_PENDING = "pending"
    const val TASK_STATUS_IN_PROGRESS = "in-progress"
    const val TASK_STATUS_COMPLETED = "completed"
    const val TASK_STATUS_FAILED = "failed"
    const val TASK_STATUS_CANCELLED = "cancelled"

    // Priority constants
    const val PRIORITY_LOW = "low"
    const val PRIORITY_MEDIUM = "medium"
    const val PRIORITY_HIGH = "high"
    const val PRIORITY_CRITICAL = "critical"

    // Tool constants
    const val TOOL_STATUS_ENABLED = "enabled"
    const val TOOL_STATUS_DISABLED = "disabled"

    // Memory constants
    const val MEMORY_CATEGORY_KNOWLEDGE = "knowledge"
    const val MEMORY_CATEGORY_CONVERSATIONS = "conversations"
    const val MEMORY_CATEGORY_SETTINGS = "settings"
    const val MEMORY_CATEGORY_CACHE = "cache"

    // Log constants
    const val LOG_LEVEL_DEBUG = "debug"
    const val LOG_LEVEL_INFO = "info"
    const val LOG_LEVEL_WARNING = "warning"
    const val LOG_LEVEL_ERROR = "error"
    const val LOG_LEVEL_CRITICAL = "critical"

    // Notification constants
    const val NOTIFICATION_CHANNEL_GENERAL = "general"
    const val NOTIFICATION_CHANNEL_TASKS = "tasks"
    const val NOTIFICATION_CHANNEL_AGENTS = "agents"
    const val NOTIFICATION_CHANNEL_ERRORS = "errors"
    const val NOTIFICATION_ID_GENERAL = 1000
    const val NOTIFICATION_ID_TASKS = 1001
    const val NOTIFICATION_ID_AGENTS = 1002
    const val NOTIFICATION_ID_ERRORS = 1003

    // Intent constants
    const val INTENT_EXTRA_AGENT_ID = "agent_id"
    const val INTENT_EXTRA_TASK_ID = "task_id"
    const val INTENT_EXTRA_TOOL_ID = "tool_id"
    const val INTENT_EXTRA_SECTION = "section"

    // Request codes
    const val REQUEST_CODE_PERMISSIONS = 100
    const val REQUEST_CODE_FILE_PICKER = 101
    const val REQUEST_CODE_IMAGE_CAPTURE = 102
    const val REQUEST_CODE_SETTINGS = 103

    // Permission constants
    val REQUIRED_PERMISSIONS = arrayOf(
        android.Manifest.permission.INTERNET,
        android.Manifest.permission.ACCESS_NETWORK_STATE,
        android.Manifest.permission.READ_EXTERNAL_STORAGE,
        android.Manifest.permission.WRITE_EXTERNAL_STORAGE,
        android.Manifest.permission.CAMERA,
        android.Manifest.permission.RECORD_AUDIO
    )

    // Theme constants
    const val THEME_DARK = "dark"
    const val THEME_LIGHT = "light"
    const val THEME_SYSTEM = "system"

    // Language constants
    const val LANGUAGE_ENGLISH = "en"
    const val LANGUAGE_URDU = "ur"
    const val LANGUAGE_SPANISH = "es"
    const val LANGUAGE_FRENCH = "fr"
    const val LANGUAGE_ARABIC = "ar"

    // Time constants
    const val TIMEOUT_SHORT = 5000L // 5 seconds
    const val TIMEOUT_MEDIUM = 10000L // 10 seconds
    const val TIMEOUT_LONG = 30000L // 30 seconds
    const val TIMEOUT_INFINITE = 0L

    // Date format constants
    const val DATE_FORMAT_FULL = "yyyy-MM-dd HH:mm:ss"
    const val DATE_FORMAT_DATE_ONLY = "yyyy-MM-dd"
    const val DATE_FORMAT_TIME_ONLY = "HH:mm:ss"
    const val DATE_FORMAT_DISPLAY = "MMM dd, yyyy h:mm a"

    // Animation constants
    const val ANIMATION_DURATION_SHORT = 200L
    const val ANIMATION_DURATION_MEDIUM = 300L
    const val ANIMATION_DURATION_LONG = 500L

    // Pagination constants
    const val PAGINATION_PAGE_SIZE = 20
    const val PAGINATION_MAX_PAGES = 100

    // Search constants
    const val SEARCH_DEBOUNCE = 300L // milliseconds
    const val SEARCH_MIN_QUERY_LENGTH = 2
    const val SEARCH_MAX_RESULTS = 50

    // Cache constants
    const val CACHE_SIZE_MAX = 50L // MB
    const val CACHE_EXPIRY_DAYS = 30

    // Error messages
    const val ERROR_NETWORK = "Network error. Please check your connection."
    const val ERROR_SERVER = "Server error. Please try again later."
    const val ERROR_UNAUTHORIZED = "Unauthorized. Please login again."
    const val ERROR_NOT_FOUND = "Resource not found."
    const val ERROR_VALIDATION = "Validation error. Please check your input."
    const val ERROR_UNKNOWN = "An unknown error occurred."

    // Success messages
    const val SUCCESS_SAVED = "Changes saved successfully."
    const val SUCCESS_DELETED = "Item deleted successfully."
    const val SUCCESS_CREATED = "Item created successfully."
    const val SUCCESS_UPDATED = "Item updated successfully."

    // Confirmation messages
    const val CONFIRM_DELETE = "Are you sure you want to delete this item?"
    const val CONFIRM_LOGOUT = "Are you sure you want to logout?"
    const val CONFIRM_CLEAR = "Are you sure you want to clear all data?"

    // Empty state messages
    const val EMPTY_AGENTS = "No agents found. Create your first agent!"
    const val EMPTY_TASKS = "No tasks found. Create your first task!"
    const val EMPTY_TOOLS = "No tools found."
    const val EMPTY_MEMORY = "No memory entries found."
    const val EMPTY_LOGS = "No logs found."

    // Loading messages
    const val LOADING = "Loading..."
    const val LOADING_AGENTS = "Loading agents..."
    const val LOADING_TASKS = "Loading tasks..."
    const val LOADING_TOOLS = "Loading tools..."
    const val LOADING_MEMORY = "Loading memory..."
    const val LOADING_LOGS = "Loading logs..."

    // File constants
    const val FILE_PROVIDER_AUTHORITY = "${APP_PACKAGE}.fileprovider"
    const val FILE_MAX_SIZE = 10L // MB
    const val FILE_ALLOWED_TYPES = arrayOf("image/*", "text/*", "application/pdf")

    // Web constants
    const val WEB_BASE_URL = "https://livingai.local"
    const val WEB_DASHBOARD_URL = "${WEB_BASE_URL}/dashboard"
    const val WEB_AGENTS_URL = "${WEB_BASE_URL}/agents"
    const val WEB_TOOLS_URL = "${WEB_BASE_URL}/tools"
    const val WEB_TASKS_URL = "${WEB_BASE_URL}/tasks"
    const val WEB_MEMORY_URL = "${WEB_BASE_URL}/memory"
    const val WEB_SETTINGS_URL = "${WEB_BASE_URL}/settings"

    // GitHub constants
    const val GITHUB_REPO = "https://github.com/abdulraheemnohri/LivingAI"
    const val GITHUB_ISSUES = "${GITHUB_REPO}/issues"
    const val GITHUB_RELEASES = "${GITHUB_REPO}/releases"

    // Contact constants
    const val CONTACT_EMAIL = "contact@livingai.dev"
    const val CONTACT_WEBSITE = "https://livingai.dev"
    const val CONTACT_TWITTER = "https://twitter.com/LivingAI"
    const val CONTACT_DISCORD = "https://discord.gg/livingai"

    // License constants
    const val LICENSE = "MIT"
    const val LICENSE_URL = "https://opensource.org/licenses/MIT"

    // Default values
    const val DEFAULT_AGENT_NAME = "General Purpose Agent"
    const val DEFAULT_TASK_PRIORITY = PRIORITY_MEDIUM
    const val DEFAULT_MAX_CONCURRENT_TASKS = 5
    const val DEFAULT_MEMORY_LIMIT = "100 MB"

    // Regex patterns
    const val REGEX_EMAIL = "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\$"
    const val REGEX_URL = "https?://(?:[-\\w.]|(?:%[\\da-fA-F]{2}))+"
    const val REGEX_PHONE = "^[+]?[0-9]{10,15}\\"

    // Shared preferences keys
    const val PREFS_NAME = "livingai_prefs"
    const val PREFS_KEY_FIRST_LAUNCH = "first_launch"
    const val PREFS_KEY_ONBOARDING_COMPLETED = "onboarding_completed"
    const val PREFS_KEY_THEME = "theme"
    const val PREFS_KEY_LANGUAGE = "language"

    // Fragment tags
    const val FRAGMENT_DASHBOARD = "fragment_dashboard"
    const val FRAGMENT_AGENTS = "fragment_agents"
    const val FRAGMENT_TOOLS = "fragment_tools"
    const val FRAGMENT_TASKS = "fragment_tasks"
    const val FRAGMENT_MEMORY = "fragment_memory"
    const val FRAGMENT_SETTINGS = "fragment_settings"
    const val FRAGMENT_TERMINAL = "fragment_terminal"
    const val FRAGMENT_ANALYTICS = "fragment_analytics"
    const val FRAGMENT_DOCUMENTATION = "fragment_documentation"
    const val FRAGMENT_ABOUT = "fragment_about"
}
