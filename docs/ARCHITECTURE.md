# Architecture — Sultan Arabic AI

## Overview

A single-module, offline-first Android app: Kotlin + Jetpack Compose (Material 3) for UI, Room
for persistence, and a hand-rolled dependency container instead of a DI framework. No backend
exists yet — see `docs/ROADMAP.md` Phase 7 for where one would plug in.

## Why no Hilt/Dagger

`di/AppContainer.kt` is a plain class that constructs the database, repositories, and exposes a
factory for the TTS engine. For a project this size, a hand-rolled graph is one file you can
read top-to-bottom, versus annotation-processor build complexity for a marginal benefit. If the
app grows a second module or the dependency graph gets deep (e.g. once Phase 3's ASR model and
Phase 4's LLM inference are added), revisit this decision.

## Data layer

- **Room** (`data/local/`) is the single source of truth. Every entity, DAO, and the database
  itself lives there. `Converters.kt` handles the enum ↔ String round-trips Room needs (Room has
  no native enum support).
- **Repositories** (`data/repository/Repositories.kt`) are thin wrappers around DAOs that also
  own the domain logic that needs a database round-trip — e.g. `VocabularyRepository.submitReview`
  applies the SM-2 algorithm and persists the result in one call.
- **Seeding** (`data/seed/ContentSeeder.kt`) populates first-run content. It is idempotent
  (`seedIfEmpty` checks a row count before inserting) so it's safe to call on every app launch.

## Domain layer

Pure, framework-free Kotlin — no Android imports — so it's trivially unit-testable:

- `domain/srs/SpacedRepetitionScheduler.kt` — SM-2 algorithm.
- `domain/gamification/RankEngine.kt` — XP thresholds and rank-progress math.
- `domain/quiz/QuizGenerator.kt` — procedural quiz question generation from vocabulary.

## TTS

`tts/ArabicTtsEngine.kt` wraps `android.speech.tts.TextToSpeech` directly (no third-party TTS
SDK). `tts/TtsPlaybackController.kt` layers pedagogical playback (word/sentence/paragraph
chunking, loop, pause/resume via re-chunking since the platform API has no true pause) on top.
See the class-level doc comments in both files for exactly what this does and does not deliver
relative to the full flagship voice-AI vision — the honest gap is documented in `docs/ROADMAP.md`
Phase 3.

## Security

- `security/BiometricAuthManager.kt` — AndroidX Biometric, gated to `BIOMETRIC_STRONG` or
  `DEVICE_CREDENTIAL` only (never a weak/convenience biometric class).
- `security/SecurePreferences.kt` — AES-256-GCM `EncryptedSharedPreferences` (Jetpack Security)
  for session/auth flags. Excluded from Android's auto-backup via
  `res/xml/data_extraction_rules.xml`, so encrypted secrets never leave the device even via
  backup.
- `res/xml/network_security_config.xml` blocks cleartext traffic app-wide.

## Certificates

`certificate/CertificateGenerator.kt` renders a certificate directly onto a `Canvas` via the
platform `PdfDocument` API (no PDF library dependency) and embeds a QR code generated locally
with ZXing's `QRCodeWriter` (no network call, no third-party QR service). The QR payload is a
verification code checked against the local `certificates` table — see `CertificateRepository.verify`.
Cloud-hosted verification (a URL a third party could scan and check without the app installed)
is a Phase 7 item once a backend exists.

## Navigation

Single `NavHost` (`navigation/SultanNavHost.kt`) with a bottom navigation bar for the five
top-level destinations (Overview, Library, Vocabulary, Speaking Lab, Profile) and a plain
back-stack for detail screens (PDF reader, lesson list/detail, flashcards, quiz, certificates).
The bottom bar is shown/hidden based on the current route rather than using a nested nav graph —
simpler for five destinations; revisit with a nested graph if the top-level count grows.

## Gate flow (onboarding → biometric → main)

`SultanNavHost` computes a `startDestination` once (via `remember`) based on
`SecurePreferences.isOnboardingComplete` and biometric availability/enrollment. First run always
sees onboarding; biometric login is only inserted into the flow if the device actually supports
it and the user has enabled it in their profile settings.

## What's deliberately not abstracted

- No repository interfaces / fake implementations for testing — there is one implementation of
  each repository, backed directly by Room. Add an interface when a second implementation
  (e.g. a remote-backed one for Phase 7) actually exists; an interface with one implementation is
  premature abstraction.
- No ViewModel layer on every screen — screens that only read reactive Room `Flow`s and dispatch
  simple repository calls do so directly from the composable via `LocalAppContainer`. This keeps
  the code path from database to UI short and readable for a project this size.
