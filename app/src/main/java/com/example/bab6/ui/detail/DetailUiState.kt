package com.example.bab6.ui.detail

import com.example.bab6.data.model.Student

data class DetailUiState(
    val student: Student? = null,
    val isFavorite: Boolean = false,
    val isSavingFavorite: Boolean = false,
    val favoriteErrorMessage: String? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)