package com.sultan.arabicai.ui.screens.certificates

import android.content.Intent
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.collectAsState
import androidx.core.content.FileProvider
import com.sultan.arabicai.R
import com.sultan.arabicai.certificate.CertificateGenerator
import com.sultan.arabicai.data.local.entity.CertificateEntity
import com.sultan.arabicai.data.local.entity.CertificateLevel
import com.sultan.arabicai.di.LocalAppContainer
import java.io.File
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@Composable
fun CertificatesScreen() {
    val container = LocalAppContainer.current
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    val certificates by container.certificateRepository.observeAll().collectAsState(initial = emptyList())
    val defaultRecipient = stringResource(R.string.certificates_default_recipient)
    var recipientName by remember { mutableStateOf(defaultRecipient) }
    var levelMenuOpen by remember { mutableStateOf(false) }
    var selectedLevel by remember { mutableStateOf(CertificateLevel.COURSE_COMPLETION) }
    val shareChooserTitle = stringResource(R.string.certificates_share_chooser_title)

    LazyColumn(
        contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(stringResource(R.string.certificates_title), style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)

            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface), modifier = Modifier.padding(top = 16.dp)) {
                Column(Modifier.padding(16.dp)) {
                    TextField(value = recipientName, onValueChange = { recipientName = it }, label = { Text(stringResource(R.string.certificates_recipient_name)) }, modifier = Modifier.fillMaxWidth())

                    Box {
                        // heightIn(min = 48.dp) + Role.DropdownList: a Phase 3 accessibility
                        // re-audit found this trigger's touch target was well under the 48dp
                        // minimum (only top padding, no enforced height) and carried no
                        // semantic role, unlike the DropdownMenu items it opens.
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .heightIn(min = 48.dp)
                                .clickable(role = Role.DropdownList) { levelMenuOpen = true }
                                .padding(top = 12.dp),
                            contentAlignment = Alignment.CenterStart
                        ) {
                            Text(
                                stringResource(R.string.certificates_level_label, stringResource(certificateLevelLabel(selectedLevel))),
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                        DropdownMenu(expanded = levelMenuOpen, onDismissRequest = { levelMenuOpen = false }) {
                            CertificateLevel.entries.forEach { level ->
                                DropdownMenuItem(text = { Text(stringResource(certificateLevelLabel(level))) }, onClick = { selectedLevel = level; levelMenuOpen = false })
                            }
                        }
                    }

                    Button(
                        onClick = {
                            scope.launch {
                                val (titleEn, titleAr) = CertificateGenerator.levelTitle(selectedLevel)
                                val code = CertificateGenerator.newVerificationCode()
                                val entity = CertificateEntity(
                                    titleAr = titleAr,
                                    titleEn = titleEn,
                                    level = selectedLevel,
                                    recipientName = recipientName.ifBlank { defaultRecipient },
                                    issuedAtEpochMillis = System.currentTimeMillis(),
                                    verificationCode = code,
                                    filePath = ""
                                )
                                val file = withContext(Dispatchers.IO) { CertificateGenerator.generate(context, entity) }
                                container.certificateRepository.save(entity.copy(filePath = file.absolutePath))
                            }
                        },
                        modifier = Modifier.fillMaxWidth().padding(top = 16.dp)
                    ) {
                        Text(stringResource(R.string.certificates_issue))
                    }
                }
            }
        }

        items(certificates, key = { it.id }) { certificate ->
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                Column(Modifier.padding(16.dp)) {
                    Text(certificate.titleEn, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
                    Text(certificate.recipientName, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(stringResource(R.string.certificates_verification, certificate.verificationCode), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Button(
                        onClick = {
                            val file = File(certificate.filePath)
                            if (file.exists()) {
                                val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)
                                val intent = Intent(Intent.ACTION_SEND).apply {
                                    type = "application/pdf"
                                    putExtra(Intent.EXTRA_STREAM, uri)
                                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                                }
                                context.startActivity(Intent.createChooser(intent, shareChooserTitle))
                            }
                        },
                        modifier = Modifier.padding(top = 8.dp)
                    ) {
                        Text(stringResource(R.string.certificates_share))
                    }
                }
            }
        }
    }
}

private fun certificateLevelLabel(level: CertificateLevel): Int = when (level) {
    CertificateLevel.COURSE_COMPLETION -> R.string.certificate_level_course_completion
    CertificateLevel.EXCELLENCE -> R.string.certificate_level_excellence
    CertificateLevel.DISTINCTION -> R.string.certificate_level_distinction
    CertificateLevel.HONOUR -> R.string.certificate_level_honour
    CertificateLevel.GRAND_HONOUR -> R.string.certificate_level_grand_honour
}
