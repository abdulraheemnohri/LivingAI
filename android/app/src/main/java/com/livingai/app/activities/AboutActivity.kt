package com.livingai.app.activities

import android.os.Bundle
import android.view.MenuItem
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.R
import com.livingai.app.utils.Constants

/**
 * AboutActivity - Displays information about the app
 */
class AboutActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_about)

        // Setup toolbar
        setupToolbar()

        // Setup content
        setupContent()
    }

    /**
     * Setup the toolbar
     */
    private fun setupToolbar() {
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.apply {
            title = getString(R.string.title_about)
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
    }

    /**
     * Setup the content
     */
    private fun setupContent() {
        // Set app info
        findViewById<TextView>(R.id.tv_app_name).text = Constants.APP_NAME
        findViewById<TextView>(R.id.tv_app_version).text = getString(R.string.version_format, Constants.APP_VERSION)
        findViewById<TextView>(R.id.tv_app_description).text = getString(R.string.app_description)

        // Set additional info
        findViewById<TextView>(R.id.tv_author).text = getString(R.string.author)
        findViewById<TextView>(R.id.tv_license).text = getString(R.string.license, Constants.LICENSE)
        findViewById<TextView>(R.id.tv_github).text = Constants.GITHUB_REPO
        findViewById<TextView>(R.id.tv_website).text = Constants.CONTACT_WEBSITE
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            android.R.id.home -> {
                onBackPressed()
                return true
            }
        }
        return super.onOptionsItemSelected(item)
    }
}
