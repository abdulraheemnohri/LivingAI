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
import com.livingai.app.adapters.TaskAdapter
import com.livingai.app.viewmodels.TaskViewModel

/**
 * TasksFragment - Displays the list of tasks
 */
class TasksFragment : Fragment() {

    private lateinit var viewModel: TaskViewModel
    private lateinit var tasksRecyclerView: RecyclerView
    private lateinit var emptyStateView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this).get(TaskViewModel::class.java)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_tasks, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize views
        tasksRecyclerView = view.findViewById(R.id.recycler_tasks)
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
        tasksRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        tasksRecyclerView.adapter = TaskAdapter(
            mutableListOf(),
            onTaskClick = { task ->
                // Navigate to task detail
            },
            onTaskRetry = { task ->
                viewModel.retryTask(task)
            },
            onTaskCancel = { task ->
                viewModel.cancelTask(task)
            },
            onTaskDelete = { task ->
                viewModel.deleteTask(task)
            }
        )
    }

    /**
     * Observe LiveData
     */
    private fun observeLiveData() {
        viewModel.tasks.observe(viewLifecycleOwner) { tasks ->
            updateTasksList(tasks)
        }
    }

    /**
     * Update tasks list
     */
    private fun updateTasksList(tasks: List<com.livingai.app.models.Task>) {
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
