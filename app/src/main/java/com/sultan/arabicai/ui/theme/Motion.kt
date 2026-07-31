package com.sultan.arabicai.ui.theme

import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.Easing

/**
 * Flagship motion language: slower, more deliberate than typical Material defaults —
 * everything should feel weighted and considered, never bouncy or playful.
 */
object SultanMotion {
    val EmphasizedEasing: Easing = CubicBezierEasing(0.2f, 0.0f, 0.0f, 1.0f)
    val StandardEasing: Easing = CubicBezierEasing(0.4f, 0.0f, 0.2f, 1.0f)

    const val DurationQuick = 180
    const val DurationStandard = 320
    const val DurationEmphasized = 520
}
