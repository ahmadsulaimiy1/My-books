package com.sultan.arabicai.navigation

import com.sultan.arabicai.R

object NavRoutes {
    const val ONBOARDING = "onboarding"
    const val BIOMETRIC_LOGIN = "biometric_login"

    const val DASHBOARD = "dashboard"
    const val LIBRARY = "library"
    const val VOCABULARY = "vocabulary"
    const val SPEAKING_LAB = "speaking_lab"
    const val PROFILE = "profile"

    const val PDF_READER = "pdf_reader/{bookId}"
    const val LESSON_LIST = "lesson_list/{bookId}"
    const val LESSON_DETAIL = "lesson_detail/{lessonId}"
    const val FLASHCARDS = "flashcards"
    const val QUIZ = "quiz"
    const val CERTIFICATES = "certificates"

    fun pdfReader(bookId: Long) = "pdf_reader/$bookId"
    fun lessonList(bookId: Long) = "lesson_list/$bookId"
    fun lessonDetail(lessonId: Long) = "lesson_detail/$lessonId"
}

/**
 * Bottom navigation destinations — the five pillars of the flagship experience.
 * [labelRes] rather than a raw String: this is the single most-visible surface in the app on
 * every screen, so it must localize like everything else (a Phase 3 QA re-audit caught this
 * enum still holding hardcoded English after the Phase 2.5 string-externalization pass).
 */
enum class TopLevelDestination(val route: String, val labelRes: Int) {
    DASHBOARD(NavRoutes.DASHBOARD, R.string.nav_overview),
    LIBRARY(NavRoutes.LIBRARY, R.string.nav_library),
    VOCABULARY(NavRoutes.VOCABULARY, R.string.nav_vocabulary),
    SPEAKING_LAB(NavRoutes.SPEAKING_LAB, R.string.nav_speaking),
    PROFILE(NavRoutes.PROFILE, R.string.nav_profile)
}
