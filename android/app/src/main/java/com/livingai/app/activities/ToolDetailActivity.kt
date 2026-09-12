package com.livingai.app.activities

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.R
import com.livingai.app.models.Tool
import com.livingai.app.utils.Constants
import com.livingai.app.viewmodels.ToolViewModel

/**
 * ToolDetailActivity - Displays detailed information about a tool
 */
class ToolDetailActivity : AppCompatActivity() {

    private lateinit var viewModel: ToolViewModel
    private var toolId: String = ""
    private var tool: Tool? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tool_detail)

        // Initialize ViewModel
        viewModel = ToolViewModel()

        // Get tool ID from intent
        toolId = intent.getStringExtra(Constants.INTENT_EXTRA_TOOL_ID) ?: ""

        // Setup toolbar
        setupToolbar()

        // Load tool data
        loadToolData()
    }

    /**
     * Setup the toolbar
     */
    private fun setupToolbar() {
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.apply {
            title = getString(R.string.title_tool_detail)
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
    }

    /**
     * Load tool data
     */
    private fun loadToolData() {
        tool = viewModel.getToolById(toolId)
        if (tool != null) {
            updateUI()
        } else {
            // Tool not found, finish activity
            finish()
        }
    }

    /**
     * Update UI with tool data
     */
    private fun updateUI() {
        tool?.let { tool ->
            // Set tool info
            findViewById<TextView>(R.id.tv_tool_name).text = tool.name
            findViewById<TextView>(R.id.tv_tool_category).text = tool.category
            findViewById<TextView>(R.id.tv_tool_status).text = tool.status
            findViewById<TextView>(R.id.tv_tool_description).text = tool.description

            // Set additional info
            findViewById<TextView>(R.id.tv_tool_version).text = tool.version
            findViewById<TextView>(R.id.tv_tool_author).text = tool.author
            findViewById<TextView>(R.id.tv_tool_license).text = tool.license

            // Set usage info
            findViewById<TextView>(R.id.tv_usage_count).text = tool.usageCount.toString()
            findViewById<TextView>(R.id.tv_last_used).text = getString(
                R.string.last_used_format, tool.lastUsed
            )

            // Set parameters
            findViewById<TextView>(R.id.tv_parameters).text = tool.parameters.joinToString(", ")
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_tool_detail, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_edit -> {
                // Edit tool
                editTool()
                return true
            }
            R.id.action_test -> {
                // Test tool
                testTool()
                return true
            }
            R.id.action_enable_disable -> {
                // Enable/disable tool
                toggleTool()
                return true
            }
            R.id.action_delete -> {
                // Delete tool
                deleteTool()
                return true
            }
            android.R.id.home -> {
                onBackPressed()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    /**
     * Edit tool
     */
    private fun editTool() {
        // Implementation for editing tool
    }

    /**
     * Test tool
     */
    private fun testTool() {
        // Implementation for testing tool
    }

    /**
     * Toggle tool enabled/disabled
     */
    private fun toggleTool() {
        tool?.let { tool ->
            viewModel.toggleTool(tool)
            loadToolData()
        }
    }

    /**
     * Delete tool
     */
    private fun deleteTool() {
        tool?.let { tool ->
            viewModel.deleteTool(tool)
            finish()
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
