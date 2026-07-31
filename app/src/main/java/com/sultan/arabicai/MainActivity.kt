package com.sultan.arabicai

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.compose.runtime.CompositionLocalProvider
import androidx.fragment.app.FragmentActivity
import com.sultan.arabicai.di.LocalAppContainer
import com.sultan.arabicai.navigation.SultanNavHost
import com.sultan.arabicai.ui.theme.SultanArabicAITheme

/**
 * Single-activity flagship shell: splash → onboarding/biometric gate → five-pillar bottom
 * navigation (Overview, Library, Vocabulary, Speaking Lab, Profile), all driven by
 * [SultanNavHost]. Extends [FragmentActivity] (not the lighter ComponentActivity) because
 * androidx.biometric's [androidx.biometric.BiometricPrompt] requires it.
 */
class MainActivity : FragmentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val container = (application as SultanApplication).container

        setContent {
            SultanArabicAITheme {
                CompositionLocalProvider(LocalAppContainer provides container) {
                    SultanNavHost(activity = this)
                }
            }
        }
    }
}
