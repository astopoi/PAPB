package com.example.bab6.ui.location

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.bab6.data.location.LocationAccess
import com.example.bab6.data.location.LocationRepository
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class LocationViewModel(
    private val repository: LocationRepository,
    private val nowMillis: () -> Long = System::currentTimeMillis
) : ViewModel() {
    private val _uiState = MutableStateFlow(LocationUiState())
    val uiState: StateFlow<LocationUiState> = _uiState.asStateFlow()
    private var requestJob: Job? = null

    fun onPermissionChanged(access: LocationAccess) {
        if (access == _uiState.value.access) return
        requestJob?.cancel()
        // A previous precise result must not remain visible after permission is downgraded.
        _uiState.value = LocationUiState(access = access)
    }

    fun onPermissionDenied() {
        requestJob?.cancel()
        _uiState.value = LocationUiState(permissionDenied = true)
    }

    fun refreshLocation() {
        if (_uiState.value.access == LocationAccess.NONE) {
            onPermissionDenied()
            return
        }
        requestJob?.cancel()
        requestJob = viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, permissionDenied = false, errorMessage = null) }
            try {
                repository.getCurrentLocation().fold(
                    onSuccess = { location ->
                        _uiState.update { it.copy(
                            location = location, lastUpdatedMillis = nowMillis(), isLoading = false
                        ) }
                    },
                    onFailure = { error ->
                        if (error is CancellationException) throw error
                        _uiState.update { it.copy(
                            isLoading = false, errorMessage = error.message ?: "Gagal mengambil lokasi"
                        ) }
                    }
                )
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, errorMessage = e.message ?: "Gagal mengambil lokasi") }
            }
        }
    }

    fun cancelRefresh() {
        requestJob?.cancel()
        _uiState.update { it.copy(isLoading = false) }
    }

    companion object {
        fun factory(repository: LocationRepository) = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                require(modelClass.isAssignableFrom(LocationViewModel::class.java))
                return LocationViewModel(repository) as T
            }
        }
    }
}
