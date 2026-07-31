package com.sultan.arabicai.navigation

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

/** Bottom navigation destinations — the five pillars of the flagship experience. */
enum class TopLevelDestination(val route: String, val label: String) {
    DASHBOARD(NavRoutes.DASHBOARD, "Overview"),
    LIBRARY(NavRoutes.LIBRARY, "Library"),
    VOCABULARY(NavRoutes.VOCABULARY, "Vocabulary"),
    SPEAKING_LAB(NavRoutes.SPEAKING_LAB, "Speaking"),
    PROFILE(NavRoutes.PROFILE, "Profile")
}
