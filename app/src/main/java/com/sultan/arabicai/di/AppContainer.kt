package com.sultan.arabicai.di

import android.content.Context
import com.sultan.arabicai.data.local.AppDatabase
import com.sultan.arabicai.data.repository.CertificateRepository
import com.sultan.arabicai.data.repository.LessonRepository
import com.sultan.arabicai.data.repository.LibraryRepository
import com.sultan.arabicai.data.repository.ProgressRepository
import com.sultan.arabicai.data.repository.QuizRepository
import com.sultan.arabicai.data.repository.VocabularyRepository
import com.sultan.arabicai.tts.ArabicTtsEngine

/**
 * Minimal, explicit dependency container — no reflection-based DI framework. For a project
 * this size a hand-rolled graph is easier to audit than adding Hilt/Dagger's build-time
 * complexity, and every dependency here is a single line to trace.
 */
class AppContainer(context: Context) {

    val database: AppDatabase = AppDatabase.getInstance(context)

    val libraryRepository = LibraryRepository(database.bookDao(), database.bookmarkDao(), database.noteDao())
    val lessonRepository = LessonRepository(database.lessonDao())
    val vocabularyRepository = VocabularyRepository(database.vocabularyDao())
    val quizRepository = QuizRepository(database.quizDao())
    val progressRepository = ProgressRepository(database.userStatsDao(), database.studySessionDao(), database.achievementDao())
    val certificateRepository = CertificateRepository(database.certificateDao())

    /** New engine instance per activity is intentional — TextToSpeech is tied to a Context. */
    fun newArabicTtsEngine(context: Context): ArabicTtsEngine = ArabicTtsEngine(context.applicationContext)
}
