package com.example.bab6.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.bab6.data.repository.StudentRepository
import com.example.bab6.data.preferences.UserPreferencesRepository
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class HomeViewModel(
    private val repository: StudentRepository,
    private val preferencesRepository: UserPreferencesRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(HomeUiState(isLoading = true))
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()
    private var requestJob: Job? = null

    private var queryEdited = false

    init {
        viewModelScope.launch {
            try {
                val saved = preferencesRepository.lastSearchQuery.first()
                if (!queryEdited) _searchQuery.value = saved
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.value = HomeUiState(errorMessage = "Gagal memulihkan pencarian")
            }
            observeSearch()
            observeQueryPersistence()
        }
    }

    @OptIn(FlowPreview::class)
    private fun observeQueryPersistence() {
        viewModelScope.launch {
            searchQuery.debounce(500).collectLatest { query ->
                try {
                    preferencesRepository.saveLastSearchQuery(query)
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    _uiState.value = _uiState.value.copy(errorMessage = "Gagal menyimpan pencarian")
                }
            }
        }
    }

    fun onSearchQueryChange(query: String) {
        queryEdited = true
        _searchQuery.value = query
    }

    @OptIn(FlowPreview::class)
    private fun observeSearch() {
        viewModelScope.launch {
            searchQuery
                .debounce(500)
                .map { it.trim() }
                .distinctUntilChanged()
                .collectLatest { query ->
                    requestJob?.cancel()
                    requestJob = launch { fetchStudents(query) }
                    requestJob?.join()
                }
        }
    }

    fun retry() = refresh()

    fun refresh() {
        requestJob?.cancel()
        requestJob = viewModelScope.launch { fetchStudents(searchQuery.value.trim()) }
    }

    private suspend fun fetchStudents(query: String) {
        _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
        try {
            val students = if (query.isBlank()) repository.getStudents()
                else repository.searchStudents(query)
            _uiState.value = HomeUiState(students = students)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            _uiState.value = HomeUiState(errorMessage = e.message ?: "Gagal mengambil data")
        }
    }

    companion object {
        fun factory(repository: StudentRepository, preferences: UserPreferencesRepository): ViewModelProvider.Factory =
            object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    require(modelClass.isAssignableFrom(HomeViewModel::class.java))
                    return HomeViewModel(repository, preferences) as T
                }
            }
    }
}
