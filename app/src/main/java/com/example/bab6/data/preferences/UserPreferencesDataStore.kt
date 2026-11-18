package com.example.bab6.data.preferences

import android.content.Context
import androidx.datastore.preferences.preferencesDataStore

internal val Context.userPreferencesDataStore by preferencesDataStore(name = "user_preferences")
