# Roadmap — Sultan Arabic AI

This document maps the full Saudi Vision 2030 flagship vision to what exists in this codebase
today versus what is genuinely future work, and — for each future item — the concrete technical
approach it would need. The goal is to be an honest engineering roadmap, not a marketing
document: nothing below is claimed as "AI-powered" unless there is a real model or algorithm
behind it.

## Status legend

- ✅ **Implemented** — real, working code in this repository today.
- 🚧 **Partial** — a working subset exists; the full ambition needs more work.
- 📋 **Planned** — scoped below with a concrete technical approach, not yet built.

---

## Phase 1 — Arabic learning core

| Feature | Status | Notes |
|---|---|---|
| Offline lessons, dialogues, grammar focus | ✅ | `LessonEntity`, seeded starter content |
| Tap-word dictionary (translation, root, grammar, synonyms/antonyms) | ✅ | `LessonDetailScreen` |
| Offline Arabic TTS (word/sentence/paragraph, loop, speed/pitch) | ✅ | `ArabicTtsEngine` + `TtsPlaybackController`, wraps Android's on-device `TextToSpeech` |
| Spaced-repetition vocabulary bank | ✅ | SM-2 scheduler, `SpacedRepetitionScheduler.kt` |
| On-device quiz generation (multiple-choice, fill-in-blank) | ✅ | Rule-based generation from the learner's vocabulary bank, `QuizGenerator.kt` |
| Digital library / PDF reader | ✅ | Platform `PdfRenderer`, bundled SULTAN Book 2 |
| Gamification (ranks, XP, streaks, achievements) | ✅ | `RankEngine.kt`, nine-tier ladder |
| Luxury certificates with QR verification | ✅ | `CertificateGenerator.kt`, on-device `PdfDocument` + ZXing |
| Biometric login, encrypted local storage | ✅ | `BiometricAuthManager`, `SecurePreferences` |
| Real book content import (replacing starter seed data) | 📋 | Needs a PDF→lesson extraction pipeline (see below) |
| Tajweed-aware pronunciation mode, Hijazi/Najdi voice styles | 📋 | Stock Android TTS voices are not dialect-specific; needs bundled neural TTS (see Phase 3) |
| AI pronunciation scoring, accent/mispronunciation detection | 📋 | Needs an on-device ASR/phoneme-alignment model (see Phase 3) |
| Arabic OCR (camera → text → pronunciation) | 📋 | ML Kit Text Recognition has limited Arabic support; likely needs a dedicated Arabic OCR model |
| AI handwriting recognition | 📋 | Google ML Kit **Digital Ink Recognition** supports Arabic script and is the most direct path here |
| Arabic calligraphy practice module | 📋 | Stroke-order overlay + ML Kit ink recognition for stroke scoring |
| Qur'an / Islamic mode (Tajweed colouring, word-by-word, tafsir) | 📋 | A large, separate content + rendering effort; deliberately out of scope for this pass |

**PDF→lesson import pipeline (concrete plan):** run OCR/text extraction (e.g. a server-side or
desktop tool using `pdfplumber`/`PyMuPDF`, or on-device via ML Kit) over the source PDF, segment
by unit/lesson heading, and produce a JSON file matching `LessonEntity`/`VocabWordEntity` shapes
that `ContentSeeder` can load instead of the hand-written starter data. This is a content
pipeline, not a model — it just wasn't runnable in the environment that produced this scaffold
(no PDF-parsing libraries were installable).

## Phase 2 — English learning

🚧 The TTS engine (`ArabicTtsEngine.ENGLISH_US` / `ENGLISH_UK` locale constants) and the quiz
generator are already language-agnostic — they operate on whatever `VocabWordEntity` rows exist.
What's missing is English lesson/vocabulary content and an English-specific UI pass (shadowing
exercises, accent evaluation UI). Accent evaluation itself needs the same ASR work as Phase 3.

## Phase 3 — AI speaking coach

📋 **Planned.** Concrete approach:
- **Speech-to-text (Arabic + English):** an on-device ASR model — Whisper-tiny/base exported to
  TensorFlow Lite or ONNX Runtime Mobile, or Android's `SpeechRecognizer` where offline language
  packs exist — to transcribe the learner's recording from the existing Speaking Lab.
