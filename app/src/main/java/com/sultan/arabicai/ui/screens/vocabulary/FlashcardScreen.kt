package com.sultan.arabicai.ui.screens.vocabulary

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.data.local.entity.VocabWordEntity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.domain.gamification.RankEngine
import com.sultan.arabicai.domain.srs.RecallQuality
import kotlinx.coroutines.launch

@Composable
fun FlashcardScreen(onFinished: () -> Unit) {
    val container = LocalAppContainer.current
    val scope = rememberCoroutineScope()

    var queue by remember { mutableStateOf<List<VocabWordEntity>>(emptyList()) }
    var index by remember { mutableIntStateOf(0) }
    var revealed by remember { mutableStateOf(false) }
    var reviewedCount by remember { mutableIntStateOf(0) }

    LaunchedEffect(Unit) {
        queue = container.vocabularyRepository.dueForReview()
    }

    Column(Modifier.fillMaxSize().padding(20.dp), verticalArrangement = Arrangement.Center) {
        Text("Flashcards", style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
        Text("$reviewedCount reviewed · ${(queue.size - index).coerceAtLeast(0)} remaining", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

        val current = queue.getOrNull(index)
        if (current == null) {
            Text(
                "No cards due right now — check back later or study a fresh lesson.",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 40.dp)
            )
            Button(onClick = onFinished, modifier = Modifier.padding(top = 24.dp)) { Text("Done") }
            return@Column
        }

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .height(320.dp)
                .padding(top = 32.dp)
                .clickable { revealed = !revealed },
            shape = RoundedCornerShape(28.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(current.arabic, style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onSurface)
                    if (revealed) {
                        Text(current.transliteration, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 12.dp))
                        Text(current.english, style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.primary)
                        Text("Root: ${current.rootLetters}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    } else {
                        Text("Tap to reveal", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 12.dp))
                    }
                }
            }
        }

        if (revealed) {
            Text("How well did you recall this?", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 20.dp))
            Row {
                GradeButton("Again", RecallQuality.INCORRECT_FAMILIAR) { grade ->
                    scope.launch {
                        container.vocabularyRepository.submitReview(current, grade)
                        container.progressRepository.awardXp(RankEngine.Xp.VOCAB_WORD_MASTERED / 4)
                        reviewedCount++; index++; revealed = false
                    }
                }
                GradeButton("Hard", RecallQuality.CORRECT_DIFFICULT) { grade ->
                    scope.launch {
                        container.vocabularyRepository.submitReview(current, grade)
                        container.progressRepository.awardXp(RankEngine.Xp.VOCAB_WORD_MASTERED / 2)
                        reviewedCount++; index++; revealed = false
                    }
                }
                GradeButton("Good", RecallQuality.CORRECT_HESITANT) { grade ->
                    scope.launch {
                        container.vocabularyRepository.submitReview(current, grade)
                        container.progressRepository.awardXp(RankEngine.Xp.VOCAB_WORD_MASTERED)
                        reviewedCount++; index++; revealed = false
                    }
                }
                GradeButton("Easy", RecallQuality.CORRECT_PERFECT) { grade ->
                    scope.launch {
                        container.vocabularyRepository.submitReview(current, grade)
                        container.progressRepository.awardXp(RankEngine.Xp.VOCAB_WORD_MASTERED)
                        reviewedCount++; index++; revealed = false
                    }
                }
            }
        }
    }
}

@Composable
private fun GradeButton(label: String, quality: RecallQuality, onClick: (RecallQuality) -> Unit) {
    Button(onClick = { onClick(quality) }, modifier = Modifier.padding(4.dp)) {
        Text(label)
    }
}
