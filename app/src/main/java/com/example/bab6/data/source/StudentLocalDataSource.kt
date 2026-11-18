package com.example.bab6.data.source

import com.example.bab6.data.model.Student

class StudentLocalDataSource {
    private val students = listOf(
        Student(2026, "Alya Putri", "alya.putri@example.com", "Universitas Brawijaya"),
        Student(2027, "Bima Pratama", "bima.pratama@example.com", "Universitas Brawijaya"),
        Student(2028, "Citra Lestari", "citra.lestari@example.com", "Universitas Brawijaya"),
        Student(2029, "Dewi Wijaya", "dewi.wijaya@example.com", "Universitas Brawijaya"),
        Student(2030, "Eka Maulana", "eka.maulana@example.com", "Universitas Brawijaya")
    )
    fun getStudents(): List<Student> = students

    fun getStudentById(id: Int): Student? =
        students.find { it.id == id }
}
