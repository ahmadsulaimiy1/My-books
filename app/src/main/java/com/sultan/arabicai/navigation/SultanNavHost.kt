package com.sultan.arabicai.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoStories
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.Translate
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.fragment.app.FragmentActivity
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import androidx.navigation.NavType
import com.sultan.arabicai.R
import com.sultan.arabicai.security.BiometricAuthManager
import com.sultan.arabicai.security.BiometricAvailability
import com.sultan.arabicai.security.BiometricResult
import com.sultan.arabicai.security.SecurePreferences
import com.sultan.arabicai.ui.screens.auth.BiometricLoginScreen
import com.sultan.arabicai.ui.screens.certificates.CertificatesScreen
import com.sultan.arabicai.ui.screens.dashboard.DashboardScreen
import com.sultan.arabicai.ui.screens.lessons.LessonDetailScreen
import com.sultan.arabicai.ui.screens.lessons.LessonListScreen
import com.sultan.arabicai.ui.screens.library.LibraryScreen
import com.sultan.arabicai.ui.screens.library.PdfReaderScreen
import com.sultan.arabicai.ui.screens.onboarding.OnboardingScreen
import com.sultan.arabicai.ui.screens.profile.ProfileScreen
import com.sultan.arabicai.ui.screens.quiz.QuizScreen
import com.sultan.arabicai.ui.screens.speaking.SpeakingLabScreen
import com.sultan.arabicai.ui.screens.vocabulary.FlashcardScreen
import com.sultan.arabicai.ui.screens.vocabulary.VocabularyBankScreen

private val TOP_LEVEL_ROUTES = TopLevelDestination.entries.map { it.route }.toSet()

@Composable
fun SultanNavHost(activity: FragmentActivity) {
    val navController = rememberNavController()
    val context = LocalContext.current
    val biometricManager = remember { BiometricAuthManager(activity) }

    val startDestination = remember {
        when {
            !SecurePreferences.isOnboardingComplete(context) -> NavRoutes.ONBOARDING
            SecurePreferences.isBiometricEnabled(context) &&
                biometricManager.checkAvailability() == BiometricAvailability.Available -> NavRoutes.BIOMETRIC_LOGIN
            else -> NavRoutes.DASHBOARD
        }
    }

    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    Scaffold(
        bottomBar = {
            if (currentRoute in TOP_LEVEL_ROUTES) {
                NavigationBar {
                    TopLevelDestination.entries.forEach { destination ->
                        NavigationBarItem(
                            selected = currentRoute == destination.route,
                            onClick = {
                                navController.navigate(destination.route) {
                                    popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = { Icon(iconFor(destination), contentDescription = stringResource(destination.labelRes)) },
                            label = { Text(stringResource(destination.labelRes)) }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(navController = navController, startDestination = startDestination, modifier = Modifier.padding(innerPadding)) {

            composable(NavRoutes.ONBOARDING) {
                OnboardingScreen(onBegin = {
                    SecurePreferences.setOnboardingComplete(context, true)
                    val next = if (biometricManager.checkAvailability() == BiometricAvailability.Available) {
                        NavRoutes.BIOMETRIC_LOGIN
                    } else {
                        NavRoutes.DASHBOARD
                    }
                    navController.navigate(next) { popUpTo(NavRoutes.ONBOARDING) { inclusive = true } }
                })
            }

            composable(NavRoutes.BIOMETRIC_LOGIN) {
                // Resolved here (a @Composable context) rather than inside onAuthenticate — that
                // lambda runs later, on a button click, where stringResource() can't be called.
                // A Phase 3 QA re-audit caught these as hardcoded English reaching the native
                // BiometricPrompt dialog even though the Compose fallback screen already used
                // the correct string resources.
                val biometricTitle = stringResource(R.string.auth_biometric_title)
                val biometricSubtitle = stringResource(R.string.auth_biometric_subtitle)
                BiometricLoginScreen(
                    availability = biometricManager.checkAvailability(),
                    onAuthenticate = {
                        biometricManager.authenticate(
                            titleRes = biometricTitle,
                            subtitleRes = biometricSubtitle
                        ) { result ->
                            if (result is BiometricResult.Success) {
                                SecurePreferences.recordUnlock(context, System.currentTimeMillis())
                                navController.navigate(NavRoutes.DASHBOARD) { popUpTo(NavRoutes.BIOMETRIC_LOGIN) { inclusive = true } }
                            }
                        }
                    },
                    onSkip = {
                        navController.navigate(NavRoutes.DASHBOARD) { popUpTo(NavRoutes.BIOMETRIC_LOGIN) { inclusive = true } }
                    }
                )
            }

            composable(NavRoutes.DASHBOARD) { DashboardScreen() }

            composable(NavRoutes.LIBRARY) {
                LibraryScreen(
                    onOpenReader = { bookId -> navController.navigate(NavRoutes.pdfReader(bookId)) },
                    onOpenLessons = { bookId -> navController.navigate(NavRoutes.lessonList(bookId)) }
                )
            }

            composable(NavRoutes.VOCABULARY) {
                VocabularyBankScreen(onOpenFlashcards = { navController.navigate(NavRoutes.FLASHCARDS) })
            }

            composable(NavRoutes.SPEAKING_LAB) { SpeakingLabScreen() }

            composable(NavRoutes.PROFILE) {
                ProfileScreen(onOpenCertificates = { navController.navigate(NavRoutes.CERTIFICATES) })
            }

            composable(
                route = NavRoutes.PDF_READER,
                arguments = listOf(navArgument("bookId") { type = NavType.LongType })
            ) { entry ->
                PdfReaderScreen(bookId = entry.arguments?.getLong("bookId") ?: 0L)
            }

            composable(
                route = NavRoutes.LESSON_LIST,
                arguments = listOf(navArgument("bookId") { type = NavType.LongType })
            ) { entry ->
                LessonListScreen(
                    bookId = entry.arguments?.getLong("bookId") ?: 0L,
                    onOpenLesson = { lessonId -> navController.navigate(NavRoutes.lessonDetail(lessonId)) }
                )
            }

            composable(
                route = NavRoutes.LESSON_DETAIL,
                arguments = listOf(navArgument("lessonId") { type = NavType.LongType })
            ) { entry ->
                LessonDetailScreen(
                    lessonId = entry.arguments?.getLong("lessonId") ?: 0L,
                    onStartQuiz = { navController.navigate(NavRoutes.QUIZ) }
                )
            }

            composable(NavRoutes.FLASHCARDS) {
                FlashcardScreen(onFinished = { navController.popBackStack() })
            }

            composable(NavRoutes.QUIZ) { QuizScreen() }

            composable(NavRoutes.CERTIFICATES) { CertificatesScreen() }
        }
    }
}

private fun iconFor(destination: TopLevelDestination) = when (destination) {
    TopLevelDestination.DASHBOARD -> Icons.Filled.Dashboard
    TopLevelDestination.LIBRARY -> Icons.Filled.AutoStories
    TopLevelDestination.VOCABULARY -> Icons.Filled.Translate
    TopLevelDestination.SPEAKING_LAB -> Icons.Filled.Mic
    TopLevelDestination.PROFILE -> Icons.Filled.Person
}
