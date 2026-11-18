package com.example.bab6.ui.theme

object Routes {
    const val FAVORITES = "favorites"
    const val HOME = "home"
    const val PROFILE = "profile"
    const val DETAIL = "detail/{studentId}"
    const val ABOUT = "about"
    fun detail(studentId: Int): String = "detail/$studentId"
}