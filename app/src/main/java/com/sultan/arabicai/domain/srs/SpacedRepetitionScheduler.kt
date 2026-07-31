package com.sultan.arabicai.domain.srs

import com.sultan.arabicai.data.local.entity.VocabWordEntity
import java.util.concurrent.TimeUnit
import kotlin.math.roundToInt

/** How well the learner recalled a word, on the standard SM-2 0-5 grade scale. */
enum class RecallQuality(val grade: Int) {
    COMPLETE_BLACKOUT(0),
    INCORRECT_FAMILIAR(1),
    INCORRECT_EASY_RECALL(2),
    CORRECT_DIFFICULT(3),
    CORRECT_HESITANT(4),
    CORRECT_PERFECT(5)
}

/**
 * SM-2 spaced-repetition scheduler (the SuperMemo-2 algorithm) — the same memory-optimisation
 * model used by Anki and most production flashcard systems. Runs entirely on-device; no
 * network or server-side model required.
 */
object SpacedRepetitionScheduler {

    fun review(word: VocabWordEntity, quality: RecallQuality, nowEpochMillis: Long): VocabWordEntity {
        val grade = quality.grade

        if (grade < 3) {
            // Failed recall: reset the interval but keep the ease factor (mostly) intact so a
            // single slip doesn't erase weeks of progress on an otherwise well-known word.
            return word.copy(
                srsRepetitions = 0,
                srsIntervalDays = 1,
                srsEaseFactor = adjustEase(word.srsEaseFactor, grade),
                srsDueAtEpochMillis = nowEpochMillis + TimeUnit.DAYS.toMillis(1)
            )
        }

        val newEase = adjustEase(word.srsEaseFactor, grade)
        val newRepetitions = word.srsRepetitions + 1
        val newInterval = when (newRepetitions) {
            1 -> 1
            2 -> 6
            else -> (word.srsIntervalDays * newEase).roundToInt().coerceAtLeast(1)
        }

        return word.copy(
            srsRepetitions = newRepetitions,
            srsIntervalDays = newInterval,
            srsEaseFactor = newEase,
            srsDueAtEpochMillis = nowEpochMillis + TimeUnit.DAYS.toMillis(newInterval.toLong())
        )
    }

    private fun adjustEase(currentEase: Float, grade: Int): Float {
        val delta = 0.1f - (5 - grade) * (0.08f + (5 - grade) * 0.02f)
        return (currentEase + delta).coerceAtLeast(1.3f)
    }
}
