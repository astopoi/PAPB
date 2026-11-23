package com.example.bab6.screen // Sesuaikan dengan lokasi package file Anda

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.bab6.data.model.Student
import com.example.bab6.ui.home.HomeUiState

@Composable
fun HomeScreen(
    uiState: HomeUiState,
    searchQuery: String,
    onStudentClick: (Int) -> Unit,
    onRetry: () -> Unit,
    onSearchQueryChange: (String) -> Unit,
    onRefresh: () -> Unit,
    onOpenLocation: () -> Unit,
    onOpenProfile: () -> Unit,
    onOpenFavorites: () -> Unit,
    onOpenAbout: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize().safeDrawingPadding()) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            TextButton(onClick = onOpenProfile) { Text("Profile") }
            TextButton(onClick = onOpenAbout) { Text("About") }
            TextButton(onClick = onOpenFavorites) { Text("Favorites") }
        }
        TextButton(onClick = onOpenLocation, modifier = Modifier.padding(horizontal = 16.dp)) { Text("Buka Lokasi") }
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = onSearchQueryChange,
                label = { Text("Cari profil") },
                singleLine = true,
                modifier = Modifier.weight(1f)
            )
            Button(onClick = onRefresh, enabled = !uiState.isLoading) { Text("Refresh") }
        }
        Box(modifier = Modifier.weight(1f)) {
            when {
                uiState.isLoading -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                }
                uiState.errorMessage != null -> {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(24.dp),
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text(uiState.errorMessage)
                        Button(onClick = onRetry) { Text("Coba Lagi") }
                    }
                }
                else -> {
                    if (uiState.students.isEmpty()) {
                        Text("Tidak ada profil ditemukan", modifier = Modifier.padding(16.dp))
                    }
                    LazyColumn {
                        items(uiState.students) { student ->
                            TextButton(onClick = { onStudentClick(student.id) }) {
                                Text("${student.id} - ${student.name}")
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun StudentItem(
    student: Student,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "ID: ${student.id}",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.primary
            )
            Text(
                text = student.name,
                style = MaterialTheme.typography.titleMedium
            )
        }
    }
}
