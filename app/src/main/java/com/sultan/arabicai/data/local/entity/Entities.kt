package com.sultan.arabicai.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

enum class ProficiencyLevel { BEGINNER, INTERMEDIATE, ADVANCED, SCHOLAR }

enum class BookFormat { PDF, EPUB, DOCX, TXT, HTML }

enum class QuizType {
    MULTIPLE_CHOICE, DRAG_AND_DROP, LISTENING, PRONUNCIATION, VOICE_RESPONSE,
    SENTENCE_BUILDING, TRANSLATION, VOCABULARY, GRAMMAR, DICTATION, FILL_IN_BLANK,
    MATCHING, TIMED_CHALLENGE
}

enum class QuizDifficulty { EASY, MEDIUM, HARD, SCHOLAR }

enum class ScholarRank(val xpThreshold: Int) {
    BEGINNER(0),
    STUDENT(500),
    SCHOLAR(1500),
    RESEARCHER(3500),
    EXPERT(7000),
    MASTER(12000),
    AMBASSADOR(20000),
    ELITE_SCHOLAR(32000),
    GRAND_SCHOLAR(50000);

    companion object {
        fun forXp(xp: Int): ScholarRank = entries.lastOrNull { xp >= it.xpThreshold } ?: BEGINNER
        fun next(rank: ScholarRank): ScholarRank? = entries.getOrNull(rank.ordinal + 1)
    }
}

enum class CertificateLevel { COURSE_COMPLETION, EXCELLENCE, DISTINCTION, HONOUR, GRAND_HONOUR }

@Entity(tableName = "books")
data class BookEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val titleAr: String,
    val titleEn: String,
    val author: String,
    val assetPath: String,
    val format: BookFormat,
    val level: ProficiencyLevel,
    val totalPages: Int,
    val coverColorHex: String = "#082A66",
    val isCoreCurriculum: Boolean = false
)

@Entity(tableName = "lessons")
data class LessonEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val bookId: Long,
    val orderIndex: Int,
    val unitNumber: Int,
    val titleAr: String,
    val titleEn: String,
    val dialogueAr: String,
    val dialogueEn: String,
    val grammarFocusAr: String,
    val grammarFocusEn: String,
    val level: ProficiencyLevel,
    val estimatedMinutes: Int
)

@Entity(tableName = "vocabulary_words")
data class VocabWordEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val lessonId: Long?,
    val arabic: String,
    val transliteration: String,
    val english: String,
    val rootLetters: String,
    val partOfSpeech: String,
    val exampleSentenceAr: String,
    val exampleSentenceEn: String,
    val synonyms: String = "",
    val antonyms: String = "",
    val isFavorite: Boolean = false,
    val isMarkedDifficult: Boolean = false,
    // SM-2 spaced-repetition state
    val srsEaseFactor: Float = 2.5f,
    val srsIntervalDays: Int = 0,
    val srsRepetitions: Int = 0,
    val srsDueAtEpochMillis: Long = 0L
)

@Entity(tableName = "quiz_questions")
data class QuizQuestionEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val lessonId: Long?,
    val type: QuizType,
    val difficulty: QuizDifficulty,
    val promptAr: String,
    val promptEn: String,
    val options: String, // pipe-delimited; see Converters for helpers
    val correctAnswer: String,
    val explanation: String
)

@Entity(tableName = "study_sessions")
data class StudySessionEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val epochDay: Long,
    val minutesStudied: Int,
    val lessonsCompleted: Int,
    val wordsReviewed: Int,
    val quizzesCompleted: Int,
    val speakingScore: Int,
    val listeningScore: Int,
    val grammarScore: Int
)

@Entity(tableName = "user_stats")
data class UserStatsEntity(
    @PrimaryKey val id: Int = SINGLETON_ID,
    val totalXp: Int = 0,
    val currentStreakDays: Int = 0,
    val longestStreakDays: Int = 0,
    val lastStudiedEpochDay: Long = 0L,
    val totalLearningMinutes: Int = 0
) {
    companion object {
        const val SINGLETON_ID = 1
    }
}

@Entity(tableName = "achievements")
data class AchievementEntity(
    @PrimaryKey val key: String,
    val titleAr: String,
    val titleEn: String,
    val descriptionAr: String,
    val descriptionEn: String,
    val tier: String, // "gold" | "platinum" | "seal"
    val unlockedAtEpochMillis: Long? = null
)

@Entity(tableName = "bookmarks")
data class BookmarkEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val bookId: Long,
    val pageIndex: Int,
    val label: String,
    val createdAtEpochMillis: Long
)

@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val bookId: Long,
    val pageIndex: Int,
    val content: String,
    val createdAtEpochMillis: Long
)

@Entity(tableName = "certificates")
data class CertificateEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val titleAr: String,
    val titleEn: String,
    val level: CertificateLevel,
    val recipientName: String,
    val issuedAtEpochMillis: Long,
    val verificationCode: String,
    val filePath: String
)
