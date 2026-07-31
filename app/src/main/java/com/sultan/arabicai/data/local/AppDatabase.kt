package com.sultan.arabicai.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.sultan.arabicai.data.local.dao.AchievementDao
import com.sultan.arabicai.data.local.dao.BookDao
import com.sultan.arabicai.data.local.dao.BookmarkDao
import com.sultan.arabicai.data.local.dao.CertificateDao
import com.sultan.arabicai.data.local.dao.LessonDao
import com.sultan.arabicai.data.local.dao.NoteDao
import com.sultan.arabicai.data.local.dao.QuizDao
import com.sultan.arabicai.data.local.dao.StudySessionDao
import com.sultan.arabicai.data.local.dao.UserStatsDao
import com.sultan.arabicai.data.local.dao.VocabularyDao
import com.sultan.arabicai.data.local.entity.AchievementEntity
import com.sultan.arabicai.data.local.entity.BookEntity
import com.sultan.arabicai.data.local.entity.BookmarkEntity
import com.sultan.arabicai.data.local.entity.CertificateEntity
import com.sultan.arabicai.data.local.entity.LessonEntity
import com.sultan.arabicai.data.local.entity.NoteEntity
import com.sultan.arabicai.data.local.entity.QuizQuestionEntity
import com.sultan.arabicai.data.local.entity.StudySessionEntity
import com.sultan.arabicai.data.local.entity.UserStatsEntity
import com.sultan.arabicai.data.local.entity.VocabWordEntity

/**
 * Single source of truth for the entire offline experience: lessons, quizzes, vocabulary SRS
 * state, gamification, and library annotations all live here so the app is 100% usable with
 * no network connection. See data/sync/ (roadmap, Phase 1 stub) for the cloud-reconciliation
 * contract that runs once connectivity returns.
 */
@Database(
    entities = [
        BookEntity::class,
        LessonEntity::class,
        VocabWordEntity::class,
        QuizQuestionEntity::class,
        StudySessionEntity::class,
        UserStatsEntity::class,
        AchievementEntity::class,
        BookmarkEntity::class,
        NoteEntity::class,
        CertificateEntity::class
    ],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun bookDao(): BookDao
    abstract fun lessonDao(): LessonDao
    abstract fun vocabularyDao(): VocabularyDao
    abstract fun quizDao(): QuizDao
    abstract fun studySessionDao(): StudySessionDao
    abstract fun userStatsDao(): UserStatsDao
    abstract fun achievementDao(): AchievementDao
    abstract fun bookmarkDao(): BookmarkDao
    abstract fun noteDao(): NoteDao
    abstract fun certificateDao(): CertificateDao

    companion object {
        @Volatile private var instance: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase =
            instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "sultan_arabic_ai.db"
                ).build().also { instance = it }
            }
    }
}
