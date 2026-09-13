package com.livingai.app.models

/**
 * RiskLevel model for LivingAI Android Application
 * 
 * Defines different risk levels for operations, tasks, and agent modes.
 * Used throughout the application for safety and security decisions.
 * 
 * Features:
 * - Multiple risk levels with descriptions
 * - Color coding for UI
 * - Confirmation requirements
 * - Autonomy mode restrictions
 * 
 * Author: Abdulraheem Nohari
 */

enum class RiskLevel(
    val level: Int,
    val description: String,
    val color: String,
    val icon: String,
    val requiresConfirmation: Boolean,
    val allowedInAutonomousMode: Boolean,
    val allowedInBackgroundMode: Boolean
) {
    LOW(
        level = 0,
        description = "Low risk - Safe operations with no side effects",
        color = "#4CAF50",
        icon = "ic_check_circle",
        requiresConfirmation = false,
        allowedInAutonomousMode = true,
        allowedInBackgroundMode = true
    ),
    
    MEDIUM(
        level = 1,
        description = "Medium risk - Operations that may have minor side effects",
        color = "#FFC107",
        icon = "ic_warning",
        requiresConfirmation = false,
        allowedInAutonomousMode = true,
        allowedInBackgroundMode = true
    ),
    
    HIGH(
        level = 2,
        description = "High risk - Operations that may have significant side effects",
        color = "#FF9800",
        icon = "ic_error",
        requiresConfirmation = true,
        allowedInAutonomousMode = false,
        allowedInBackgroundMode = false
    ),
    
    CRITICAL(
        level = 3,
        description = "Critical risk - Operations that may cause harm or data loss",
        color = "#F44336",
        icon = "ic_danger",
        requiresConfirmation = true,
        allowedInAutonomousMode = false,
        allowedInBackgroundMode = false
    ),
    
    BLOCKED(
        level = 4,
        description = "Blocked - Operations that are not allowed under any circumstances",
        color = "#9E9E9E",
        icon = "ic_block",
        requiresConfirmation = true,
        allowedInAutonomousMode = false,
        allowedInBackgroundMode = false
    );
    
    fun needsConfirmation(): Boolean = requiresConfirmation
    fun isAllowedInAutonomous(): Boolean = allowedInAutonomousMode
    fun isAllowedInBackground(): Boolean = allowedInBackgroundMode
    fun isSaferThan(other: RiskLevel): Boolean = this.level < other.level
    fun isMoreDangerousThan(other: RiskLevel): Boolean = this.level > other.level
    fun isSameAs(other: RiskLevel): Boolean = this.level == other.level
    
    fun getHigherLevel(): RiskLevel? {
        val allLevels = values().sortedBy { it.level }
        val currentIndex = allLevels.indexOf(this)
        return if (currentIndex < allLevels.size - 1) allLevels[currentIndex + 1] else null
    }
    
    fun getLowerLevel(): RiskLevel? {
        val allLevels = values().sortedBy { it.level }
        val currentIndex = allLevels.indexOf(this)
        return if (currentIndex > 0) allLevels[currentIndex - 1] else null
    }
    
    fun toMap(): Map<String, Any> {
        return mapOf(
            "name" to name,
            "level" to level,
            "description" to description,
            "color" to color,
            "icon" to icon,
            "requiresConfirmation" to requiresConfirmation,
            "allowedInAutonomousMode" to allowedInAutonomousMode,
            "allowedInBackgroundMode" to allowedInBackgroundMode
        )
    }
    
    companion object {
        fun fromLevel(level: Int): RiskLevel = values().find { it.level == level } ?: LOW
        fun fromString(name: String): RiskLevel = values().find { it.name == name } ?: LOW
        fun getAllLevels(): List<RiskLevel> = listOf(LOW, MEDIUM, HIGH, CRITICAL, BLOCKED)
        fun getSafeLevels(): List<RiskLevel> = listOf(LOW, MEDIUM)
        fun getDangerousLevels(): List<RiskLevel> = listOf(HIGH, CRITICAL, BLOCKED)
        fun getLevelsRequiringConfirmation(): List<RiskLevel> = values().filter { it.requiresConfirmation }
        fun getLevelsAllowedInAutonomous(): List<RiskLevel> = values().filter { it.allowedInAutonomousMode }
        fun getLevelsAllowedInBackground(): List<RiskLevel> = values().filter { it.allowedInBackgroundMode }
        fun getDefault(): RiskLevel = LOW
        fun getHighest(): RiskLevel = BLOCKED
        fun getLowest(): RiskLevel = LOW
    }
}