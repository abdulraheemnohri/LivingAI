package com.livingai.app.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.livingai.app.models.Agent
import com.livingai.app.utils.Constants

/**
 * AgentViewModel - ViewModel for managing agents
 */
class AgentViewModel : ViewModel() {

    private val _agents = MutableLiveData<List<Agent>>()
    val agents: LiveData<List<Agent>> = _agents

    private val _selectedAgent = MutableLiveData<Agent?>()
    val selectedAgent: LiveData<Agent?> = _selectedAgent

    // Mock data
    private val mockAgents = mutableListOf(
        Agent(
            id = "1",
            name = "Research Agent",
            description = "Performs research tasks and data gathering",
            type = Constants.AGENT_TYPE_RESEARCH,
            status = Constants.AGENT_STATUS_ACTIVE,
            createdAt = "2024-01-01 10:00:00",
            updatedAt = "2024-01-15 14:30:00",
            tasksCompleted = 42,
            averageExecutionTime = 125.5,
            version = "1.0.0",
            author = "LivingAI Team",
            tags = listOf("research", "data", "analysis")
        ),
        Agent(
            id = "2",
            name = "Development Agent",
            description = "Handles code development and debugging",
            type = Constants.AGENT_TYPE_DEVELOPMENT,
            status = Constants.AGENT_STATUS_INACTIVE,
            createdAt = "2024-01-02 11:00:00",
            updatedAt = "2024-01-14 09:15:00",
            tasksCompleted = 28,
            averageExecutionTime = 85.2,
            version = "1.1.0",
            author = "LivingAI Team",
            tags = listOf("development", "coding", "debugging")
        ),
        Agent(
            id = "3",
            name = "Analysis Agent",
            description = "Performs data analysis and visualization",
            type = Constants.AGENT_TYPE_ANALYSIS,
            status = Constants.AGENT_STATUS_ACTIVE,
            createdAt = "2024-01-03 12:00:00",
            updatedAt = "2024-01-16 16:45:00",
            tasksCompleted = 35,
            averageExecutionTime = 95.7,
            version = "1.0.0",
            author = "LivingAI Team",
            tags = listOf("analysis", "data", "visualization")
        ),
        Agent(
            id = "4",
            name = "Creative Agent",
            description = "Generates creative content and ideas",
            type = Constants.AGENT_TYPE_CREATIVE,
            status = Constants.AGENT_STATUS_INACTIVE,
            createdAt = "2024-01-04 13:00:00",
            updatedAt = "2024-01-13 10:20:00",
            tasksCompleted = 18,
            averageExecutionTime = 150.0,
            version = "1.0.0",
            author = "LivingAI Team",
            tags = listOf("creative", "content", "ideas")
        ),
        Agent(
            id = "5",
            name = "General Purpose Agent",
            description = "Handles general tasks and queries",
            type = Constants.AGENT_TYPE_GENERAL,
            status = Constants.AGENT_STATUS_ACTIVE,
            createdAt = "2024-01-05 14:00:00",
            updatedAt = "2024-01-17 11:30:00",
            tasksCompleted = 56,
            averageExecutionTime = 75.3,
            version = "1.2.0",
            author = "LivingAI Team",
            tags = listOf("general", "tasks", "queries")
        )
    )

    init {
        _agents.value = mockAgents
    }

    /**
     * Get all agents
     */
    fun getAllAgents(): List<Agent> {
        return mockAgents
    }

    /**
     * Get agent by ID
     */
    fun getAgentById(agentId: String): Agent? {
        return mockAgents.find { it.id == agentId }
    }

    /**
     * Get agents by type
     */
    fun getAgentsByType(type: String): List<Agent> {
        return mockAgents.filter { it.type == type }
    }

    /**
     * Get active agents
     */
    fun getActiveAgents(): List<Agent> {
        return mockAgents.filter { it.status == Constants.AGENT_STATUS_ACTIVE }
    }

    /**
     * Add a new agent
     */
    fun addAgent(agent: Agent) {
        mockAgents.add(agent)
        _agents.value = mockAgents
    }

    /**
     * Update an existing agent
     */
    fun updateAgent(updatedAgent: Agent) {
        val index = mockAgents.indexOfFirst { it.id == updatedAgent.id }
        if (index >= 0) {
            mockAgents[index] = updatedAgent
            _agents.value = mockAgents
        }
    }

    /**
     * Delete an agent
     */
    fun deleteAgent(agent: Agent) {
        mockAgents.remove(agent)
        _agents.value = mockAgents
    }

    /**
     * Start an agent
     */
    fun startAgent(agent: Agent) {
        val index = mockAgents.indexOfFirst { it.id == agent.id }
        if (index >= 0) {
            mockAgents[index] = mockAgents[index].copy(
                status = Constants.AGENT_STATUS_ACTIVE,
                updatedAt = System.currentTimeMillis().toString()
            )
            _agents.value = mockAgents
        }
    }

    /**
     * Stop an agent
     */
    fun stopAgent(agent: Agent) {
        val index = mockAgents.indexOfFirst { it.id == agent.id }
        if (index >= 0) {
            mockAgents[index] = mockAgents[index].copy(
                status = Constants.AGENT_STATUS_INACTIVE,
                updatedAt = System.currentTimeMillis().toString()
            )
            _agents.value = mockAgents
        }
    }

    /**
     * Select an agent
     */
    fun selectAgent(agent: Agent) {
        _selectedAgent.value = agent
    }

    /**
     * Refresh agents list
     */
    fun refresh() {
        _agents.value = mockAgents
    }
}
