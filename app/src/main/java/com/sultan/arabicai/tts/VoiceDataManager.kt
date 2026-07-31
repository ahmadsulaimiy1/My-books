package com.sultan.arabicai.tts

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.speech.tts.TextToSpeech

/** Whether a given language's voice data is actually usable right now. */
enum class VoiceReadiness { READY, MISSING_DATA, ENGINE_UNAVAILABLE, UNKNOWN }

data class VoiceCheckResult(
    val arabicReadiness: VoiceReadiness,
    val englishReadiness: VoiceReadiness,
    val availableLocales: List<String> = emptyList(),
    val unavailableLocales: List<String> = emptyList()
)

/**
 * Wraps the platform contracts for detecting and recovering from missing TTS voice data
 * (`ACTION_CHECK_TTS_DATA` / `ACTION_INSTALL_TTS_DATA` / `ACTION_TTS_SETTINGS`) so a missing
 * Arabic or English voice becomes a visible, recoverable UI state instead of a silent no-op —
 * see [com.sultan.arabicai.ui.components.VoiceDataMissingDialog] for where this surfaces.
 *
 * Deliberately scoped to fixing that one defect: this is NOT a settings screen, does not manage
 * downloadable audio packs, and does not implement a multi-persona voice architecture (Saudi /
 * Teacher / Child / Qur'anic voices). Those are new-feature work explicitly out of scope for a
 * stabilization pass — see docs/ROADMAP.md for where they're tracked as future phases.
 */
object VoiceDataManager {

    // The Android SDK has no TextToSpeech.Engine.ACTION_TTS_SETTINGS constant (unlike
    // ACTION_CHECK_TTS_DATA/ACTION_INSTALL_TTS_DATA, which are real Engine constants) — this is
    // the actual, long-stable action string apps use to open the system TTS settings screen.
    private const val ACTION_TTS_SETTINGS = "com.android.settings.TTS_SETTINGS"

    fun checkTtsDataIntent(): Intent = Intent(TextToSpeech.Engine.ACTION_CHECK_TTS_DATA)

    fun installTtsDataIntent(): Intent = Intent(TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA)

    fun ttsSettingsIntent(): Intent = Intent(ACTION_TTS_SETTINGS)

    /** Maps a raw [TextToSpeech.isLanguageAvailable] result to a UI-friendly readiness state. */
    fun readinessFor(languageAvailability: Int): VoiceReadiness = when (languageAvailability) {
        TextToSpeech.LANG_AVAILABLE,
        TextToSpeech.LANG_COUNTRY_AVAILABLE,
        TextToSpeech.LANG_COUNTRY_VAR_AVAILABLE -> VoiceReadiness.READY
        TextToSpeech.LANG_MISSING_DATA -> VoiceReadiness.MISSING_DATA
        TextToSpeech.LANG_NOT_SUPPORTED -> VoiceReadiness.ENGINE_UNAVAILABLE
        else -> VoiceReadiness.UNKNOWN
    }

    /** Parses the result Intent from launching [checkTtsDataIntent] via startActivityForResult. */
    fun parseCheckResult(data: Intent?): VoiceCheckResult {
        val available = data?.getStringArrayListExtra(TextToSpeech.Engine.EXTRA_AVAILABLE_VOICES) ?: arrayListOf()
        val unavailable = data?.getStringArrayListExtra(TextToSpeech.Engine.EXTRA_UNAVAILABLE_VOICES) ?: arrayListOf()
        val arabicReady = available.any { it.startsWith("ar", ignoreCase = true) }
        val englishReady = available.any { it.startsWith("eng", ignoreCase = true) || it.startsWith("en-", ignoreCase = true) }
        return VoiceCheckResult(
            arabicReadiness = if (arabicReady) VoiceReadiness.READY else VoiceReadiness.MISSING_DATA,
            englishReadiness = if (englishReady) VoiceReadiness.READY else VoiceReadiness.MISSING_DATA,
            availableLocales = available,
            unavailableLocales = unavailable
        )
    }

    /** @return true if an activity existed to handle the request. */
    fun launchInstallTtsData(context: Context): Boolean = launchSafely(context, installTtsDataIntent())

    /** @return true if an activity existed to handle the request. */
    fun launchTtsSettings(context: Context): Boolean = launchSafely(context, ttsSettingsIntent())

    private fun launchSafely(context: Context, intent: Intent): Boolean {
        if (context !is Activity) intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        return try {
            context.startActivity(intent)
            true
        } catch (e: ActivityNotFoundException) {
            // No TTS engine/settings UI installed at all (rare, but real on some AOSP-derived
            // devices) — the caller is expected to fall back to an in-dialog explanation.
            false
        }
    }
}
