package com.livingai.app.utils

import android.content.Context
import android.content.SharedPreferences
import androidx.preference.PreferenceManager

/**
 * Preference Helper
 * Manages shared preferences for the application
 */
object PreferenceHelper {

    // Preference keys
    const val KEY_THEME = "pref_theme"
    const val KEY_LANGUAGE = "pref_language"
    const val KEY_FIRST_LAUNCH = "pref_first_launch"
    const val KEY_ONBOARDING_COMPLETED = "pref_onboarding_completed"
    const val KEY_NOTIFICATIONS_ENABLED = "pref_notifications_enabled"
    const val KEY_AUTO_UPDATE = "pref_auto_update"
    const val KEY_ANALYTICS_ENABLED = "pref_analytics_enabled"
    const val KEY_DEFAULT_AGENT = "pref_default_agent"
    const val KEY_MAX_CONCURRENT_TASKS = "pref_max_concurrent_tasks"
    const val KEY_MEMORY_LIMIT = "pref_memory_limit"

    // Theme constants
    const val THEME_SYSTEM = "system"
    const val THEME_LIGHT = "light"
    const val THEME_DARK = "dark"

    // Language constants
    const val LANGUAGE_ENGLISH = "en"
    const val LANGUAGE_URDU = "ur"
    const val LANGUAGE_SPANISH = "es"
    const val LANGUAGE_FRENCH = "fr"
    const val LANGUAGE_ARABIC = "ar"

    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var context: Context

    /**
     * Initialize the preference helper
     */
    fun init(context: Context) {
        this.context = context.applicationContext
        sharedPreferences = PreferenceManager.getDefaultSharedPreferences(context)
    }

    /**
     * Get theme preference
     */
    fun getTheme(): String {
        return sharedPreferences.getString(KEY_THEME, THEME_DARK) ?: THEME_DARK
    }

    /**
     * Set theme preference
     */
    fun setTheme(theme: String) {
        sharedPreferences.edit().putString(KEY_THEME, theme).apply()
    }

    /**
     * Get language preference
     */
    fun getLanguage(): String {
        return sharedPreferences.getString(KEY_LANGUAGE, LANGUAGE_ENGLISH) ?: LANGUAGE_ENGLISH
    }

    /**
     * Set language preference
     */
    fun setLanguage(language: String) {
        sharedPreferences.edit().putString(KEY_LANGUAGE, language).apply()
    }

    /**
     * Check if first launch
     */
    fun isFirstLaunch(): Boolean {
        return sharedPreferences.getBoolean(KEY_FIRST_LAUNCH, true)
    }

    /**
     * Set first launch flag
     */
    fun setFirstLaunch(isFirst: Boolean) {
        sharedPreferences.edit().putBoolean(KEY_FIRST_LAUNCH, isFirst).apply()
    }

    /**
     * Check if onboarding is completed
     */
    fun isOnboardingCompleted(): Boolean {
        return sharedPreferences.getBoolean(KEY_ONBOARDING_COMPLETED, false)
    }

    /**
     * Set onboarding completion flag
     */
    fun setOnboardingCompleted(isCompleted: Boolean) {
        sharedPreferences.edit().putBoolean(KEY_ONBOARDING_COMPLETED, isCompleted).apply()
    }

    /**
     * Check if notifications are enabled
     */
    fun areNotificationsEnabled(): Boolean {
        return sharedPreferences.getBoolean(KEY_NOTIFICATIONS_ENABLED, true)
    }

    /**
     * Set notifications enabled flag
     */
    fun setNotificationsEnabled(isEnabled: Boolean) {
        sharedPreferences.edit().putBoolean(KEY_NOTIFICATIONS_ENABLED, isEnabled).apply()
    }

    /**
     * Check if auto-update is enabled
     */
    fun isAutoUpdateEnabled(): Boolean {
        return sharedPreferences.getBoolean(KEY_AUTO_UPDATE, true)
    }

