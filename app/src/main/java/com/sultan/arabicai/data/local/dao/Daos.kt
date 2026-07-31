package com.sultan.arabicai.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
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
import kotlinx.coroutines.flow.Flow

@Dao
interface BookDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(books: List<BookEntity>)

    @Query("SELECT * FROM books ORDER BY isCoreCurriculum DESC, titleEn ASC")
    fun observeAll(): Flow<List<BookEntity>>

    @Query("SELECT * FROM books WHERE id = :id")
    suspend fun getById(id: Long): BookEntity?

    @Query("SELECT COUNT(*) FROM books")
    suspend fun count(): Int
}

@Dao
interface LessonDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(lessons: List<LessonEntity>)

    @Query("SELECT * FROM lessons WHERE bookId = :bookId ORDER BY orderIndex ASC")
    fun observeForBook(bookId: Long): Flow<List<LessonEntity>>

    @Query("SELECT * FROM lessons WHERE id = :id")
    suspend fun getById(id: Long): LessonEntity?

    @Query("SELECT COUNT(*) FROM lessons")
    suspend fun count(): Int
}

@Dao
interface VocabularyDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(words: List<VocabWordEntity>)

    @Update
    suspend fun update(word: VocabWordEntity)

    @Query("SELECT * FROM vocabulary_words ORDER BY arabic ASC")
    fun observeAll(): Flow<List<VocabWordEntity>>

    @Query("SELECT * FROM vocabulary_words WHERE isFavorite = 1 ORDER BY arabic ASC")
    fun observeFavorites(): Flow<List<VocabWordEntity>>

    @Query("SELECT * FROM vocabulary_words WHERE isMarkedDifficult = 1 ORDER BY arabic ASC")
    fun observeDifficult(): Flow<List<VocabWordEntity>>

    @Query("SELECT * FROM vocabulary_words WHERE srsDueAtEpochMillis <= :nowEpochMillis ORDER BY srsDueAtEpochMillis ASC")
    suspend fun getDueForReview(nowEpochMillis: Long): List<VocabWordEntity>

    @Query("SELECT COUNT(*) FROM vocabulary_words")
    suspend fun count(): Int
}

@Dao
interface QuizDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(questions: List<QuizQuestionEntity>)

    @Query("SELECT * FROM quiz_questions WHERE lessonId = :lessonId")
    suspend fun getForLesson(lessonId: Long): List<QuizQuestionEntity>

    @Query("SELECT * FROM quiz_questions WHERE difficulty = :difficulty ORDER BY RANDOM() LIMIT :limit")
    suspend fun getRandomByDifficulty(difficulty: String, limit: Int): List<QuizQuestionEntity>

    @Query("SELECT COUNT(*) FROM quiz_questions")
    suspend fun count(): Int
}

@Dao
interface StudySessionDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(session: StudySessionEntity)

    @Query("SELECT * FROM study_sessions WHERE epochDay = :epochDay LIMIT 1")
    suspend fun getForDay(epochDay: Long): StudySessionEntity?

    @Query("SELECT * FROM study_sessions WHERE epochDay >= :sinceEpochDay ORDER BY epochDay ASC")
    fun observeSince(sinceEpochDay: Long): Flow<List<StudySessionEntity>>
}

@Dao
interface UserStatsDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(stats: UserStatsEntity)

    @Query("SELECT * FROM user_stats WHERE id = 1")
    fun observe(): Flow<UserStatsEntity?>

    @Query("SELECT * FROM user_stats WHERE id = 1")
    suspend fun get(): UserStatsEntity?
}

@Dao
interface AchievementDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(achievements: List<AchievementEntity>)

    @Update
    suspend fun update(achievement: AchievementEntity)

    @Query("SELECT * FROM achievements ORDER BY unlockedAtEpochMillis DESC")
    fun observeAll(): Flow<List<AchievementEntity>>

    @Query("SELECT COUNT(*) FROM achievements")
    suspend fun count(): Int

    @Query("SELECT * FROM achievements WHERE `key` = :key")
    suspend fun getByKey(key: String): AchievementEntity?
}

@Dao
interface BookmarkDao {
    @Insert
    suspend fun insert(bookmark: BookmarkEntity)

    @Query("SELECT * FROM bookmarks WHERE bookId = :bookId ORDER BY pageIndex ASC")
    fun observeForBook(bookId: Long): Flow<List<BookmarkEntity>>
}

@Dao
interface NoteDao {
    @Insert
    suspend fun insert(note: NoteEntity)

    @Query("SELECT * FROM notes WHERE bookId = :bookId ORDER BY pageIndex ASC")
    fun observeForBook(bookId: Long): Flow<List<NoteEntity>>
}

@Dao
interface CertificateDao {
    @Insert
    suspend fun insert(certificate: CertificateEntity): Long

    @Query("SELECT * FROM certificates ORDER BY issuedAtEpochMillis DESC")
    fun observeAll(): Flow<List<CertificateEntity>>

    @Query("SELECT * FROM certificates WHERE verificationCode = :code LIMIT 1")
    suspend fun getByVerificationCode(code: String): CertificateEntity?
}
