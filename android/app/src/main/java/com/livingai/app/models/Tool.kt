package com.livingai.app.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * Tool - Represents an AI tool in the LivingAI system
 */
@Parcelize
@kotlinx.serialization.Serializable
data class Tool(
    val id: String = "",
    val name: String = "",
    val description: String = "",
    val category: String = "",
    val version: String = "",
    val author: String = "",
    val license: String = "",
    val status: String = "",
    val isEnabled: Boolean = true,
    val isAsync: Boolean = false,
    val parameters: List<ToolParameter> = emptyList(),
    val tags: List<String> = emptyList(),
    val dependencies: List<String> = emptyList(),
    val usageCount: Int = 0,
    val lastUsed: String = "",
    val createdAt: String = "",
    val updatedAt: String = "",
    val requiresPermissions: List<String> = emptyList(),
    val timeout: Long = 30000,
    val maxRetries: Int = 3
) : Parcelable {
    // Additional computed properties
    val displayName: String get() = if (name.isNotEmpty()) name else "Unnamed Tool"
    val isAvailable: Boolean get() = isEnabled && status != "error"
}

/**
 * ToolParameter - Represents a parameter for an AI tool
 */
@Parcelize
@kotlinx.serialization.Serializable
data class ToolParameter(
    val name: String = "",
    val type: String = "",
    val description: String = "",
    val isRequired: Boolean = false,
    val defaultValue: Any? = null,
    val possibleValues: List<String> = emptyList()
) : Parcelable
