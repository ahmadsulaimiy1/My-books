package com.sultan.arabicai.domain.quiz

import com.sultan.arabicai.data.local.entity.ProficiencyLevel
import com.sultan.arabicai.data.local.entity.QuizDifficulty
import com.sultan.arabicai.data.local.entity.QuizQuestionEntity
import com.sultan.arabicai.data.local.entity.QuizType
import com.sultan.arabicai.data.local.entity.VocabWordEntity
import kotlin.random.Random

/**
 * On-device, rule-based quiz generation from the vocabulary bank the learner already owns —
 * fully offline, no server round-trip. This is deliberately a deterministic generator rather
 * than an LLM: it never fabricates Arabic that hasn't been vetted by curriculum content. The
 * Phase-3 roadmap item ("AI speaking coach") layers a real generative model on top of this for
 * open-ended dialogue practice; see docs/ROADMAP.md.
 */
object QuizGenerator {

    fun generateVocabularyQuiz(
        pool: List<VocabWordEntity>,
        difficulty: QuizDifficulty,
        count: Int = 10,
        random: Random = Random.Default
    ): List<QuizQuestionEntity> {
        if (pool.size < 4) return emptyList()

        return pool.shuffled(random).take(count).map { target ->
            val distractors = pool.filter { it.id != target.id }.shuffled(random).take(3)
            val options = (distractors.map { it.english } + target.english).shuffled(random)

            QuizQuestionEntity(
                lessonId = target.lessonId,
                type = QuizType.MULTIPLE_CHOICE,
                difficulty = difficulty,
                promptAr = target.arabic,
                promptEn = "What does \"${target.arabic}\" mean?",
                options = options.joinToString("|"),
                correctAnswer = target.english,
                explanation = "${target.arabic} (${target.transliteration}) — root ${target.rootLetters}"
            )
        }
    }

    fun generateFillInBlankQuiz(
        pool: List<VocabWordEntity>,
        difficulty: QuizDifficulty,
        count: Int = 10,
        random: Random = Random.Default
    ): List<QuizQuestionEntity> {
        return pool.filter { it.exampleSentenceAr.contains(it.arabic) }
            .shuffled(random)
            .take(count)
            .map { target ->
                val blanked = target.exampleSentenceAr.replaceFirst(target.arabic, "_____")
                QuizQuestionEntity(
                    lessonId = target.lessonId,
                    type = QuizType.FILL_IN_BLANK,
                    difficulty = difficulty,
                    promptAr = blanked,
                    promptEn = target.exampleSentenceEn,
                    options = "",
                    correctAnswer = target.arabic,
                    explanation = "${target.arabic} (${target.transliteration}) fits the ${target.partOfSpeech} slot."
                )
            }
    }

    fun generateMatchingQuiz(
        pool: List<VocabWordEntity>,
        difficulty: QuizDifficulty,
        pairCount: Int = 6,
        random: Random = Random.Default
    ): QuizQuestionEntity? {
        val chosen = pool.shuffled(random).take(pairCount)
        if (chosen.size < 4) return null

        val pairs = chosen.joinToString("|") { "${it.arabic}=${it.english}" }
        return QuizQuestionEntity(
            lessonId = null,
            type = QuizType.MATCHING,
            difficulty = difficulty,
            promptAr = "طابق بين الكلمة ومعناها",
            promptEn = "Match each word to its meaning",
            options = pairs,
            correctAnswer = pairs,
            explanation = "Matching set drawn from ${chosen.mapNotNull { it.lessonId }.distinct().size} lesson(s)."
        )
    }

    fun difficultyForLevel(level: ProficiencyLevel): QuizDifficulty = when (level) {
        ProficiencyLevel.BEGINNER -> QuizDifficulty.EASY
        ProficiencyLevel.INTERMEDIATE -> QuizDifficulty.MEDIUM
        ProficiencyLevel.ADVANCED -> QuizDifficulty.HARD
        ProficiencyLevel.SCHOLAR -> QuizDifficulty.SCHOLAR
    }
}
