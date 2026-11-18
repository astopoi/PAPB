package com.example.bab6.ui.favorites

import androidx.lifecycle.viewModelScope
import com.example.bab6.data.FakeFavorites
import com.example.bab6.data.FakePreferences
import com.example.bab6.data.model.Student
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class FavoritesViewModelTest {
    @Test fun favoritesReactToInsertDeleteAndPersistedSort() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        val favorites = FakeFavorites()
        val preferences = FakePreferences(ascending = false)
        val model = FavoritesViewModel(favorites, preferences)
        try {
            runCurrent()
            assertFalse(model.uiState.value.isLoading)
            assertTrue(model.uiState.value.students.isEmpty())
            val emily = Student(1, "Emily", "emily@example.com", "University")
            val john = Student(102, "John", "john@example.com", "University")
            favorites.add(emily); favorites.add(john); runCurrent()
            assertEquals(listOf(john, emily), model.uiState.value.students)
            model.onSortAscendingChange(true); runCurrent()
            assertTrue(preferences.sortAscending.value)
            assertEquals(listOf(emily, john), model.uiState.value.students)
            favorites.remove(1); runCurrent()
            assertEquals(listOf(john), model.uiState.value.students)
            favorites.remove(102); runCurrent()
            assertTrue(model.uiState.value.students.isEmpty())
        } finally { model.viewModelScope.cancel(); Dispatchers.resetMain() }
    }
}
