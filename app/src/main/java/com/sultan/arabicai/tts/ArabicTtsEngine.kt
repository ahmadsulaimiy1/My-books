package com.sultan.arabicai.tts

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.speech.tts.Voice
import java.util.Locale
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class TtsEngineState { UNINITIALIZED, READY, UNAVAILABLE }

data class VoiceProfile(
    val id: String,
    val displayName: String,
    val locale: Locale,
    val isNetworkRequired: Boolean
)

/**
 * Thin, honest wrapper around Android's on-device [TextToSpeech] engine.
 *
 * This delivers genuinely offline Arabic + English speech synthesis using whatever voice
 * data the user has installed on-device (Settings → System → Languages → Text-to-speech →
 * install Arabic voice data once; no network needed after that). What it does NOT claim to
 * do: dialect-accurate Hijazi/Najdi voice modelling, Tajweed-rule-aware phoneme shaping, or
 * accent/mispronunciation scoring — those require a purpose-built neural TTS/ASR model
 * bundled on-device (see docs/ROADMAP.md, Phase 3) and are out of scope for the stock system
 * TTS this class wraps.
 */
class ArabicTtsEngine(private val context: Context) {

    private var tts: TextToSpeech? = null
    private var pendingProgressListener: UtteranceProgressListener? = null

    private val _engineState = MutableStateFlow(TtsEngineState.UNINITIALIZED)
    val engineState: StateFlow<TtsEngineState> = _engineState.asStateFlow()

    fun initialize(onReady: (Boolean) -> Unit) {
        tts = TextToSpeech(context) { status ->
            val ok = status == TextToSpeech.SUCCESS
            _engineState.value = if (ok) TtsEngineState.READY else TtsEngineState.UNAVAILABLE
            // The underlying TextToSpeech instance is only just becoming usable here, so a
            // listener registered earlier via setProgressListener() (before this callback
            // fired) needs to be (re-)attached now, not lost.
            if (ok) pendingProgressListener?.let { tts?.setOnUtteranceProgressListener(it) }
            onReady(ok)
        }
    }

    /** Returns true if the requested locale can be synthesized without any network access. */
    fun selectLocale(locale: Locale): Boolean {
        val engine = tts ?: return false
        val result = engine.setLanguage(locale)
        return result == TextToSpeech.LANG_AVAILABLE ||
            result == TextToSpeech.LANG_COUNTRY_AVAILABLE ||
            result == TextToSpeech.LANG_COUNTRY_VAR_AVAILABLE
    }

    /**
     * Non-mutating check for whether [locale]'s voice data is actually installed — unlike
     * [selectLocale], this never changes the engine's active language, so it's safe to call
     * before every playback action to decide whether to show [VoiceDataManager]'s recovery UI
     * instead of silently attempting (and possibly failing) speech synthesis.
     */
    fun isLanguageAvailable(locale: Locale): Int =
        tts?.isLanguageAvailable(locale) ?: TextToSpeech.LANG_NOT_SUPPORTED

    /** Human-readable labels of every TTS engine installed on the device (e.g. "Google Speech Services"). */
    fun installedEngineLabels(): List<String> =
        tts?.engines?.map { it.label } ?: emptyList()

    /** The label of whichever engine is currently active, if resolvable. */
    fun currentEngineLabel(): String? {
        val engine = tts ?: return null
        val defaultPackage = engine.defaultEngine ?: return null
        return engine.engines?.firstOrNull { it.name == defaultPackage }?.label ?: defaultPackage
    }

    fun availableVoicesFor(languageTag: String): List<VoiceProfile> {
        val voices: Set<Voice> = tts?.voices ?: emptySet()
        return voices
            .filter { it.locale.language == languageTag }
            .map { voice ->
                VoiceProfile(
                    id = voice.name,
                    displayName = voice.name,
                    locale = voice.locale,
                    isNetworkRequired = voice.isNetworkConnectionRequired
                )
            }
            .sortedBy { it.isNetworkRequired } // offline-capable voices surface first
    }

    fun setVoice(profile: VoiceProfile) {
        val engine = tts ?: return
        engine.voices?.firstOrNull { it.name == profile.id }?.let { engine.voice = it }
    }

    fun setSpeechRate(rate: Float) {
        tts?.setSpeechRate(rate.coerceIn(0.3f, 2.5f))
    }

    fun setPitch(pitch: Float) {
        tts?.setPitch(pitch.coerceIn(0.5f, 2.0f))
    }

    fun speakChunk(text: String, utteranceId: String, queueMode: Int = TextToSpeech.QUEUE_ADD) {
        tts?.speak(text, queueMode, null, utteranceId)
    }

    fun setProgressListener(listener: UtteranceProgressListener) {
        pendingProgressListener = listener
        tts?.setOnUtteranceProgressListener(listener)
    }

    fun stop() {
        tts?.stop()
    }

    fun shutdown() {
        tts?.shutdown()
        tts = null
        _engineState.value = TtsEngineState.UNINITIALIZED
    }

    companion object {
        val ARABIC_MSA: Locale = Locale.forLanguageTag("ar")
        val ARABIC_SAUDI: Locale = Locale.forLanguageTag("ar-SA")
        val ENGLISH_US: Locale = Locale.US
        val ENGLISH_UK: Locale = Locale.UK
    }
}
