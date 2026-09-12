package com.livingai.app.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

/**
 * DocumentationViewModel - ViewModel for documentation content
 */
class DocumentationViewModel : ViewModel() {

    private val _documentation = MutableLiveData<Map<String, String>>()
    val documentation: LiveData<Map<String, String>> = _documentation

    private val _currentSection = MutableLiveData<String>()
    val currentSection: LiveData<String> = _currentSection

    private val _searchResults = MutableLiveData<List<Pair<String, String>>>()
    val searchResults: LiveData<List<Pair<String, String>>> = _searchResults

    // Mock documentation content
    private val mockDocumentation = mapOf(
        "overview" to "# LivingAI Overview\n\nLivingAI is a local AI operating system for Android that provides...",
        "getting_started" to "# Getting Started\n\nTo get started with LivingAI, follow these steps...",
        "agents" to "# Agents\n\nAgents are AI entities that perform specific tasks...",
        "tools" to "# Tools\n\nTools are utilities that agents can use to perform tasks...",
        "tasks" to "# Tasks\n\nTasks are jobs that agents execute...",
        "memory" to "# Memory\n\nMemory stores information for agents to use...",
        "terminal" to "# Terminal\n\nThe terminal allows you to execute commands...",
        "settings" to "# Settings\n\nConfigure LivingAI to your preferences...",
        "api" to "# API Reference\n\nLivingAI provides a REST API for integration...",
        "faq" to "# FAQ\n\nFrequently asked questions about LivingAI..."
    )

    init {
        _documentation.value = mockDocumentation
        _currentSection.value = "overview"
    }

    /**
     * Get documentation content
     */
    fun getDocumentationContent(): Map<String, String> {
        return mockDocumentation
    }

    /**
     * Get content for a specific section
     */
    fun getSectionContent(section: String): String? {
        return mockDocumentation[section]
    }

    /**
     * Set current section
     */
    fun setCurrentSection(section: String) {
        _currentSection.value = section
    }

    /**
     * Search documentation
     */
    fun search(query: String) {
        val results = mockDocumentation.entries
            .filter { it.value.contains(query, ignoreCase = true) }
            .map { Pair(it.key, it.value) }
        _searchResults.value = results
    }

    /**
     * Get all section titles
     */
    fun getSectionTitles(): List<String> {
        return mockDocumentation.keys.toList()
    }

    /**
     * Refresh documentation
     */
    fun refresh() {
        _documentation.value = mockDocumentation
    }
}
