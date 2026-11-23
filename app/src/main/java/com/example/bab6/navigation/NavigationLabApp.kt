package com.example.bab6.navigation

import com.google.android.gms.location.LocationServices
import com.example.bab6.data.location.DefaultLocationRepository
import com.example.bab6.ui.location.LocationViewModel
import com.example.bab6.ui.location.LocationScreen
import androidx.compose.ui.platform.LocalContext
import com.example.bab6.data.local.DatabaseProvider
import com.example.bab6.data.preferences.DataStoreUserPreferencesRepository
import com.example.bab6.data.repository.RoomFavoriteRepository
import com.example.bab6.ui.favorites.FavoritesViewModel
import com.example.bab6.screen.FavoritesScreen
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.bab6.data.remote.RetrofitClient
import com.example.bab6.data.remote.StudentRemoteDataSource
import com.example.bab6.data.repository.DefaultStudentRepository
import com.example.bab6.ui.screen.DetailScreen
import com.example.bab6.screen.HomeScreen
import com.example.bab6.screen.AboutScreen
import com.example.bab6.screen.ProfileScreen
import com.example.bab6.ui.detail.DetailViewModel
import com.example.bab6.ui.home.HomeViewModel
import com.example.bab6.ui.theme.Routes

@Composable
fun NavigationLabApp() {
    val dataSource = remember { StudentRemoteDataSource(RetrofitClient.apiService) }
    val repository = remember { DefaultStudentRepository(dataSource) }

    val context = LocalContext.current.applicationContext
    val preferencesRepository = remember(context) { DataStoreUserPreferencesRepository(context) }
    val favoriteRepository = remember(context) {
        RoomFavoriteRepository(DatabaseProvider.getDatabase(context).favoriteStudentDao())
    }
    val locationRepository = remember(context) {
        DefaultLocationRepository(context, LocationServices.getFusedLocationProviderClient(context))
    }
    val navController = rememberNavController()
    NavHost(
        navController = navController,
        startDestination = Routes.HOME
    ) {
        composable(Routes.HOME) {
            val homeViewModel: HomeViewModel = viewModel(factory = HomeViewModel.factory(repository, preferencesRepository))
            val homeUiState by homeViewModel.uiState.collectAsStateWithLifecycle()
            val searchQuery by homeViewModel.searchQuery.collectAsStateWithLifecycle()
            HomeScreen(
                uiState = homeUiState,
                searchQuery = searchQuery,
                onStudentClick = { id -> navController.navigate(Routes.detail(id)) },
                onRetry = homeViewModel::retry,
                onSearchQueryChange = homeViewModel::onSearchQueryChange,
                onRefresh = homeViewModel::refresh,
                onOpenLocation = { navController.navigate(Routes.LOCATION) },
                onOpenFavorites = { navController.navigate(Routes.FAVORITES) },
                onOpenProfile = { navController.navigate(Routes.PROFILE) },
                onOpenAbout = { navController.navigate(Routes.ABOUT) }
            )
        }
        composable(
            route = Routes.DETAIL,
            arguments = listOf(
                navArgument("studentId") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val studentId = backStackEntry.arguments?.getInt("studentId") ?: -1

            val viewModel: DetailViewModel = viewModel(
                factory = DetailViewModel.factory(repository, favoriteRepository)
            )
            LaunchedEffect(studentId) {
                viewModel.loadStudent(studentId)
            }
            val detailUiState by viewModel.uiState.collectAsStateWithLifecycle()
            DetailScreen(
                uiState = detailUiState,
                onToggleFavorite = viewModel::toggleFavorite,
                onBack = { navController.popBackStack() }
            )
        }
        composable(Routes.LOCATION) {
            val locationViewModel: LocationViewModel = viewModel(factory = LocationViewModel.factory(locationRepository))
            LocationScreen(viewModel = locationViewModel, onBack = { navController.popBackStack() })
        }
        composable(Routes.FAVORITES) {
            val favoritesViewModel: FavoritesViewModel = viewModel(
                factory = FavoritesViewModel.factory(favoriteRepository, preferencesRepository)
            )
            val favoritesUiState by favoritesViewModel.uiState.collectAsStateWithLifecycle()
            FavoritesScreen(
                uiState = favoritesUiState,
                onStudentClick = { id -> navController.navigate(Routes.detail(id)) },
                onSortAscendingChange = favoritesViewModel::onSortAscendingChange,
                onBack = { navController.popBackStack() }
            )
        }
        composable(Routes.PROFILE) {
            ProfileScreen(
                onBack = { navController.popBackStack() }
            )
        }
        composable(Routes.ABOUT) {
            AboutScreen(
                onBack = { navController.popBackStack() }
            )
        }
    }
}
