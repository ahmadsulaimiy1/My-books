package com.sultan.arabicai.data.seed

import com.sultan.arabicai.data.local.entity.AchievementEntity
import com.sultan.arabicai.data.local.entity.BookEntity
import com.sultan.arabicai.data.local.entity.BookFormat
import com.sultan.arabicai.data.local.entity.LessonEntity
import com.sultan.arabicai.data.local.entity.ProficiencyLevel
import com.sultan.arabicai.data.local.entity.VocabWordEntity
import com.sultan.arabicai.data.repository.LessonRepository
import com.sultan.arabicai.data.repository.LibraryRepository
import com.sultan.arabicai.data.repository.ProgressRepository
import com.sultan.arabicai.data.repository.VocabularyRepository

/**
 * Seeds first-run offline content: the bundled SULTAN book asset plus a starter set of
 * lessons/vocabulary in its structural style (dialogue + grammar focus + graded vocabulary).
 *
 * IMPORTANT — this is scaffold content, not a transcription of the book. Automated text
 * extraction from the source PDF was not available in the build environment that produced
 * this scaffold. Before shipping, replace [seedLessons]/[seedVocabulary] with content
 * produced by the curriculum team's PDF→lesson import pipeline (see docs/ROADMAP.md, Phase 1)
 * so every lesson traces back to an actual page of "SULTAN: Intermediate Book 2".
 */
object ContentSeeder {

    const val SULTAN_BOOK_ASSET_PATH = "books/sultan_intermediate_book_2.pdf"

    suspend fun seedAll(
        libraryRepository: LibraryRepository,
        lessonRepository: LessonRepository,
        vocabularyRepository: VocabularyRepository,
        progressRepository: ProgressRepository
    ) {
        libraryRepository.seedIfEmpty(seedBooks())
        lessonRepository.seedIfEmpty(seedLessons())
        vocabularyRepository.seedIfEmpty(seedVocabulary())
        progressRepository.ensureInitialized()
        progressRepository.seedAchievementsIfEmpty(seedAchievements())
    }

    private fun seedBooks(): List<BookEntity> = listOf(
        BookEntity(
            titleAr = "سلطان: الكتاب المتوسط الثاني",
            titleEn = "SULTAN: Saudi Ultimate Language Training of Arabic for Non-Natives — Intermediate Book 2",
            author = "Ahmad Sulaimiy",
            assetPath = SULTAN_BOOK_ASSET_PATH,
            format = BookFormat.PDF,
            level = ProficiencyLevel.INTERMEDIATE,
            totalPages = 0, // resolved at runtime from PdfRenderer.getPageCount()
            coverColorHex = "#082A66",
            isCoreCurriculum = true
        )
    )

    private fun seedLessons(): List<LessonEntity> = listOf(
        LessonEntity(
            bookId = 1L,
            orderIndex = 0,
            unitNumber = 1,
            titleAr = "في المطار",
            titleEn = "At the Airport",
            dialogueAr = "أ: أهلاً وسهلاً، هل معك جواز السفر؟\nب: نعم، تفضل. أين مكتب الاستقبال؟\nأ: مكتب الاستقبال أمامك مباشرة.",
            dialogueEn = "A: Welcome, do you have your passport?\nB: Yes, here you are. Where is the reception desk?\nA: The reception desk is straight ahead.",
            grammarFocusAr = "أسماء الإشارة وحروف الجر",
            grammarFocusEn = "Demonstrative pronouns and prepositions of place",
            level = ProficiencyLevel.INTERMEDIATE,
            estimatedMinutes = 18
        ),
        LessonEntity(
            bookId = 1L,
            orderIndex = 1,
            unitNumber = 2,
            titleAr = "التسوق في السوق",
            titleEn = "Shopping at the Market",
            dialogueAr = "أ: بكم هذا القميص؟\nب: بخمسين ريالاً، وهو من أجود الأقمشة.\nأ: هل يمكن تخفيض السعر؟",
            dialogueEn = "A: How much is this shirt?\nB: Fifty riyals, and it's made of the finest fabric.\nA: Can you lower the price?",
            grammarFocusAr = "أسلوب السؤال بـ(كم) والأعداد",
            grammarFocusEn = "Question forms with \"how much/many\" and cardinal numbers",
            level = ProficiencyLevel.INTERMEDIATE,
            estimatedMinutes = 20
        ),
        LessonEntity(
            bookId = 1L,
            orderIndex = 2,
            unitNumber = 3,
            titleAr = "الحياة اليومية",
            titleEn = "Daily Life",
            dialogueAr = "أ: متى تستيقظ عادة؟\nب: أستيقظ في السادسة صباحاً وأذهب إلى العمل بعد الفطور.",
            dialogueEn = "A: When do you usually wake up?\nB: I wake up at six in the morning and go to work after breakfast.",
            grammarFocusAr = "الفعل المضارع والظروف الزمانية",
            grammarFocusEn = "Present-tense verbs and time adverbials",
            level = ProficiencyLevel.INTERMEDIATE,
            estimatedMinutes = 22
        )
    )

