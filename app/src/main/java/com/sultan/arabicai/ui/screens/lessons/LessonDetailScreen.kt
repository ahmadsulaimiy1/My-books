package com.sultan.arabicai.ui.screens.lessons

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.sultan.arabicai.R
import com.sultan.arabicai.data.local.entity.LessonEntity
import com.sultan.arabicai.data.local.entity.VocabWordEntity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.tts.ArabicTtsEngine
import com.sultan.arabicai.tts.DeliveryPreset
import com.sultan.arabicai.tts.ReadingMode
import com.sultan.arabicai.tts.TtsPlaybackController
import com.sultan.arabicai.tts.VoiceDataManager
import com.sultan.arabicai.tts.VoiceReadiness
import com.sultan.arabicai.ui.components.VoiceDataMissingDialog

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun LessonDetailScreen(lessonId: Long, onStartQuiz: (Long) -> Unit) {
    val container = LocalAppContainer.current
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    var lesson by remember { mutableStateOf<LessonEntity?>(null) }
    var vocabForLesson by remember { mutableStateOf<List<VocabWordEntity>>(emptyList()) }
    var selectedWord by remember { mutableStateOf<VocabWordEntity?>(null) }
    var mode by remember { mutableStateOf(ReadingMode.SENTENCE) }
    var preset by remember { mutableStateOf(DeliveryPreset.NATIVE_PACE) }
    var showVoiceMissingDialog by remember { mutableStateOf(false) }

    val allVocab by container.vocabularyRepository.observeAll().collectAsState(initial = emptyList())

    val engine = remember { container.newArabicTtsEngine(context) }
    val controller = remember { TtsPlaybackController(engine) }
    var engineReady by remember { mutableStateOf(false) }

    LaunchedEffect(lessonId) {
        lesson = container.lessonRepository.getById(lessonId)
    }
    LaunchedEffect(lesson, allVocab) {
        vocabForLesson = allVocab.filter { it.lessonId == lessonId }
    }
    LaunchedEffect(Unit) {
        engine.initialize { success ->
            engineReady = success
            if (success) engine.selectLocale(ArabicTtsEngine.ARABIC_MSA)
        }
    }
    DisposableEffect(Unit) {
        onDispose { engine.shutdown() }
    }
    // Stop playback when the app is backgrounded (onPause/onStop), not just when this
    // composable leaves the composition — otherwise a lesson left playing while the user
    // switches apps keeps synthesizing speech in the background.
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_STOP) controller.stop()
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }
    LaunchedEffect(lesson, mode) {
        lesson?.let { controller.load(it.dialogueAr, mode) }
    }
    LaunchedEffect(preset) {
        controller.applyPreset(preset)
    }

    val currentLesson = lesson ?: return
    val arabicVoiceLabel = stringResource(R.string.voice_language_arabic)

    fun attemptPlay() {
        // Phase 3 TTS-scenario tracing caught this: when there is no TTS engine on the device
        // at all, `engineReady` never becomes true, so the old `if (!engineReady) return` here
        // made Play silently do nothing — exactly the failure mode the voice-missing dialog
        // was built to eliminate, just for a case its trigger condition didn't cover.
        val readiness = if (!engineReady) {
            VoiceReadiness.ENGINE_UNAVAILABLE
        } else {
            VoiceDataManager.readinessFor(engine.isLanguageAvailable(ArabicTtsEngine.ARABIC_MSA))
        }
        if (readiness == VoiceReadiness.READY) {
            controller.play()
        } else {
            showVoiceMissingDialog = true
        }
    }

    LazyColumn(contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp)) {
        item {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text(stringResource(R.string.lesson_unit_number, currentLesson.unitNumber), style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
                Text(currentLesson.titleEn, style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
                Text(currentLesson.titleAr, style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(16.dp)) {
                        Text(stringResource(R.string.lesson_tap_word_hint), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        FlowRow(Modifier.padding(top = 8.dp)) {
                            currentLesson.dialogueAr.split(Regex("\\s+")).forEach { token ->
                                // Trimming only strips non-letters from the token's *edges*;
                                // Arabic tashkeel (diacritics) sitting mid-word survive that and
                                // previously broke matching against unvoweled vocab entries — a
                                // Phase 3 QA re-audit caught that the tashkeel fix claimed in an
                                // earlier pass was never actually applied. stripTashkeel() now
                                // removes diacritics from both sides of the comparison.
                                val clean = token.trim { !it.isLetter() }.stripTashkeel()
                                Text(
                                    text = "$token ",
                                    style = MaterialTheme.typography.headlineMedium,
                                    color = MaterialTheme.colorScheme.onSurface,
                                    modifier = Modifier.padding(2.dp).let { base ->
                                        val match = vocabForLesson.firstOrNull {
                                            val vocabWord = it.arabic.stripTashkeel()
                                            vocabWord.contains(clean) || clean.contains(vocabWord)
                                        }
                                        if (match != null) base.clickable { selectedWord = match } else base
                                    }
                                )
                            }
                        }
                    }
                }

                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(16.dp)) {
                        Text(stringResource(R.string.lesson_speaking_practice), style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)

                        Row(Modifier.padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            ReadingMode.entries.forEach { m ->
                                FilterChip(selected = mode == m, onClick = { mode = m }, label = { Text(stringResource(readingModeLabel(m))) })
                            }
                        }
                        Row(Modifier.padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            DeliveryPreset.entries.forEach { p ->
                                FilterChip(selected = preset == p, onClick = { preset = p }, label = { Text(stringResource(deliveryPresetLabel(p))) })
                            }
                        }

                        var speed by remember { mutableFloatStateOf(1.0f) }
                        Text(stringResource(R.string.lesson_speed_label, "%.1f".format(speed)), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 8.dp))
                        Slider(value = speed, onValueChange = { speed = it; engine.setSpeechRate(it) }, valueRange = 0.4f..1.8f)

                        Row(Modifier.padding(top = 12.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Button(onClick = { attemptPlay() }) { Text(stringResource(R.string.lesson_action_play)) }
                            Button(onClick = { controller.pause() }) { Text(stringResource(R.string.lesson_action_pause)) }
                            Button(onClick = { controller.repeatCurrentChunk() }) { Text(stringResource(R.string.lesson_action_repeat)) }
                        }
                        var loopOn by remember { mutableStateOf(false) }
                        AssistChip(
                            onClick = {
                                loopOn = !loopOn
                                controller.setLoopMode(if (loopOn) TtsPlaybackController.LoopMode.CURRENT_CHUNK else TtsPlaybackController.LoopMode.OFF)
                            },
                            label = { Text(stringResource(if (loopOn) R.string.lesson_loop_on else R.string.lesson_loop_off)) },
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    }
                }

                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(16.dp)) {
                        Text(stringResource(R.string.lesson_grammar_focus), style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
                        Text(currentLesson.grammarFocusEn, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(currentLesson.grammarFocusAr, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }

                Button(onClick = { onStartQuiz(currentLesson.id) }, modifier = Modifier.fillMaxWidth()) {
                    Text(stringResource(R.string.lesson_start_quiz))
                }
            }
        }
    }

    selectedWord?.let { word ->
        AlertDialog(
            onDismissRequest = { selectedWord = null },
            confirmButton = {},
            title = { Text(word.arabic) },
            text = {
                Column {
                    Text(stringResource(R.string.lesson_word_translation, word.english))
                    Text(stringResource(R.string.lesson_word_transliteration, word.transliteration))
                    Text(stringResource(R.string.lesson_word_root, word.rootLetters))
                    Text(stringResource(R.string.lesson_word_part_of_speech, word.partOfSpeech))
                    if (word.synonyms.isNotBlank()) Text(stringResource(R.string.lesson_word_synonyms, word.synonyms))
                    if (word.antonyms.isNotBlank()) Text(stringResource(R.string.lesson_word_antonyms, word.antonyms))
                }
            }
        )
    }

    if (showVoiceMissingDialog) {
        VoiceDataMissingDialog(
            languageLabel = arabicVoiceLabel,
            onDismiss = { showVoiceMissingDialog = false }
        )
    }
}

/**
 * Strips Arabic tashkeel (U+064B–U+0652: fathatan..sukun, covering the harakat, tanwin, and
 * shadda), the superscript alef (U+0670), and tatweel (U+0640) so a fully-voweled dialogue
 * token can match an unvoweled vocabulary entry, and vice versa. Unicode escapes are used
 * explicitly rather than literal diacritic glyphs in source to keep the pattern unambiguous.
 */
private fun String.stripTashkeel(): String = replace(Regex("[\u064B-\u0652\u0670\u0640]"), "")

private fun readingModeLabel(mode: ReadingMode): Int = when (mode) {
    ReadingMode.WORD -> R.string.reading_mode_word
    ReadingMode.SENTENCE -> R.string.reading_mode_sentence
    ReadingMode.PARAGRAPH -> R.string.reading_mode_paragraph
}

private fun deliveryPresetLabel(preset: DeliveryPreset): Int = when (preset) {
    DeliveryPreset.NATIVE_PACE -> R.string.delivery_preset_native_pace
    DeliveryPreset.SLOW_LEARNING -> R.string.delivery_preset_slow_learning
    DeliveryPreset.TEACHER_MODE -> R.string.delivery_preset_teacher_mode
    DeliveryPreset.CHILD_MODE -> R.string.delivery_preset_child_mode
}