- **Pronunciation scoring:** align the ASR transcript (or phoneme sequence, via a
  forced-aligner) against the target word/sentence and score similarity — this is the
  "accent detection / mispronunciation detection / phonetic breakdown" capability from the
  original brief. Requires a trained or fine-tuned model; not something to fake with a random
  number.
- **Mouth-position illustrations:** static articulation-guide assets per phoneme, licensed or
  produced by a linguist — a content task, not an engineering one.

## Phase 4 — Real-time conversation AI

📋 **Planned.** A genuine conversational tutor needs either (a) a small on-device LLM
(e.g. a quantized Gemma/Phi-class model via MediaPipe LLM Inference or ONNX Runtime) for fully
offline operation, or (b) a cloud LLM API call when online, with the current offline-first
architecture (Room, background `WorkManager` sync) as the natural fallback path. Given the
app's "complete offline functionality" requirement, the on-device route should be evaluated
first; a cloud fallback should be opt-in and clearly disclosed to the user.

## Phase 5 — AI Arabic teacher avatar

📋 **Planned.** A "Saudi academic mentor" companion avatar is a content/animation project
(a rigged 2D/3D character, TTS-driven lip sync) layered on top of Phase 3/4's voice and
conversation capabilities. No architecture blocker — sequenced after the underlying voice AI
exists so the avatar has something real to say.

## Phase 6 — AI classroom

📋 **Planned.** Builds on Phase 4 (multi-turn conversation) plus a classroom/session model
(multiple learners, a teacher-led session state) — this is additive to the existing Room schema
(a `ClassroomSession` entity, roughly) once conversation AI exists.

## Phase 7 — AI educational ecosystem

📋 **Planned.** The long-horizon integration layer: parent/teacher dashboards, classroom mode
for institutions, leaderboards by institution/country, and LMS integration for Sultan Hanafi
Royal Schools and Sultan Hanafi Qur'an College. This is primarily a **backend** project (a
multi-tenant API, auth, and sync service) that the current offline-first client is already
architected to talk to — `data/repository/` is the seam where a remote data source would plug
in alongside the existing Room-backed one, and `WorkManager` (already a dependency) is where
background sync would live. None of that backend exists yet; building it is a distinct,
much larger effort from the Android client in this repository.

---

## Additional recommended features — status

| Feature | Status |
|---|---|
| Parent/teacher dashboard | 📋 Phase 7 (needs backend + roles) |
| Classroom mode for schools/colleges | 📋 Phase 7 |
| Leaderboards by institution/country | 📋 Phase 7 (needs backend for cross-device aggregation) |
| Smart revision planner (AI-scheduled) | 🚧 The SM-2 scheduler already drives *what's* due; a calendar/planner UI on top is straightforward future work |
| Adaptive difficulty engine | 🚧 `QuizDifficulty` + `ProficiencyLevel` exist as the levers; an engine that *automatically* moves a learner between them based on quiz history is not yet built |
| Live pronunciation heatmaps | 📋 Depends on Phase 3's phoneme-level scoring |
| Luxury dark mode + premium light mode | ✅ Both fully themed, see `ui/theme/Theme.kt` |
| Downloadable lesson packs for offline study | ✅ Everything is offline by default (Room-backed); a "download pack" UI is mostly a re-framing of existing state, not new architecture |
| AI-generated lesson summaries | 📋 Needs an LLM (on-device or cloud), see Phase 4 |
| One-tap lesson-to-quiz conversion | ✅ `LessonDetailScreen`'s "Start Quiz" button, generating from the learner's vocabulary |
| Digital Arabic dictionary throughout the app | 🚧 Tap-word lookup exists inside lessons; a standalone searchable dictionary screen is not yet built |
| Companion avatar (Saudi academic mentor) | 📋 Phase 5 |
| Annual "Grand Scholar" certification pathway | ✅ `ScholarRank.GRAND_SCHOLAR` is the top rank tier; an annual/dated certification ceremony flow on top of the existing certificate generator is straightforward future work |
| Enterprise LMS integration (Sultan Hanafi Royal Schools / Qur'an College) | 📋 Phase 7 |
