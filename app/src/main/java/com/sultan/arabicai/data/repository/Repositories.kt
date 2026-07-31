package com.sultan.arabicai.data.repository

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
import com.sultan.arabicai.data.local.entity.QuizDifficulty
import com.sultan.arabicai.data.local.entity.QuizQuestionEntity
import com.sultan.arabicai.data.local.entity.ScholarRank
import com.sultan.arabicai.data.local.entity.StudySessionEntity
import com.sultan.arabicai.data.local.entity.UserStatsEntity
import com.sultan.arabicai.data.local.entity.VocabWordEntity
import com.sultan.arabicai.domain.quiz.QuizGenerator
import com.sultan.arabicai.domain.srs.RecallQuality
import com.sultan.arabicai.domain.srs.SpacedRepetitionScheduler
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.flow.Flow

class LibraryRepository(
    private val bookDao: BookDao,
    private val bookmarkDao: BookmarkDao,
    private val noteDao: NoteDao
) {
    fun observeBooks(): Flow<List<BookEntity>> = bookDao.observeAll()
    suspend fun getBook(id: Long): BookEntity? = bookDao.getById(id)
    suspend fun seedIfEmpty(books: List<BookEntity>) {
        if (bookDao.count() == 0) bookDao.upsertAll(books)
    }

    fun observeBookmarks(bookId: Long): Flow<List<BookmarkEntity>> = bookmarkDao.observeForBook(bookId)
    suspend fun addBookmark(bookId: Long, pageIndex: Int, label: String, nowEpochMillis: Long) {
        bookmarkDao.insert(BookmarkEntity(bookId = bookId, pageIndex = pageIndex, label = label, createdAtEpochMillis = nowEpochMillis))
    }

    fun observeNotes(bookId: Long): Flow<List<NoteEntity>> = noteDao.observeForBook(bookId)
    suspend fun addNote(bookId: Long, pageIndex: Int, content: String, nowEpochMillis: Long) {
        noteDao.insert(NoteEntity(bookId = bookId, pageIndex = pageIndex, content = content, createdAtEpochMillis = nowEpochMillis))
    }
}

class LessonRepository(private val lessonDao: LessonDao) {
    fun observeForBook(bookId: Long): Flow<List<LessonEntity>> = lessonDao.observeForBook(bookId)
    suspend fun getById(id: Long): LessonEntity? = lessonDao.getById(id)
    suspend fun seedIfEmpty(lessons: List<LessonEntity>) {
        if (lessonDao.count() == 0) lessonDao.upsertAll(lessons)
    }
}

class VocabularyRepository(private val vocabularyDao: VocabularyDao) {
    fun observeAll(): Flow<List<VocabWordEntity>> = vocabularyDao.observeAll()
    fun observeFavorites(): Flow<List<VocabWordEntity>> = vocabularyDao.observeFavorites()
    fun observeDifficult(): Flow<List<VocabWordEntity>> = vocabularyDao.observeDifficult()

    suspend fun seedIfEmpty(words: List<VocabWordEntity>) {
        if (vocabularyDao.count() == 0) vocabularyDao.upsertAll(words)
    }

    suspend fun dueForReview(nowEpochMillis: Long = System.currentTimeMillis()): List<VocabWordEntity> =
        vocabularyDao.getDueForReview(nowEpochMillis)

    suspend fun toggleFavorite(word: VocabWordEntity) {
        vocabularyDao.update(word.copy(isFavorite = !word.isFavorite))
    }

    suspend fun toggleDifficult(word: VocabWordEntity) {
        vocabularyDao.update(word.copy(isMarkedDifficult = !word.isMarkedDifficult))
    }

    /** Applies one SM-2 review step and persists the updated schedule. */
    suspend fun submitReview(word: VocabWordEntity, quality: RecallQuality, nowEpochMillis: Long = System.currentTimeMillis()) {
        vocabularyDao.update(SpacedRepetitionScheduler.review(word, quality, nowEpochMillis))
    }
}

class QuizRepository(private val quizDao: QuizDao) {
    suspend fun seedIfEmpty(questions: List<QuizQuestionEntity>) {
        if (quizDao.count() == 0) quizDao.upsertAll(questions)
    }

