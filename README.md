# Sultan Arabic AI — Saudi Vision 2030 Flagship Edition

A premium, offline-first Arabic learning platform for Android, built around **SULTAN: Saudi
Ultimate Language Training of Arabic for Non-Natives — Intermediate Book 2** by Ahmad Sulaimiy
(bundled at `app/src/main/assets/books/sultan_intermediate_book_2.pdf`).

This repository is a native Android application (Kotlin + Jetpack Compose), not a web app or a
design mockup. It targets the full ambition described in the product brief — a flagship,
Vision‑2030‑grade learning experience — by shipping a solid, genuinely working core today and
documenting the more ambitious AI‑research features as an honest, staged roadmap rather than
faking them. See [`docs/ROADMAP.md`](docs/ROADMAP.md) for exactly what is real right now versus
what is planned, and [`docs/PHASE3_RELEASE_READINESS.md`](docs/PHASE3_RELEASE_READINESS.md) for
the current, evidence-based release-readiness status (build verification, device/version
compatibility, and a release decision — currently **Not Ready For Release**, primarily because
no build has ever successfully compiled in any environment this project has been developed in
so far). Play Store draft materials (privacy policy, terms of service, data safety form, store
listing copy) live in [`docs/store/`](docs/store/).

## What's implemented (real, working code)

- **Premium design system** — Royal Navy Blue / Royal Gold / Platinum flagship theme, luxury
  dark mode as default with a fully designed light mode, calm motion language, Arabic RTL
  support. See [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md).
- **Fully offline-first architecture** — Room database for lessons, vocabulary, quizzes,
  progress, achievements, bookmarks, notes, and certificates. Nothing in the core learning loop
  requires a network connection.
- **Digital Library** — the bundled SULTAN PDF rendered on-device via Android's platform
  `PdfRenderer` (no third-party PDF SDK), with page navigation, bookmarking and notes hooks.
- **Interactive lessons** — tap any Arabic word in a lesson's dialogue to see its translation,
  transliteration, root letters, part of speech, synonyms and antonyms.
- **Offline Arabic + English TTS** — a real wrapper around Android's on-device
  `TextToSpeech` engine with word/sentence/paragraph reading modes, loop, pause/resume/repeat,
  adjustable speed and pitch, and pedagogical presets (native pace, slow learning, teacher mode,
  child mode).
- **Spaced-repetition vocabulary bank** — a genuine SM‑2 (SuperMemo‑2) scheduler, the same
  algorithm behind Anki, driving a flashcard review flow.
- **On-device quiz generation** — multiple-choice and fill-in-the-blank questions generated
  procedurally from the learner's own vocabulary bank, no network or LLM call required.
  Difficulty tiers (Easy/Medium/Hard/Scholar) map onto the app's proficiency levels.
  See the honesty note in [`docs/ROADMAP.md`](docs/ROADMAP.md) about why this is rule-based
  rather than LLM-generated.
- **Gamification** — XP, a nine-tier prestige rank ladder (Beginner → Grand Scholar), streaks,
  and an achievements system.
- **Speaking Lab** — real microphone recording (`MediaRecorder`), native-voice comparison via
  the TTS engine, and local playback (`MediaPlayer`).
- **Luxury certificates** — an on-device PDF certificate generator (platform `PdfDocument` API)
  with an embedded QR code (generated locally via ZXing, no network) that encodes a
  verification code checkable against the local database.
- **Security** — biometric (fingerprint/face) login gated to `BIOMETRIC_STRONG` /
  `DEVICE_CREDENTIAL` only, AES‑256‑GCM `EncryptedSharedPreferences` for session state, and a
  network security config that blocks cleartext traffic outright. The Room database itself
  (lessons, vocabulary, progress, certificates) is **not** encrypted at rest — this is a known,
  tracked gap, not an oversight; see "Security debt: database encryption" in
  [`docs/ROADMAP.md`](docs/ROADMAP.md) for why it's deferred and what compensating control is
  in place today.
- **Voice data recovery** — before any TTS playback, the app checks whether the requested
  language's voice data is actually installed (`tts/VoiceDataManager.kt`) and shows a clear,
  actionable dialog instead of silently failing if it isn't — no Play button appears to do
  nothing.
- **Executive dashboard** — learning hours, lessons completed, vocabulary mastered, and
  speaking/listening/grammar analytics, aggregated from real session data.

