package com.sultan.arabicai.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

/**
 * Luxury dark mode is the flagship default (executive dashboards, premium fintech, Qur'an
 * apps all skew dark-first). Light mode is a fully designed peer, not an afterthought.
 */
private val SultanDarkColorScheme = darkColorScheme(
    primary = SultanColors.RoyalGold,
    onPrimary = SultanColors.RoyalNavyDeep,
    primaryContainer = SultanColors.RoyalNavyLight,
    onPrimaryContainer = SultanColors.RoyalGoldBright,
    secondary = SultanColors.Silver,
    onSecondary = SultanColors.InkBlack,
    background = SultanColors.RoyalNavyDeep,
    onBackground = SultanColors.Platinum,
    surface = SultanColors.RoyalNavy,
    onSurface = SultanColors.Platinum,
    surfaceVariant = SultanColors.RoyalNavyLight,
    onSurfaceVariant = SultanColors.Silver,
    outline = SultanColors.RoyalGoldDim,
    error = SultanColors.Error
)

private val SultanLightColorScheme = lightColorScheme(
    primary = SultanColors.RoyalNavy,
    onPrimary = SultanColors.PureWhite,
    primaryContainer = SultanColors.Platinum,
    onPrimaryContainer = SultanColors.RoyalNavyDeep,
    secondary = SultanColors.RoyalGoldDim,
    // PureWhite on RoyalGoldDim measures ~3.8:1 (WCAG relative-luminance formula) — fails the
    // 4.5:1 AA threshold for normal text. InkBlack on the same background measures ~5.25:1,
    // which passes. See docs/DESIGN_SYSTEM.md for the computed values.
    onSecondary = SultanColors.InkBlack,
    background = SultanColors.PureWhite,
    onBackground = SultanColors.InkBlack,
    surface = SultanColors.Platinum,
    onSurface = SultanColors.InkBlack,
    surfaceVariant = SultanColors.Silver,
    onSurfaceVariant = SultanColors.RoyalNavyDeep,
    outline = SultanColors.RoyalGold,
    error = SultanColors.Error
)

@Composable
fun SultanArabicAITheme(
    useDarkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (useDarkTheme) SultanDarkColorScheme else SultanLightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = SultanTypography,
        shapes = SultanShapes,
        content = content
    )
}
