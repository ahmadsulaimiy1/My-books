package com.sultan.arabicai.ui.screens.onboarding

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.R
import com.sultan.arabicai.ui.theme.SultanColors

@Composable
fun OnboardingScreen(onBegin: () -> Unit) {
    Box(
        Modifier
            .fillMaxSize()
            .background(SultanColors.RoyalNavyDeep)
    ) {
        Column(
            Modifier
                .fillMaxSize()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            EightPointSeal()

            Text(
                stringResource(R.string.onboarding_kicker),
                color = SultanColors.RoyalGoldBright,
                style = MaterialTheme.typography.labelLarge,
                modifier = Modifier.padding(top = 32.dp)
            )
            Text(
                stringResource(R.string.onboarding_edition),
                color = SultanColors.Silver,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 4.dp)
            )

            Text(
                stringResource(R.string.onboarding_welcome_title),
                color = SultanColors.Platinum,
                style = MaterialTheme.typography.displayMedium,
                textAlign = TextAlign.Center,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(top = 40.dp)
            )
            Text(
                stringResource(R.string.onboarding_welcome_subtitle),
                color = SultanColors.Silver,
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(top = 16.dp)
            )

            Button(
                onClick = onBegin,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 48.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = SultanColors.RoyalGold,
                    contentColor = SultanColors.RoyalNavyDeep
                )
            ) {
                Text(stringResource(R.string.onboarding_cta_begin), style = MaterialTheme.typography.titleMedium)
            }
        }
    }
}

@Composable
private fun EightPointSeal() {
    Box(
        Modifier
            .size(84.dp)
            .background(SultanColors.RoyalGold.copy(alpha = 0.15f), CircleShape),
        contentAlignment = Alignment.Center
    ) {
        Box(
            Modifier
                .size(48.dp)
                .background(SultanColors.RoyalGold, CircleShape)
        )
    }
}
