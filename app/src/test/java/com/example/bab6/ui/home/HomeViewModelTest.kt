package com.example.bab6.ui.home

import com.example.bab6.data.FakePreferences
import androidx.lifecycle.viewModelScope
import com.example.bab6.data.model.Student
import com.example.bab6.data.repository.StudentRepository
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class HomeViewModelTest {
    private val dispatcher = StandardTestDispatcher()
    private val models = mutableListOf<HomeViewModel>()
    @Before fun setup() { Dispatchers.setMain(dispatcher) }
    @After fun cleanup() {
        models.forEach { it.viewModelScopeForTestCancel() }
        Dispatchers.resetMain()
    }
    private fun HomeViewModel.viewModelScopeForTestCancel() { viewModelScope.cancel() }

    private class FakeRepository : StudentRepository {
        val queries = mutableListOf<String>()
        var fail = false
        var delayMs = 0L
        var cancelled = false
        override suspend fun getStudents() = searchStudents("")
        override suspend fun searchStudents(query: String): List<Student> {
            queries.add(query)
            try { delay(delayMs) } catch (e: CancellationException) { cancelled = true; throw e }
            if (fail) error("Offline")
            return listOf(Student(1, query.ifBlank { "Emily" }, "a@example.com", "University"))
        }
        override suspend fun getStudent(id: Int) = Student(id, "Emily", "a@example.com", "University")
    }
    private fun model(r: FakeRepository) = HomeViewModel(r, FakePreferences()).also { models.add(it) }

    @Test fun debounceBlankAndDuplicateQueries() = runTest(dispatcher) {
        val r = FakeRepository(); val m = model(r)
        runCurrent(); advanceTimeBy(500); runCurrent()
        assertEquals(listOf(""), r.queries)
        for (q in listOf("j", "jo", "joh", "john")) {
            m.onSearchQueryChange(q); runCurrent(); advanceTimeBy(100)
        }
        assertEquals(1, r.queries.size)
        advanceTimeBy(500); runCurrent()
        assertEquals(listOf("", "john"), r.queries)
        m.onSearchQueryChange(" john "); advanceTimeBy(501); runCurrent()
        assertEquals(2, r.queries.size)
        m.onSearchQueryChange(""); advanceTimeBy(501); runCurrent()
        assertEquals("", r.queries.last())
    }
    @Test fun retryAndRefreshUseActiveQuery() = runTest(dispatcher) {
        val r = FakeRepository(); val m = model(r)
        m.onSearchQueryChange("John"); r.fail = true
        advanceTimeBy(501); runCurrent()
        assertEquals("Offline", m.uiState.value.errorMessage)
        r.fail = false; m.retry(); runCurrent()
        assertEquals("John", r.queries.last())
        assertNull(m.uiState.value.errorMessage)
        m.refresh(); runCurrent()
        assertEquals(listOf("John", "John", "John"), r.queries)
        assertFalse(m.uiState.value.isLoading)
    }
    @Test fun newerQueryCancelsPreviousRequest() = runTest(dispatcher) {
        val r = FakeRepository(); r.delayMs = 2000; val m = model(r)
        advanceTimeBy(501); runCurrent()
        m.onSearchQueryChange("John"); advanceTimeBy(501); runCurrent()
        assertTrue(r.cancelled)
        advanceTimeBy(2001); runCurrent()
        assertEquals("John", m.uiState.value.students.single().name)
        assertNull(m.uiState.value.errorMessage)
    }
    @Test fun restoresQueryBeforeFirstRequestAndSavesEdits() = runTest(dispatcher) {
        val r = FakeRepository(); val preferences = FakePreferences("Emily")
        val m = HomeViewModel(r, preferences).also { models.add(it) }
        advanceTimeBy(501); runCurrent()
        assertEquals(listOf("Emily"), r.queries)
        assertEquals("Emily", m.searchQuery.value)
        m.onSearchQueryChange("John")
        advanceTimeBy(501); runCurrent()
        assertEquals("John", preferences.lastSearchQuery.value)
    }

}
