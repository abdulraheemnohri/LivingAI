package com.livingai.app.models

/**
 * BackupConfig model for LivingAI Android Application
 * 
 * Configuration for backup and restore operations including:
 * - Backup type (full, incremental, custom)
 * - Backup format (JSON, SQL, ZIP)
 * - Backup location (local, cloud, external)
 * - Compression settings
 * - Encryption settings
 * - Verification settings
 * - Schedule settings
 * 
 * Author: Abdulraheem Nohari
 */

data class BackupConfig(
    val id: String,
    val name: String,
    val type: String,
    val format: String,
    val location: String,
    val path: String,
    val timestamp: Long,
    val sizeBytes: Long,
    val checksum: String?,
    val isEncrypted: Boolean,
    val encryptionAlgorithm: String?,
    val compressionEnabled: Boolean,
    val compressionLevel: Int,
    val verificationEnabled: Boolean,
    val verified: Boolean,
    val status: String,
    val errorMessage: String?
) {
    companion object {
        const val TYPE_FULL = "full"
        const val TYPE_INCREMENTAL = "incremental"
        const val TYPE_CUSTOM = "custom"
        const val TYPE_AUTO = "auto"
        const val FORMAT_JSON = "json"
        const val FORMAT_SQL = "sql"
        const val FORMAT_ZIP = "zip"
        const val LOCATION_LOCAL = "local"
        const val LOCATION_CLOUD = "cloud"
        const val LOCATION_EXTERNAL = "external"
        const val STATUS_CREATED = "created"
        const val STATUS_IN_PROGRESS = "in_progress"
        const val STATUS_COMPLETED = "completed"
        const val STATUS_FAILED = "failed"
        const val STATUS_CANCELLED = "cancelled"
        
        fun default(): BackupConfig {
            return BackupConfig(
                id = "default",
                name = "Backup",
                type = TYPE_FULL,
                format = FORMAT_ZIP,
                location = LOCATION_LOCAL,
                path = "",
                timestamp = System.currentTimeMillis(),
                sizeBytes = 0L,
                checksum = null,
                isEncrypted = false,
                encryptionAlgorithm = null,
                compressionEnabled = true,
                compressionLevel = 6,
                verificationEnabled = true,
                verified = false,
                status = STATUS_CREATED,
                errorMessage = null
            )
        }
        
        fun forAutoBackup(timestamp: Long = System.currentTimeMillis()): BackupConfig {
            return BackupConfig(
                id = "auto_${timestamp}",
                name = "Auto Backup",
                type = TYPE_INCREMENTAL,
                format = FORMAT_ZIP,
                location = LOCATION_LOCAL,
                path = "",
                timestamp = timestamp,
                sizeBytes = 0L,
                checksum = null,
                isEncrypted = false,
                encryptionAlgorithm = null,
                compressionEnabled = true,
                compressionLevel = 6,
                verificationEnabled = true,
                verified = false,
                status = STATUS_CREATED,
                errorMessage = null
            )
        }
    }
    
    fun getSizeString(): String {
        return when {
            sizeBytes >= 1024 * 1024 * 1024 -> "${(sizeBytes / (1024.0 * 1024.0 * 1024.0))} GB"
            sizeBytes >= 1024 * 1024 -> "${(sizeBytes / (1024.0 * 1024.0))} MB"
            sizeBytes >= 1024 -> "${(sizeBytes / 1024.0)} KB"
            else -> "${sizeBytes} B"
        }
    }
    
    fun getTypeString(): String {
        return when (type) {
            TYPE_FULL -> "Full"
            TYPE_INCREMENTAL -> "Incremental"
            TYPE_CUSTOM -> "Custom"
            TYPE_AUTO -> "Auto"
            else -> "Unknown"
        }
    }
    
    fun getFormatString(): String {
        return when (format) {
            FORMAT_JSON -> "JSON"
            FORMAT_SQL -> "SQL"
            FORMAT_ZIP -> "ZIP"
            else -> "Unknown"
        }
    }
    
    fun getLocationString(): String {
        return when (location) {
            LOCATION_LOCAL -> "Local"
            LOCATION_CLOUD -> "Cloud"
            LOCATION_EXTERNAL -> "External"
            else -> "Unknown"
        }
    }
    
    fun getStatusString(): String {
        return when (status) {
            STATUS_CREATED -> "Created"
            STATUS_IN_PROGRESS -> "In Progress"
            STATUS_COMPLETED -> "Completed"
            STATUS_FAILED -> "Failed"
            STATUS_CANCELLED -> "Cancelled"
            else -> "Unknown"
        }
    }
    
    fun isComplete(): Boolean = status == STATUS_COMPLETED
    fun isFailed(): Boolean = status == STATUS_FAILED
    fun isInProgress(): Boolean = status == STATUS_IN_PROGRESS
    fun isVerified(): Boolean = verified
    
    fun toMap(): Map<String, Any?> {
        return mapOf(
            "id" to id,
            "name" to name,
            "type" to getTypeString(),
            "format" to getFormatString(),
            "location" to getLocationString(),
            "path" to path,
            "timestamp" to timestamp,
            "size" to getSizeString(),
            "size_bytes" to sizeBytes,
            "checksum" to checksum,
            "encrypted" to isEncrypted,
            "encryption_algorithm" to encryptionAlgorithm,
            "compression_enabled" to compressionEnabled,
            "compression_level" to compressionLevel,
            "verification_enabled" to verificationEnabled,
            "verified" to verified,
            "status" to getStatusString(),
            "error_message" to errorMessage
        )
    }
    
    override fun toString(): String {
        return "BackupConfig(id=${id}, name=${name}, type=${type}, format=${format})"
    }
}