package com.example.bab6.ui.location

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.bab6.data.location.LocationAccess
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun LocationScreen(viewModel: LocationViewModel, onBack: () -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    fun currentAccess(): LocationAccess = LocationAccess.fromPermissions(
        fine = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED,
        coarse = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
    )

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val access = LocationAccess.fromPermissions(
            fine = permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true,
            coarse = permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true
        )
        viewModel.onPermissionChanged(access)
        if (access != LocationAccess.NONE) viewModel.refreshLocation()
        else viewModel.onPermissionDenied()
    }

    DisposableEffect(lifecycleOwner, viewModel) {
        viewModel.onPermissionChanged(currentAccess())
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_RESUME -> viewModel.onPermissionChanged(currentAccess())
                Lifecycle.Event.ON_STOP -> viewModel.cancelRefresh()
                else -> Unit
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer); viewModel.cancelRefresh() }
    }

    fun requestLocation() {
        // Re-evaluate on every click; permission may have changed through Settings.
        val access = currentAccess()
        viewModel.onPermissionChanged(access)
        if (access != LocationAccess.NONE) {
            viewModel.refreshLocation()
        } else {
            permissionLauncher.launch(arrayOf(
                Manifest.permission.ACCESS_COARSE_LOCATION,
                Manifest.permission.ACCESS_FINE_LOCATION
            ))
        }
    }

    Column(
        Modifier.fillMaxSize().safeDrawingPadding().verticalScroll(rememberScrollState()).padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Lokasi Saya", style = MaterialTheme.typography.headlineMedium)
        Text("Jenis akses: ${uiState.access.label}")
        Text("Lokasi hanya diambil satu kali saat tombol ditekan. Approximate tetap dapat digunakan.")
        if (uiState.permissionDenied) {
            Text("Izin lokasi ditolak. Berikan izin untuk mengambil lokasi perangkat.", color = MaterialTheme.colorScheme.error)
            Text("Jika dialog izin tidak muncul, aktifkan izin melalui Pengaturan aplikasi.")
            Button(onClick = ::requestLocation) { Text("Minta Izin Lagi") }
            TextButton(onClick = {
                context.startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:${context.packageName}")))
            }) { Text("Buka Pengaturan") }
        } else {
            Button(onClick = ::requestLocation, enabled = !uiState.isLoading) {
                Text(if (uiState.location != null || uiState.errorMessage != null) "Perbarui Lokasi" else "Ambil Lokasi Saya")
            }
        }
        if (uiState.isLoading) {
            CircularProgressIndicator()
            Text("Mengambil lokasi...")
        }
        uiState.errorMessage?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        uiState.location?.let { location ->
            Text("Latitude: ${location.latitude}")
            Text("Longitude: ${location.longitude}")
            Text("Accuracy: ${location.accuracy?.let { String.format(Locale.getDefault(), "%.1f m", it) } ?: "Tidak tersedia"}")
        }
        Text("Terakhir diperbarui: ${uiState.lastUpdatedMillis?.let {
            SimpleDateFormat("dd-MM-yyyy HH:mm:ss", Locale.getDefault()).format(Date(it))
        } ?: "Belum ada pembaruan berhasil"}")
        if (uiState.location == null && uiState.errorMessage == null && !uiState.isLoading && !uiState.permissionDenied) {
            Text("Lokasi belum diminta")
        }
        Button(onClick = onBack) { Text("Kembali") }
    }
}
