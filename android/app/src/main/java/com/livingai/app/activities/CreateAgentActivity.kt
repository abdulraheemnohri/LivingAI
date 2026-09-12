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
import com.livingai.app.models.Agent
import com.livingai.app.utils.Constants
import com.livingai.app.utils.PreferenceHelper
import com.livingai.app.viewmodels.AgentViewModel

/**
 * CreateAgentActivity - Allows users to create a new AI agent
 */
class CreateAgentActivity : AppCompatActivity() {

    private lateinit var viewModel: AgentViewModel
    private lateinit var nameEditText: EditText
    private lateinit var descriptionEditText: EditText
    private lateinit var typeSpinner: Spinner
    private lateinit var createButton: Button
    private lateinit var cancelButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_create_agent)

        // Initialize ViewModel
        viewModel = AgentViewModel()

        // Initialize views
        initializeViews()

        // Setup spinner
        setupSpinner()

        // Setup buttons
        setupButtons()

        // Setup toolbar
        setupToolbar()
    }

    /**
     * Initialize all views
     */
    private fun initializeViews() {
        nameEditText = findViewById(R.id.et_agent_name)
        descriptionEditText = findViewById(R.id.et_agent_description)
        typeSpinner = findViewById(R.id.spinner_agent_type)
        createButton = findViewById(R.id.btn_create)
        cancelButton = findViewById(R.id.btn_cancel)
    }

    /**
     * Setup the type spinner
     */
    private fun setupSpinner() {
        val agentTypes = listOf(
            Constants.AGENT_TYPE_GENERAL,
            Constants.AGENT_TYPE_RESEARCH,
            Constants.AGENT_TYPE_DEVELOPMENT,
            Constants.AGENT_TYPE_ANALYSIS,
            Constants.AGENT_TYPE_CREATIVE
        )

        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, agentTypes)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        typeSpinner.adapter = adapter
    }

    /**
     * Setup buttons
     */
    private fun setupButtons() {
        createButton.setOnClickListener {
            createAgent()
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
            title = getString(R.string.title_create_agent)
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
    }

    /**
     * Create a new agent
     */
    private fun createAgent() {
        val name = nameEditText.text.toString().trim()
        val description = descriptionEditText.text.toString().trim()
        val type = typeSpinner.selectedItem.toString()

        // Validate inputs
        if (name.isEmpty()) {
            Toast.makeText(this, R.string.error_name_required, Toast.LENGTH_SHORT).show()
            return
        }

        // Create agent
        val agent = Agent(
            id = System.currentTimeMillis().toString(),
            name = name,
            description = description,
            type = type,
            status = Constants.AGENT_STATUS_INACTIVE,
            createdAt = System.currentTimeMillis().toString(),
            updatedAt = System.currentTimeMillis().toString(),
            tasksCompleted = 0,
            averageExecutionTime = 0.0
        )

        // Save agent
        viewModel.addAgent(agent)

        // Show success message
        Toast.makeText(this, R.string.agent_created_successfully, Toast.LENGTH_SHORT).show()

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
                createAgent()
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