    /**
     * Set auto-update enabled flag
     */
    fun setAutoUpdateEnabled(isEnabled: Boolean) {
        sharedPreferences.edit().putBoolean(KEY_AUTO_UPDATE, isEnabled).apply()
    }

    /**
     * Check if analytics are enabled
     */
    fun areAnalyticsEnabled(): Boolean {
        return sharedPreferences.getBoolean(KEY_ANALYTICS_ENABLED, false)
    }

    /**
     * Set analytics enabled flag
     */
    fun setAnalyticsEnabled(isEnabled: Boolean) {
        sharedPreferences.edit().putBoolean(KEY_ANALYTICS_ENABLED, isEnabled).apply()
    }

    /**
     * Get default agent
     */
    fun getDefaultAgent(): String {
        return sharedPreferences.getString(KEY_DEFAULT_AGENT, "General Purpose Agent") ?: "General Purpose Agent"
    }

    /**
     * Set default agent
     */
    fun setDefaultAgent(agentName: String) {
        sharedPreferences.edit().putString(KEY_DEFAULT_AGENT, agentName).apply()
    }

    /**
     * Get max concurrent tasks
     */
    fun getMaxConcurrentTasks(): Int {
        return sharedPreferences.getInt(KEY_MAX_CONCURRENT_TASKS, 5)
    }

    /**
     * Set max concurrent tasks
     */
    fun setMaxConcurrentTasks(maxTasks: Int) {
        sharedPreferences.edit().putInt(KEY_MAX_CONCURRENT_TASKS, maxTasks).apply()
    }

    /**
     * Get memory limit
     */
    fun getMemoryLimit(): String {
        return sharedPreferences.getString(KEY_MEMORY_LIMIT, "100 MB") ?: "100 MB"
    }

    /**
     * Set memory limit
     */
    fun setMemoryLimit(memoryLimit: String) {
        sharedPreferences.edit().putString(KEY_MEMORY_LIMIT, memoryLimit).apply()
    }

    /**
     * Clear all preferences
     */
    fun clearAll() {
        sharedPreferences.edit().clear().apply()
    }

    /**
     * Get string preference
     */
    fun getString(key: String, defaultValue: String = ""): String {
        return sharedPreferences.getString(key, defaultValue) ?: defaultValue
    }

    /**
     * Get boolean preference
     */
    fun getBoolean(key: String, defaultValue: Boolean = false): Boolean {
        return sharedPreferences.getBoolean(key, defaultValue)
    }

    /**
     * Get integer preference
     */
    fun getInt(key: String, defaultValue: Int = 0): Int {
        return sharedPreferences.getInt(key, defaultValue)
    }

    /**
     * Get long preference
     */
    fun getLong(key: String, defaultValue: Long = 0L): Long {
        return sharedPreferences.getLong(key, defaultValue)
    }

    /**
     * Get float preference
     */
    fun getFloat(key: String, defaultValue: Float = 0f): Float {
        return sharedPreferences.getFloat(key, defaultValue)
    }

    /**
     * Set string preference
     */
    fun setString(key: String, value: String) {
        sharedPreferences.edit().putString(key, value).apply()
    }

    /**
     * Set boolean preference
     */
    fun setBoolean(key: String, value: Boolean) {
        sharedPreferences.edit().putBoolean(key, value).apply()
    }

    /**
     * Set integer preference
     */
    fun setInt(key: String, value: Int) {
        sharedPreferences.edit().putInt(key, value).apply()
    }

    /**
     * Set long preference
     */
    fun setLong(key: String, value: Long) {
        sharedPreferences.edit().putLong(key, value).apply()
    }

    /**
     * Set float preference
     */
    fun setFloat(key: String, value: Float) {
        sharedPreferences.edit().putFloat(key, value).apply()
    }

    /**
     * Remove preference
     */
    fun remove(key: String) {
        sharedPreferences.edit().remove(key).apply()
    }
}
