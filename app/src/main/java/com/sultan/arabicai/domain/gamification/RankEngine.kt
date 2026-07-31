package com.sultan.arabicai.domain.gamification

import com.sultan.arabicai.data.local.entity.ScholarRank
import com.sultan.arabicai.data.local.entity.UserStatsEntity
import kotlin.math.max

data class RankProgress(
    val currentRank: ScholarRank,
    val nextRank: ScholarRank?,
    /** 0f..1f progress toward [nextRank]; 1f when at the top rank. */
    val progressToNext: Float,
    val xpIntoCurrentRank: Int,
    val xpNeededForNext: Int?
)

/** Prestige-ladder math: XP thresholds live on [ScholarRank] itself so this stays a pure function. */
object RankEngine {

    fun progressFor(stats: UserStatsEntity): RankProgress {
        val current = ScholarRank.forXp(stats.totalXp)
        val next = ScholarRank.next(current)

        if (next == null) {
            return RankProgress(current, null, 1f, stats.totalXp - current.xpThreshold, null)
        }

        val span = next.xpThreshold - current.xpThreshold
        val into = stats.totalXp - current.xpThreshold
        val progress = if (span <= 0) 1f else (into.toFloat() / span).coerceIn(0f, 1f)

        return RankProgress(current, next, progress, into, max(0, next.xpThreshold - stats.totalXp))
    }

    /** XP awards for common actions — tuned so a focused daily session earns roughly 80-150 XP. */
    object Xp {
        const val LESSON_COMPLETED = 40
        const val QUIZ_CORRECT_ANSWER = 5
        const val QUIZ_PERFECT_BONUS = 30
        const val VOCAB_WORD_MASTERED = 8
        const val DAILY_STREAK_BONUS = 15
        const val SPEAKING_SESSION_COMPLETED = 20
    }
}
