package com.example.bab6.ui.detail

import androidx.lifecycle.viewModelScope
import com.example.bab6.data.FakeFavorites
import com.example.bab6.data.model.Student
import com.example.bab6.data.repository.StudentRepository
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class DetailViewModelTest {
    @Test fun opensSavedProfileOfflineAndToggleUpdatesRepository() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        val favorites = FakeFavorites()
        val student = Student(102, "John Doe", "john@example.com", "Brown University")
        val offline = object : StudentRepository {
            override suspend fun getStudents(): List<Student> = error("Offline")
            override suspend fun searchStudents(query: String): List<Student> = error("Offline")
            override suspend fun getStudent(id: Int): Student = error("Offline")
        }
        favorites.add(student)
        val model = DetailViewModel(offline, favorites)
        try {
            model.loadStudent(102); runCurrent()
            assertEquals(student, model.uiState.value.student)
            assertTrue(model.uiState.value.isFavorite)
            model.toggleFavorite(); runCurrent()
            assertNull(favorites.getFavorite(102))
            assertFalse(model.uiState.value.isFavorite)
            model.toggleFavorite(); runCurrent()
            assertEquals(student, favorites.getFavorite(102))
            assertTrue(model.uiState.value.isFavorite)
        } finally { model.viewModelScope.cancel(); Dispatchers.resetMain() }
    }
}
