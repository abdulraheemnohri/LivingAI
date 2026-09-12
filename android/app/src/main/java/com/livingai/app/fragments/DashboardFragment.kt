package com.livingai.app.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.adapters.AgentAdapter
import com.livingai.app.adapters.TaskAdapter
import com.livingai.app.viewmodels.DashboardViewModel

/**
 * DashboardFragment - Displays the main dashboard content
 */
class DashboardFragment : Fragment() {

    private lateinit var viewModel: DashboardViewModel
    private lateinit var recentAgentsRecyclerView: RecyclerView
    private lateinit var recentTasksRecyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this).get(DashboardViewModel::class.java)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_dashboard, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize views
        recentAgentsRecyclerView = view.findViewById(R.id.recycler_recent_agents)
        recentTasksRecyclerView = view.findViewById(R.id.recycler_recent_tasks)

        // Setup RecyclerViews
        setupRecyclerViews()

        // Observe LiveData
        observeLiveData()

        // Load data
        loadData()
    }

    /**
     * Setup RecyclerViews
     */
    private fun setupRecyclerViews() {
        // Recent Agents RecyclerView
        recentAgentsRecyclerView.layoutManager = LinearLayoutManager(
            requireContext(), LinearLayoutManager.HORIZONTAL, false
        )
        recentAgentsRecyclerView.adapter = AgentAdapter(
            mutableListOf(),
            onAgentClick = { agent ->
                // Navigate to agent detail
            }
        )

        // Recent Tasks RecyclerView
        recentTasksRecyclerView.layoutManager = LinearLayoutManager(
            requireContext(), LinearLayoutManager.HORIZONTAL, false
        )
        recentTasksRecyclerView.adapter = TaskAdapter(
            mutableListOf(),
            onTaskClick = { task ->
                // Navigate to task detail
            }
        )
    }

    /**
     * Observe LiveData
     */
    private fun observeLiveData() {
        viewModel.recentAgents.observe(viewLifecycleOwner) { agents ->
            (recentAgentsRecyclerView.adapter as? AgentAdapter)?.updateAgents(agents)
        }

        viewModel.recentTasks.observe(viewLifecycleOwner) { tasks ->
            (recentTasksRecyclerView.adapter as? TaskAdapter)?.updateTasks(tasks)
        }
    }

    /**
     * Load data
     */
    private fun loadData() {
        viewModel.refresh()
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
}
