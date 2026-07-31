package com.sultan.arabicai.security

import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.fragment.app.FragmentActivity
import androidx.core.content.ContextCompat

sealed interface BiometricAvailability {
    data object Available : BiometricAvailability
    data object NoHardware : BiometricAvailability
    data object HardwareUnavailable : BiometricAvailability
    data object NoneEnrolled : BiometricAvailability
    data object SecurityUpdateRequired : BiometricAvailability
    data object Unsupported : BiometricAvailability
}

sealed interface BiometricResult {
    data object Success : BiometricResult
    data class Error(val message: String) : BiometricResult
    data object Cancelled : BiometricResult
}

/**
 * Wraps AndroidX Biometric for fingerprint/face unlock, gated to STRONG or DEVICE_CREDENTIAL
 * authenticators only — never a weak/convenience biometric class — appropriate for an
 * enterprise-grade education platform that stores personal progress and certificates.
 */
class BiometricAuthManager(private val activity: FragmentActivity) {

    private val allowedAuthenticators =
        BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.DEVICE_CREDENTIAL

    fun checkAvailability(): BiometricAvailability {
        val manager = BiometricManager.from(activity)
        return when (manager.canAuthenticate(allowedAuthenticators)) {
            BiometricManager.BIOMETRIC_SUCCESS -> BiometricAvailability.Available
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> BiometricAvailability.NoHardware
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> BiometricAvailability.HardwareUnavailable
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> BiometricAvailability.NoneEnrolled
            BiometricManager.BIOMETRIC_ERROR_SECURITY_UPDATE_REQUIRED -> BiometricAvailability.SecurityUpdateRequired
            else -> BiometricAvailability.Unsupported
        }
    }

    fun authenticate(
        titleRes: String,
        subtitleRes: String,
        onResult: (BiometricResult) -> Unit
    ) {
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(titleRes)
            .setSubtitle(subtitleRes)
            .setAllowedAuthenticators(allowedAuthenticators)
            .build()

        val callback = object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                onResult(BiometricResult.Success)
            }

            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                val isCancel = errorCode == BiometricPrompt.ERROR_USER_CANCELED ||
                    errorCode == BiometricPrompt.ERROR_NEGATIVE_BUTTON
                onResult(if (isCancel) BiometricResult.Cancelled else BiometricResult.Error(errString.toString()))
            }
        }

        val prompt = BiometricPrompt(activity, ContextCompat.getMainExecutor(activity), callback)
        prompt.authenticate(promptInfo)
    }
}
