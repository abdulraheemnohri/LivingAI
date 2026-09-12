package com.livingai.app.activities

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
import com.livingai.app.adapters.MemoryAdapter
import com.livingai.app.models.MemoryEntry
import com.livingai.app.viewmodels.MemoryViewModel

/**
 * MemoryActivity - Displays the memory entries
 */
class MemoryActivity : AppCompatActivity() {

    private lateinit var viewModel: MemoryViewModel
    private lateinit var memoryRecyclerView: RecyclerView
    private lateinit var fab: FloatingActionButton
    private lateinit var searchView: SearchView
    private lateinit var emptyStateView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_memory)

        // Initialize ViewModel
        viewModel = MemoryViewModel()

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
        memoryRecyclerView = findViewById(R.id.recycler_memory)
        fab = findViewById(R.id.fab)
        emptyStateView = findViewById(R.id.tv_empty_state)
    }

    /**
     * Setup RecyclerView
     */
    private fun setupRecyclerView() {
        memoryRecyclerView.layoutManager = LinearLayoutManager(this)
        memoryRecyclerView.adapter = MemoryAdapter(
            mutableListOf(),
            onMemoryClick = { entry ->
                // Navigate to memory detail or show content
                showMemoryDetail(entry)
            },
            onMemoryDelete = { entry ->
                // Delete the memory entry
                viewModel.deleteMemoryEntry(entry)
                loadData()
            }
        )
    }

    /**
     * Setup FAB
     */
    private fun setupFAB() {
        fab.setOnClickListener {
            // Create new memory entry
            createNewMemoryEntry()
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
                // Filter memory entries based on search query
                filterMemory(newText)
                return true
            }
        })
    }

    /**
     * Load data from ViewModel
     */
    private fun loadData() {
        val entries = viewModel.getAllMemoryEntries()
        updateMemoryList(entries)
    }

    /**
     * Update memory list
     */
    private fun updateMemoryList(entries: List<MemoryEntry>) {
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
     * Filter memory entries based on search query
     */
    private fun filterMemory(query: String?) {
        val allEntries = viewModel.getAllMemoryEntries()
        val filteredEntries = if (query.isNullOrEmpty()) {
            allEntries
        } else {
            allEntries.filter {
                it.key.contains(query, ignoreCase = true) ||
                        it.value.contains(query, ignoreCase = true) ||
                        it.category.contains(query, ignoreCase = true)
            }
        }
        updateMemoryList(filteredEntries)
    }

    /**
     * Show memory detail
     */
    private fun showMemoryDetail(entry: MemoryEntry) {
        // Implementation for showing memory detail
    }

    /**
     * Create new memory entry
     */
    private fun createNewMemoryEntry() {
        // Implementation for creating new memory entry
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_memory, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_search -> {
                // Search action handled by SearchView
                return true
            }
            R.id.action_clear_all -> {
                // Clear all memory
                viewModel.clearAllMemory()
                loadData()
                return true
            }
            R.id.action_export -> {
                // Export memory
                viewModel.exportMemory()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    override fun onResume() {
        super.onResume()
        // Refresh data when resumed
        loadData()
    }
}
