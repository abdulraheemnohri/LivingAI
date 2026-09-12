package com.livingai.app.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.livingai.app.models.Tool
import com.livingai.app.models.ToolParameter
import com.livingai.app.utils.Constants

/**
 * ToolViewModel - ViewModel for managing tools
 */
class ToolViewModel : ViewModel() {

    private val _tools = MutableLiveData<List<Tool>>()
    val tools: LiveData<List<Tool>> = _tools

    private val _selectedTool = MutableLiveData<Tool?>()
    val selectedTool: LiveData<Tool?> = _selectedTool

    // Mock data
    private val mockTools = mutableListOf(
        Tool(
            id = "1",
            name = "Web Search",
            description = "Search the web for information",
            category = Constants.TOOL_CATEGORY_NETWORK,
            version = "1.0.0",
            author = "LivingAI Team",
            license = "MIT",
            status = Constants.TOOL_STATUS_ENABLED,
            isEnabled = true,
            isAsync = true,
            parameters = listOf(
                ToolParameter(
                    name = "query",
                    type = "string",
                    description = "Search query",
                    isRequired = true
                ),
                ToolParameter(
                    name = "limit",
                    type = "integer",
                    description = "Maximum number of results",
                    isRequired = false,
                    defaultValue = 10
                )
            ),
            tags = listOf("search", "web", "information"),
            usageCount = 42,
            lastUsed = "2024-01-15 14:30:00",
            createdAt = "2024-01-01 10:00:00",
            updatedAt = "2024-01-10 11:00:00",
            requiresPermissions = listOf("network_access"),
            timeout = 30000,
            maxRetries = 3
        ),
        Tool(
            id = "2",
            name = "Code Analysis",
            description = "Analyze code for quality and issues",
            category = Constants.TOOL_CATEGORY_CODE,
            version = "1.1.0",
            author = "LivingAI Team",
            license = "MIT",
            status = Constants.TOOL_STATUS_ENABLED,
            isEnabled = true,
            isAsync = false,
            parameters = listOf(
                ToolParameter(
                    name = "code",
                    type = "string",
                    description = "Code to analyze",
                    isRequired = true
                ),
                ToolParameter(
                    name = "language",
                    type = "string",
                    description = "Programming language",
                    isRequired = false,
                    defaultValue = "python"
                )
            ),
            tags = listOf("code", "analysis", "quality"),
            usageCount = 28,
            lastUsed = "2024-01-16 09:15:00",
            createdAt = "2024-01-02 11:00:00",
            updatedAt = "2024-01-12 12:00:00",
            requiresPermissions = listOf(),
            timeout = 60000,
            maxRetries = 2
        ),
        Tool(
            id = "3",
            name = "Data Visualization",
            description = "Create visualizations from data",
            category = Constants.TOOL_CATEGORY_DATA,
            version = "1.0.0",
            author = "LivingAI Team",
            license = "MIT",
            status = Constants.TOOL_STATUS_ENABLED,
            isEnabled = true,
            isAsync = true,
            parameters = listOf(
                ToolParameter(
                    name = "data",
                    type = "object",
                    description = "Data to visualize",
                    isRequired = true
                ),
                ToolParameter(
                    name = "chart_type",
                    type = "string",
                    description = "Type of chart",
                    isRequired = false,
                    defaultValue = "bar",
                    possibleValues = listOf("bar", "line", "pie", "scatter")
                )
            ),
            tags = listOf("data", "visualization", "charts"),
            usageCount = 35,
            lastUsed = "2024-01-14 16:45:00",
            createdAt = "2024-01-03 12:00:00",
            updatedAt = "2024-01-14 15:00:00",
            requiresPermissions = listOf(),
            timeout = 45000,
            maxRetries = 2
        ),
        Tool(
            id = "4",
            name = "Text Generation",
            description = "Generate text content",
            category = Constants.TOOL_CATEGORY_AI,
            version = "1.2.0",
            author = "LivingAI Team",
            license = "MIT",
            status = Constants.TOOL_STATUS_DISABLED,
            isEnabled = false,
            isAsync = true,
            parameters = listOf(
                ToolParameter(
                    name = "prompt",
                    type = "string",
                    description = "Text generation prompt",
                    isRequired = true
                ),
                ToolParameter(
                    name = "max_length",
                    type = "integer",
                    description = "Maximum length of output",
                    isRequired = false,
                    defaultValue = 500
                )
            ),
            tags = listOf("text", "generation", "ai"),
            usageCount = 18,
            lastUsed = "2024-01-13 10:20:00",
            createdAt = "2024-01-04 13:00:00",
            updatedAt = "2024-01-13 11:00:00",
            requiresPermissions = listOf("network_access"),
            timeout = 60000,
            maxRetries = 3
        ),
        Tool(
            id = "5",
            name = "File Manager",
            description = "Manage files and directories",
            category = Constants.TOOL_CATEGORY_FILE,
            version = "1.0.0",
            author = "LivingAI Team",
            license = "MIT",
            status = Constants.TOOL_STATUS_ENABLED,
            isEnabled = true,
            isAsync = false,
            parameters = listOf(
                ToolParameter(
                    name = "path",
                    type = "string",
                    description = "File or directory path",
                    isRequired = true
                ),
                ToolParameter(
                    name = "operation",
                    type = "string",
                    description = "Operation to perform",
                    isRequired = true,
                    possibleValues = listOf("read", "write", "delete", "list")
                )
            ),
            tags = listOf("file", "manager", "storage"),
            usageCount = 25,
            lastUsed = "2024-01-17 11:30:00",
            createdAt = "2024-01-05 14:00:00",
            updatedAt = "2024-01-15 10:00:00",
            requiresPermissions = listOf("file_system"),
            timeout = 30000,
            maxRetries = 2
        )
    )

