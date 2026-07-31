package com.sultan.arabicai.ui.theme

import androidx.compose.ui.graphics.Color

/**
 * Flagship palette. Keep numerically identical to res/values/colors.xml so XML-themed
 * surfaces (splash, notifications) and Compose surfaces never visually drift apart.
 */
object SultanColors {
    val RoyalNavy = Color(0xFF082A66)
    val RoyalNavyDeep = Color(0xFF051A40)
    val RoyalNavyLight = Color(0xFF12408F)

    val RoyalGold = Color(0xFFC9A961)
    val RoyalGoldBright = Color(0xFFE4C77E)
    val RoyalGoldDim = Color(0xFF9C7F42)

    val Platinum = Color(0xFFE8E9EC)
    val Silver = Color(0xFFB9BDC7)
    val PureWhite = Color(0xFFFFFFFF)
    val InkBlack = Color(0xFF0B0D12)

    val Success = Color(0xFF2E9E6B)
    val Warning = Color(0xFFCB8A2E)
    val Error = Color(0xFFB3413A)

    // Rank tier accents — used on badges/certificates, ascending in prestige.
    val TierBeginner = Color(0xFF7C8698)
    val TierStudent = Color(0xFF4C7BB0)
    val TierScholar = Color(0xFF2E6F8E)
    val TierResearcher = Color(0xFF3E7A5E)
    val TierExpert = Color(0xFF7A5EA6)
    val TierMaster = Color(0xFFB0784C)
    val TierAmbassador = Color(0xFF0F3D7A)
    val TierEliteScholar = Color(0xFFC9A961)
    val TierGrandScholar = Color(0xFFE4C77E)
}
