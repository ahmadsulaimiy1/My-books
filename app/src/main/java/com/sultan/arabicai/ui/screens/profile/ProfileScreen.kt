package com.sultan.arabicai.ui.screens.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.R
import com.sultan.arabicai.data.local.entity.UserStatsEntity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.domain.gamification.RankEngine
import com.sultan.arabicai.security.SecurePreferences
import com.sultan.arabicai.ui.components.RankBadge
import com.sultan.arabicai.ui.components.SectionHeading
import com.sultan.arabicai.ui.components.rankLabelRes
import com.sultan.arabicai.ui.components.rankTierColor

@Composable
fun ProfileScreen(onOpenCertificates: () -> Unit) {
    val container = LocalAppContainer.current
    val context = LocalContext.current

    val stats by container.progressRepository.observeStats().collectAsState(initial = null)
    val achievements by container.progressRepository.observeAchievements().collectAsState(initial = emptyList())
    val resolvedStats = stats ?: UserStatsEntity()
    val progress = RankEngine.progressFor(resolvedStats)

    var biometricEnabled by remember { mutableStateOf(SecurePreferences.isBiometricEnabled(context)) }

    LazyColumn(
        contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(stringResource(R.string.profile_title), style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
            RankBadge(
                rankLabel = stringResource(rankLabelRes(progress.currentRank)),
                tierColor = rankTierColor(progress.currentRank),
                progress = progress.progressToNext,
                modifier = Modifier.padding(top = 12.dp)
            )
            Text(
                stringResource(R.string.profile_xp_streak, resolvedStats.totalXp, resolvedStats.currentStreakDays, resolvedStats.longestStreakDays),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 8.dp)
            )
        }

        item {
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                Row(Modifier.fillMaxWidth().padding(16.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column {
                        Text(stringResource(R.string.profile_biometric_lock_title), style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
                        Text(stringResource(R.string.profile_biometric_lock_subtitle), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Switch(checked = biometricEnabled, onCheckedChange = {
                        biometricEnabled = it
                        SecurePreferences.setBiometricEnabled(context, it)
                    })
                }
            }
        }

        item {
            Button(onClick = onOpenCertificates, modifier = Modifier.fillMaxWidth()) {
                Text(stringResource(R.string.profile_view_certificates))
            }
        }

        item { SectionHeading(stringResource(R.string.profile_achievements)) }

        items(achievements, key = { it.key }) { achievement ->
            val unlocked = achievement.unlockedAtEpochMillis != null
            Card(colors = CardDefaults.cardColors(containerColor = if (unlocked) MaterialTheme.colorScheme.surface else MaterialTheme.colorScheme.surfaceVariant)) {
                Column(Modifier.padding(16.dp)) {
                    Text(achievement.titleEn, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
                    Text(achievement.descriptionEn, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(
                        stringResource(if (unlocked) R.string.profile_achievement_unlocked else R.string.profile_achievement_locked),
                        style = MaterialTheme.typography.labelMedium,
                        color = if (unlocked) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}
