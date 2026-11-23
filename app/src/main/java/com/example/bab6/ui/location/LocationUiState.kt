package com.example.bab6.ui.location

import com.example.bab6.data.location.DeviceLocation
import com.example.bab6.data.location.LocationAccess

data class LocationUiState(
    val access: LocationAccess = LocationAccess.NONE,
    val location: DeviceLocation? = null,
    val lastUpdatedMillis: Long? = null,
    val isLoading: Boolean = false,
    val permissionDenied: Boolean = false,
    val errorMessage: String? = null
)
