package com.sultan.arabicai.ui.screens.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Fingerprint
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.sultan.arabicai.security.BiometricAvailability
import com.sultan.arabicai.ui.theme.SultanColors

@Composable
fun BiometricLoginScreen(
    availability: BiometricAvailability,
    onAuthenticate: () -> Unit,
    onSkip: () -> Unit
) {
    LaunchedEffect(availability) {
        if (availability != BiometricAvailability.Available) onSkip()
    }

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
            Box(
                Modifier
                    .size(96.dp)
                    .background(SultanColors.RoyalGold.copy(alpha = 0.15f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    Icons.Filled.Fingerprint,
                    contentDescription = null,
                    tint = SultanColors.RoyalGold,
                    modifier = Modifier.size(48.dp)
                )
            }

            Text(
                "Unlock Sultan Arabic AI",
                color = SultanColors.Platinum,
                style = MaterialTheme.typography.headlineLarge,
                modifier = Modifier.padding(top = 32.dp)
            )
            Text(
                "Use your fingerprint or face to continue",
                color = SultanColors.Silver,
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(top = 8.dp)
            )

            Button(
                onClick = onAuthenticate,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 40.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = SultanColors.RoyalGold,
                    contentColor = SultanColors.RoyalNavyDeep
                )
            ) {
                Text("Authenticate", style = MaterialTheme.typography.titleMedium)
            }

            TextButton(onClick = onSkip, modifier = Modifier.padding(top = 8.dp)) {
                Text("Use passcode instead", color = SultanColors.Silver)
            }
        }
    }
}
