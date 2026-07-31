package com.sultan.arabicai.ui.screens.dashboard

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.R
import com.sultan.arabicai.data.local.entity.UserStatsEntity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.domain.gamification.RankEngine
import com.sultan.arabicai.ui.components.RankBadge
import com.sultan.arabicai.ui.components.SectionHeading
import com.sultan.arabicai.ui.components.StatCard
import com.sultan.arabicai.ui.components.rankLabelRes
import com.sultan.arabicai.ui.components.rankTierColor
import com.sultan.arabicai.ui.theme.SultanColors

@Composable
fun DashboardScreen() {
    val container = LocalAppContainer.current
    val stats by container.progressRepository.observeStats().collectAsState(initial = null)
    val sessions by container.progressRepository.observeRecentSessions(30).collectAsState(initial = emptyList())

    val resolvedStats = stats ?: UserStatsEntity()
    val progress = RankEngine.progressFor(resolvedStats)

    val weeklyMinutes = sessions.takeLast(7).sumOf { it.minutesStudied }
    val monthlyMinutes = sessions.sumOf { it.minutesStudied }
    val lessonsCompleted = sessions.sumOf { it.lessonsCompleted }
    val wordsReviewed = sessions.sumOf { it.wordsReviewed }
    val avgSpeaking = sessions.map { it.speakingScore }.filter { it > 0 }.let { if (it.isEmpty()) 0 else it.average().toInt() }
    val avgListening = sessions.map { it.listeningScore }.filter { it > 0 }.let { if (it.isEmpty()) 0 else it.average().toInt() }
    val avgGrammar = sessions.map { it.grammarScore }.filter { it > 0 }.let { if (it.isEmpty()) 0 else it.average().toInt() }

    LazyColumn(
        contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        item {
            Text(stringResource(R.string.dashboard_title), style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
            Text(
                stringResource(R.string.dashboard_streak_xp, resolvedStats.currentStreakDays, resolvedStats.totalXp),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        item {
            RankBadge(
                rankLabel = stringResource(rankLabelRes(progress.currentRank)),
                tierColor = rankTierColor(progress.currentRank),
                progress = progress.progressToNext
            )
        }

        item {
            SectionHeading(stringResource(R.string.dashboard_section_this_week))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatCard(stringResource(R.string.dashboard_learning_minutes), stringResource(R.string.dashboard_minutes_value, weeklyMinutes), Modifier.weight(1f))
                StatCard(stringResource(R.string.dashboard_lessons_completed), "$lessonsCompleted", Modifier.weight(1f))
            }
        }

        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatCard(stringResource(R.string.dashboard_vocabulary_reviewed), "$wordsReviewed", Modifier.weight(1f))
                StatCard(stringResource(R.string.dashboard_monthly_minutes), stringResource(R.string.dashboard_minutes_value, monthlyMinutes), Modifier.weight(1f))
            }
        }

        item {
            SectionHeading(stringResource(R.string.dashboard_section_skill_analytics))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatCard(stringResource(R.string.dashboard_speaking_score), stringResource(R.string.dashboard_percent_value, avgSpeaking), Modifier.weight(1f), accent = SultanColors.TierExpert)
                StatCard(stringResource(R.string.dashboard_listening_score), stringResource(R.string.dashboard_percent_value, avgListening), Modifier.weight(1f), accent = SultanColors.TierResearcher)
                StatCard(stringResource(R.string.dashboard_grammar_score), stringResource(R.string.dashboard_percent_value, avgGrammar), Modifier.weight(1f), accent = SultanColors.TierMaster)
            }
        }

        item {
            SectionHeading(stringResource(R.string.dashboard_section_recent_sessions))
        }
        items(sessions.takeLast(10).reversed(), key = { it.id }) { session ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(stringResource(R.string.dashboard_session_day, session.epochDay), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface)
                Text(stringResource(R.string.dashboard_session_summary, session.minutesStudied, session.lessonsCompleted), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}
