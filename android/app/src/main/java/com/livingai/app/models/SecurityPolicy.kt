package com.livingai.app.models

/**
 * SecurityPolicy model for LivingAI Android Application
 * 
 * Defines security policies and risk levels for actions.
 * 
 * Author: Abdulraheem Nohari
 */

data class SecurityPolicy(
    val id: String,
    val name: String,
    val description: String,
    val riskLevel: String,
    val category: String,
    val isEnabled: Boolean = true,
    val requiresConfirmation: Boolean = false,
    val requiresPermission: Boolean = false,
    val allowedInSandbox: Boolean = true,
    val allowedInPrivacyMode: Boolean = true,
    val allowedInSecureMode: Boolean = true,
    val maxRetries: Int = 3,
    val timeoutSeconds: Long = 30L,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
) {
    companion object {
        const val RISK_LOW = "low"
        const val RISK_MEDIUM = "medium"
        const val RISK_HIGH = "high"
        const val RISK_CRITICAL = "critical"
        const val RISK_LEVEL_LOW = 1
        const val RISK_LEVEL_MEDIUM = 2
        const val RISK_LEVEL_HIGH = 3
        const val RISK_LEVEL_CRITICAL = 4
        const val CATEGORY_FILE = "file"
        const val CATEGORY_NETWORK = "network"
        const val CATEGORY_SYSTEM = "system"
        const val CATEGORY_DATA = "data"
        const val CATEGORY_PRIVACY = "privacy"
        const val CATEGORY_EXECUTION = "execution"
        
        fun getRiskLevelValue(riskLevel: String): Int {
            return when (riskLevel) {
                RISK_LOW -> RISK_LEVEL_LOW
                RISK_MEDIUM -> RISK_LEVEL_MEDIUM
                RISK_HIGH -> RISK_LEVEL_HIGH
                RISK_CRITICAL -> RISK_LEVEL_CRITICAL
                else -> RISK_LEVEL_MEDIUM
            }
        }
        
        fun isActionAllowed(policyId: String, isSandbox: Boolean, isPrivacy: Boolean, isSecure: Boolean): Boolean {
            val policies = listOf(
                SecurityPolicy("file_read", "File Read", "Read files", RISK_LOW, CATEGORY_FILE, true, false, true, true, true, true, 3, 30),
                SecurityPolicy("file_write", "File Write", "Write files", RISK_MEDIUM, CATEGORY_FILE, true, false, true, true, true, true, 3, 30),
                SecurityPolicy("file_delete", "File Delete", "Delete files", RISK_HIGH, CATEGORY_FILE, true, true, true, false, false, false, 1, 10),
                SecurityPolicy("network_http", "HTTP Request", "Make HTTP requests", RISK_MEDIUM, CATEGORY_NETWORK, true, false, true, true, false, true, 3, 30),
                SecurityPolicy("network_download", "Download", "Download files", RISK_MEDIUM, CATEGORY_NETWORK, true, true, true, false, false, true, 3, 60),
                SecurityPolicy("network_upload", "Upload", "Upload files", RISK_HIGH, CATEGORY_NETWORK, true, true, true, false, false, false, 3, 30),
                SecurityPolicy("system_settings", "Modify Settings", "Modify system settings", RISK_HIGH, CATEGORY_SYSTEM, true, true, true, false, false, false, 0, 10),
                SecurityPolicy("data_read", "Read Data", "Read app data", RISK_LOW, CATEGORY_DATA, true, false, false, true, true, true, 3, 30),
                SecurityPolicy("data_write", "Write Data", "Write app data", RISK_LOW, CATEGORY_DATA, true, false, false, true, true, true, 3, 30),
                SecurityPolicy("privacy_location", "Access Location", "Access device location", RISK_HIGH, CATEGORY_PRIVACY, true, true, true, false, false, false, 0, 10),
                SecurityPolicy("privacy_camera", "Access Camera", "Access device camera", RISK_HIGH, CATEGORY_PRIVACY, true, true, true, false, false, false, 0, 10),
                SecurityPolicy("privacy_microphone", "Access Microphone", "Access device microphone", RISK_HIGH, CATEGORY_PRIVACY, true, true, true, false, false, false, 0, 10)
            )
            val policy = policies.find { it.id == policyId } ?: return false
            if (!policy.isEnabled) return false
            if (isSandbox && !policy.allowedInSandbox) return false
            if (isPrivacy && !policy.allowedInPrivacyMode) return false
            if (isSecure && !policy.allowedInSecureMode) return false
            return true
        }
    }
    
    fun getRiskLevelString(): String = when (riskLevel) {
        RISK_LOW -> "Low"
        RISK_MEDIUM -> "Medium"
        RISK_HIGH -> "High"
        RISK_CRITICAL -> "Critical"
        else -> "Unknown"
    }
    
    fun getCategoryString(): String = when (category) {
        CATEGORY_FILE -> "File"
        CATEGORY_NETWORK -> "Network"
        CATEGORY_SYSTEM -> "System"
        CATEGORY_DATA -> "Data"
        CATEGORY_PRIVACY -> "Privacy"
        CATEGORY_EXECUTION -> "Execution"
        else -> "Unknown"
    }
    
    fun getRiskLevelValue(): Int = Companion.getRiskLevelValue(riskLevel)
    
    fun isAllowed(isSandbox: Boolean = false, isPrivacy: Boolean = false, isSecure: Boolean = false): Boolean {
        return Companion.isActionAllowed(id, isSandbox, isPrivacy, isSecure)
    }
    
    fun toMap(): Map<String, Any> = mapOf(
        "id" to id, "name" to name, "description" to description,
        "risk_level" to getRiskLevelString(), "category" to getCategoryString(),
        "enabled" to isEnabled, "requires_confirmation" to requiresConfirmation,
        "requires_permission" to requiresPermission
    )
}