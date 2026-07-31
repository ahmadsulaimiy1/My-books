package com.sultan.arabicai.tts

import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class ReadingMode { WORD, SENTENCE, PARAGRAPH }

enum class PlaybackState { IDLE, SPEAKING, PAUSED, FINISHED }

/** Pedagogical speed/pitch presets requested by the spec ("teacher mode", "child mode", ...). */
enum class DeliveryPreset(val rate: Float, val pitch: Float) {
    NATIVE_PACE(rate = 1.0f, pitch = 1.0f),
    SLOW_LEARNING(rate = 0.6f, pitch = 1.0f),
    TEACHER_MODE(rate = 0.75f, pitch = 0.95f),
    CHILD_MODE(rate = 0.85f, pitch = 1.25f)
}

private val SENTENCE_BOUNDARY = Regex("(?<=[.!?؟،])\\s+")
private val WORD_BOUNDARY = Regex("\\s+")

/**
 * Sits on top of [ArabicTtsEngine] and turns raw text into the practice flows the learner
 * actually wants: read word-by-word, read sentence-by-sentence, loop a single word or
 * sentence for drilling, and pause/resume mid-passage. The Android TTS API only exposes
 * stop() (no true pause), so pause/resume here is implemented by chunking text ourselves and
 * remembering the current chunk index — an honest, working substitute for native pause.
 */
class TtsPlaybackController(private val engine: ArabicTtsEngine) {

    private val _playbackState = MutableStateFlow(PlaybackState.IDLE)
    val playbackState: StateFlow<PlaybackState> = _playbackState.asStateFlow()

    private val _currentChunkIndex = MutableStateFlow(0)
    val currentChunkIndex: StateFlow<Int> = _currentChunkIndex.asStateFlow()

    private var chunks: List<String> = emptyList()
    private var loopMode: LoopMode = LoopMode.OFF

    val currentChunkText: String?
        get() = chunks.getOrNull(_currentChunkIndex.value)

    enum class LoopMode { OFF, CURRENT_CHUNK, WHOLE_PASSAGE }

    init {
        engine.setProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {
                _playbackState.value = PlaybackState.SPEAKING
            }

            override fun onDone(utteranceId: String?) {
                advanceAfterChunk()
            }

            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String?) {
                _playbackState.value = PlaybackState.IDLE
            }
        })
    }

    fun applyPreset(preset: DeliveryPreset) {
        engine.setSpeechRate(preset.rate)
        engine.setPitch(preset.pitch)
    }

    fun load(text: String, mode: ReadingMode) {
        chunks = when (mode) {
            ReadingMode.WORD -> text.split(WORD_BOUNDARY).filter { it.isNotBlank() }
            ReadingMode.SENTENCE -> text.split(SENTENCE_BOUNDARY).filter { it.isNotBlank() }
            ReadingMode.PARAGRAPH -> listOf(text)
        }
        _currentChunkIndex.value = 0
        _playbackState.value = PlaybackState.IDLE
    }

    fun setLoopMode(mode: LoopMode) {
        loopMode = mode
    }

    fun play() {
        val chunk = currentChunkText ?: return
        engine.speakChunk(chunk, utteranceId = "chunk_${_currentChunkIndex.value}", queueMode = TextToSpeech.QUEUE_FLUSH)
    }

    fun pause() {
        engine.stop()
        _playbackState.value = PlaybackState.PAUSED
    }

    fun resume() {
        play()
    }

    fun repeatCurrentChunk() {
        play()
    }

    fun skipToChunk(index: Int) {
        if (index in chunks.indices) {
            _currentChunkIndex.value = index
            play()
        }
    }

    fun stop() {
        engine.stop()
        _currentChunkIndex.value = 0
        _playbackState.value = PlaybackState.IDLE
    }

    private fun advanceAfterChunk() {
        when (loopMode) {
            LoopMode.CURRENT_CHUNK -> {
                play() // re-speak the same word/sentence for drilling
                return
            }
            LoopMode.WHOLE_PASSAGE, LoopMode.OFF -> Unit
        }

        val nextIndex = _currentChunkIndex.value + 1
        if (nextIndex < chunks.size) {
            _currentChunkIndex.value = nextIndex
            play()
        } else if (loopMode == LoopMode.WHOLE_PASSAGE) {
            _currentChunkIndex.value = 0
            play()
        } else {
            _playbackState.value = PlaybackState.FINISHED
        }
    }
}
