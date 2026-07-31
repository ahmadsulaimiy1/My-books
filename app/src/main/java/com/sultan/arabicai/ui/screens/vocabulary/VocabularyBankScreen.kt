package com.sultan.arabicai.ui.screens.vocabulary

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.Flag
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.data.local.entity.VocabWordEntity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.ui.theme.SultanColors
import kotlinx.coroutines.launch

@Composable
fun VocabularyBankScreen(onOpenFlashcards: () -> Unit) {
    val container = LocalAppContainer.current
    val scope = rememberCoroutineScope()
    val words by container.vocabularyRepository.observeAll().collectAsState(initial = emptyList())

    LazyColumn(
        contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text("Vocabulary Bank", style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
            Text("${words.size} words · spaced repetition powered", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Button(onClick = onOpenFlashcards, modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
                Text("Review Due Flashcards")
            }
        }

        items(words, key = { it.id }) { word ->
            VocabRow(
                word = word,
                onToggleFavorite = { scope.launch { container.vocabularyRepository.toggleFavorite(word) } },
                onToggleDifficult = { scope.launch { container.vocabularyRepository.toggleDifficult(word) } }
            )
        }
    }
}

@Composable
private fun VocabRow(word: VocabWordEntity, onToggleFavorite: () -> Unit, onToggleDifficult: () -> Unit) {
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Row(Modifier.padding(16.dp).fillMaxWidth()) {
            Column(Modifier.weight(1f)) {
                Text(word.arabic, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onSurface)
                Text("${word.transliteration} · ${word.english}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text("Root: ${word.rootLetters}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            IconButton(onClick = onToggleFavorite) {
                Icon(
                    if (word.isFavorite) Icons.Filled.Favorite else Icons.Filled.FavoriteBorder,
                    contentDescription = "Favourite",
                    tint = SultanColors.RoyalGold
                )
            }
            IconButton(onClick = onToggleDifficult) {
                Icon(
                    Icons.Filled.Flag,
                    contentDescription = "Mark difficult",
                    tint = if (word.isMarkedDifficult) SultanColors.Error else SultanColors.Silver
                )
            }
        }
    }
}
