package com.livingai.app.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.adapters.AgentAdapter
import com.livingai.app.viewmodels.AgentViewModel

/**
 * AgentsFragment - Displays the list of agents
 */
class AgentsFragment : Fragment() {

    private lateinit var viewModel: AgentViewModel
    private lateinit var agentsRecyclerView: RecyclerView
    private lateinit var emptyStateView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this).get(AgentViewModel::class.java)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_agents, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize views
        agentsRecyclerView = view.findViewById(R.id.recycler_agents)
        emptyStateView = view.findViewById(R.id.tv_empty_state)

        // Setup RecyclerView
        setupRecyclerView()

        // Observe LiveData
        observeLiveData()

        // Load data
        loadData()
    }

    /**
     * Setup RecyclerView
     */
    private fun setupRecyclerView() {
        agentsRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        agentsRecyclerView.adapter = AgentAdapter(
            mutableListOf(),
            onAgentClick = { agent ->
                // Navigate to agent detail
            },
            onAgentStart = { agent ->
                viewModel.startAgent(agent)
            },
            onAgentStop = { agent ->
                viewModel.stopAgent(agent)
            },
            onAgentDelete = { agent ->
                viewModel.deleteAgent(agent)
            }
        )
    }

    /**
     * Observe LiveData
     */
    private fun observeLiveData() {
        viewModel.agents.observe(viewLifecycleOwner) { agents ->
            updateAgentsList(agents)
        }
    }

    /**
     * Update agents list
     */
    private fun updateAgentsList(agents: List<com.livingai.app.models.Agent>) {
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
     * Load data
     */
    private fun loadData() {
        viewModel.refresh()
    }

    override fun onResume() {
        super.onResume()
        loadData()
    }
}
