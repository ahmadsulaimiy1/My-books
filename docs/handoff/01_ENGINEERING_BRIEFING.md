# Engineering Handoff Briefing — Sultan Arabic AI

Read this first. It's the fastest path to being productive in this codebase with zero prior
context. Everything here was re-verified directly against current source at the time of
writing (Phase 5), not recalled from memory of earlier phases.

## Project purpose

Sultan Arabic AI is a native Android app (Kotlin + Jetpack Compose) for intermediate learners of
Arabic as a foreign language, built around the bundled textbook *SULTAN: Saudi Ultimate Language
Training of Arabic for Non-Natives — Intermediate Book 2* by Ahmad Sulaimiy. It is designed to
be fully usable offline: lessons, vocabulary, quizzes, text-to-speech, and progress tracking all
work with no network connection (the app requests no `INTERNET` permission at all — this is a
deliberate constraint, not an oversight).

The product ambition (documented in `docs/ROADMAP.md`) is considerably larger than what's built
— things like AI pronunciation scoring, OCR, handwriting recognition, and a conversational
tutor are explicitly out of scope for the current codebase and tracked as future phases with
concrete technical approaches, not implemented as stubs pretending to work.

**Critical context you need before touching anything:** as of this handoff, **no build of this
project has ever succeeded** in any environment it has been developed in. All prior "Phase"
audits (2 through 4, referenced throughout this repo's `docs/`) were performed by extensive
manual code reading and fresh independent re-audits — real, substantive verification work, but
not equivalent to a compiler or a device ever running this code. See
`docs/handoff/02_KNOWN_ISSUES_REGISTER.md` and `docs/PHASE3_RELEASE_READINESS.md` /
`docs/PHASE4_BUILD_AND_DEVICE_VALIDATION.md` for the full evidence trail. Your first job with
real tooling is simply: **make it compile, then see what's actually true.**

## Architecture overview

Single-module Android app. Kotlin + Jetpack Compose (Material 3) for UI, Room for persistence,
a hand-rolled dependency container instead of a DI framework (no Hilt/Dagger — see
`docs/ARCHITECTURE.md` for the reasoning), no ViewModel layer (screens read Room `Flow`s and
call repository methods directly via a `CompositionLocal`). No backend exists; everything is
on-device.

```
UI (Compose screens)
    │  reads Flow<T>, calls suspend fns
    ▼
Repositories (data/repository/Repositories.kt)
    │  wraps DAOs + domain logic (SRS scheduling, XP awarding)
    ▼
Room (data/local/) ──────────────── domain/ (pure Kotlin, no Android deps)
    │                                   SM-2 scheduler, rank engine, quiz generator
    ▼
SQLite (on-device, unencrypted — see Known Issues Register)
```

Cross-cutting subsystems (`tts/`, `security/`, `certificate/`) are consumed directly by screens
via the DI container (`di/AppContainer.kt`), not routed through the repository layer.

## Module structure

Everything lives under `app/src/main/java/com/sultan/arabicai/` (42 Kotlin files, single
Gradle module `:app`):

| Package | Contents |
|---|---|
| *(root)* | `MainActivity.kt` (single-Activity host), `SultanApplication.kt` (DI container init + first-run content seeding) |
| `data/local/` | `AppDatabase.kt`, `Converters.kt` (enum↔String, Room has no native enum support), `dao/Daos.kt`, `entity/Entities.kt` |
| `data/repository/` | `Repositories.kt` — one class per domain area (Library, Lesson, Vocabulary, Quiz, Progress, Certificate) |
| `data/seed/` | `ContentSeeder.kt` — first-run data population (idempotent, see Known Issues re: representative vs. real content) |
| `domain/` | `srs/SpacedRepetitionScheduler.kt` (SM-2), `gamification/RankEngine.kt` (XP/rank math), `quiz/QuizGenerator.kt` (rule-based question generation) — all pure Kotlin, zero `android.*` imports, trivially unit-testable |
| `tts/` | `ArabicTtsEngine.kt` (wraps `android.speech.tts.TextToSpeech`), `TtsPlaybackController.kt` (word/sentence/paragraph chunking, loop, pause/resume), `VoiceDataManager.kt` (voice-data-missing detection/recovery) |
| `security/` | `BiometricAuthManager.kt`, `SecurePreferences.kt` (`EncryptedSharedPreferences`) |
| `certificate/` | `CertificateGenerator.kt` (on-device `PdfDocument` rendering + ZXing QR) |
| `navigation/` | `NavRoutes.kt`, `SultanNavHost.kt` — single `NavHost`, bottom nav for 5 top-level destinations |
| `di/` | `AppContainer.kt` (manual dependency graph), `LocalAppContainer.kt` (CompositionLocal) |
| `ui/theme/` | Design system: `Color.kt`, `Type.kt`, `Shape.kt`, `Motion.kt`, `Theme.kt` |
| `ui/components/` | Shared composables: `Components.kt`, `RankPresentation.kt`, `VoiceDataMissingDialog.kt` |
| `ui/screens/` | One package per feature screen: `onboarding/`, `auth/`, `dashboard/`, `library/` (includes the PDF reader), `lessons/`, `vocabulary/` (includes flashcards), `quiz/`, `speaking/`, `profile/`, `certificates/` |

## Dependency map

From `app/build.gradle.kts`, grouped by purpose (exact versions — verify these haven't drifted
if this file has been touched since):

| Purpose | Dependencies |
|---|---|
| Core / Compose | `compose-bom:2024.12.01`, `core-ktx:1.15.0`, `core-splashscreen:1.0.1`, `lifecycle-runtime-ktx:2.8.7`, `lifecycle-viewmodel-compose:2.8.7`, `activity-compose:1.9.3`, `fragment-ktx:1.8.5`, `compose.ui`/`ui-graphics`/`ui-tooling-preview`, `material3`, `material-icons-extended`, `navigation-compose:2.8.5` |
| Persistence | `room-runtime:2.6.1`, `room-ktx:2.6.1`, `room-compiler:2.6.1` (via KSP) |
| Security | `biometric:1.1.0`, `security-crypto:1.1.0-alpha06` (⚠ only non-stable dependency in the project — see Known Issues) |
| Certificates | `com.google.zxing:core:3.5.3` |
| Coroutines | `kotlinx-coroutines-android:1.9.0` |
| Test (unused — see Known Issues) | `junit:4.13.2`, `androidx.test.ext:junit:1.2.1`, `ui-test-junit4` |

Build tooling: AGP 8.7.2, Kotlin 2.0.21, Compose compiler plugin 2.0.21 (must match Kotlin
exactly), KSP 2.0.21-1.0.28, Gradle wrapper 8.10.2, JDK target 17, compileSdk/targetSdk 35,
minSdk 26. No NDK, no product flavors, 2 build variants (debug/release).

## Database schema

Room database `sultan_arabic_ai.db`, 10 entities, version 1, no migrations yet (fresh schema).
**Not encrypted at rest** — see Known Issues Register. No `@Index`/`@ForeignKey` declared on any
foreign-key-style column (`bookId`, `lessonId`) — acceptable at current seed-data scale, a real
risk once content scales up (also in Known Issues Register).

| Table | Key columns | Notes |
|---|---|---|
| `books` | `id` (PK, autogen), `titleAr`, `titleEn`, `author`, `assetPath`, `format` (enum), `level` (enum), `totalPages`, `coverColorHex`, `isCoreCurriculum` | One row per library book; the bundled SULTAN PDF is seeded here |
| `lessons` | `id` (PK), `bookId`, `orderIndex`, `unitNumber`, `titleAr`/`titleEn`, `dialogueAr`/`dialogueEn`, `grammarFocusAr`/`grammarFocusEn`, `level` (enum), `estimatedMinutes` | No FK constraint to `books.id` (soft reference only) |
| `vocabulary_words` | `id` (PK), `lessonId` (nullable soft FK), `arabic`, `transliteration`, `english`, `rootLetters`, `partOfSpeech`, `exampleSentenceAr`/`En`, `synonyms`, `antonyms`, `isFavorite`, `isMarkedDifficult`, plus **SM-2 state**: `srsEaseFactor` (Float, default 2.5), `srsIntervalDays`, `srsRepetitions`, `srsDueAtEpochMillis` | The SRS columns are mutated in place by `SpacedRepetitionScheduler.review()` |
| `quiz_questions` | `id` (PK), `lessonId` (nullable), `type` (enum, 13 values though only `MULTIPLE_CHOICE`/`FILL_IN_BLANK` are actually generated today), `difficulty` (enum), `promptAr`/`promptEn`, `options` (pipe-delimited string, see `Converters.kt`'s `toOptionList()`/`toOptionsColumn()`), `correctAnswer`, `explanation` | |
| `study_sessions` | `id` (PK), `epochDay`, `minutesStudied`, `lessonsCompleted`, `wordsReviewed`, `quizzesCompleted`, `speakingScore`, `listeningScore`, `grammarScore` | One row per calendar day, merged/upserted by `ProgressRepository.recordSession()` |
| `user_stats` | `id` (PK, always `1` — singleton row), `totalXp`, `currentStreakDays`, `longestStreakDays`, `lastStudiedEpochDay`, `totalLearningMinutes` | Single-row table by convention, not enforced by schema |
| `achievements` | `key` (PK, String), `titleAr`/`titleEn`, `descriptionAr`/`descriptionEn`, `tier`, `unlockedAtEpochMillis` (nullable — null = locked) | Seeded once; **fixed in Phase 2.5** after a real bug where every unlocked achievement was wiped on every app launch |
| `bookmarks` | `id` (PK), `bookId`, `pageIndex`, `label`, `createdAtEpochMillis` | |
| `notes` | `id` (PK), `bookId`, `pageIndex`, `content`, `createdAtEpochMillis` | |
| `certificates` | `id` (PK), `titleAr`/`titleEn`, `level` (enum), `recipientName`, `issuedAtEpochMillis`, `verificationCode`, `filePath` | `verificationCode` has no cryptographic binding to the row's content — see Known Issues |

Enum↔String conversion for all `enum`-typed columns is handled by `Converters.kt` (Room has no
built-in enum support); `ScholarRank` is never persisted as a column (computed from `totalXp` at
read time via `ScholarRank.forXp()`), so it correctly has no converter.

## TTS subsystem

Three files, `tts/`:
- **`ArabicTtsEngine.kt`** — thin wrapper around `android.speech.tts.TextToSpeech`. Exposes
  `initialize()`, `selectLocale()`, `isLanguageAvailable()` (non-mutating check, added in Phase
  2.5 specifically to enable pre-flight checks before playback), `setSpeechRate()`/`setPitch()`,
  `speakChunk()`, `installedEngineLabels()`/`currentEngineLabel()`. Honestly documents in its
  own doc comment what it does *not* do (dialect-accurate voices, Tajweed-aware phoneme shaping,
  accent scoring — all require a dedicated neural TTS/ASR model, tracked as Phase 3 in
  `docs/ROADMAP.md`, unrelated to this project's own "Phase" numbering for audits).
- **`TtsPlaybackController.kt`** — layers pedagogical playback on top: `ReadingMode`
  (WORD/SENTENCE/PARAGRAPH chunking via regex split), `DeliveryPreset` (native/slow/teacher/
  child pace+pitch combos), loop mode, and pause/resume implemented via manual chunk-index
  tracking (the platform TTS API has no true pause, only stop).
- **`VoiceDataManager.kt`** (added Phase 2.5/3) — wraps `ACTION_CHECK_TTS_DATA`/
  `ACTION_INSTALL_TTS_DATA`/`ACTION_TTS_SETTINGS` intents and maps `TextToSpeech` language-
  availability constants to a `VoiceReadiness` enum, driving `ui/components/
  VoiceDataMissingDialog.kt` — shown instead of silently failing when voice data or the TTS
  engine itself is unavailable (this exact defect was found and fixed twice — see Known Issues
  Register for the full history of that specific bug).

Consumed from `LessonDetailScreen.kt` and `SpeakingLabScreen.kt` directly (not via the
repository layer) — each screen owns its own `ArabicTtsEngine` instance via `container.
newArabicTtsEngine(context)`, with `DisposableEffect`-based lifecycle cleanup including an
`ON_STOP` observer (Phase 2.5) so backgrounding the app stops playback.

## PDF subsystem

`ui/screens/library/PdfReaderScreen.kt`. Uses the platform `android.graphics.pdf.PdfRenderer` —
no third-party PDF library. Since `PdfRenderer` needs a real file descriptor and the book ships
as a bundled asset, the file is copied to `context.cacheDir` on first open (`copyAssetToCache()`
private helper) and reused on subsequent opens. Both the asset-copy/renderer-construction and
the per-page bitmap render run on `Dispatchers.IO` inside `LaunchedEffect` (this threading fix
landed in Phase 3, after Phase 2's audit caught the original version doing this synchronously
on the main thread inside a `DisposableEffect`). Each page renders to an `ARGB_8888` bitmap at
2x the PDF's native point-size — **this sizing was never revisited after being flagged as a
low-RAM-device memory-pressure risk; see Known Issues Register.**

## Quiz subsystem

`domain/quiz/QuizGenerator.kt` (pure Kotlin) + `data/repository/Repositories.kt`'s
`QuizRepository`. Deliberately **rule-based, not LLM-based** — generates multiple-choice
questions (correct answer + 3 distractors sampled from the same vocabulary pool) and
fill-in-blank questions (from vocabulary entries whose example sentence contains the target
word) directly from whatever's in the learner's own `vocabulary_words` table. No network call,
no generative model. `QuizScreen.kt` currently only renders the `MULTIPLE_CHOICE` type from
what's generated (fill-in-blank questions are generated and stored but not yet surfaced in the
UI — worth checking if that's intentional or an oversight when you have a running app to look
at).

## Certificate subsystem

`certificate/CertificateGenerator.kt`. Renders directly onto a `Canvas` via the platform
`android.graphics.pdf.PdfDocument` API (no PDF library dependency) — draws the Royal Navy/Gold
certificate layout, the eight-pointed-star seal motif, and an embedded QR code generated locally
via ZXing's `QRCodeWriter` (no network, no third-party QR service). The QR payload is a
verification code checked against the local `certificates` table
(`CertificateRepository.verify()`) — **there is no cryptographic signature binding the code to
the certificate's actual content**, so a direct database edit could alter a certificate's
recipient/level without invalidating its still-"valid" code. Documented, not fixed — see Known
Issues Register.

## Security subsystem

- **`security/BiometricAuthManager.kt`** — wraps AndroidX Biometric, gated to
  `BIOMETRIC_STRONG | DEVICE_CREDENTIAL` only (never a weak/convenience biometric class).
  **Functions as a soft, optional unlock gate, not real access control**: it only appears once,
  optionally, at app launch if the user enabled it in Profile settings; nothing re-checks
  biometric state anywhere else in the app, and "Skip"/no hardware reaches all local data
  unconditionally. This was true from the start and is documented as a known characteristic,
  not a regression — but it means "biometric lock" should not be marketed as securing the app's
  data, only as a launch-time convenience gate, unless that's deliberately redesigned.
- **`security/SecurePreferences.kt`** — `EncryptedSharedPreferences` (AES-256-GCM, Keystore-
  backed `MasterKey`) for exactly three flags: biometric-enabled, onboarding-complete, last-
  unlock-timestamp. Excluded from Android auto-backup via `res/xml/data_extraction_rules.xml`.
- **The Room database itself is NOT encrypted.** This was a deliberate, documented deferral (see
  `docs/ROADMAP.md`'s "Security debt: database encryption" section) rather than an oversight —
  the reasoning given was that adding an unverified crypto dependency (SQLCipher) in an
  environment with no way to compile-test it would repeat the exact kind of unchecked claim
  these audit phases exist to eliminate. A compensating control (database excluded from Android
  backup) is in place. **This is the single most consequential item for whoever picks this up
  next to actually decide on**, since it's the one deferred-by-necessity item that a real
  toolchain removes the excuse for.
- **`res/xml/network_security_config.xml`** blocks cleartext traffic app-wide (though moot today
  since the app requests no `INTERNET` permission at all).
- **Manifest**: only `RECORD_AUDIO` and `USE_BIOMETRIC` permissions remain (Phase 2.5 removed
  `INTERNET`, `ACCESS_NETWORK_STATE`, `POST_NOTIFICATIONS` as confirmed-unused).
