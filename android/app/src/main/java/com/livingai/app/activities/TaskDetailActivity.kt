package com.livingai.app.activities

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.R
import com.livingai.app.models.Task
import com.livingai.app.utils.Constants
import com.livingai.app.viewmodels.TaskViewModel

/**
 * TaskDetailActivity - Displays detailed information about a task
 */
class TaskDetailActivity : AppCompatActivity() {

    private lateinit var viewModel: TaskViewModel
    private var taskId: String = ""
    private var task: Task? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_task_detail)

        // Initialize ViewModel
        viewModel = TaskViewModel()

        // Get task ID from intent
        taskId = intent.getStringExtra(Constants.INTENT_EXTRA_TASK_ID) ?: ""

        // Setup toolbar
        setupToolbar()

        // Load task data
        loadTaskData()
    }

    /**
     * Setup the toolbar
     */
    private fun setupToolbar() {
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.apply {
            title = getString(R.string.title_task_detail)
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
    }

    /**
     * Load task data
     */
    private fun loadTaskData() {
        task = viewModel.getTaskById(taskId)
        if (task != null) {
            updateUI()
        } else {
            // Task not found, finish activity
            finish()
        }
    }

    /**
     * Update UI with task data
     */
    private fun updateUI() {
        task?.let { task ->
            // Set task info
            findViewById<TextView>(R.id.tv_task_name).text = task.name
            findViewById<TextView>(R.id.tv_task_status).text = task.status
            findViewById<TextView>(R.id.tv_task_priority).text = task.priority
            findViewById<TextView>(R.id.tv_task_description).text = task.description

            // Set additional info
            findViewById<TextView>(R.id.tv_task_created).text = getString(
                R.string.created_format, task.createdAt
            )
            findViewById<TextView>(R.id.tv_task_updated).text = getString(
                R.string.updated_format, task.updatedAt
            )
            findViewById<TextView>(R.id.tv_task_completed).text = getString(
                R.string.completed_format, task.completedAt ?: "Not completed"
            )

            // Set agent info
            findViewById<TextView>(R.id.tv_agent_name).text = task.agentName

            // Set execution info
            findViewById<TextView>(R.id.tv_execution_time).text = getString(
                R.string.execution_time_format, task.executionTime
            )
            findViewById<TextView>(R.id.tv_retry_count).text = task.retryCount.toString()

            // Set output
            findViewById<TextView>(R.id.tv_output).text = task.output ?: getString(R.string.no_output)
            findViewById<TextView>(R.id.tv_error).text = task.error ?: getString(R.string.no_errors)
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_task_detail, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_retry -> {
                // Retry task
                retryTask()
                return true
            }
            R.id.action_cancel -> {
                // Cancel task
                cancelTask()
                return true
            }
            R.id.action_delete -> {
                // Delete task
                deleteTask()
                return true
            }
            android.R.id.home -> {
                onBackPressed()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    /**
     * Retry task
     */
    private fun retryTask() {
        task?.let { task ->
            viewModel.retryTask(task)
            loadTaskData()
        }
    }

    /**
     * Cancel task
     */
    private fun cancelTask() {
        task?.let { task ->
            viewModel.cancelTask(task)
            loadTaskData()
        }
    }

    /**
     * Delete task
     */
    private fun deleteTask() {
        task?.let { task ->
            viewModel.deleteTask(task)
            finish()
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
