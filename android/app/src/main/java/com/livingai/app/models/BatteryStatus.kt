package com.livingai.app.models

import java.text.SimpleDateFormat
import java.util.*

/**
 * BatteryStatus model for LivingAI Android Application
 * 
 * Represents the current battery status of the device.
 * Used for battery monitoring and protection features.
 * 
 * Features:
 * - Battery level and percentage
 * - Charging state
 * - Temperature
 * - Health status
 * - Technology type
 * - Voltage
 * - Timestamp
 * 
 * Author: Abdulraheem Nohari
 */

data class BatteryStatus(
    val level: Int,
    val scale: Int,
    val percentage: Float,
    val isCharging: Boolean,
    val isPlugged: Boolean,
    val temperature: Float,
    val status: String,
    val health: String,
    val technology: String,
    val voltage: Int,
    val timestamp: Long
) {
    companion object {
        fun default(): BatteryStatus {
            return BatteryStatus(
                level = 50,
                scale = 100,
                percentage = 50.0f,
                isCharging = false,
                isPlugged = false,
                temperature = 25.0f,
                status = "DISCHARGING",
                health = "GOOD",
                technology = "Li-ion",
                voltage = 3800,
                timestamp = System.currentTimeMillis()
            )
        }
    }
    
    fun getPercentageString(): String {
        return "${percentage}%"
    }
    
    fun getTemperatureString(): String {
        return "${temperature}°C"
    }
    
    fun getStatusString(): String {
        return when (status) {
            "CHARGING" -> "Charging"
            "DISCHARGING" -> "Discharging"
            "FULL" -> "Full"
            "NOT_CHARGING" -> "Not Charging"
            "UNKNOWN" -> "Unknown"
            else -> status
        }
    }
    
    fun getHealthString(): String {
        return when (health) {
            "GOOD" -> "Good"
            "OVERHEAT" -> "Overheat"
            "DEAD" -> "Dead"
            "OVER_VOLTAGE" -> "Over Voltage"
            "UNSPECIFIED_FAILURE" -> "Unspecified Failure"
            "COLD" -> "Cold"
            "UNKNOWN" -> "Unknown"
            else -> health
        }
    }
    
    fun isCritical(): Boolean {
        return percentage <= 5.0f && !isCharging
    }
    
    fun isLow(): Boolean {
        return percentage <= 15.0f && !isCharging
    }
    
    fun isWarning(): Boolean {
        return percentage <= 25.0f && !isCharging
    }
    
    fun isHealthy(): Boolean {
        return health == "GOOD"
    }
    
    fun toMap(): Map<String, Any> {
        return mapOf(
            "level" to level,
            "scale" to scale,
            "percentage" to percentage,
            "is_charging" to isCharging,
            "is_plugged" to isPlugged,
            "temperature" to temperature,
            "status" to getStatusString(),
            "health" to getHealthString(),
            "technology" to technology,
            "voltage" to voltage,
            "timestamp" to timestamp,
            "formatted_percentage" to getPercentageString(),
            "formatted_temperature" to getTemperatureString()
        )
    }
    
    fun toJson(): String {
        return toMap().toString()
    }
    
    override fun toString(): String {
        return "BatteryStatus(level=${level}, percentage=${percentage}%, charging=${isCharging}, temp=${temperature}°C)"
    }
}