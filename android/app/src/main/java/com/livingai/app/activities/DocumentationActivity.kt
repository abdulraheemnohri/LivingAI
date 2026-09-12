package com.livingai.app.activities

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.R
import com.livingai.app.fragments.DocumentationFragment

/**
 * DocumentationActivity - Displays app documentation
 */
class DocumentationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_documentation)

        // Display DocumentationFragment
        supportFragmentManager
            .beginTransaction()
            .replace(R.id.fragment_container, DocumentationFragment())
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
            title = getString(R.string.title_documentation)
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_documentation, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_search -> {
                // Search documentation
                searchDocumentation()
                return true
            }
            R.id.action_bookmarks -> {
                // Show bookmarks
                showBookmarks()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    /**
     * Search documentation
     */
    private fun searchDocumentation() {
        // Implementation for searching documentation
    }

    /**
     * Show bookmarks
     */
    private fun showBookmarks() {
        // Implementation for showing bookmarks
    }
}
