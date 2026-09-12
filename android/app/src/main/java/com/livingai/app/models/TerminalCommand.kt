package com.livingai.app.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * TerminalCommand - Represents a command executed in the terminal
 */
@Parcelize
@kotlinx.serialization.Serializable
data class TerminalCommand(
    val id: String = "",
    val command: String = "",
    val timestamp: Long = 0L,
    val output: String = "",
    val isSuccess: Boolean = false,
    val error: String? = null,
    val executionTime: Long = 0L,
    val workingDirectory: String = "",
    val sessionId: String = ""
) : Parcelable {
    // Additional computed properties
    val displayTime: String get() = java.text.SimpleDateFormat.getDateTimeInstance().format(timestamp)
    val hasOutput: Boolean get() = output.isNotEmpty()
    val hasError: Boolean get() = !error.isNullOrEmpty()
}

/**
 * TerminalSession - Represents a terminal session
 */
@Parcelize
@kotlinx.serialization.Serializable
data class TerminalSession(
    val id: String = "",
    val name: String = "",
    val createdAt: Long = 0L,
    val updatedAt: Long = 0L,
    val commands: List<TerminalCommand> = emptyList(),
    val workingDirectory: String = "",
    val isActive: Boolean = false
) : Parcelable
