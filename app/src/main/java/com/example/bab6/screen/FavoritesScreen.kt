package com.example.bab6.screen

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.bab6.ui.favorites.FavoritesUiState

@Composable
fun FavoritesScreen(
    uiState: FavoritesUiState,
    onStudentClick: (Int) -> Unit,
    onSortAscendingChange: (Boolean) -> Unit,
    onBack: () -> Unit
) {
    Column(Modifier.fillMaxSize().safeDrawingPadding().padding(16.dp)) {
        Text("Favorites", style = MaterialTheme.typography.headlineMedium)
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text("Urutan nama: ${if (uiState.sortAscending) "A–Z" else "Z–A"}", Modifier.weight(1f))
            Switch(checked = uiState.sortAscending, onCheckedChange = onSortAscendingChange)
        }
        uiState.errorMessage?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        when {
            uiState.isLoading -> CircularProgressIndicator()
            uiState.students.isEmpty() -> Text("Belum ada favorit. Simpan profil dari halaman Detail.", Modifier.padding(vertical = 24.dp))
        }
        LazyColumn(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(uiState.students, key = { it.id }) { student ->
                Card(Modifier.fillMaxWidth().clickable { onStudentClick(student.id) }) {
                    Column(Modifier.padding(16.dp)) {
                        Text(student.name, style = MaterialTheme.typography.titleMedium)
                        Text(student.email, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
        Button(onClick = onBack) { Text("Kembali") }
    }
}