## What's intentionally not implemented yet

Automated pronunciation scoring, accent/mispronunciation detection, Tajweed-aware phoneme
shaping, Arabic OCR, handwriting recognition, a conversational AI tutor, and an AI teacher
avatar all require dedicated ML models (ASR, TTS voice cloning, on-device LLMs, ink recognition)
that go well beyond what a scaffold like this can respons­ibly claim to deliver. They are
scoped, phased, and given concrete technical approaches in [`docs/ROADMAP.md`](docs/ROADMAP.md)
rather than stubbed out with fake success states.

## Project structure

```
app/src/main/java/com/sultan/arabicai/
├── data/           # Room entities, DAOs, database, repositories, first-run content seeding
├── domain/         # SM-2 scheduler, rank/XP engine, on-device quiz generator
├── tts/            # Offline Arabic/English TTS engine + playback controller
├── security/       # Biometric auth, encrypted preferences
├── certificate/     # PDF certificate + QR generation
├── navigation/      # NavHost + routes
├── ui/
│   ├── theme/        # Design system (colour, type, shape, motion)
│   ├── components/   # Shared premium UI components
│   └── screens/       # One package per feature screen
├── di/              # Minimal hand-rolled dependency container
└── MainActivity.kt / SultanApplication.kt
```

## Building

**Requirements** (exact versions this project is pinned to — see `build.gradle.kts` /
`app/build.gradle.kts` / `gradle/wrapper/gradle-wrapper.properties`):

| Tool | Version |
|---|---|
| JDK | 17 |
| Gradle (via wrapper — do not use a system Gradle) | 8.10.2 |
| Android Gradle Plugin | 8.7.2 |
| Kotlin | 2.0.21 |
| Compose compiler plugin | 2.0.21 (must match the Kotlin version exactly) |
| KSP | 2.0.21-1.0.28 |
| compileSdk / targetSdk | 35 |
| minSdk | 26 |

Android Studio Ladybug (2024.2) or newer bundles a compatible SDK/toolchain and is the easiest
path — open the project root and let it sync.

From the command line:

```bash
./gradlew assembleDebug      # unsigned debug APK
./gradlew assembleRelease    # release APK — unsigned unless keystore.properties exists (see below)
./gradlew lint                # Android Lint
```

**Honesty note on verification status:** the environment that produced this codebase had no
Android SDK and no network access to Google's Maven repository (`dl.google.com` — confirmed
blocked, not just absent), so none of the commands above have actually been run against this
code. What *has* been done instead, as a substitute:

- A full manual, line-by-line audit of every Kotlin file against the real Compose/Room/
  Navigation/Biometric/TTS/PdfRenderer/ZXing API surfaces for the pinned versions above (see
  the Phase 2 audit this project went through — ask in-repo history / PR description for the
  full report), which found and fixed several real defects.
- A scripted check that every `.kt` file's package declaration matches its directory path.
- A scripted check for balanced braces/parens across every file (catches gross structural
  errors, not semantic ones).
- A scripted cross-reference of every `R.string.*` reference against both `values/strings.xml`
  and `values-ar/strings.xml` to confirm 1:1 key parity and no orphaned/unused string resources.
- A manual "lint-equivalent" pass for the specific classes of issue Android Lint would catch
  that are checkable without the toolchain: unused imports, unused resources, hardcoded
  user-facing strings, missing `contentDescription`.

None of this substitutes for actually running `./gradlew assembleDebug`/`lint` on a real
toolchain — do that before trusting a release build, and treat this project as **audited and
manually verified, not compiler-verified**, until someone does.

### Signing a release build

Release builds are unsigned by default (see `app/build.gradle.kts`). To sign one, copy
`keystore.properties.example` to `keystore.properties` (repo root, already gitignored) and fill
in real values pointing at your own keystore — never commit `keystore.properties` or the
keystore file itself.

## Content note

The seeded lessons/vocabulary in `data/seed/ContentSeeder.kt` are representative starter content
in the structural style of the SULTAN curriculum (dialogue + grammar focus + graded vocabulary),
**not** a transcription of the bundled book — automated PDF text extraction wasn't available in
the build environment. The bundled PDF itself is wired into the Digital Library as the canonical
source; before shipping, replace the seed data with real content extracted from the book via a
proper import pipeline (see the Phase 1 roadmap item).
