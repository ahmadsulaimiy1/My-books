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
import androidx.compose.foundation.lazy.item
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
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.data.local.entity.LessonEntity
import com.sultan.arabicai.data.local.entity.VocabWordEntity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.tts.ArabicTtsEngine
import com.sultan.arabicai.tts.DeliveryPreset
import com.sultan.arabicai.tts.ReadingMode
import com.sultan.arabicai.tts.TtsPlaybackController

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun LessonDetailScreen(lessonId: Long, onStartQuiz: (Long) -> Unit) {
    val container = LocalAppContainer.current
    val context = LocalContext.current

    var lesson by remember { mutableStateOf<LessonEntity?>(null) }
    var vocabForLesson by remember { mutableStateOf<List<VocabWordEntity>>(emptyList()) }
    var selectedWord by remember { mutableStateOf<VocabWordEntity?>(null) }
    var mode by remember { mutableStateOf(ReadingMode.SENTENCE) }
    var preset by remember { mutableStateOf(DeliveryPreset.NATIVE_PACE) }

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
    LaunchedEffect(lesson, mode) {
        lesson?.let { controller.load(it.dialogueAr, mode) }
    }
    LaunchedEffect(preset) {
        controller.applyPreset(preset)
    }

    val currentLesson = lesson ?: return

    LazyColumn(contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp)) {
        item {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text("Unit ${currentLesson.unitNumber}", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
                Text(currentLesson.titleEn, style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
                Text(currentLesson.titleAr, style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Tap any word for translation, root & grammar", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        FlowRow(Modifier.padding(top = 8.dp)) {
                            currentLesson.dialogueAr.split(Regex("\\s+")).forEach { token ->
                                val clean = token.trim { !it.isLetter() }
                                Text(
                                    text = "$token ",
                                    style = MaterialTheme.typography.headlineMedium,
                                    color = MaterialTheme.colorScheme.onSurface,
                                    modifier = Modifier.padding(2.dp).let { base ->
                                        val match = vocabForLesson.firstOrNull { it.arabic.contains(clean) || clean.contains(it.arabic) }
                                        if (match != null) base.clickable { selectedWord = match } else base
                                    }
                                )
                            }
                        }
                    }
                }

                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Speaking Practice", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)

                        Row(Modifier.padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            ReadingMode.entries.forEach { m ->
                                FilterChip(selected = mode == m, onClick = { mode = m }, label = { Text(m.name.lowercase().replaceFirstChar { it.uppercase() }) })
                            }
                        }
                        Row(Modifier.padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            DeliveryPreset.entries.forEach { p ->
                                FilterChip(selected = preset == p, onClick = { preset = p }, label = { Text(p.name.replace("_", " ").lowercase().replaceFirstChar { it.uppercase() }) })
                            }
                        }

                        var speed by remember { mutableFloatStateOf(1.0f) }
                        Text("Speed: ${"%.1f".format(speed)}x", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 8.dp))
                        Slider(value = speed, onValueChange = { speed = it; engine.setSpeechRate(it) }, valueRange = 0.4f..1.8f)

                        Row(Modifier.padding(top = 12.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Button(onClick = { if (engineReady) controller.play() }) { Text("Play") }
                            Button(onClick = { controller.pause() }) { Text("Pause") }
                            Button(onClick = { controller.repeatCurrentChunk() }) { Text("Repeat") }
                        }
                        var loopOn by remember { mutableStateOf(false) }
                        AssistChip(
                            onClick = {
                                loopOn = !loopOn
                                controller.setLoopMode(if (loopOn) TtsPlaybackController.LoopMode.CURRENT_CHUNK else TtsPlaybackController.LoopMode.OFF)
                            },
                            label = { Text(if (loopOn) "Loop: On" else "Loop: Off") },
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    }
                }

                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Grammar Focus", style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
                        Text(currentLesson.grammarFocusEn, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(currentLesson.grammarFocusAr, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }

                Button(onClick = { onStartQuiz(currentLesson.id) }, modifier = Modifier.fillMaxWidth()) {
                    Text("Start Quiz for This Lesson")
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
                    Text("Translation: ${word.english}")
                    Text("Transliteration: ${word.transliteration}")
                    Text("Root: ${word.rootLetters}")
                    Text("Part of speech: ${word.partOfSpeech}")
                    if (word.synonyms.isNotBlank()) Text("Synonyms: ${word.synonyms}")
                    if (word.antonyms.isNotBlank()) Text("Antonyms: ${word.antonyms}")
                }
            }
        )
    }
}