    private fun seedVocabulary(): List<VocabWordEntity> = listOf(
        VocabWordEntity(
            lessonId = 1L, arabic = "جواز السفر", transliteration = "jawāz as-safar", english = "passport",
            rootLetters = "ج و ز", partOfSpeech = "noun",
            exampleSentenceAr = "هل معك جواز السفر؟", exampleSentenceEn = "Do you have your passport?",
            synonyms = "وثيقة السفر", antonyms = ""
        ),
        VocabWordEntity(
            lessonId = 1L, arabic = "مكتب الاستقبال", transliteration = "maktab al-istiqbāl", english = "reception desk",
            rootLetters = "ق ب ل", partOfSpeech = "noun",
            exampleSentenceAr = "مكتب الاستقبال أمامك مباشرة.", exampleSentenceEn = "The reception desk is straight ahead.",
            synonyms = "", antonyms = ""
        ),
        VocabWordEntity(
            lessonId = 2L, arabic = "قميص", transliteration = "qamīṣ", english = "shirt",
            rootLetters = "ق م ص", partOfSpeech = "noun",
            exampleSentenceAr = "بكم هذا القميص؟", exampleSentenceEn = "How much is this shirt?",
            synonyms = "", antonyms = ""
        ),
        VocabWordEntity(
            lessonId = 2L, arabic = "تخفيض", transliteration = "takhfīḍ", english = "discount",
            rootLetters = "خ ف ض", partOfSpeech = "noun",
            exampleSentenceAr = "هل يمكن تخفيض السعر؟", exampleSentenceEn = "Can you lower the price?",
            synonyms = "خصم", antonyms = "زيادة"
        ),
        VocabWordEntity(
            lessonId = 3L, arabic = "يستيقظ", transliteration = "yastayqiẓ", english = "he wakes up",
            rootLetters = "ي ق ظ", partOfSpeech = "verb",
            exampleSentenceAr = "متى تستيقظ عادة؟", exampleSentenceEn = "When do you usually wake up?",
            synonyms = "", antonyms = "ينام"
        ),
        VocabWordEntity(
            lessonId = 3L, arabic = "الفطور", transliteration = "al-fuṭūr", english = "breakfast",
            rootLetters = "ف ط ر", partOfSpeech = "noun",
            exampleSentenceAr = "أذهب إلى العمل بعد الفطور.", exampleSentenceEn = "I go to work after breakfast.",
            synonyms = "", antonyms = "العشاء"
        )
    )

    private fun seedAchievements(): List<AchievementEntity> = listOf(
        AchievementEntity("daily_streak_7", "أسبوع من الالتزام", "Seven-Day Streak", "حافظ على التعلم سبعة أيام متتالية", "Maintain a seven-day learning streak", "gold"),
        AchievementEntity("perfect_score", "الإجابة الكاملة", "Perfect Score", "أكمل اختباراً بإجابات صحيحة كاملة", "Complete a quiz with a perfect score", "gold"),
        AchievementEntity("fast_learner", "المتعلم السريع", "Fast Learner", "أكمل خمسة دروس في أسبوع واحد", "Complete five lessons within one week", "platinum"),
        AchievementEntity("vocabulary_champion", "بطل المفردات", "Vocabulary Champion", "أتقن مئة كلمة جديدة", "Master one hundred vocabulary words", "platinum"),
        AchievementEntity("grammar_master", "أستاذ القواعد", "Grammar Master", "أجب بشكل صحيح على خمسين سؤال قواعد", "Answer fifty grammar questions correctly", "seal"),
        AchievementEntity("speaking_champion", "بطل التحدث", "Speaking Champion", "أكمل عشر جلسات في مختبر التحدث", "Complete ten Speaking Lab sessions", "seal")
    )
}
