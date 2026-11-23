package com.example.bab6.data.location

data class DeviceLocation(
    val latitude: Double,
    val longitude: Double,
    val accuracy: Float? = null
)

enum class LocationAccess(val label: String) {
    NONE("Belum diberikan"), APPROXIMATE("Approximate"), PRECISE("Precise");

    companion object {
        fun fromPermissions(fine: Boolean, coarse: Boolean): LocationAccess = when {
            fine -> PRECISE
            coarse -> APPROXIMATE
            else -> NONE
        }
    }
}
