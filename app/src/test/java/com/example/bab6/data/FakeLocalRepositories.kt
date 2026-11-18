package com.example.bab6.data

import com.example.bab6.data.model.Student
import com.example.bab6.data.preferences.UserPreferencesRepository
import com.example.bab6.data.repository.FavoriteRepository
import kotlinx.coroutines.flow.*

class FakePreferences(query: String = "", ascending: Boolean = true) : UserPreferencesRepository {
    override val lastSearchQuery = MutableStateFlow(query)
    override val sortAscending = MutableStateFlow(ascending)
    override suspend fun saveLastSearchQuery(value: String) { lastSearchQuery.value = value }
    override suspend fun saveSortAscending(value: Boolean) { sortAscending.value = value }
}

class FakeFavorites : FavoriteRepository {
    private val students = MutableStateFlow<List<Student>>(emptyList())
    override fun observeFavorites(): Flow<List<Student>> = students
    override fun observeIsFavorite(id: Int) = students.map { list -> list.any { it.id == id } }
    override suspend fun getFavorite(id: Int) = students.value.find { it.id == id }
    override suspend fun add(student: Student) { students.value = students.value.filterNot { it.id == student.id } + student }
    override suspend fun remove(id: Int) { students.value = students.value.filterNot { it.id == id } }
}
