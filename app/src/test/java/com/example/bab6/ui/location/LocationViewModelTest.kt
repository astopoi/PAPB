package com.example.bab6.ui.location

import androidx.lifecycle.viewModelScope
import com.example.bab6.data.location.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class LocationViewModelTest {
    private class FakeRepository : LocationRepository {
        var calls = 0
        var delayMs = 0L
        var cancelled = 0
        var result = Result.success(DeviceLocation(-7.95, 112.61, 20f))
        override suspend fun getCurrentLocation(): Result<DeviceLocation> {
            calls++
            val response = result
            try { delay(delayMs) } catch (e: CancellationException) { cancelled++; throw e }
            return response
        }
    }

    @Test fun permissionDeniedDoesNotCallRepository() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        val repository = FakeRepository(); val model = LocationViewModel(repository)
        try {
            model.refreshLocation(); runCurrent()
            assertEquals(0, repository.calls)
            assertTrue(model.uiState.value.permissionDenied)
            assertNull(model.uiState.value.location)
        } finally { model.viewModelScope.cancel(); Dispatchers.resetMain() }
    }

    @Test fun approximateCanRefreshWithoutChangingPermissionAndUpdatesTimeOnlyOnSuccess() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        val repository = FakeRepository(); var clock = 1000L
        val model = LocationViewModel(repository) { clock }
        try {
            model.onPermissionChanged(LocationAccess.APPROXIMATE)
            model.refreshLocation(); runCurrent()
            assertEquals(LocationAccess.APPROXIMATE, model.uiState.value.access)
            assertEquals(1000L, model.uiState.value.lastUpdatedMillis)
            clock = 2000L; model.refreshLocation(); runCurrent()
            assertEquals(2, repository.calls)
            assertEquals(2000L, model.uiState.value.lastUpdatedMillis)
            repository.result = Result.failure(IllegalStateException("Lokasi belum tersedia"))
            clock = 3000L; model.refreshLocation(); runCurrent()
            assertEquals(2000L, model.uiState.value.lastUpdatedMillis)
            assertEquals("Lokasi belum tersedia", model.uiState.value.errorMessage)
            assertFalse(model.uiState.value.isLoading)
        } finally { model.viewModelScope.cancel(); Dispatchers.resetMain() }
    }

    @Test fun errorCanBeRetriedSuccessfully() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        val repository = FakeRepository(); val model = LocationViewModel(repository) { 5000L }
        try {
            model.onPermissionChanged(LocationAccess.PRECISE)
            repository.result = Result.failure(IllegalStateException("Layanan lokasi sedang nonaktif"))
            model.refreshLocation(); runCurrent()
            assertNull(model.uiState.value.lastUpdatedMillis)
            assertNotNull(model.uiState.value.errorMessage)
            repository.result = Result.success(DeviceLocation(-7.95, 112.61, 5f))
            model.refreshLocation(); runCurrent()
            assertNull(model.uiState.value.errorMessage)
            assertEquals(5000L, model.uiState.value.lastUpdatedMillis)
        } finally { model.viewModelScope.cancel(); Dispatchers.resetMain() }
    }

    @Test fun changingPermissionCancelsRequestAndClearsOldPreciseResult() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        val repository = FakeRepository(); val model = LocationViewModel(repository)
        try {
            model.onPermissionChanged(LocationAccess.PRECISE)
            model.refreshLocation(); runCurrent()
            assertNotNull(model.uiState.value.location)
            repository.delayMs = 2000
            model.refreshLocation(); runCurrent()
            assertTrue(model.uiState.value.isLoading)
            model.onPermissionChanged(LocationAccess.APPROXIMATE); runCurrent()
            assertEquals(1, repository.cancelled)
            assertNull(model.uiState.value.location)
            assertNull(model.uiState.value.lastUpdatedMillis)
            model.onPermissionDenied(); model.refreshLocation(); runCurrent()
            assertEquals(2, repository.calls)
            assertTrue(model.uiState.value.permissionDenied)
        } finally { model.viewModelScope.cancel(); Dispatchers.resetMain() }
    }

    @Test fun leavingScreenCancelsPendingOneShotRequest() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        val repository = FakeRepository(); repository.delayMs = 2000
        val model = LocationViewModel(repository)
        try {
            model.onPermissionChanged(LocationAccess.PRECISE)
            model.refreshLocation(); runCurrent()
            model.cancelRefresh(); runCurrent()
            advanceTimeBy(3000); runCurrent()
            assertEquals(1, repository.cancelled)
            assertFalse(model.uiState.value.isLoading)
            assertNull(model.uiState.value.location)
        } finally { model.viewModelScope.cancel(); Dispatchers.resetMain() }
    }

    @Test fun accessLabelAcceptsCoarseWithoutFine() {
        assertEquals(LocationAccess.PRECISE, LocationAccess.fromPermissions(true, true))
        assertEquals(LocationAccess.APPROXIMATE, LocationAccess.fromPermissions(false, true))
        assertEquals(LocationAccess.NONE, LocationAccess.fromPermissions(false, false))
    }
}
