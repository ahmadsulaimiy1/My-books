package com.sultan.arabicai.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * AES-256-GCM-encrypted local storage (via Jetpack Security) for session/auth state.
 * Deliberately excluded from cloud backup in res/xml/data_extraction_rules.xml — session
 * secrets never leave this device, encrypted or not.
 */
object SecurePreferences {

    private const val FILE_NAME = "secure_prefs"
    private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
    private const val KEY_LAST_UNLOCKED_EPOCH_MILLIS = "last_unlocked_epoch_millis"
    private const val KEY_ONBOARDING_COMPLETE = "onboarding_complete"

    private var prefs: SharedPreferences? = null

    private fun get(context: Context): SharedPreferences {
        return prefs ?: synchronized(this) {
            prefs ?: run {
                val masterKey = MasterKey.Builder(context.applicationContext)
                    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                    .build()

                EncryptedSharedPreferences.create(
                    context.applicationContext,
                    FILE_NAME,
                    masterKey,
                    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
                ).also { prefs = it }
            }
        }
    }

    fun setBiometricEnabled(context: Context, enabled: Boolean) {
        get(context).edit().putBoolean(KEY_BIOMETRIC_ENABLED, enabled).apply()
    }

    fun isBiometricEnabled(context: Context): Boolean =
        get(context).getBoolean(KEY_BIOMETRIC_ENABLED, false)

    fun recordUnlock(context: Context, epochMillis: Long) {
        get(context).edit().putLong(KEY_LAST_UNLOCKED_EPOCH_MILLIS, epochMillis).apply()
    }

    fun lastUnlockedEpochMillis(context: Context): Long =
        get(context).getLong(KEY_LAST_UNLOCKED_EPOCH_MILLIS, 0L)

    fun setOnboardingComplete(context: Context, complete: Boolean) {
        get(context).edit().putBoolean(KEY_ONBOARDING_COMPLETE, complete).apply()
    }

    fun isOnboardingComplete(context: Context): Boolean =
        get(context).getBoolean(KEY_ONBOARDING_COMPLETE, false)
}
