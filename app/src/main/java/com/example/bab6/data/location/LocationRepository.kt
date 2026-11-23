package com.example.bab6.data.location

interface LocationRepository {
    suspend fun getCurrentLocation(): Result<DeviceLocation>
}
