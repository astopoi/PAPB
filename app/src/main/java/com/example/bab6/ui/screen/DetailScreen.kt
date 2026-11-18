package com.example.bab6.ui.screen

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.bab6.ui.detail.DetailUiState

@Composable
fun DetailScreen(
    uiState: DetailUiState,
    onToggleFavorite: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .safeDrawingPadding()
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Detail Student", style = MaterialTheme.typography.headlineMedium)
        when {
            uiState.isLoading -> CircularProgressIndicator()
            uiState.errorMessage != null ->
                Text(uiState.errorMessage)
            uiState.student != null -> {
                val student = uiState.student
                Text("ID: ${student.id}")
                Text("Name: ${student.name}")
                Text("University: ${student.university}")
                Text("Email: ${student.email}")
                Button(onClick = onToggleFavorite, enabled = !uiState.isSavingFavorite) {
                    Text(if (uiState.isFavorite) "Hapus dari Favorit" else "Simpan ke Favorit")
                }
                uiState.favoriteErrorMessage?.let { Text(it, color = MaterialTheme.colorScheme.error) }
            }
        }
        Button(onClick = onBack) {
            Text("Kembali")
        }
    }
}

