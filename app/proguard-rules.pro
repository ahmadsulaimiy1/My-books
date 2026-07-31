# Sultan Arabic AI — release shrink/obfuscation rules
#
# Room, Biometric, and ZXing each ship their own consumer proguard rules inside their AARs
# (applied automatically by AGP), so this file only covers app-specific reflection surfaces.
# NOTE: none of this has been verified against a real R8 run — no Android SDK/build toolchain
# was available in the environment that produced this scaffold. Run `./gradlew assembleRelease`
# and exercise every screen (especially TTS callbacks, Room queries, and certificate/QR
# generation) before trusting a real release build.

# Room entities are constructed via reflection during migration diffing
-keep class com.sultan.arabicai.data.local.entity.** { *; }

# Keep TTS/biometric callback classes intact — UtteranceProgressListener and
# BiometricPrompt.AuthenticationCallback overrides are invoked by the platform, not app code.
-keepclassmembers class com.sultan.arabicai.tts.** { *; }
-keepclassmembers class com.sultan.arabicai.security.** { *; }

# ZXing's format-detection path uses reflection internally.
-keep class com.google.zxing.** { *; }
