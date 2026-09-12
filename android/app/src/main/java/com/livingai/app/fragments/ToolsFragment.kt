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
import com.livingai.app.adapters.ToolAdapter
import com.livingai.app.viewmodels.ToolViewModel

/**
 * ToolsFragment - Displays the list of tools
 */
class ToolsFragment : Fragment() {

    private lateinit var viewModel: ToolViewModel
    private lateinit var toolsRecyclerView: RecyclerView
    private lateinit var emptyStateView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this).get(ToolViewModel::class.java)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_tools, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize views
        toolsRecyclerView = view.findViewById(R.id.recycler_tools)
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
        toolsRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        toolsRecyclerView.adapter = ToolAdapter(
            mutableListOf(),
            onToolClick = { tool ->
                // Navigate to tool detail
            },
            onToolToggle = { tool ->
                viewModel.toggleTool(tool)
            }
        )
    }

    /**
     * Observe LiveData
     */
    private fun observeLiveData() {
        viewModel.tools.observe(viewLifecycleOwner) { tools ->
            updateToolsList(tools)
        }
    }

    /**
     * Update tools list
     */
    private fun updateToolsList(tools: List<com.livingai.app.models.Tool>) {
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
