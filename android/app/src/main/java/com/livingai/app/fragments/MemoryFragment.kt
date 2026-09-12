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
import com.livingai.app.adapters.MemoryAdapter
import com.livingai.app.viewmodels.MemoryViewModel

/**
 * MemoryFragment - Displays the list of memory entries
 */
class MemoryFragment : Fragment() {

    private lateinit var viewModel: MemoryViewModel
    private lateinit var memoryRecyclerView: RecyclerView
    private lateinit var emptyStateView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this).get(MemoryViewModel::class.java)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_memory, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize views
        memoryRecyclerView = view.findViewById(R.id.recycler_memory)
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
        memoryRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        memoryRecyclerView.adapter = MemoryAdapter(
            mutableListOf(),
            onMemoryClick = { entry ->
                // Show memory detail
            },
            onMemoryDelete = { entry ->
                viewModel.deleteMemoryEntry(entry)
            }
        )
    }

    /**
     * Observe LiveData
     */
    private fun observeLiveData() {
        viewModel.memoryEntries.observe(viewLifecycleOwner) { entries ->
            updateMemoryList(entries)
        }
    }

    /**
     * Update memory list
     */
    private fun updateMemoryList(entries: List<com.livingai.app.models.MemoryEntry>) {
        val adapter = memoryRecyclerView.adapter as? MemoryAdapter
        adapter?.updateEntries(entries)

        // Update empty state
        if (entries.isEmpty()) {
            emptyStateView.visibility = View.VISIBLE
            memoryRecyclerView.visibility = View.GONE
        } else {
            emptyStateView.visibility = View.GONE
            memoryRecyclerView.visibility = View.VISIBLE
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
