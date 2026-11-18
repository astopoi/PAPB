package com.example.bab6.ui.favorites

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.bab6.data.model.Student
import com.example.bab6.data.preferences.UserPreferencesRepository
import com.example.bab6.data.repository.FavoriteRepository
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.util.Locale

data class FavoritesUiState(
    val students: List<Student> = emptyList(),
    val sortAscending: Boolean = true,
    val isLoading: Boolean = true,
    val errorMessage: String? = null
)

class FavoritesViewModel(
    private val favorites: FavoriteRepository,
    private val preferences: UserPreferencesRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(FavoritesUiState())
    val uiState: StateFlow<FavoritesUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(favorites.observeFavorites(), preferences.sortAscending) { students, ascending ->
                val sorted = students.sortedWith(compareBy<Student> { it.name.lowercase(Locale.ROOT) }.thenBy { it.id })
                FavoritesUiState(students = if (ascending) sorted else sorted.reversed(), sortAscending = ascending, isLoading = false)
            }.catch { error ->
                if (error is CancellationException) throw error
                emit(FavoritesUiState(isLoading = false, errorMessage = error.message ?: "Gagal memuat favorit"))
            }.collect { state -> _uiState.value = state }
        }
    }

    fun onSortAscendingChange(ascending: Boolean) {
        viewModelScope.launch {
            try {
                preferences.saveSortAscending(ascending)
                _uiState.update { it.copy(errorMessage = null) }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.update { it.copy(errorMessage = e.message ?: "Gagal menyimpan urutan") }
            }
        }
    }

    companion object {
        fun factory(favorites: FavoriteRepository, preferences: UserPreferencesRepository) =
            object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    require(modelClass.isAssignableFrom(FavoritesViewModel::class.java))
                    return FavoritesViewModel(favorites, preferences) as T
                }
            }
    }
}
