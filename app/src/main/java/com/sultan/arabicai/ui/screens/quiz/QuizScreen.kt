package com.sultan.arabicai.ui.screens.quiz

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.R
import com.sultan.arabicai.data.local.entity.QuizDifficulty
import com.sultan.arabicai.data.local.entity.QuizQuestionEntity
import com.sultan.arabicai.data.local.entity.QuizType
import com.sultan.arabicai.data.local.toOptionList
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.domain.gamification.RankEngine
import com.sultan.arabicai.ui.theme.SultanColors
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

private enum class QuizStage { SETUP, IN_PROGRESS, RESULTS }

@Composable
fun QuizScreen() {
    val container = LocalAppContainer.current
    val scope = rememberCoroutineScope()

    var stage by remember { mutableStateOf(QuizStage.SETUP) }
    var difficulty by remember { mutableStateOf(QuizDifficulty.MEDIUM) }
    var questions by remember { mutableStateOf<List<QuizQuestionEntity>>(emptyList()) }
    var questionIndex by remember { mutableIntStateOf(0) }
    var correctCount by remember { mutableIntStateOf(0) }
    var selectedAnswer by remember { mutableStateOf<String?>(null) }

    when (stage) {
        QuizStage.SETUP -> Column(Modifier.fillMaxSize().padding(20.dp)) {
            Text(stringResource(R.string.quiz_title), style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
            Text(stringResource(R.string.quiz_subtitle), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 8.dp))

            Row(Modifier.padding(top = 20.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                QuizDifficulty.entries.forEach { d ->
                    FilterChip(selected = difficulty == d, onClick = { difficulty = d }, label = { Text(stringResource(quizDifficultyLabel(d))) })
                }
            }

            Button(
                onClick = {
                    scope.launch {
                        val words = container.vocabularyRepository.observeAll().first()
                        val generated = container.quizRepository.generateFromVocabulary(words, difficulty, count = 8)
                        questions = generated.filter { it.type == QuizType.MULTIPLE_CHOICE }
                        questionIndex = 0
                        correctCount = 0
                        selectedAnswer = null
                        stage = if (questions.isNotEmpty()) QuizStage.IN_PROGRESS else QuizStage.SETUP
                    }
                },
                modifier = Modifier.fillMaxWidth().padding(top = 24.dp)
            ) {
                Text(stringResource(R.string.quiz_generate))
            }
        }

        QuizStage.IN_PROGRESS -> {
            val question = questions.getOrNull(questionIndex)
            if (question == null) {
                stage = QuizStage.RESULTS
                return
            }
            Column(Modifier.fillMaxSize().padding(20.dp)) {
                Text(stringResource(R.string.quiz_question_progress, questionIndex + 1, questions.size), style = MaterialTheme.typography.labelLarge, color = SultanColors.RoyalGold)
                Text(question.promptAr, style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onBackground, modifier = Modifier.padding(top = 12.dp))
                Text(question.promptEn, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

                question.options.toOptionList().forEach { option ->
                    val isCorrect = option == question.correctAnswer
                    val isSelected = option == selectedAnswer
                    val containerColor = when {
                        selectedAnswer == null -> MaterialTheme.colorScheme.surface
                        isSelected && isCorrect -> SultanColors.Success
                        isSelected && !isCorrect -> SultanColors.Error
                        isCorrect -> SultanColors.Success.copy(alpha = 0.4f)
                        else -> MaterialTheme.colorScheme.surface
                    }
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 12.dp),
                        colors = CardDefaults.cardColors(containerColor = containerColor)
                    ) {
                        Text(
                            option,
                            style = MaterialTheme.typography.titleMedium,
                            color = Color.White,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                                .let { m ->
                                    if (selectedAnswer == null) {
                                        m.clickable {
                                            selectedAnswer = option
                                            if (isCorrect) correctCount++
                                        }
                                    } else {
                                        m
                                    }
                                }
                        )
                    }
                }

                if (selectedAnswer != null) {
                    Text(question.explanation, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 12.dp))
                    Button(
                        onClick = {
                            selectedAnswer = null
                            questionIndex++
                            if (questionIndex >= questions.size) stage = QuizStage.RESULTS
                        },
                        modifier = Modifier.fillMaxWidth().padding(top = 16.dp)
                    ) { Text(stringResource(if (questionIndex + 1 >= questions.size) R.string.quiz_action_finish else R.string.quiz_action_next)) }
                }
            }
        }

        QuizStage.RESULTS -> {
            LaunchedEffect(Unit) {
                val xp = correctCount * RankEngine.Xp.QUIZ_CORRECT_ANSWER +
                    if (correctCount == questions.size) RankEngine.Xp.QUIZ_PERFECT_BONUS else 0
                container.progressRepository.awardXp(xp)
                val percent = if (questions.isEmpty()) 0 else (correctCount * 100 / questions.size)
                container.progressRepository.recordSession(
                    epochDay = TimeUnit.MILLISECONDS.toDays(System.currentTimeMillis()),
                    quizzesCompleted = 1,
                    grammarScore = percent
                )
                if (correctCount == questions.size && questions.isNotEmpty()) {
                    container.progressRepository.unlock("perfect_score")
                }
            }
            Column(Modifier.fillMaxSize().padding(20.dp), verticalArrangement = Arrangement.Center) {
                Text(stringResource(R.string.quiz_complete_title), style = MaterialTheme.typography.displayMedium, color = MaterialTheme.colorScheme.onBackground)
                Text(stringResource(R.string.quiz_score, correctCount, questions.size), style = MaterialTheme.typography.headlineLarge, color = SultanColors.RoyalGold, modifier = Modifier.padding(top = 12.dp))
                Button(
                    onClick = { stage = QuizStage.SETUP },
                    colors = ButtonDefaults.buttonColors(containerColor = SultanColors.RoyalGold, contentColor = SultanColors.RoyalNavyDeep),
                    modifier = Modifier.fillMaxWidth().padding(top = 24.dp)
                ) { Text(stringResource(R.string.quiz_new_assessment)) }
            }
        }
    }
}

private fun quizDifficultyLabel(difficulty: QuizDifficulty): Int = when (difficulty) {
    QuizDifficulty.EASY -> R.string.quiz_difficulty_easy
    QuizDifficulty.MEDIUM -> R.string.quiz_difficulty_medium
    QuizDifficulty.HARD -> R.string.quiz_difficulty_hard
    QuizDifficulty.SCHOLAR -> R.string.quiz_difficulty_scholar
}
