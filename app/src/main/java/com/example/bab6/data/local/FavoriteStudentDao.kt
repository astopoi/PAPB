package com.example.bab6.data.local

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface FavoriteStudentDao {
    @Query("SELECT * FROM favorite_students ORDER BY firstName COLLATE NOCASE ASC, id ASC")
    fun observeFavorites(): Flow<List<FavoriteStudentEntity>>

    @Query("SELECT EXISTS(SELECT 1 FROM favorite_students WHERE id = :id)")
    fun observeIsFavorite(id: Int): Flow<Boolean>

    @Query("SELECT * FROM favorite_students WHERE id = :id")
    suspend fun getFavorite(id: Int): FavoriteStudentEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(student: FavoriteStudentEntity)

    @Query("DELETE FROM favorite_students WHERE id = :id")
    suspend fun deleteById(id: Int)
}
