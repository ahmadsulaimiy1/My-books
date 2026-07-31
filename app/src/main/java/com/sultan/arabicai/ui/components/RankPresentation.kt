package com.sultan.arabicai.ui.components

import androidx.compose.ui.graphics.Color
import com.sultan.arabicai.R
import com.sultan.arabicai.data.local.entity.ScholarRank
import com.sultan.arabicai.ui.theme.SultanColors

/** Localized display label + tier accent colour for a [ScholarRank] — shared by Dashboard and Profile. */
fun rankLabelRes(rank: ScholarRank): Int = when (rank) {
    ScholarRank.BEGINNER -> R.string.rank_beginner
    ScholarRank.STUDENT -> R.string.rank_student
    ScholarRank.SCHOLAR -> R.string.rank_scholar
    ScholarRank.RESEARCHER -> R.string.rank_researcher
    ScholarRank.EXPERT -> R.string.rank_expert
    ScholarRank.MASTER -> R.string.rank_master
    ScholarRank.AMBASSADOR -> R.string.rank_ambassador
    ScholarRank.ELITE_SCHOLAR -> R.string.rank_elite_scholar
    ScholarRank.GRAND_SCHOLAR -> R.string.rank_grand_scholar
}

fun rankTierColor(rank: ScholarRank): Color = when (rank) {
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
