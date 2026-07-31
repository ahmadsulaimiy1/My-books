package com.sultan.arabicai.ui.screens.speaking

import android.Manifest
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.media.MediaRecorder
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.sultan.arabicai.data.local.entity.VocabWordEntity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.domain.gamification.RankEngine
import com.sultan.arabicai.tts.ArabicTtsEngine
import com.sultan.arabicai.ui.theme.SultanColors
import java.io.File
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.launch

/**
 * A real recording/playback studio: on-device mic capture via [MediaRecorder], native-voice
 * comparison via the offline TTS engine, and local playback via [MediaPlayer]. Studio-grade DSP
 * (noise reduction, voice isolation, broadcast-quality normalisation) and automated
 * pronunciation scoring are NOT implemented here — those require dedicated audio-ML models and
 * are tracked as Phase 3 in docs/ROADMAP.md. This screen gives the learner a genuine
 * record-compare-repeat loop today.
 */
@Composable
fun SpeakingLabScreen() {
    val container = LocalAppContainer.current
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    val words by container.vocabularyRepository.observeAll().collectAsState(initial = emptyList())
    var selectedWord by remember { mutableStateOf<VocabWordEntity?>(null) }
    var hasMicPermission by remember {
        mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED)
    }
    val permissionLauncher = androidx.activity.compose.rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        hasMicPermission = granted
    }

    val engine = remember { container.newArabicTtsEngine(context) }
    var engineReady by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) {
        engine.initialize { success ->
            engineReady = success
            if (success) engine.selectLocale(ArabicTtsEngine.ARABIC_MSA)
        }
    }
    DisposableEffect(Unit) { onDispose { engine.shutdown() } }

    var isRecording by remember { mutableStateOf(false) }
    var hasRecording by remember { mutableStateOf(false) }
    var recorder by remember { mutableStateOf<MediaRecorder?>(null) }
    var player by remember { mutableStateOf<MediaPlayer?>(null) }
    val outputFile = remember { File(context.cacheDir, "speaking_lab_take.3gp") }

    DisposableEffect(Unit) {
        onDispose {
            recorder?.release()
            player?.release()
        }
    }

    Column(Modifier.fillMaxSize().padding(20.dp)) {
        Text("Speaking Lab", style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
        Text("Record, compare against the native voice, repeat.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

        LazyRow(Modifier.padding(top = 16.dp)) {
            items(words) { word ->
                FilterChip(
                    selected = selectedWord?.id == word.id,
                    onClick = { selectedWord = word },
                    label = { Text(word.arabic) },
                    modifier = Modifier.padding(end = 8.dp)
                )
            }
        }

        val word = selectedWord
        if (word != null) {
            Card(
                modifier = Modifier.fillMaxWidth().padding(top = 20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(Modifier.padding(20.dp)) {
                    Text(word.arabic, style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onSurface)
                    Text("${word.transliteration} · ${word.english}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

                    Row(Modifier.padding(top = 20.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Button(onClick = { if (engineReady) engine.speakChunk(word.arabic, "native_${word.id}") }) {
                            Text("Hear Native Voice")
                        }
                    }

                    Row(Modifier.padding(top = 12.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        if (!hasMicPermission) {
                            Button(onClick = { permissionLauncher.launch(Manifest.permission.RECORD_AUDIO) }) {
                                Text("Grant Microphone Access")
                            }
                        } else {
                            Button(
                                onClick = {
                                    if (!isRecording) {
                                        recorder = MediaRecorder().apply {
                                            setAudioSource(MediaRecorder.AudioSource.MIC)
                                            setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
                                            setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB)
                                            setOutputFile(outputFile.absolutePath)
                                            prepare()
                                            start()
                                        }
                                        isRecording = true
                                    } else {
                                        // stop() throws if the take was too short to produce a
                                        // valid recording — treat that as "nothing captured"
                                        // rather than crashing the screen.
                                        val captured = runCatching { recorder?.apply { stop() } }.isSuccess
                                        recorder?.release()
                                        recorder = null
                                        isRecording = false
                                        hasRecording = captured
                                    }
                                },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (isRecording) SultanColors.Error else SultanColors.RoyalGold,
                                    contentColor = SultanColors.RoyalNavyDeep
                                )
                            ) {
                                Text(if (isRecording) "Stop Recording" else "Record My Voice")
                            }

                            if (hasRecording && !isRecording) {
                                Button(onClick = {
                                    player?.release()
                                    player = MediaPlayer().apply {
                                        setDataSource(outputFile.absolutePath)
                                        prepare()
                                        start()
                                    }
                                    scope.launch {
                                        container.progressRepository.awardXp(RankEngine.Xp.SPEAKING_SESSION_COMPLETED)
                                        // speakingScore here is a practice-completion signal (no
                                        // automated pronunciation scoring exists yet — see
                                        // docs/ROADMAP.md Phase 3), not a measured accuracy grade.
                                        container.progressRepository.recordSession(
                                            epochDay = TimeUnit.MILLISECONDS.toDays(System.currentTimeMillis()),
                                            speakingScore = 80
                                        )
                                    }
                                }) {
                                    Text("Play My Recording")
                                }
                            }
                        }
                    }
                }
            }
        } else {
            Text(
                "Select a word above to begin a practice session.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 24.dp)
            )
        }
    }
}
