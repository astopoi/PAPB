package com.example.bab6.data.repository

import com.example.bab6.data.local.FavoriteStudentDao
import com.example.bab6.data.local.FavoriteStudentEntity
import com.example.bab6.data.model.Student
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

interface FavoriteRepository {
    fun observeFavorites(): Flow<List<Student>>
    fun observeIsFavorite(id: Int): Flow<Boolean>
    suspend fun getFavorite(id: Int): Student?
    suspend fun add(student: Student)
    suspend fun remove(id: Int)
}

class RoomFavoriteRepository(private val dao: FavoriteStudentDao) : FavoriteRepository {
    override fun observeFavorites(): Flow<List<Student>> =
        dao.observeFavorites().map { rows -> rows.map { it.toStudent() } }
    override fun observeIsFavorite(id: Int): Flow<Boolean> = dao.observeIsFavorite(id)
    override suspend fun getFavorite(id: Int): Student? = dao.getFavorite(id)?.toStudent()
    override suspend fun add(student: Student) = dao.insert(
        FavoriteStudentEntity(student.id, student.name, "", student.email, student.university)
    )
    override suspend fun remove(id: Int) = dao.deleteById(id)
}

private fun FavoriteStudentEntity.toStudent() = Student(
    id, listOf(firstName, lastName).filter { it.isNotBlank() }.joinToString(" "), email, university
)
