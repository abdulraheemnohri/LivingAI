package com.livingai.app.activities

import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.card.MaterialCardView
import com.livingai.app.R
import com.livingai.app.adapters.AgentAdapter
import com.livingai.app.adapters.TaskAdapter
import com.livingai.app.models.Agent
import com.livingai.app.models.Task
import com.livingai.app.utils.Constants
import com.livingai.app.utils.PreferenceHelper
import com.livingai.app.viewmodels.DashboardViewModel

/**
 * DashboardActivity - Displays the main dashboard with system overview
 */
class DashboardActivity : AppCompatActivity() {

    private lateinit var viewModel: DashboardViewModel
    private lateinit var recentAgentsRecyclerView: RecyclerView
    private lateinit var recentTasksRecyclerView: RecyclerView
    private lateinit var statsCard: MaterialCardView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Initialize ViewModel
        viewModel = DashboardViewModel()

        // Initialize views
        initializeViews()

        // Setup RecyclerViews
        setupRecyclerViews()

        // Load data
        loadData()

        // Setup refresh
        setupRefresh()
    }

    /**
     * Initialize all views
     */
    private fun initializeViews() {
        recentAgentsRecyclerView = findViewById(R.id.recycler_recent_agents)
        recentTasksRecyclerView = findViewById(R.id.recycler_recent_tasks)
        statsCard = findViewById(R.id.card_stats)

        // Set up stats
        updateStats()
    }

    /**
     * Setup RecyclerViews
     */
    private fun setupRecyclerViews() {
        // Recent Agents RecyclerView
        recentAgentsRecyclerView.layoutManager = LinearLayoutManager(
            this, LinearLayoutManager.HORIZONTAL, false
        )
        recentAgentsRecyclerView.adapter = AgentAdapter(
            mutableListOf(),
            onAgentClick = { agent ->
                // Navigate to agent detail
                navigateToAgentDetail(agent)
            }
        )

        // Recent Tasks RecyclerView
        recentTasksRecyclerView.layoutManager = LinearLayoutManager(
            this, LinearLayoutManager.HORIZONTAL, false
        )
        recentTasksRecyclerView.adapter = TaskAdapter(
            mutableListOf(),
            onTaskClick = { task ->
                // Navigate to task detail
                navigateToTaskDetail(task)
            }
        )
    }

    /**
     * Load data from ViewModel
     */
    private fun loadData() {
        // Load recent agents
        val recentAgents = viewModel.getRecentAgents(5)
        (recentAgentsRecyclerView.adapter as? AgentAdapter)?.updateAgents(recentAgents)

        // Load recent tasks
        val recentTasks = viewModel.getRecentTasks(5)
        (recentTasksRecyclerView.adapter as? TaskAdapter)?.updateTasks(recentTasks)

        // Update stats
        updateStats()
    }

    /**
     * Update statistics
     */
    private fun updateStats() {
        val totalAgents = viewModel.getTotalAgentCount()
        val totalTasks = viewModel.getTotalTaskCount()
        val completedTasks = viewModel.getCompletedTaskCount()
        val activeAgents = viewModel.getActiveAgentCount()

        // Update UI with stats
        findViewById<TextView>(R.id.tv_total_agents).text = totalAgents.toString()
        findViewById<TextView>(R.id.tv_total_tasks).text = totalTasks.toString()
        findViewById<TextView>(R.id.tv_completed_tasks).text = completedTasks.toString()
        findViewById<TextView>(R.id.tv_active_agents).text = activeAgents.toString()
    }

    /**
     * Setup refresh functionality
     */
    private fun setupRefresh() {
        // Implementation for pull-to-refresh or manual refresh
    }

    /**
     * Navigate to agent detail
     */
    private fun navigateToAgentDetail(agent: Agent) {
        // Implementation for navigating to agent detail
    }

    /**
     * Navigate to task detail
     */
    private fun navigateToTaskDetail(task: Task) {
        // Implementation for navigating to task detail
    }

    /**
     * Quick action handlers
     */
    fun onStartAgentClick(view: View) {
        // Handle start agent action
    }

    fun onRunTaskClick(view: View) {
        // Handle run task action
    }

    fun onOpenTerminalClick(view: View) {
        // Handle open terminal action
    }

    fun onClearCacheClick(view: View) {
        // Handle clear cache action
    }

    override fun onResume() {
        super.onResume()
        // Refresh data when resumed
        loadData()
    }
}
