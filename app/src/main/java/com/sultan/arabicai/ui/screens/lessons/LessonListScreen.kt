package com.sultan.arabicai.ui.screens.lessons

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.R
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.ui.theme.SultanColors

@Composable
fun LessonListScreen(bookId: Long, onOpenLesson: (Long) -> Unit) {
    val container = LocalAppContainer.current
    val lessons by container.lessonRepository.observeForBook(bookId).collectAsState(initial = emptyList())

    LazyColumn(
        contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text(stringResource(R.string.lessons_title), style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
        }
        items(lessons, key = { it.id }) { lesson ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onOpenLesson(lesson.id) },
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(Modifier.padding(16.dp)) {
                    Text(stringResource(R.string.lesson_unit_number, lesson.unitNumber), style = MaterialTheme.typography.labelMedium, color = SultanColors.RoyalGold)
                    Text(lesson.titleEn, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.onSurface)
                    Text(lesson.titleAr, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(stringResource(R.string.lesson_summary, lesson.estimatedMinutes, lesson.grammarFocusEn), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}
