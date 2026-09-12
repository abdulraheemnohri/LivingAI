package com.livingai.app.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * Agent - Represents an AI agent in the LivingAI system
 */
@Parcelize
@kotlinx.serialization.Serializable
data class Agent(
    val id: String = "",
    val name: String = "",
    val description: String = "",
    val type: String = "",
    val status: String = "",
    val createdAt: String = "",
    val updatedAt: String = "",
    val tasksCompleted: Int = 0,
    val averageExecutionTime: Double = 0.0,
    val configuration: Map<String, Any> = emptyMap(),
    val capabilities: List<String> = emptyList(),
    val dependencies: List<String> = emptyList(),
    val version: String = "1.0.0",
    val author: String = "",
    val license: String = "",
    val tags: List<String> = emptyList()
) : Parcelable {
    // Additional computed properties
    val isActive: Boolean get() = status == "active"
    val isEnabled: Boolean get() = status != "disabled"
    val displayName: String get() = if (name.isNotEmpty()) name else "Unnamed Agent"
}
