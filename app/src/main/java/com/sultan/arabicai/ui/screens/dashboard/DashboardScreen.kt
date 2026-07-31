package com.sultan.arabicai.ui.screens.dashboard

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.data.local.entity.ScholarRank
import com.sultan.arabicai.data.local.entity.UserStatsEntity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.domain.gamification.RankEngine
import com.sultan.arabicai.ui.components.RankBadge
import com.sultan.arabicai.ui.components.SectionHeading
import com.sultan.arabicai.ui.components.StatCard
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
            Text("Executive Overview", style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
            Text(
                "${resolvedStats.currentStreakDays}-day streak · ${resolvedStats.totalXp} XP",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        item {
            RankBadge(
                rankLabel = progress.currentRank.displayName(),
                tierColor = tierColorFor(progress.currentRank),
                progress = progress.progressToNext
            )
        }

        item {
            SectionHeading("This Week")
            val minutesLabel = "$weeklyMinutes min"
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatCard("Learning Minutes", minutesLabel, Modifier.weight(1f))
                StatCard("Lessons Completed", "$lessonsCompleted", Modifier.weight(1f))
            }
        }

        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatCard("Vocabulary Reviewed", "$wordsReviewed", Modifier.weight(1f))
                StatCard("Monthly Minutes", "$monthlyMinutes min", Modifier.weight(1f))
            }
        }

        item {
            SectionHeading("Skill Analytics", Modifier)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatCard("Speaking", "$avgSpeaking%", Modifier.weight(1f), accent = SultanColors.TierExpert)
                StatCard("Listening", "$avgListening%", Modifier.weight(1f), accent = SultanColors.TierResearcher)
                StatCard("Grammar", "$avgGrammar%", Modifier.weight(1f), accent = SultanColors.TierMaster)
            }
        }

        item {
            SectionHeading("Recent Sessions")
        }
        items(sessions.takeLast(10).reversed()) { session ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Day ${session.epochDay}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface)
                Text("${session.minutesStudied} min · ${session.lessonsCompleted} lessons", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

private fun ScholarRank.displayName(): String = name.split("_").joinToString(" ") { it.lowercase().replaceFirstChar(Char::uppercase) }

private fun tierColorFor(rank: ScholarRank) = when (rank) {
    ScholarRank.BEGINNER -> SultanColors.TierBeginner
    ScholarRank.STUDENT -> SultanColors.TierStudent
    ScholarRank.SCHOLAR -> SultanColors.TierScholar
    ScholarRank.RESEARCHER -> SultanColors.TierResearcher
    ScholarRank.EXPERT -> SultanColors.TierExpert
    ScholarRank.MASTER -> SultanColors.TierMaster
    ScholarRank.AMBASSADOR -> SultanColors.TierAmbassador
    ScholarRank.ELITE_SCHOLAR -> SultanColors.TierEliteScholar
    ScholarRank.GRAND_SCHOLAR -> SultanColors.TierGrandScholar
}
