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
import com.livingai.app.adapters.TaskAdapter
import com.livingai.app.models.Task
import com.livingai.app.utils.Constants
import com.livingai.app.viewmodels.TaskViewModel

/**
 * TasksActivity - Displays the list of tasks
 */
class TasksActivity : AppCompatActivity() {

    private lateinit var viewModel: TaskViewModel
    private lateinit var tasksRecyclerView: RecyclerView
    private lateinit var fab: FloatingActionButton
    private lateinit var searchView: SearchView
    private lateinit var emptyStateView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tasks)

        // Initialize ViewModel
        viewModel = TaskViewModel()

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
        tasksRecyclerView = findViewById(R.id.recycler_tasks)
        fab = findViewById(R.id.fab)
        emptyStateView = findViewById(R.id.tv_empty_state)
    }

    /**
     * Setup RecyclerView
     */
    private fun setupRecyclerView() {
        tasksRecyclerView.layoutManager = LinearLayoutManager(this)
        tasksRecyclerView.adapter = TaskAdapter(
            mutableListOf(),
            onTaskClick = { task ->
                // Navigate to task detail
                navigateToTaskDetail(task)
            },
            onTaskRetry = { task ->
                // Retry the task
                viewModel.retryTask(task)
            },
            onTaskCancel = { task ->
                // Cancel the task
                viewModel.cancelTask(task)
            },
            onTaskDelete = { task ->
                // Delete the task
                viewModel.deleteTask(task)
                loadData()
            }
        )
    }

    /**
     * Setup FAB
     */
    private fun setupFAB() {
        fab.setOnClickListener {
            // Navigate to create task
            val intent = Intent(this, CreateTaskActivity::class.java)
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
                // Filter tasks based on search query
                filterTasks(newText)
                return true
            }
        })
    }

    /**
     * Load data from ViewModel
     */
    private fun loadData() {
        val tasks = viewModel.getAllTasks()
        updateTasksList(tasks)
    }

    /**
     * Update tasks list
     */
    private fun updateTasksList(tasks: List<Task>) {
        val adapter = tasksRecyclerView.adapter as? TaskAdapter
        adapter?.updateTasks(tasks)

        // Update empty state
        if (tasks.isEmpty()) {
            emptyStateView.visibility = View.VISIBLE
            tasksRecyclerView.visibility = View.GONE
        } else {
            emptyStateView.visibility = View.GONE
            tasksRecyclerView.visibility = View.VISIBLE
        }
    }

    /**
     * Filter tasks based on search query
     */
    private fun filterTasks(query: String?) {
        val allTasks = viewModel.getAllTasks()
        val filteredTasks = if (query.isNullOrEmpty()) {
            allTasks
        } else {
            allTasks.filter {
                it.name.contains(query, ignoreCase = true) ||
                        it.description.contains(query, ignoreCase = true) ||
                        it.status.contains(query, ignoreCase = true)
            }
        }
        updateTasksList(filteredTasks)
    }

    /**
     * Navigate to task detail
     */
    private fun navigateToTaskDetail(task: Task) {
        val intent = Intent(this, TaskDetailActivity::class.java).apply {
            putExtra(Constants.INTENT_EXTRA_TASK_ID, task.id)
        }
        startActivity(intent)
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_tasks, menu)
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
        // Implementation for showing filter options by status
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
