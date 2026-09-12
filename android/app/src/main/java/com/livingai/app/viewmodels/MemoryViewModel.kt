package com.livingai.app.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.livingai.app.models.MemoryEntry
import com.livingai.app.utils.Constants

/**
 * MemoryViewModel - ViewModel for managing memory entries
 */
class MemoryViewModel : ViewModel() {

    private val _memoryEntries = MutableLiveData<List<MemoryEntry>>()
    val memoryEntries: LiveData<List<MemoryEntry>> = _memoryEntries

    private val _selectedEntry = MutableLiveData<MemoryEntry?>()
    val selectedEntry: LiveData<MemoryEntry?> = _selectedEntry

    // Mock data
    private val mockEntries = mutableListOf(
        MemoryEntry(
            id = "1",
            key = "user_preferences",
            value = "{\"theme\":\"dark\",\"language\":\"en\"}",
            category = Constants.MEMORY_CATEGORY_SETTINGS,
            type = "json",
            metadata = mapOf("source" to "app_settings"),
            createdAt = "2024-01-01 10:00:00",
            updatedAt = "2024-01-15 14:30:00",
            expiresAt = null,
            priority = 1,
            tags = listOf("settings", "preferences")
        ),
        MemoryEntry(
            id = "2",
            key = "last_search_query",
            value = "Artificial Intelligence trends 2024",
            category = Constants.MEMORY_CATEGORY_CONVERSATIONS,
            type = "string",
            metadata = mapOf("timestamp" to "2024-01-15T14:30:00"),
            createdAt = "2024-01-15 14:30:00",
            updatedAt = "2024-01-15 14:30:00",
            expiresAt = "2024-01-22 14:30:00",
            priority = 2,
            tags = listOf("search", "query")
        ),
        MemoryEntry(
            id = "3",
            key = "api_response_cache",
            value = "{\"data\":[...],\"timestamp\":\"2024-01-16T09:00:00\"}",
            category = Constants.MEMORY_CATEGORY_CACHE,
            type = "json",
            metadata = mapOf("size" to "1024", "source" to "api_call"),
            createdAt = "2024-01-16 09:00:00",
            updatedAt = "2024-01-16 09:00:00",
            expiresAt = "2024-01-23 09:00:00",
            priority = 3,
            tags = listOf("cache", "api")
        ),
        MemoryEntry(
            id = "4",
            key = "user_history",
            value = "[\"search1\",\"search2\",\"search3\"]",
            category = Constants.MEMORY_CATEGORY_CONVERSATIONS,
            type = "json",
            metadata = mapOf("count" to "3"),
            createdAt = "2024-01-10 11:00:00",
            updatedAt = "2024-01-16 11:00:00",
            expiresAt = null,
            priority = 2,
            tags = listOf("history", "user")
        ),
        MemoryEntry(
            id = "5",
            key = "system_config",
            value = "{\"max_connections\":5,\"timeout\":30}",
            category = Constants.MEMORY_CATEGORY_SETTINGS,
            type = "json",
            metadata = mapOf("version" to "1.0"),
            createdAt = "2024-01-01 08:00:00",
            updatedAt = "2024-01-10 09:00:00",
            expiresAt = null,
            priority = 1,
            tags = listOf("system", "config")
        )
    )

    init {
        _memoryEntries.value = mockEntries
    }

    /**
     * Get all memory entries
     */
    fun getAllMemoryEntries(): List<MemoryEntry> {
        return mockEntries
    }

    /**
     * Get memory entry by ID
     */
    fun getMemoryEntryById(entryId: String): MemoryEntry? {
        return mockEntries.find { it.id == entryId }
    }

    /**
     * Get entries by category
     */
    fun getEntriesByCategory(category: String): List<MemoryEntry> {
        return mockEntries.filter { it.category == category }
    }

    /**
     * Get entries by key
     */
    fun getEntryByKey(key: String): MemoryEntry? {
        return mockEntries.find { it.key == key }
    }

    /**
     * Add a new memory entry
     */
    fun addMemoryEntry(entry: MemoryEntry) {
        mockEntries.add(entry)
        _memoryEntries.value = mockEntries
    }

    /**
     * Update an existing memory entry
     */
    fun updateMemoryEntry(updatedEntry: MemoryEntry) {
        val index = mockEntries.indexOfFirst { it.id == updatedEntry.id }
        if (index >= 0) {
            mockEntries[index] = updatedEntry
            _memoryEntries.value = mockEntries
        }
    }

    /**
     * Delete a memory entry
     */
    fun deleteMemoryEntry(entry: MemoryEntry) {
        mockEntries.remove(entry)
        _memoryEntries.value = mockEntries
    }

    /**
     * Select a memory entry
     */
    fun selectEntry(entry: MemoryEntry) {
        _selectedEntry.value = entry
    }

    /**
     * Clear all memory entries
     */
    fun clearAllMemory() {
        mockEntries.clear()
        _memoryEntries.value = mockEntries
    }

    /**
     * Export memory entries
     */
    fun exportMemory() {
        // Implementation for exporting memory
    }

    /**
     * Refresh memory list
     */
    fun refresh() {
        _memoryEntries.value = mockEntries
    }
}
