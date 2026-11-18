package com.example.bab6.data

import androidx.datastore.preferences.core.PreferenceDataStoreFactory
import androidx.room.Room
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.bab6.data.local.AppDatabase
import com.example.bab6.data.model.Student
import com.example.bab6.data.preferences.DataStoreUserPreferencesRepository
import com.example.bab6.data.repository.RoomFavoriteRepository
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

@RunWith(AndroidJUnit4::class)
class LocalStorageTest {
    private val context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test fun roomPersistsRecordsAndEmitsDeletion() = runBlocking {
        val name = "test_favorites_${System.nanoTime()}.db"
        val student = Student(102, "John Doe", "john.doe@example.com", "Brown University")
        var db = Room.databaseBuilder(context, AppDatabase::class.java, name).build()
        try {
            var repository = RoomFavoriteRepository(db.favoriteStudentDao())
            repository.add(student)
            assertEquals(listOf(student), withTimeout(5000) { repository.observeFavorites().first { it.size == 1 } })
            assertTrue(repository.observeIsFavorite(102).first())
            db.close()
            db = Room.databaseBuilder(context, AppDatabase::class.java, name).build()
            repository = RoomFavoriteRepository(db.favoriteStudentDao())
            assertEquals(student, repository.getFavorite(102))
            val deletion = async(start = CoroutineStart.UNDISPATCHED) {
                withTimeout(5000) { repository.observeFavorites().first { it.isEmpty() } }
            }
            repository.remove(102)
            assertTrue(deletion.await().isEmpty())
            assertFalse(repository.observeIsFavorite(102).first())
        } finally { db.close(); context.deleteDatabase(name) }
    }

    @Test fun dataStoreRestoresQueryAndAdditionalSortPreference() = runBlocking {
        val file = File(context.cacheDir, "test_preferences_${System.nanoTime()}.preferences_pb")
        var scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
        try {
            var store = PreferenceDataStoreFactory.create(scope = scope, produceFile = { file })
            var repository = DataStoreUserPreferencesRepository(store)
            repository.saveLastSearchQuery("john")
            repository.saveSortAscending(false)
            scope.coroutineContext[Job]!!.cancelAndJoin()
            scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
            store = PreferenceDataStoreFactory.create(scope = scope, produceFile = { file })
            repository = DataStoreUserPreferencesRepository(store)
            assertEquals("john", repository.lastSearchQuery.first())
            assertFalse(repository.sortAscending.first())
        } finally { scope.coroutineContext[Job]!!.cancelAndJoin(); file.delete() }
    }
}
