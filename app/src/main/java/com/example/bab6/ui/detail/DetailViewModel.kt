package com.example.bab6.ui.detail

import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import com.example.bab6.data.repository.FavoriteRepository
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.bab6.data.repository.StudentRepository

class DetailViewModel(
    private val repository: StudentRepository,
    private val favoriteRepository: FavoriteRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(DetailUiState())
    val uiState: StateFlow<DetailUiState> = _uiState.asStateFlow()
    private var requestJob: Job? = null

    private var favoriteJob: Job? = null

    fun loadStudent(id: Int) {
        favoriteJob?.cancel()
        requestJob?.cancel()
        requestJob = viewModelScope.launch {
            _uiState.value = DetailUiState(isLoading = true)
            try {
                // Saved profiles can also be opened from Favorites without a network request.
                val student = favoriteRepository.getFavorite(id) ?: repository.getStudent(id)
                _uiState.value = DetailUiState(student = student)
                observeFavorite(id)
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.value = DetailUiState(errorMessage = e.message ?: "Data tidak tersedia")
            }
        }
    }
    private fun observeFavorite(id: Int) {
        favoriteJob?.cancel()
        favoriteJob = viewModelScope.launch {
            try {
                favoriteRepository.observeIsFavorite(id).collect { favorite ->
                    _uiState.update { it.copy(isFavorite = favorite) }
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.update { it.copy(favoriteErrorMessage = "Gagal membaca status favorit") }
            }
        }
    }

    fun toggleFavorite() {
        val state = uiState.value
        val student = state.student ?: return
        if (state.isSavingFavorite) return
        _uiState.update { it.copy(isSavingFavorite = true, favoriteErrorMessage = null) }
        viewModelScope.launch {
            try {
                if (state.isFavorite) favoriteRepository.remove(student.id)
                else favoriteRepository.add(student)
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.update { it.copy(favoriteErrorMessage = e.message ?: "Gagal mengubah favorit") }
            } finally {
                _uiState.update { it.copy(isSavingFavorite = false) }
            }
        }
    }

    companion object {
        fun factory(repository: StudentRepository, favorites: FavoriteRepository): ViewModelProvider.Factory =
            object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    return DetailViewModel(repository, favorites) as T
                }
            }
    }
}