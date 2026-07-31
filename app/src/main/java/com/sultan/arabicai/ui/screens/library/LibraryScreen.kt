package com.sultan.arabicai.ui.screens.library

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.R
import com.sultan.arabicai.data.local.entity.BookEntity
import com.sultan.arabicai.data.local.entity.ProficiencyLevel
import com.sultan.arabicai.di.LocalAppContainer

@Composable
fun LibraryScreen(
    onOpenReader: (Long) -> Unit,
    onOpenLessons: (Long) -> Unit
) {
    val container = LocalAppContainer.current
    val books by container.libraryRepository.observeBooks().collectAsState(initial = emptyList())

    LazyColumn(
        contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(stringResource(R.string.library_title), style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
            Text(
                stringResource(R.string.library_subtitle),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        items(books, key = { it.id }) { book ->
            BookCard(book, onOpenReader = { onOpenReader(book.id) }, onOpenLessons = { onOpenLessons(book.id) })
        }
    }
}

@Composable
private fun BookCard(book: BookEntity, onOpenReader: () -> Unit, onOpenLessons: () -> Unit) {
    val coverColor = runCatching { Color(android.graphics.Color.parseColor(book.coverColorHex)) }.getOrDefault(MaterialTheme.colorScheme.primary)

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            androidx.compose.foundation.layout.Box(
                Modifier
                    .size(56.dp, 76.dp)
                    .background(coverColor, RoundedCornerShape(8.dp))
            )
            Column(Modifier.padding(start = 16.dp).weight(1f)) {
                Text(book.titleEn, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
                Text(book.titleAr, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text(stringResource(R.string.library_book_byline, book.author, stringResource(proficiencyLevelLabel(book.level))), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)

                Row(Modifier.padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    // Real buttons rather than clickable Text: guaranteed touch target size,
                    // Role.Button semantics, and focus/pressed-state styling for screen-reader
                    // and D-pad/keyboard navigation.
                    TextButton(onClick = onOpenReader) { Text(stringResource(R.string.library_action_read)) }
                    TextButton(onClick = onOpenLessons) { Text(stringResource(R.string.library_action_lessons)) }
                }
            }
        }
    }
}

private fun proficiencyLevelLabel(level: ProficiencyLevel): Int = when (level) {
    ProficiencyLevel.BEGINNER -> R.string.proficiency_level_beginner
    ProficiencyLevel.INTERMEDIATE -> R.string.proficiency_level_intermediate
    ProficiencyLevel.ADVANCED -> R.string.proficiency_level_advanced
    ProficiencyLevel.SCHOLAR -> R.string.proficiency_level_scholar
}
