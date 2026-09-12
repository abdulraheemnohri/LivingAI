package com.livingai.app.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.livingai.app.models.Agent
import com.livingai.app.models.Task
import com.livingai.app.utils.Constants

/**
 * DashboardViewModel - ViewModel for the dashboard
 */
class DashboardViewModel : ViewModel() {

    // LiveData for statistics
    private val _totalAgentCount = MutableLiveData<Int>()
    val totalAgentCount: LiveData<Int> = _totalAgentCount

    private val _totalTaskCount = MutableLiveData<Int>()
    val totalTaskCount: LiveData<Int> = _totalTaskCount

    private val _completedTaskCount = MutableLiveData<Int>()
    val completedTaskCount: LiveData<Int> = _completedTaskCount

    private val _activeAgentCount = MutableLiveData<Int>()
    val activeAgentCount: LiveData<Int> = _activeAgentCount

    // LiveData for recent items
    private val _recentAgents = MutableLiveData<List<Agent>>()
    val recentAgents: LiveData<List<Agent>> = _recentAgents

    private val _recentTasks = MutableLiveData<List<Task>>()
    val recentTasks: LiveData<List<Task>> = _recentTasks

    // Mock data for demonstration
    private val mockAgents = listOf(
        Agent(
            id = "1",
            name = "Research Agent",
            description = "Performs research tasks",
            type = Constants.AGENT_TYPE_RESEARCH,
            status = Constants.AGENT_STATUS_ACTIVE,
            createdAt = "2024-01-01",
            updatedAt = "2024-01-15",
            tasksCompleted = 42,
            averageExecutionTime = 125.5
        ),
        Agent(
            id = "2",
            name = "Development Agent",
            description = "Handles development tasks",
            type = Constants.AGENT_TYPE_DEVELOPMENT,
            status = Constants.AGENT_STATUS_INACTIVE,
            createdAt = "2024-01-02",
            updatedAt = "2024-01-14",
            tasksCompleted = 28,
            averageExecutionTime = 85.2
        ),
        Agent(
            id = "3",
            name = "Analysis Agent",
            description = "Performs data analysis",
            type = Constants.AGENT_TYPE_ANALYSIS,
            status = Constants.AGENT_STATUS_ACTIVE,
            createdAt = "2024-01-03",
            updatedAt = "2024-01-16",
            tasksCompleted = 35,
            averageExecutionTime = 95.7
        )
    )

    private val mockTasks = listOf(
        Task(
            id = "1",
            name = "Market Research",
            description = "Research market trends",
            agentName = "Research Agent",
            priority = Constants.PRIORITY_HIGH,
            status = Constants.TASK_STATUS_COMPLETED,
            createdAt = "2024-01-10",
            updatedAt = "2024-01-15",
            completedAt = "2024-01-15",
            executionTime = 125.5,
            retryCount = 0
        ),
        Task(
            id = "2",
            name = "Code Review",
            description = "Review recent code changes",
            agentName = "Development Agent",
            priority = Constants.PRIORITY_MEDIUM,
            status = Constants.TASK_STATUS_IN_PROGRESS,
            createdAt = "2024-01-12",
            updatedAt = "2024-01-16",
            completedAt = null,
            executionTime = 0.0,
            retryCount = 0
        ),
        Task(
            id = "3",
            name = "Data Analysis",
            description = "Analyze user data",
            agentName = "Analysis Agent",
            priority = Constants.PRIORITY_HIGH,
            status = Constants.TASK_STATUS_PENDING,
            createdAt = "2024-01-14",
            updatedAt = "2024-01-14",
            completedAt = null,
            executionTime = 0.0,
            retryCount = 0
        )
    )

    init {
        // Initialize with mock data
        updateStatistics()
        _recentAgents.value = mockAgents.take(5)
        _recentTasks.value = mockTasks.take(5)
    }

    /**
     * Get recent agents
     */
    fun getRecentAgents(limit: Int): List<Agent> {
        return mockAgents.take(limit)
    }

    /**
     * Get recent tasks
     */
    fun getRecentTasks(limit: Int): List<Task> {
        return mockTasks.take(limit)
    }

    /**
     * Get total agent count
     */
    fun getTotalAgentCount(): Int {
        return mockAgents.size
    }

    /**
     * Get total task count
     */
    fun getTotalTaskCount(): Int {
        return mockTasks.size
    }

    /**
     * Get completed task count
     */
    fun getCompletedTaskCount(): Int {
        return mockTasks.count { it.status == Constants.TASK_STATUS_COMPLETED }
    }

    /**
     * Get active agent count
     */
    fun getActiveAgentCount(): Int {
        return mockAgents.count { it.status == Constants.AGENT_STATUS_ACTIVE }
    }

    /**
     * Update statistics
     */
    private fun updateStatistics() {
        _totalAgentCount.value = getTotalAgentCount()
        _totalTaskCount.value = getTotalTaskCount()
        _completedTaskCount.value = getCompletedTaskCount()
        _activeAgentCount.value = getActiveAgentCount()
    }

    /**
     * Refresh data
     */
    fun refresh() {
        // In a real implementation, this would fetch fresh data
        updateStatistics()
        _recentAgents.value = getRecentAgents(5)
        _recentTasks.value = getRecentTasks(5)
    }
}
