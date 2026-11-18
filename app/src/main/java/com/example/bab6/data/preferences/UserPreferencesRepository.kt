package com.example.bab6.data.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import java.io.IOException

interface UserPreferencesRepository {
    val lastSearchQuery: Flow<String>
    val sortAscending: Flow<Boolean>
    suspend fun saveLastSearchQuery(value: String)
    suspend fun saveSortAscending(value: Boolean)
}

class DataStoreUserPreferencesRepository(
    private val dataStore: DataStore<Preferences>
) : UserPreferencesRepository {
    constructor(context: Context) : this(context.applicationContext.userPreferencesDataStore)

    private val lastSearchQueryKey = stringPreferencesKey("last_search_query")
    private val sortAscendingKey = booleanPreferencesKey("sort_ascending")
    private val preferences = dataStore.data.catch { error ->
        if (error is IOException) emit(emptyPreferences()) else throw error
    }
    override val lastSearchQuery = preferences.map { it[lastSearchQueryKey] ?: "" }
    override val sortAscending = preferences.map { it[sortAscendingKey] ?: true }
    override suspend fun saveLastSearchQuery(value: String) {
        dataStore.edit { it[lastSearchQueryKey] = value }
    }
    override suspend fun saveSortAscending(value: Boolean) {
        dataStore.edit { it[sortAscendingKey] = value }
    }
}