    suspend fun generateFromVocabulary(pool: List<VocabWordEntity>, difficulty: QuizDifficulty, count: Int = 10): List<QuizQuestionEntity> {
        val generated = QuizGenerator.generateVocabularyQuiz(pool, difficulty, count) +
            QuizGenerator.generateFillInBlankQuiz(pool, difficulty, count / 2)
        quizDao.upsertAll(generated)
        return generated
    }

    suspend fun randomByDifficulty(difficulty: QuizDifficulty, limit: Int = 10): List<QuizQuestionEntity> =
        quizDao.getRandomByDifficulty(difficulty.name, limit)
}

class ProgressRepository(
    private val statsDao: UserStatsDao,
    private val sessionDao: StudySessionDao,
    private val achievementDao: AchievementDao
) {
    fun observeStats(): Flow<UserStatsEntity?> = statsDao.observe()

    suspend fun ensureInitialized() {
        if (statsDao.get() == null) statsDao.upsert(UserStatsEntity())
    }

    fun observeRecentSessions(daysBack: Int = 365): Flow<List<StudySessionEntity>> {
        val sinceEpochDay = TimeUnit.MILLISECONDS.toDays(System.currentTimeMillis()) - daysBack
        return sessionDao.observeSince(sinceEpochDay)
    }

    suspend fun recordSession(
        epochDay: Long,
        minutesStudied: Int = 0,
        lessonsCompleted: Int = 0,
        wordsReviewed: Int = 0,
        quizzesCompleted: Int = 0,
        speakingScore: Int = 0,
        listeningScore: Int = 0,
        grammarScore: Int = 0
    ) {
        val existing = sessionDao.getForDay(epochDay)
        val merged = (existing ?: StudySessionEntity(
            epochDay = epochDay, minutesStudied = 0, lessonsCompleted = 0, wordsReviewed = 0,
            quizzesCompleted = 0, speakingScore = 0, listeningScore = 0, grammarScore = 0
        )).let {
            it.copy(
                minutesStudied = it.minutesStudied + minutesStudied,
                lessonsCompleted = it.lessonsCompleted + lessonsCompleted,
                wordsReviewed = it.wordsReviewed + wordsReviewed,
                quizzesCompleted = it.quizzesCompleted + quizzesCompleted,
                speakingScore = maxOf(it.speakingScore, speakingScore),
                listeningScore = maxOf(it.listeningScore, listeningScore),
                grammarScore = maxOf(it.grammarScore, grammarScore)
            )
        }
        sessionDao.upsert(merged)
        updateStreak(epochDay)
    }

    suspend fun awardXp(amount: Int) {
        val stats = statsDao.get() ?: UserStatsEntity()
        statsDao.upsert(stats.copy(totalXp = stats.totalXp + amount))
    }

    private suspend fun updateStreak(activeEpochDay: Long) {
        val stats = statsDao.get() ?: UserStatsEntity()
        val newStreak = when (activeEpochDay - stats.lastStudiedEpochDay) {
            0L -> stats.currentStreakDays.coerceAtLeast(1)
            1L -> stats.currentStreakDays + 1
            else -> 1
        }
        statsDao.upsert(
            stats.copy(
                currentStreakDays = newStreak,
                longestStreakDays = maxOf(stats.longestStreakDays, newStreak),
                lastStudiedEpochDay = activeEpochDay
            )
        )
    }

    fun observeAchievements(): Flow<List<AchievementEntity>> = achievementDao.observeAll()

    suspend fun seedAchievementsIfEmpty(achievements: List<AchievementEntity>) {
        if (achievementDao.count() == 0) achievementDao.upsertAll(achievements)
    }

    suspend fun unlock(key: String, nowEpochMillis: Long = System.currentTimeMillis()) {
        val achievement = achievementDao.getByKey(key) ?: return
        if (achievement.unlockedAtEpochMillis == null) {
            achievementDao.update(achievement.copy(unlockedAtEpochMillis = nowEpochMillis))
        }
    }

    suspend fun currentRank(): ScholarRank = ScholarRank.forXp(statsDao.get()?.totalXp ?: 0)
}

class CertificateRepository(private val certificateDao: CertificateDao) {
    fun observeAll(): Flow<List<CertificateEntity>> = certificateDao.observeAll()
    suspend fun save(certificate: CertificateEntity): Long = certificateDao.insert(certificate)
    suspend fun verify(code: String): CertificateEntity? = certificateDao.getByVerificationCode(code)
}
