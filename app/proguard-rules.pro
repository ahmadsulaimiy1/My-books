# Sultan Arabic AI — release shrink/obfuscation rules

# Room entities are constructed via reflection during migration diffing
-keep class com.sultan.arabicai.data.local.entity.** { *; }

# Keep TTS/biometric callback classes intact
-keepclassmembers class com.sultan.arabicai.tts.** { *; }
-keepclassmembers class com.sultan.arabicai.security.** { *; }
