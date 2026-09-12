package com.livingai.app.activities

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.animation.AlphaAnimation
import android.view.animation.Animation
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.LivingAIApplication
import com.livingai.app.R
import com.livingai.app.utils.Constants
import com.livingai.app.utils.PreferenceHelper

/**
 * SplashActivity - Displayed when the app is launched
 * Shows the LivingAI logo and performs initial setup
 */
class SplashActivity : AppCompatActivity() {

    private val splashTimeout: Long = 3000 // 3 seconds
    private val fadeInDuration: Long = 1500 // 1.5 seconds

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        // Initialize application components
        initializeApp()

        // Animate the splash screen
        animateSplash()

        // Navigate to main activity after timeout
        navigateToMainActivity()
    }

    /**
     * Initialize application components
     */
    private fun initializeApp() {
        // Ensure application context is available
        val appContext = LivingAIApplication.getAppContext()

        // Initialize preferences if not already done
        PreferenceHelper.init(appContext)

        // Check if this is the first launch
        if (PreferenceHelper.isFirstLaunch()) {
            PreferenceHelper.setFirstLaunch(false)
            // Perform first-time setup
            setupFirstLaunch()
        }

        // Initialize other components
        initializeComponents()
    }

    /**
     * Setup for first launch
     */
    private fun setupFirstLaunch() {
        // Set default preferences for first launch
        PreferenceHelper.setTheme(PreferenceHelper.THEME_DARK)
        PreferenceHelper.setLanguage(PreferenceHelper.LANGUAGE_ENGLISH)
        PreferenceHelper.setOnboardingCompleted(false)
        PreferenceHelper.setNotificationsEnabled(true)
        PreferenceHelper.setAutoUpdateEnabled(true)
        PreferenceHelper.setAnalyticsEnabled(false)
    }

    /**
     * Initialize other app components
     */
    private fun initializeComponents() {
        // Initialize database
        // DatabaseManager.init(this)

        // Initialize analytics
        // AnalyticsManager.init(this)

        // Initialize logging
        // Logger.init(this)
    }

    /**
     * Animate the splash screen
     */
    private fun animateSplash() {
        val logoView = findViewById<ImageView>(R.id.splash_logo)
        val titleView = findViewById<TextView>(R.id.splash_title)
        val subtitleView = findViewById<TextView>(R.id.splash_subtitle)

        // Fade in animation for logo
        val fadeIn = AlphaAnimation(0f, 1f).apply {
            duration = fadeInDuration
            fillAfter = true
        }

        // Fade in animation for text
        val fadeInText = AlphaAnimation(0f, 1f).apply {
            duration = fadeInDuration * 2 / 3
            fillAfter = true
            startOffset = fadeInDuration / 3
        }

        logoView.startAnimation(fadeIn)
        titleView.startAnimation(fadeInText)
        subtitleView.startAnimation(fadeInText)
    }

    /**
     * Navigate to the main activity after splash timeout
     */
    private fun navigateToMainActivity() {
        Handler(Looper.getMainLooper()).postDelayed({
            // Check if onboarding is completed
            if (PreferenceHelper.isOnboardingCompleted()) {
                // Navigate to Dashboard
                val intent = Intent(this, MainActivity::class.java)
                startActivity(intent)
            } else {
                // Navigate to Onboarding (for now, just go to MainActivity)
                val intent = Intent(this, MainActivity::class.java)
                startActivity(intent)
            }
            finish()
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
        }, splashTimeout)
    }

    override fun onBackPressed() {
        // Disable back button on splash screen
        // super.onBackPressed()
    }
}