    init {
        _tools.value = mockTools
    }

    /**
     * Get all tools
     */
    fun getAllTools(): List<Tool> {
        return mockTools
    }

    /**
     * Get tool by ID
     */
    fun getToolById(toolId: String): Tool? {
        return mockTools.find { it.id == toolId }
    }

    /**
     * Get tools by category
     */
    fun getToolsByCategory(category: String): List<Tool> {
        return mockTools.filter { it.category == category }
    }

    /**
     * Get enabled tools
     */
    fun getEnabledTools(): List<Tool> {
        return mockTools.filter { it.isEnabled }
    }

    /**
     * Get disabled tools
     */
    fun getDisabledTools(): List<Tool> {
        return mockTools.filter { !it.isEnabled }
    }

    /**
     * Add a new tool
     */
    fun addTool(tool: Tool) {
        mockTools.add(tool)
        _tools.value = mockTools
    }

    /**
     * Update an existing tool
     */
    fun updateTool(updatedTool: Tool) {
        val index = mockTools.indexOfFirst { it.id == updatedTool.id }
        if (index >= 0) {
            mockTools[index] = updatedTool
            _tools.value = mockTools
        }
    }

    /**
     * Delete a tool
     */
    fun deleteTool(tool: Tool) {
        mockTools.remove(tool)
        _tools.value = mockTools
    }

    /**
     * Toggle tool enabled/disabled
     */
    fun toggleTool(tool: Tool) {
        val index = mockTools.indexOfFirst { it.id == tool.id }
        if (index >= 0) {
            mockTools[index] = mockTools[index].copy(
                isEnabled = !tool.isEnabled,
                status = if (tool.isEnabled) Constants.TOOL_STATUS_DISABLED else Constants.TOOL_STATUS_ENABLED,
                updatedAt = System.currentTimeMillis().toString()
            )
            _tools.value = mockTools
        }
    }

    /**
     * Select a tool
     */
    fun selectTool(tool: Tool) {
        _selectedTool.value = tool
    }

    /**
     * Refresh tools list
     */
    fun refresh() {
        _tools.value = mockTools
    }
}
