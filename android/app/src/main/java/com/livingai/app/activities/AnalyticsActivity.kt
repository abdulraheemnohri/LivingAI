package com.livingai.app.activities

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.R
import com.livingai.app.fragments.AnalyticsFragment

/**
 * AnalyticsActivity - Displays analytics and usage statistics
 */
class AnalyticsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_analytics)

        // Display AnalyticsFragment
        supportFragmentManager
            .beginTransaction()
            .replace(R.id.fragment_container, AnalyticsFragment())
            .commit()

        // Setup toolbar
        setupToolbar()
    }

    /**
     * Setup the toolbar
     */
    private fun setupToolbar() {
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.apply {
            title = getString(R.string.title_analytics)
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_analytics, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_refresh -> {
                // Refresh analytics data
                refreshData()
                return true
            }
            R.id.action_export -> {
                // Export analytics data
                exportData()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    /**
     * Refresh analytics data
     */
    private fun refreshData() {
        // Implementation for refreshing data
    }

    /**
     * Export analytics data
     */
    private fun exportData() {
        // Implementation for exporting data
    }
}
