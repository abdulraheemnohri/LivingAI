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
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.livingai.app.R
import com.livingai.app.adapters.AgentAdapter
import com.livingai.app.models.Agent
import com.livingai.app.utils.Constants
import com.livingai.app.viewmodels.AgentViewModel

/**
 * AgentsActivity - Displays the list of AI agents
 */
class AgentsActivity : AppCompatActivity() {

    private lateinit var viewModel: AgentViewModel
    private lateinit var agentsRecyclerView: RecyclerView
    private lateinit var fab: FloatingActionButton
    private lateinit var searchView: SearchView
    private lateinit var emptyStateView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_agents)

        // Initialize ViewModel
        viewModel = AgentViewModel()

        // Initialize views
        initializeViews()

        // Setup RecyclerView
        setupRecyclerView()

        // Setup FAB
        setupFAB()

        // Setup SearchView
        setupSearchView()

        // Load data
        loadData()
    }

    /**
     * Initialize all views
     */
    private fun initializeViews() {
        agentsRecyclerView = findViewById(R.id.recycler_agents)
        fab = findViewById(R.id.fab)
        emptyStateView = findViewById(R.id.tv_empty_state)
    }

    /**
     * Setup RecyclerView
     */
    private fun setupRecyclerView() {
        agentsRecyclerView.layoutManager = LinearLayoutManager(this)
        agentsRecyclerView.adapter = AgentAdapter(
            mutableListOf(),
            onAgentClick = { agent ->
                // Navigate to agent detail
                navigateToAgentDetail(agent)
            },
            onAgentStart = { agent ->
                // Start the agent
                viewModel.startAgent(agent)
            },
            onAgentStop = { agent ->
                // Stop the agent
                viewModel.stopAgent(agent)
            },
            onAgentDelete = { agent ->
                // Delete the agent
                viewModel.deleteAgent(agent)
                loadData()
            }
        )
    }

    /**
     * Setup FAB
     */
    private fun setupFAB() {
        fab.setOnClickListener {
            // Navigate to create agent
            val intent = Intent(this, CreateAgentActivity::class.java)
            startActivity(intent)
        }
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
                // Filter agents based on search query
                filterAgents(newText)
                return true
            }
        })
    }

    /**
     * Load data from ViewModel
     */
    private fun loadData() {
        val agents = viewModel.getAllAgents()
        updateAgentsList(agents)
    }

    /**
     * Update agents list
     */
    private fun updateAgentsList(agents: List<Agent>) {
        val adapter = agentsRecyclerView.adapter as? AgentAdapter
        adapter?.updateAgents(agents)

        // Update empty state
        if (agents.isEmpty()) {
            emptyStateView.visibility = View.VISIBLE
            agentsRecyclerView.visibility = View.GONE
        } else {
            emptyStateView.visibility = View.GONE
            agentsRecyclerView.visibility = View.VISIBLE
        }
    }

    /**
     * Filter agents based on search query
     */
    private fun filterAgents(query: String?) {
        val allAgents = viewModel.getAllAgents()
        val filteredAgents = if (query.isNullOrEmpty()) {
            allAgents
        } else {
            allAgents.filter {
                it.name.contains(query, ignoreCase = true) ||
                        it.description.contains(query, ignoreCase = true) ||
                        it.type.contains(query, ignoreCase = true)
            }
        }
        updateAgentsList(filteredAgents)
    }

    /**
     * Navigate to agent detail
     */
    private fun navigateToAgentDetail(agent: Agent) {
        val intent = Intent(this, AgentDetailActivity::class.java).apply {
            putExtra(Constants.INTENT_EXTRA_AGENT_ID, agent.id)
        }
        startActivity(intent)
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_agents, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_search -> {
                // Search action handled by SearchView
                return true
            }
            R.id.action_filter -> {
                // Show filter options
                showFilterOptions()
                return true
            }
            R.id.action_sort -> {
                // Show sort options
                showSortOptions()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    /**
     * Show filter options
     */
    private fun showFilterOptions() {
        // Implementation for showing filter options
    }

    /**
     * Show sort options
     */
    private fun showSortOptions() {
        // Implementation for showing sort options
    }

    override fun onResume() {
        super.onResume()
        // Refresh data when resumed
        loadData()
    }
}
