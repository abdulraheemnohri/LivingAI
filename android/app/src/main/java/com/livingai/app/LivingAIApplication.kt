package com.livingai.app

import android.app.Application
import android.content.Context
import androidx.appcompat.app.AppCompatDelegate
import androidx.multidex.MultiDex
import com.livingai.app.utils.PreferenceHelper
import com.livingai.app.utils.PreferenceHelper.THEME_DARK
import com.livingai.app.utils.PreferenceHelper.THEME_LIGHT
import com.livingai.app.utils.PreferenceHelper.THEME_SYSTEM
import dagger.hilt.android.HiltAndroidApp

/**
 * LivingAI Application class
 * Main application entry point that initializes app-wide configurations
 */
@HiltAndroidApp
class LivingAIApplication : Application() {

    init {
        // Initialize app-wide settings
        instance = this
    }

    override fun onCreate() {
        super.onCreate()
        
        // Initialize MultiDex for apps with many dependencies
        MultiDex.install(this)
        
        // Initialize preferences
        PreferenceHelper.init(this)
        
        // Set theme based on user preference
        applyTheme()
        
        // Initialize other app components
        initializeComponents()
    }

    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(base)
        MultiDex.install(this)
    }

    /**
     * Apply theme based on user preference
     */
    private fun applyTheme() {
        val themePreference = PreferenceHelper.getTheme()
        
        when (themePreference) {
            THEME_DARK -> {
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
            }
            THEME_LIGHT -> {
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
            }
            THEME_SYSTEM -> {
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
            }
        }
    }

    /**
     * Initialize app components
     */
    private fun initializeComponents() {
        // Initialize database
        // DatabaseManager.init(this)
        
        // Initialize analytics
        // AnalyticsManager.init(this)
        
        // Initialize crash reporting
        // CrashReporting.init(this)
        
        // Initialize logging
        // Logger.init(this)
    }

    companion object {
        private lateinit var instance: LivingAIApplication
        
        /**
         * Get application context
         */
        fun getAppContext(): Context {
            return instance.applicationContext
        }
    }
}
