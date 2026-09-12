package com.livingai.app.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.livingai.app.models.Task
import com.livingai.app.utils.Constants

/**
 * TaskViewModel - ViewModel for managing tasks
 */
class TaskViewModel : ViewModel() {

    private val _tasks = MutableLiveData<List<Task>>()
    val tasks: LiveData<List<Task>> = _tasks

    private val _selectedTask = MutableLiveData<Task?>()
    val selectedTask: LiveData<Task?> = _selectedTask

    // Mock data
    private val mockTasks = mutableListOf(
        Task(
            id = "1",
            name = "Market Research",
            description = "Research current market trends and opportunities",
            agentName = "Research Agent",
            priority = Constants.PRIORITY_HIGH,
            status = Constants.TASK_STATUS_COMPLETED,
            createdAt = "2024-01-10 09:00:00",
            updatedAt = "2024-01-15 14:30:00",
            completedAt = "2024-01-15 14:30:00",
            executionTime = 125.5,
            retryCount = 0,
            output = "Market research completed successfully. Found 5 new opportunities.",
            error = null
        ),
        Task(
            id = "2",
            name = "Code Review",
            description = "Review recent code changes for quality",
            agentName = "Development Agent",
            priority = Constants.PRIORITY_MEDIUM,
            status = Constants.TASK_STATUS_IN_PROGRESS,
            createdAt = "2024-01-12 10:00:00",
            updatedAt = "2024-01-16 11:00:00",
            completedAt = null,
            executionTime = 45.2,
            retryCount = 0,
            output = null,
            error = null
        ),
        Task(
            id = "3",
            name = "Data Analysis",
            description = "Analyze user behavior data from last quarter",
            agentName = "Analysis Agent",
            priority = Constants.PRIORITY_HIGH,
            status = Constants.TASK_STATUS_PENDING,
            createdAt = "2024-01-14 13:00:00",
            updatedAt = "2024-01-14 13:00:00",
            completedAt = null,
            executionTime = 0.0,
            retryCount = 0,
            output = null,
            error = null
        ),
        Task(
            id = "4",
            name = "Content Generation",
            description = "Generate blog post content for next week",
            agentName = "Creative Agent",
            priority = Constants.PRIORITY_MEDIUM,
            status = Constants.TASK_STATUS_FAILED,
            createdAt = "2024-01-13 11:00:00",
            updatedAt = "2024-01-13 12:15:00",
            completedAt = null,
            executionTime = 75.3,
            retryCount = 2,
            output = null,
            error = "Failed to generate content: API rate limit exceeded"
        ),
        Task(
            id = "5",
            name = "System Check",
            description = "Perform system health check and diagnostics",
            agentName = "General Purpose Agent",
            priority = Constants.PRIORITY_LOW,
            status = Constants.TASK_STATUS_COMPLETED,
            createdAt = "2024-01-16 08:00:00",
            updatedAt = "2024-01-16 08:15:00",
            completedAt = "2024-01-16 08:15:00",
            executionTime = 15.2,
            retryCount = 0,
            output = "System health check passed. All systems operational.",
            error = null
        )
    )

    init {
        _tasks.value = mockTasks
    }

    /**
     * Get all tasks
     */
    fun getAllTasks(): List<Task> {
        return mockTasks
    }

    /**
     * Get task by ID
     */
    fun getTaskById(taskId: String): Task? {
        return mockTasks.find { it.id == taskId }
    }

    /**
     * Get tasks by status
     */
    fun getTasksByStatus(status: String): List<Task> {
        return mockTasks.filter { it.status == status }
    }

    /**
     * Get tasks by priority
     */
    fun getTasksByPriority(priority: String): List<Task> {
        return mockTasks.filter { it.priority == priority }
    }

    /**
     * Get pending tasks
     */
    fun getPendingTasks(): List<Task> {
        return mockTasks.filter { it.status == Constants.TASK_STATUS_PENDING }
    }

    /**
     * Get in-progress tasks
     */
    fun getInProgressTasks(): List<Task> {
        return mockTasks.filter { it.status == Constants.TASK_STATUS_IN_PROGRESS }
    }

    /**
     * Get completed tasks
     */
    fun getCompletedTasks(): List<Task> {
        return mockTasks.filter { it.status == Constants.TASK_STATUS_COMPLETED }
    }

    /**
     * Add a new task
     */
    fun addTask(task: Task) {
        mockTasks.add(task)
        _tasks.value = mockTasks
    }

    /**
     * Update an existing task
     */
    fun updateTask(updatedTask: Task) {
        val index = mockTasks.indexOfFirst { it.id == updatedTask.id }
        if (index >= 0) {
            mockTasks[index] = updatedTask
            _tasks.value = mockTasks
        }
    }

    /**
     * Delete a task
     */
    fun deleteTask(task: Task) {
        mockTasks.remove(task)
        _tasks.value = mockTasks
    }

    /**
     * Retry a task
     */
    fun retryTask(task: Task) {
        val index = mockTasks.indexOfFirst { it.id == task.id }
        if (index >= 0) {
            mockTasks[index] = mockTasks[index].copy(
                status = Constants.TASK_STATUS_PENDING,
                retryCount = task.retryCount + 1,
                updatedAt = System.currentTimeMillis().toString(),
                error = null
            )
            _tasks.value = mockTasks
        }
    }

    /**
     * Cancel a task
     */
    fun cancelTask(task: Task) {
        val index = mockTasks.indexOfFirst { it.id == task.id }
        if (index >= 0) {
            mockTasks[index] = mockTasks[index].copy(
                status = Constants.TASK_STATUS_CANCELLED,
                updatedAt = System.currentTimeMillis().toString()
            )
            _tasks.value = mockTasks
        }
    }

    /**
     * Select a task
     */
    fun selectTask(task: Task) {
        _selectedTask.value = task
    }

    /**
     * Refresh tasks list
     */
    fun refresh() {
        _tasks.value = mockTasks
    }
}
