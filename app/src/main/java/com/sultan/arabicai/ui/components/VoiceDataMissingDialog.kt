package com.sultan.arabicai.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.R
import com.sultan.arabicai.tts.VoiceDataManager

/**
 * The recovery UI for the Phase 2 audit's "TTS may silently fail" finding: shown instead of
 * attempting playback whenever [com.sultan.arabicai.tts.ArabicTtsEngine.isLanguageAvailable]
 * reports the requested language isn't actually installed. No Play button should ever appear to
 * do nothing — this is what fires instead.
 */
@Composable
fun VoiceDataMissingDialog(
    languageLabel: String,
    onDismiss: () -> Unit
) {
    val context = LocalContext.current
    var showDetails by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.voice_missing_title)) },
        text = {
            Column {
                Text(stringResource(R.string.voice_missing_message, languageLabel))
                if (showDetails) {
                    Text(
                        stringResource(R.string.voice_missing_details),
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(top = 12.dp)
                    )
                }
                TextButton(onClick = { showDetails = !showDetails }) {
                    Text(
                        stringResource(
                            if (showDetails) R.string.voice_missing_action_hide_details
                            else R.string.voice_missing_action_learn_more
                        )
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = {
                VoiceDataManager.launchInstallTtsData(context)
                onDismiss()
            }) {
                Text(stringResource(R.string.voice_missing_action_download))
            }
        },
        dismissButton = {
            TextButton(onClick = {
                VoiceDataManager.launchTtsSettings(context)
                onDismiss()
            }) {
                Text(stringResource(R.string.voice_missing_action_settings))
            }
        }
    )
}
