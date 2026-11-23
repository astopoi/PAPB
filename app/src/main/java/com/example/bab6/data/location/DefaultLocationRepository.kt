package com.example.bab6.data.location

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.LocationManager
import androidx.core.content.ContextCompat
import androidx.core.location.LocationManagerCompat
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.Priority
import com.google.android.gms.tasks.CancellationTokenSource
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withTimeoutOrNull

class DefaultLocationRepository(
    context: Context,
    private val client: FusedLocationProviderClient
) : LocationRepository {
    private val context = context.applicationContext

    override suspend fun getCurrentLocation(): Result<DeviceLocation> {
        val cancellation = CancellationTokenSource()
        return try {
            val fineGranted = ContextCompat.checkSelfPermission(
                context, Manifest.permission.ACCESS_FINE_LOCATION
            ) == PackageManager.PERMISSION_GRANTED
            val coarseGranted = ContextCompat.checkSelfPermission(
                context, Manifest.permission.ACCESS_COARSE_LOCATION
            ) == PackageManager.PERMISSION_GRANTED
            check(fineGranted || coarseGranted) { "Izin lokasi belum diberikan. Tekan Minta Izin Lagi." }

            val manager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
            check(LocationManagerCompat.isLocationEnabled(manager)) {
                "Layanan lokasi sedang nonaktif. Aktifkan Lokasi di perangkat, lalu coba lagi."
            }
            val priority = if (fineGranted) Priority.PRIORITY_HIGH_ACCURACY
                else Priority.PRIORITY_BALANCED_POWER_ACCURACY
            val location = withTimeoutOrNull(20_000L) {
                client.getCurrentLocation(priority, cancellation.token).await()
            } ?: error("Lokasi belum tersedia. Pastikan layanan Lokasi aktif, lalu coba lagi.")

            Result.success(DeviceLocation(
                latitude = location.latitude,
                longitude = location.longitude,
                accuracy = if (location.hasAccuracy()) location.accuracy else null
            ))
        } catch (e: CancellationException) {
            throw e
        } catch (e: SecurityException) {
            Result.failure(IllegalStateException("Izin lokasi berubah. Tekan Minta Izin Lagi untuk melanjutkan.", e))
        } catch (e: Exception) {
            Result.failure(e)
        } finally {
            // Cancel the underlying one-shot request on timeout, screen exit, or cancellation.
            cancellation.cancel()
        }
    }
}
