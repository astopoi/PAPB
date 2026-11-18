package com.example.bab6.data.repository

import com.example.bab6.data.model.Student

interface StudentRepository {
    suspend fun getStudents(): List<Student>
    suspend fun getStudent(id: Int): Student
    suspend fun searchStudents(query: String): List<Student>
}
