package com.livingai.app.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * MemoryEntry - Represents a memory entry in the LivingAI system
 */
@Parcelize
@kotlinx.serialization.Serializable
data class MemoryEntry(
    val id: String = "",
    val key: String = "",
    val value: String = "",
    val category: String = "",
    val type: String = "",
    val metadata: Map<String, Any> = emptyMap(),
    val createdAt: String = "",
    val updatedAt: String = "",
    val expiresAt: String? = null,
    val priority: Int = 0,
    val tags: List<String> = emptyList()
) : Parcelable {
    // Additional computed properties
    val isExpired: Boolean get() = expiresAt?.let { System.currentTimeMillis() > it.toLong() } ?: false
    val isValid: Boolean get() = key.isNotEmpty() && value.isNotEmpty() && !isExpired
    val displayKey: String get() = if (key.isNotEmpty()) key else "Unnamed Entry"
}
