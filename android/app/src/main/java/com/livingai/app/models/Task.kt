package com.livingai.app.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * Task - Represents a task for AI agents to execute
 */
@Parcelize
@kotlinx.serialization.Serializable
data class Task(
    val id: String = "",
    val name: String = "",
    val description: String = "",
    val agentName: String = "",
    val priority: String = "",
    val status: String = "",
    val createdAt: String = "",
    val updatedAt: String = "",
    val completedAt: String? = null,
    val executionTime: Double = 0.0,
    val retryCount: Int = 0,
    val maxRetries: Int = 3,
    val output: String? = null,
    val error: String? = null,
    val inputData: Map<String, Any> = emptyMap(),
    val outputData: Map<String, Any> = emptyMap(),
    val metadata: Map<String, Any> = emptyMap()
) : Parcelable {
    // Additional computed properties
    val isCompleted: Boolean get() = status == "completed"
    val isFailed: Boolean get() = status == "failed"
    val isRunning: Boolean get() = status == "in-progress"
    val isPending: Boolean get() = status == "pending"
    val isCancelled: Boolean get() = status == "cancelled"
    val hasOutput: Boolean get() = !output.isNullOrEmpty()
    val hasError: Boolean get() = !error.isNullOrEmpty()
    val displayName: String get() = if (name.isNotEmpty()) name else "Unnamed Task"
}
