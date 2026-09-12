package com.livingai.app.activities

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.R
import com.livingai.app.models.Task
import com.livingai.app.utils.Constants
import com.livingai.app.viewmodels.AgentViewModel
import com.livingai.app.viewmodels.TaskViewModel

/**
 * CreateTaskActivity - Allows users to create a new task
 */
class CreateTaskActivity : AppCompatActivity() {

    private lateinit var taskViewModel: TaskViewModel
    private lateinit var agentViewModel: AgentViewModel
    private lateinit var nameEditText: EditText
    private lateinit var descriptionEditText: EditText
    private lateinit var agentSpinner: Spinner
    private lateinit var prioritySpinner: Spinner
    private lateinit var createButton: Button
    private lateinit var cancelButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_create_task)

        // Initialize ViewModels
        taskViewModel = TaskViewModel()
        agentViewModel = AgentViewModel()

        // Initialize views
        initializeViews()

        // Setup spinners
        setupSpinners()

        // Setup buttons
        setupButtons()

        // Setup toolbar
        setupToolbar()
    }

    /**
     * Initialize all views
     */
    private fun initializeViews() {
        nameEditText = findViewById(R.id.et_task_name)
        descriptionEditText = findViewById(R.id.et_task_description)
        agentSpinner = findViewById(R.id.spinner_task_agent)
        prioritySpinner = findViewById(R.id.spinner_task_priority)
        createButton = findViewById(R.id.btn_create)
        cancelButton = findViewById(R.id.btn_cancel)
    }

    /**
     * Setup the spinners
     */
    private fun setupSpinners() {
        // Setup agent spinner
        val agents = agentViewModel.getAllAgents()
        val agentNames = agents.map { it.name }
        if (agentNames.isEmpty()) {
            agentNames.add(getString(R.string.no_agents_available))
        }

        val agentAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, agentNames)
        agentAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        agentSpinner.adapter = agentAdapter

        // Setup priority spinner
        val priorities = listOf(
            Constants.PRIORITY_LOW,
            Constants.PRIORITY_MEDIUM,
            Constants.PRIORITY_HIGH,
            Constants.PRIORITY_CRITICAL
        )

        val priorityAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, priorities)
        priorityAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        prioritySpinner.adapter = priorityAdapter
    }

    /**
     * Setup buttons
     */
    private fun setupButtons() {
        createButton.setOnClickListener {
            createTask()
        }

        cancelButton.setOnClickListener {
            finish()
        }
    }

    /**
     * Setup the toolbar
     */
    private fun setupToolbar() {
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.apply {
            title = getString(R.string.title_create_task)
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
    }

    /**
     * Create a new task
     */
    private fun createTask() {
        val name = nameEditText.text.toString().trim()
        val description = descriptionEditText.text.toString().trim()
        val agentName = agentSpinner.selectedItem.toString()
        val priority = prioritySpinner.selectedItem.toString()

        // Validate inputs
        if (name.isEmpty()) {
            Toast.makeText(this, R.string.error_name_required, Toast.LENGTH_SHORT).show()
            return
        }

        // Create task
        val task = Task(
            id = System.currentTimeMillis().toString(),
            name = name,
            description = description,
            agentName = agentName,
            priority = priority,
            status = Constants.TASK_STATUS_PENDING,
            createdAt = System.currentTimeMillis().toString(),
            updatedAt = System.currentTimeMillis().toString(),
            completedAt = null,
            executionTime = 0.0,
            retryCount = 0,
            output = null,
            error = null
        )

        // Save task
        taskViewModel.addTask(task)

        // Show success message
        Toast.makeText(this, R.string.task_created_successfully, Toast.LENGTH_SHORT).show()

        // Finish activity
        finish()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_create, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_save -> {
                createTask()
                return true
            }
            android.R.id.home -> {
                onBackPressed()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
