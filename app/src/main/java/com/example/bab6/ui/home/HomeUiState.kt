package com.example.bab6.ui.home

import com.example.bab6.data.model.Student
data class HomeUiState(
    val students: List<Student> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)