# Sultan Arabic AI — Saudi Vision 2030 Flagship Edition

A premium, offline-first Arabic learning platform for Android, built around **SULTAN: Saudi
Ultimate Language Training of Arabic for Non-Natives — Intermediate Book 2** by Ahmad Sulaimiy
(bundled at `app/src/main/assets/books/sultan_intermediate_book_2.pdf`).

This repository is a native Android application (Kotlin + Jetpack Compose), not a web app or a
design mockup. It targets the full ambition described in the product brief — a flagship,
Vision‑2030‑grade learning experience — by shipping a solid, genuinely working core today and
documenting the more ambitious AI‑research features as an honest, staged roadmap rather than
faking them. See [`docs/ROADMAP.md`](docs/ROADMAP.md) for exactly what is real right now versus
what is planned.

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
  network security config that blocks cleartext traffic outright.
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

This project requires the Android SDK and a network connection able to reach Google's Maven
repository (`dl.google.com`) to resolve AndroidX/Compose dependencies — neither was available in
the environment that produced this scaffold, so the code has been written and manually reviewed
for correctness but **has not been compiled**. To build:

```bash
./gradlew assembleDebug
```

Open in Android Studio (Ladybird/Koala or newer) for the smoothest experience — it will offer to
download the Gradle/AGP toolchain and Android SDK automatically.

## Content note

The seeded lessons/vocabulary in `data/seed/ContentSeeder.kt` are representative starter content
in the structural style of the SULTAN curriculum (dialogue + grammar focus + graded vocabulary),
**not** a transcription of the bundled book — automated PDF text extraction wasn't available in
the build environment. The bundled PDF itself is wired into the Digital Library as the canonical
source; before shipping, replace the seed data with real content extracted from the book via a
proper import pipeline (see the Phase 1 roadmap item).
