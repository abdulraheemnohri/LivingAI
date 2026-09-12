package com.livingai.app.activities

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.SearchView
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.adapters.ToolAdapter
import com.livingai.app.models.Tool
import com.livingai.app.utils.Constants
import com.livingai.app.viewmodels.ToolViewModel

/**
 * ToolsActivity - Displays the list of available AI tools
 */
class ToolsActivity : AppCompatActivity() {

    private lateinit var viewModel: ToolViewModel
    private lateinit var toolsRecyclerView: RecyclerView
    private lateinit var searchView: SearchView
    private lateinit var emptyStateView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tools)

        // Initialize ViewModel
        viewModel = ToolViewModel()

        // Initialize views
        initializeViews()

        // Setup RecyclerView
        setupRecyclerView()

        // Setup SearchView
        setupSearchView()

        // Load data
        loadData()
    }

    /**
     * Initialize all views
     */
    private fun initializeViews() {
        toolsRecyclerView = findViewById(R.id.recycler_tools)
        emptyStateView = findViewById(R.id.tv_empty_state)
    }

    /**
     * Setup RecyclerView
     */
    private fun setupRecyclerView() {
        toolsRecyclerView.layoutManager = LinearLayoutManager(this)
        toolsRecyclerView.adapter = ToolAdapter(
            mutableListOf(),
            onToolClick = { tool ->
                // Navigate to tool detail
                navigateToToolDetail(tool)
            },
            onToolToggle = { tool ->
                // Toggle tool enabled/disabled
                viewModel.toggleTool(tool)
            }
        )
    }

    /**
     * Setup SearchView
     */
    private fun setupSearchView() {
        searchView = findViewById(R.id.search_view)
        searchView.setOnQueryTextListener(object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean {
                return false
            }

            override fun onQueryTextChange(newText: String?): Boolean {
                // Filter tools based on search query
                filterTools(newText)
                return true
            }
        })
    }

    /**
     * Load data from ViewModel
     */
    private fun loadData() {
        val tools = viewModel.getAllTools()
        updateToolsList(tools)
    }

    /**
     * Update tools list
     */
    private fun updateToolsList(tools: List<Tool>) {
        val adapter = toolsRecyclerView.adapter as? ToolAdapter
        adapter?.updateTools(tools)

        // Update empty state
        if (tools.isEmpty()) {
            emptyStateView.visibility = View.VISIBLE
            toolsRecyclerView.visibility = View.GONE
        } else {
            emptyStateView.visibility = View.GONE
            toolsRecyclerView.visibility = View.VISIBLE
        }
    }

    /**
     * Filter tools based on search query
     */
    private fun filterTools(query: String?) {
        val allTools = viewModel.getAllTools()
        val filteredTools = if (query.isNullOrEmpty()) {
            allTools
        } else {
            allTools.filter {
                it.name.contains(query, ignoreCase = true) ||
                        it.description.contains(query, ignoreCase = true) ||
                        it.category.contains(query, ignoreCase = true)
            }
        }
        updateToolsList(filteredTools)
    }

    /**
     * Navigate to tool detail
     */
    private fun navigateToToolDetail(tool: Tool) {
        val intent = Intent(this, ToolDetailActivity::class.java).apply {
            putExtra(Constants.INTENT_EXTRA_TOOL_ID, tool.id)
        }
        startActivity(intent)
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_tools, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_search -> {
                // Search action handled by SearchView
                return true
            }
            R.id.action_refresh -> {
                // Refresh tools list
                loadData()
                return true
            }
            R.id.action_filter -> {
                // Show filter options
                showFilterOptions()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    /**
     * Show filter options
     */
    private fun showFilterOptions() {
        // Implementation for showing filter options by category
    }

    override fun onResume() {
        super.onResume()
        // Refresh data when resumed
        loadData()
    }
}
