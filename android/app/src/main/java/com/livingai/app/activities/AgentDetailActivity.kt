package com.livingai.app.activities

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.R
import com.livingai.app.models.Agent
import com.livingai.app.utils.Constants
import com.livingai.app.viewmodels.AgentViewModel

/**
 * AgentDetailActivity - Displays detailed information about an agent
 */
class AgentDetailActivity : AppCompatActivity() {

    private lateinit var viewModel: AgentViewModel
    private var agentId: String = ""
    private var agent: Agent? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_agent_detail)

        // Initialize ViewModel
        viewModel = AgentViewModel()

        // Get agent ID from intent
        agentId = intent.getStringExtra(Constants.INTENT_EXTRA_AGENT_ID) ?: ""

        // Setup toolbar
        setupToolbar()

        // Load agent data
        loadAgentData()
    }

    /**
     * Setup the toolbar
     */
    private fun setupToolbar() {
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.apply {
            title = getString(R.string.title_agent_detail)
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
        }
    }

    /**
     * Load agent data
     */
    private fun loadAgentData() {
        agent = viewModel.getAgentById(agentId)
        if (agent != null) {
            updateUI()
        } else {
            // Agent not found, finish activity
            finish()
        }
    }

    /**
     * Update UI with agent data
     */
    private fun updateUI() {
        agent?.let { agent ->
            // Set agent info
            findViewById<TextView>(R.id.tv_agent_name).text = agent.name
            findViewById<TextView>(R.id.tv_agent_type).text = agent.type
            findViewById<TextView>(R.id.tv_agent_status).text = agent.status
            findViewById<TextView>(R.id.tv_agent_description).text = agent.description

            // Set additional info
            findViewById<TextView>(R.id.tv_agent_created).text = getString(
                R.string.created_format, agent.createdAt
            )
            findViewById<TextView>(R.id.tv_agent_updated).text = getString(
                R.string.updated_format, agent.updatedAt
            )

            // Set statistics
            findViewById<TextView>(R.id.tv_tasks_completed).text = agent.tasksCompleted.toString()
            findViewById<TextView>(R.id.tv_execution_time).text = getString(
                R.string.execution_time_format, agent.averageExecutionTime
            )
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_agent_detail, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_edit -> {
                // Edit agent
                editAgent()
                return true
            }
            R.id.action_start -> {
                // Start agent
                startAgent()
                return true
            }
            R.id.action_stop -> {
                // Stop agent
                stopAgent()
                return true
            }
            R.id.action_delete -> {
                // Delete agent
                deleteAgent()
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
     * Edit agent
     */
    private fun editAgent() {
        // Implementation for editing agent
    }

    /**
     * Start agent
     */
    private fun startAgent() {
        agent?.let { agent ->
            viewModel.startAgent(agent)
            loadAgentData()
        }
    }

    /**
     * Stop agent
     */
    private fun stopAgent() {
        agent?.let { agent ->
            viewModel.stopAgent(agent)
            loadAgentData()
        }
    }

    /**
     * Delete agent
     */
    private fun deleteAgent() {
        agent?.let { agent ->
            viewModel.deleteAgent(agent)
            finish()
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
