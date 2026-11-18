package com.example.bab6

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.example.bab6.ui.theme.Bab6Theme
import com.example.bab6.navigation.NavigationLabApp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            Bab6Theme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    NavigationLabApp()
                }
            }
        }
    }
}

