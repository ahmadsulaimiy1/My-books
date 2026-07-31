# Phase 6 — Flagship Implementation Roadmap

**What this document is:** implementation *plans* for 30 requested flagship capabilities, grounded
in the actual current codebase (package structure, entities, DAOs, DI container, TTS/PDF/quiz
subsystems as they exist in this repository today — cross-checked against
[`docs/handoff/01_ENGINEERING_BRIEFING.md`](handoff/01_ENGINEERING_BRIEFING.md) while writing this).
**No source code was written or modified to produce this document.** Per the instructions this
phase was scoped under, this is planning documentation only.

**Where the project stands going into this:** per
[`docs/handoff/07_FINAL_STATUS_REPORT.md`](handoff/07_FINAL_STATUS_REPORT.md), the current codebase
is classified **C — Advanced Prototype** — it has never successfully compiled in any environment
this project has had access to. Everything below is additive planning on top of that codebase; it
does not change, and should not be read as changing, that classification. Building any Phase 6
feature on an unbuilt foundation without first clearing
[`docs/handoff/03_FIRST_BUILD_PLAYBOOK.md`](handoff/03_FIRST_BUILD_PLAYBOOK.md) would compound risk
rather than reduce it — that remains the actual next step regardless of this roadmap.

**Honesty note on "AI-generated" features:** several requested features are named "AI-generated"
(#19, #20, #21) or imply a conversational AI (#8, #9). This project's existing quiz engine
(`domain/quiz/QuizGenerator.kt`) is deliberately **rule-based, not LLM-based** — see the honesty
note already in [`docs/ROADMAP.md`](ROADMAP.md) about why. This roadmap keeps that same honesty
discipline: where a feature can be delivered with deterministic/template logic that produces a
genuinely useful result, the plan below says so plainly and scopes it as low/medium complexity in
Phase 6A. Where a feature requires an actual machine-learning model (on-device OCR, ink
recognition, speech recognition, or a real generative language model), the plan says exactly which
model/library and is honest that it is materially higher complexity, storage cost, and risk —
these are pushed to 6B/6C/6D accordingly. No feature below claims "AI" as a label for logic that
isn't.

## How to read each entry

Every feature gets the 9 requested dimensions:

- **Architecture** — what new/changed classes, and where they sit relative to the existing
  `data/` / `domain/` / `tts/` / `security/` / `certificate/` / `ui/` / `di/` package structure.
- **Database changes** — new Room entities/DAOs, or fields added to existing ones.
- **UI changes** — new screens/composables, or changes to existing ones.
- **Dependencies** — exact new Gradle dependencies, if any (today's full dependency list is in
  `app/build.gradle.kts` / `docs/handoff/01_ENGINEERING_BRIEFING.md`).
- **Offline strategy** — how the feature behaves with zero connectivity (the app's current
  design point; see README "Fully offline-first architecture").
- **Storage requirements** — realistic on-device footprint (model files, cached data).
- **Security implications** — new attack surface, PII, or permission requirements.
- **Implementation order** — what it depends on, both within its tier and across tiers.
- **Estimated complexity** — **S / M / L / XL**, defined qualitatively (this project has no build
  history to derive time estimates from, and fabricating hours/days would violate the same
  no-fabrication standard applied throughout this project's audits):
  - **S** — extends an existing class/table, no new dependency, no new screen or one small one.
  - **M** — one new subsystem package, at most one new dependency, one or two new screens.
  - **L** — a new dependency with a real model/asset footprint, new DAOs/entities, multi-screen.
  - **XL** — a new architectural layer (networking, ML runtime) touching most of the app; carries
    real unknowns even in the plan itself.

## Architectural prerequisite common to every tier below

`AppDatabase.kt` is currently `version = 1` with `exportSchema = false`
(`app/src/main/java/com/sultan/arabicai/data/local/AppDatabase.kt:48-49`) — no schema JSON history
exists anywhere in the repo. **Before any Phase 6A entity change**, flip `exportSchema = true`,
commit the generated `schemas/` directory, and write the first real `Migration` object. This isn't
a new feature — it's fixing a gap that would otherwise make every Room change below untestable and
risks a silent `fallbackToDestructiveMigration`-style data wipe on first upgrade. This is a one-time
prerequisite, not a per-feature line item, so it isn't repeated in every entry below.

---

# Phase 6A — MVP Expansion

Highest educational value relative to lowest complexity. Every item here extends an existing
subsystem (`domain/quiz`, `domain/srs`, `tts/`, `data/repository`) rather than introducing a new
architectural layer. No cloud dependency in this tier — everything stays offline-first.

## 1. #19 — AI-generated quizzes (rule-based expansion, honestly named)

- **Architecture:** extend `domain/quiz/QuizGenerator.kt` rather than replace it. Add generation
  strategies keyed on `VocabWordEntity` fields already present (`rootLetters`, `synonyms`,
  `antonyms`, `partOfSpeech`) to produce new `QuizType` variants beyond the current
  multiple-choice/fill-in-blank pair — the `QuizType` enum already declares `MATCHING`,
  `SENTENCE_BUILDING`, `TRANSLATION`, `DICTATION` as unused values (`Entities.kt:10-14`), so this
  is substantially filling in an already-designed-but-unimplemented enum, not inventing new scope.
- **Database changes:** none required — `QuizQuestionEntity` already has the fields needed
  (`options`, `correctAnswer`, `explanation`). Optionally add a `generatedAtEpochMillis: Long` and
  `sourceStrategy: String` pair of columns to `QuizQuestionEntity` for traceability/debugging.
- **UI changes:** none required beyond `ui/screens/quiz/QuizScreen.kt` gaining renderers for the
  newly-implemented `QuizType` cases (currently only multiple-choice/fill-in-blank are rendered).
- **Dependencies:** none.
- **Offline strategy:** fully offline — same as today, generation runs from local `VocabWordEntity`
  rows already in the database.
- **Storage requirements:** negligible (a few extra Long/String columns).
- **Security implications:** none.
- **Implementation order:** first in 6A — every downstream 6A/6B feature that references "quiz
  performance" (#10, #21, #24, #25) benefits from a richer `QuizType` set existing first.
- **Estimated complexity:** **S**.

## 2. #20 — AI-generated lesson summaries (template-based, honestly named)

- **Architecture:** new `domain/summary/LessonSummaryGenerator.kt` — a pure function taking a
  `LessonEntity` and its associated `VocabWordEntity` list and producing a structured summary
  (key vocabulary count, grammar focus restated, estimated review time) via string templates, not
  a language model. Mirrors the existing pattern of `domain/gamification/RankEngine.kt` and
  `domain/srs/SpacedRepetitionScheduler.kt` — pure Kotlin, no I/O, unit-testable.
- **Database changes:** none — reads existing `LessonEntity`/`VocabWordEntity` fields
  (`grammarFocusAr/En`, `dialogueAr/En`).
- **UI changes:** a summary card/section added to `ui/screens/lessons/LessonDetailScreen.kt`
  (already heavily touched in Phases 2.5/3, so this is a known-quantity file to extend).
- **Dependencies:** none.
- **Offline strategy:** fully offline.
- **Storage requirements:** negligible.
- **Security implications:** none.
- **Implementation order:** after #19 (shares the "generation strategy" pattern, easier to review
  together); no other dependency.
- **Estimated complexity:** **S**.

## 3. #21 — AI-generated revision plans (rule-based, honestly named)

- **Architecture:** new `domain/revision/RevisionPlanner.kt` combining two data sources that
  already exist independently: `domain/srs/SpacedRepetitionScheduler.kt`'s due-date logic (via
  `VocabWordEntity.srsDueAtEpochMillis`) and per-topic weak-spot detection from
  `QuizQuestionEntity`/session score history (`StudySessionEntity.grammarScore` etc.). Produces an
  ordered `List<RevisionItem>` (vocab due for review + lessons whose grammar focus correlates with
  low quiz scores) — genuinely useful prioritization logic, not a fabricated "AI" claim.
- **Database changes:** new `RevisionPlanEntity` (id, generatedAtEpochMillis, itemsJson) if plans
  should persist across sessions, or none if computed fresh each time (recommended for 6A — avoids
  a migration for a feature that's cheap to recompute).
- **UI changes:** new `ui/screens/revision/RevisionPlanScreen.kt`, reachable from the dashboard.
- **Dependencies:** none.
- **Offline strategy:** fully offline.
- **Storage requirements:** negligible if computed fresh (recommended).
- **Security implications:** none.
- **Implementation order:** depends on #19 only in that a richer `QuizType` set gives better
  weak-spot signal; not a hard blocker.
- **Estimated complexity:** **M** (new package, new screen, but no new dependency).

## 4. #10 — Adaptive learning engine

- **Architecture:** new `domain/adaptive/DifficultyAdjuster.kt`. Rule-based: tracks a rolling
  per-`ProficiencyLevel` accuracy from recent `QuizQuestionEntity` attempts (needs a new
  `QuizAttemptEntity` — see below, since today's `QuizQuestionEntity` stores the question bank,
  not attempt history) and shifts the `QuizDifficulty` distribution `QuizGenerator` draws from.
- **Database changes:** new `QuizAttemptEntity` (id, questionId FK, isCorrect, answeredAtEpochMillis,
  timeTakenMillis) + `QuizAttemptDao`. This is a real, currently-missing gap — today's schema has
  no attempt-level history at all, only aggregate `StudySessionEntity.quizzesCompleted` counts, so
  this entity is a prerequisite for #10, #24, and #29 as well, not 6A-only scope creep.
- **UI changes:** none required for the engine itself; `QuizScreen.kt` gains a call to log each
  attempt via the new DAO (one new repository method call, not a new screen).
- **Dependencies:** none.
- **Offline strategy:** fully offline.
- **Storage requirements:** small — attempt rows are lightweight; recommend a retention cap (e.g.
  keep last 500 attempts) to bound growth, since this table has no natural upper limit otherwise.
- **Security implications:** none new.
- **Implementation order:** after #19 (needs the richer `QuizType` set to adapt meaningfully across).
  `QuizAttemptEntity` introduced here is reused by #24 and #29 in later tiers.
- **Estimated complexity:** **M**.

## 5. #27 — Digital library expansion (EPUB / DOCX / TXT / HTML)

- **Architecture:** `BookEntity.format: BookFormat` already declares `EPUB, DOCX, TXT, HTML` as
  values (`Entities.kt:8`) with only `PDF` actually wired to a renderer
  (`ui/screens/library/PdfReaderScreen.kt`). New `ui/screens/library/format/` sub-package with one
  renderer composable per format: TXT/HTML are cheap (read asset text, render in a `WebView` for
  HTML, plain `Text` for TXT); EPUB is the real work (an EPUB is a zip of XHTML+CSS — needs a
  parser, not a from-scratch implementation).
- **Database changes:** none — `BookEntity.format`/`assetPath` already generalize correctly.
- **UI changes:** a new `LibraryReaderScreen` router that dispatches to the right renderer by
  `book.format`, replacing today's PDF-only assumption in the library flow.
- **Dependencies:** for EPUB, a lightweight parsing library (no full "epub reader" dependency
  exists that's Compose-native — most viable path is parsing the EPUB zip/OPF/XHTML manually with
  `java.util.zip` + Android's built-in `Html.fromHtml`/`WebView`, avoiding a heavy new dependency).
- **Offline strategy:** fully offline — same asset-bundling model as the current PDF book.
- **Storage requirements:** depends entirely on what content is added; the mechanism itself adds
  no fixed footprint.
- **Security implications:** if HTML/EPUB content is ever sourced from outside the app's own
  assets (e.g. a future "import your own book" feature), `WebView` rendering of untrusted HTML is
  a real XSS-class risk — for 6A, scope this to bundled assets only and flag this explicitly for
  any later "user-supplied file" extension.
- **Implementation order:** independent of the rest of 6A; can run in parallel.
- **Estimated complexity:** **M** (TXT/HTML) blended with **L** (EPUB) — recommend shipping
  TXT/HTML first and scoping EPUB as a fast-follow within the same tier rather than blocking on it.

## 6. #11 — Downloadable voice packs

- **Architecture:** extends the `tts/VoiceDataManager.kt` object created in Phase 2.5 — today it
  only detects and redirects to system TTS data install; this adds an in-app catalogue of voice
  "packs" (metadata only — the actual voice data still installs via the existing
  `ACTION_INSTALL_TTS_DATA` system flow, since Android's `TextToSpeech` API doesn't expose a way
  to sideload third-party voice models into the system TTS engine). New
  `tts/VoicePackCatalogue.kt` holding a static or DB-backed list of persona metadata (name,
  language, description) mapped to the underlying system `Locale`/engine the pack corresponds to.
- **Database changes:** new `VoicePackEntity` (id, nameAr, nameEn, locale, isInstalled — the last
  field refreshed by re-querying `VoiceDataManager.checkTtsDataIntent()` results, not stored as
  ground truth, since actual install state lives in the OS).
- **UI changes:** the "Voice Center screen" concept raised (and flagged as contradictory scope) in
  Phase 2.5 belongs here, now that this is explicitly a feature-development phase rather than a
  stabilization freeze: `ui/screens/voice/VoiceCenterScreen.kt` listing packs with install-state
  badges, reusing `VoiceDataMissingDialog.kt`'s existing install/settings actions.
- **Dependencies:** none new.
- **Offline strategy:** the catalogue itself is fully offline (bundled metadata); actual voice
  data installation still depends on whatever the OS's TTS engine offers, which may itself require
  connectivity — this is an existing OS-level constraint, not something this app controls or can
  make more offline than it already is.
- **Storage requirements:** catalogue metadata is negligible; actual voice model storage is
  entirely owned by the OS TTS engine, outside this app's control or `data/` footprint.
- **Security implications:** none new.
- **Implementation order:** independent; can run in parallel with the rest of 6A. Feeds #12 (Saudi
  Arabic voice pack) in 6C, which is a specific catalogue entry rather than new infrastructure.
- **Estimated complexity:** **M**.

## 7. #5 — Offline speech-to-text

- **Architecture:** new `stt/` package (sibling to `tts/`, same pattern) — `stt/OfflineSttEngine.kt`.
  Android's built-in `SpeechRecognizer` with `RecognizerIntent.EXTRA_PREFER_OFFLINE` is the
  zero-dependency option, but offline Arabic language-pack availability through it is
  OEM/Google-app-dependent and not guaranteed — this project's standing "prove it, don't assume it"
  discipline means that gap needs to be named, not glossed over. The more reliable offline
  guarantee is bundling **Vosk** (open-source, Apache-2.0, genuinely offline, has a published
  Arabic model) directly, at the cost of a real dependency and model file.
  Recommend: `stt/OfflineSttEngine.kt` as an interface with two implementations
  (`SystemSpeechRecognizerStt`, `VoskStt`), selected by a capability check — ship the free
  system-recognizer path first, add Vosk as the guaranteed fallback once model bundling logistics
  (below) are worked out, rather than blocking the whole feature on Vosk integration.
- **Database changes:** none required for the engine itself; if transcripts should feed the
  Speaking Lab's existing recording flow (`ui/screens/speaking/SpeakingLabScreen.kt`), add a
  nullable `transcript: String?` column to whatever entity backs recorded speaking attempts today
  (currently there isn't one — recordings are ephemeral `MediaRecorder` output, not persisted rows;
  persisting them is itself new scope worth flagging, not assumed here).
- **UI changes:** `SpeakingLabScreen.kt` gains a transcript display after each recording.
- **Dependencies:** `org.vosk:vosk-android` (or equivalent), if the Vosk path is taken.
- **Offline strategy:** the system-recognizer path is "offline where the OS allows it" (a
  meaningfully weaker guarantee than the rest of this app); the Vosk path is genuinely offline by
  construction, matching this app's stated design point. This distinction should be surfaced to the
  user in-product (e.g. a badge), not hidden.
- **Storage requirements:** a Vosk Arabic small model is realistically **~50MB**; this is a real,
  user-visible app-size increase, not a rounding error, and should be an optional download
  (matching the "downloadable voice packs" pattern from #11) rather than bundled into the base APK.
- **Security implications:** `RECORD_AUDIO` permission is already declared and used
  (`AndroidManifest.xml`) — no new permission required. If Vosk's model download path is used, that
  reintroduces the `INTERNET` permission this app deliberately removed in Phase 2.5 for exactly this
  kind of on-demand asset — scope that download to a single, narrow, explicitly-user-initiated
  action, and document it as the one legitimate network use case this offline-first app has.
- **Implementation order:** last in 6A — highest complexity and the only 6A item touching the
  permission model. Feeds #6/#7 (pronunciation/accent scoring) in 6B, which benefit from having a
  transcript to compare against a reference.
- **Estimated complexity:** **L**.

---

# Phase 6B — Professional Edition

Teacher/parent-facing features plus the first tier of genuine speech-analysis ML. Everything here
still runs against the same local Room database as a single source of truth — no cloud dependency
is introduced in this tier (that's 6C's job); "dashboards" in 6B are views over the *current
device's own data*, not multi-user aggregation.

## 8. #13 — Teacher dashboard

- **Architecture:** new `ui/screens/teacher/TeacherDashboardScreen.kt` reading from the existing
  `progressRepository`/`quizRepository` (`AppContainer.kt`) — this is a read-oriented aggregation
  view, no new write path.
- **Database changes:** none beyond what #10's `QuizAttemptEntity` already adds (reused here for
  per-student — really per-device, see note below — performance breakdowns).
- **UI changes:** new screen + a new bottom-nav or profile-menu entry point.
- **Dependencies:** none.
- **Offline strategy:** fully offline — this dashboard, as scoped for 6B, reflects **this device's
  own local data only**. A true multi-student teacher dashboard requires #17 (cloud sync) to
  aggregate across devices — that composed version belongs in 6C once sync exists; shipping a
  single-device dashboard now is real, honest, incremental value, not a mislabeled placeholder, as
  long as the UI is explicit about that scope.
- **Storage requirements:** negligible.
- **Security implications:** none new for the single-device version. A multi-student version (6C)
  will need real authentication/authorization design, not assumed here.
- **Implementation order:** depends on #10's `QuizAttemptEntity`. Precedes the 6C multi-student
  version.
- **Estimated complexity:** **M**.

## 9. #14 — Parent dashboard

- **Architecture/DB/UI/Deps/Offline/Storage/Security:** identical shape to #13 — same underlying
  data, a different presentation lens (progress trends, streaks, time-on-task from
  `StudySessionEntity`, rather than per-question breakdowns). `ui/screens/parent/ParentDashboardScreen.kt`.
- **Implementation order:** can be built alongside #13, sharing a common `domain/analytics/`
  aggregation helper introduced for both rather than duplicating query logic twice.
- **Estimated complexity:** **S** (given #13 already exists — mostly a new composable over the same
  aggregation layer).

## 10. #23 — Assignment system

- **Architecture:** new `domain/assignment/` package. An "assignment" is a scoped subset of
  existing content (a lesson list + a due date) — new `AssignmentEntity` (id, titleAr/En,
  lessonIds (comma/JSON list), dueAtEpochMillis, assignedAtEpochMillis) + `AssignmentDao`, following
  the exact same entity/DAO/repository pattern already established for every other table.
- **Database changes:** new `AssignmentEntity` + `AssignmentDao`, wired into a new
  `AssignmentRepository` in `AppContainer.kt`.
- **UI changes:** new `ui/screens/assignment/AssignmentListScreen.kt` +
  `AssignmentDetailScreen.kt` (progress against the assignment's lesson list, using existing
  lesson-completion tracking).
- **Dependencies:** none.
- **Offline strategy:** fully offline — single-device assignment creation/completion. Creating and
  *distributing* assignments to other students' devices requires #17; single-device
  create-and-track is real value on its own (e.g. self-assigned study plans) even before sync
  exists.
- **Storage requirements:** negligible.
- **Security implications:** none new.
- **Implementation order:** after #13 (dashboards are the natural place to view assignment
  completion). Prerequisite for #24 (an examination is effectively a graded, timed assignment).
- **Estimated complexity:** **M**.

## 11. #24 — Examination system

- **Architecture:** new `domain/exam/ExamEngine.kt` — composes existing `QuizGenerator` output
  into a timed, scored, non-repeatable session (distinct from the practice `QuizScreen` flow, which
  allows retries). Reuses `QuizAttemptEntity` from #10 for scoring.
- **Database changes:** new `ExamEntity` (id, titleAr/En, questionIds, timeLimitMinutes,
  passingScorePercent) + `ExamAttemptEntity` (examId, startedAt, submittedAt, score) + DAOs.
- **UI changes:** new `ui/screens/exam/ExamScreen.kt` (timed, no-retry variant of `QuizScreen`) +
  `ExamResultScreen.kt`.
- **Dependencies:** none.
- **Offline strategy:** fully offline.
- **Storage requirements:** negligible.
- **Security implications:** if exams are ever used for real certification/grading stakes, on-device
  answer storage without integrity protection means a rooted device could tamper with recorded
  scores — acceptable for a self-study tool, worth flagging explicitly if this ever feeds #28
  (certificate verification) or any school-facing (6C) use.
- **Implementation order:** depends on #10 and #23.
- **Estimated complexity:** **M**.

## 12. #25 — Student ranking system

- **Architecture:** extends `domain/gamification/RankEngine.kt` (already computes `ScholarRank`
  from XP) with a *relative* ranking view — for 6B, single-device only means "rank" is really just
  a richer presentation of the existing `ScholarRank` ladder (percentile-style framing against the
  fixed XP thresholds already defined in `Entities.kt:18-33`), not a real multi-user leaderboard —
  that's #26 in 6C, which has an actual population to rank against.
- **Database changes:** none.
- **UI changes:** enrich `ui/screens/profile/` or dashboard with a rank/percentile visualization.
- **Dependencies:** none.
- **Offline strategy:** fully offline (by necessity — there is no peer data to compare against on
  one device).
- **Storage requirements:** negligible.
- **Security implications:** none.
- **Implementation order:** trivial extension, can be built any time after #13.
- **Estimated complexity:** **S**.

## 13. #28 — Premium certificate verification

- **Architecture:** extends `certificate/` (existing PDF+QR generator). Today's
  `CertificateEntity.verificationCode` has **no cryptographic binding to certificate content** —
  flagged as risk #13 in `docs/handoff/05_RELEASE_RISK_REGISTER.md`. "Premium" verification means
  fixing that: generate `verificationCode` as an HMAC (e.g. HMAC-SHA256) over the certificate's
  actual content fields (recipient name, level, issued date) keyed by a per-install secret stored
  via the existing `security/` `EncryptedSharedPreferences` wrapper, so a verification check can
  detect tampering, not just existence.
- **Database changes:** none — `CertificateEntity` already has the needed fields; the change is in
  how `verificationCode` is computed, in `certificate/` generation code.
- **UI changes:** `ui/screens/certificates/CertificatesScreen.kt` gains a "Verify" action that
  recomputes the HMAC from a scanned/entered code and compares.
- **Dependencies:** none — `javax.crypto.Mac` is part of the Android platform, no new library.
- **Offline strategy:** fully offline — verification is local HMAC recomputation, no server round
  trip needed for on-device checks (a *public*, cross-installation verification service is a 6C+
  concept requiring #17, out of scope here).
- **Storage requirements:** negligible.
- **Security implications:** this is a direct, positive fix to an existing, already-documented
  security gap — should be prioritized within 6B for that reason, not just its own feature value.
- **Implementation order:** independent of the rest of 6B; can run first.
- **Estimated complexity:** **S**.

## 14. #6 — Advanced Arabic pronunciation scoring

- **Architecture:** new `domain/pronunciation/PronunciationScorer.kt`. Honest staging, matching
  this project's existing pattern of not overclaiming ML capability: a true phoneme-level scorer
  needs a forced-alignment or acoustic model this project has no current access to build or
  validate. The realistic 6B version is a **DSP-heuristic v1**: compare the learner's recorded
  audio (`MediaRecorder` output, already captured in `SpeakingLabScreen.kt`) against the reference
  TTS-generated audio for the same phrase using coarse signal features — duration ratio, pitch
  contour correlation, energy envelope — computed via a lightweight on-device DSP pass (Android's
  `AudioRecord`/`MediaExtractor` PCM access + a manual FFT, or a small library like TarsosDSP).
  This produces a genuinely useful "how close was your rhythm/intonation" score, honestly labeled
  as heuristic, not a claim of phoneme-accurate ASR scoring.
- **Database changes:** new `PronunciationAttemptEntity` (id, wordOrPhraseId, score, recordedAt) if
  history should persist; optional for a v1.
- **UI changes:** `SpeakingLabScreen.kt` gains a score display after each recording/comparison.
- **Dependencies:** TarsosDSP (or equivalent lightweight on-device signal-processing library) if not
  hand-rolling the FFT/pitch-detection logic.
- **Offline strategy:** fully offline — all comparison happens against the already-offline TTS
  reference audio.
- **Storage requirements:** negligible (no ML model file needed for the heuristic v1).
- **Security implications:** none new (`RECORD_AUDIO` already covers this).
- **Implementation order:** depends on #5 (offline STT) only if scoring should also factor in
  *what was said*, not just *how* — for a v1 scoped to rhythm/intonation only, it does not need
  #5 as a hard dependency, which is why it's placed in 6B rather than waiting for 6C.
- **Estimated complexity:** **L** (real signal-processing work, even at heuristic grade).

## 15. #7 — Accent detection

- **Architecture:** extends `domain/pronunciation/PronunciationScorer.kt` from #6 rather than a
  separate subsystem — "accent detection" at a genuinely offline, honestly-scoped level means
  classifying which reference-accent cluster (e.g. Saudi/Gulf vs. Levantine vs. Egyptian MSA
  pronunciation norms, if reference audio for more than one accent exists — see #12) a learner's
  pronunciation most resembles, using the same DSP feature vector as #6 plus a small
  nearest-centroid classifier trained offline ahead of time (shipped as a small bundled model/
  parameter file, not trained on-device).
- **Database changes:** none beyond #6's.
- **UI changes:** extends the same score display in `SpeakingLabScreen.kt` with an accent-match
  indicator.
- **Dependencies:** none beyond #6's, unless a real classifier (vs. hand-tuned centroids) is used,
  in which case a small on-device inference runtime (TFLite) would be added.
- **Offline strategy:** fully offline.
- **Storage requirements:** small (a few KB–MB classifier parameter file).
- **Security implications:** none.
- **Implementation order:** hard dependency on #6 (shares its feature-extraction pipeline) and soft
  dependency on #12 (Saudi Arabic voice pack) — without a Saudi-accent reference, this can only
  detect "does this differ from the single shipped reference accent," which is a materially weaker
  and should be labeled as such if shipped before #12.
- **Estimated complexity:** **L**.

## 16. #8 — AI Arabic tutor

- **Architecture:** this is the first genuinely "AI" (as opposed to rule-based) feature in this
  roadmap, and the honesty note at the top of this document applies directly here. A real
  conversational tutor needs an actual language model. The realistic, honestly-scoped offline path
  is Google's **AI Edge / MediaPipe LLM Inference API** running a small instruction-tuned model
  (e.g. a quantized Gemma variant) fully on-device — genuinely offline, but a real multi-GB
  download and a real minimum-hardware bar (this will not run acceptably on low-RAM devices, which
  is a meaningful chunk of the Arabic-learner audience this app is nominally built for — that
  tension should be surfaced to the user, not hidden). New `ai/` package (sibling to `tts/`, `stt/`)
  — `ai/OnDeviceTutorEngine.kt` wrapping the MediaPipe LLM Inference API, with the tutor's system
  prompt/context grounded in the current lesson's vocabulary/grammar focus (from `LessonEntity`) so
  responses stay curriculum-relevant rather than open-ended.
- **Database changes:** new `TutorConversationEntity` (id, lessonId?, role, message, timestampMillis)
  if conversation history should persist across sessions.
- **UI changes:** new `ui/screens/tutor/ArabicTutorScreen.kt` — a chat-style interface.
- **Dependencies:** `com.google.mediapipe:tasks-genai` (or the current equivalent artifact for the
  LLM Inference API).
- **Offline strategy:** genuinely offline once the model file is downloaded — the download itself
  is the one place this needs connectivity, same pattern flagged for #5's Vosk model.
- **Storage requirements:** realistically **1.5–4GB** depending on the chosen quantized model size
  — by far the largest storage line item in this entire roadmap. This must be an explicit,
  user-initiated optional download, never bundled into the base APK, and the app needs a clear
  device-capability check (RAM, available storage) before offering it at all.
- **Security implications:** re-introduces `INTERNET` permission for the model download (same
  narrow, justified exception pattern as #5); the model itself runs fully local after that, so no
  conversation content leaves the device — worth stating explicitly as a privacy property.
- **Implementation order:** last substantive item in 6B given its size — should not block anything
  else in the tier. Depends on nothing else in 6B; #9 (English tutor, 6C) reuses this exact engine
  with a different system prompt, not a separate implementation.
- **Estimated complexity:** **XL**.

---

# Phase 6C — Enterprise Edition

Cloud/institutional features. This tier is where the app's "offline-first" architecture is
deliberately extended, not replaced — every feature here must degrade gracefully to the existing
fully-offline behavior when connectivity is absent, since that guarantee is core to what this
project has repeatedly represented to be true about itself.

## 17. #17 — Cloud synchronization (foundational for this tier)

- **Architecture:** new `data/remote/` package (sibling to `data/local/`) — a `SyncEngine.kt`
  reconciling local Room state against a remote store. `AppDatabase.kt`'s own doc comment already
  references a not-yet-built `data/sync/` roadmap stub (`AppDatabase.kt:32`), so this slot was
  anticipated in the architecture from the start, not being retrofitted in awkwardly. Sync should
  be last-write-wins per-row with a `lastModifiedEpochMillis` column added to every syncable
  entity, not a full CRDT system — proportionate to this app's actual conflict surface (a single
  user's own progress data, not concurrent multi-writer editing).
- **Database changes:** add `lastModifiedEpochMillis: Long` + `syncState: String` (SYNCED /
  PENDING / CONFLICT) to every entity that should sync (`UserStatsEntity`, `StudySessionEntity`,
  `QuizAttemptEntity`, `AchievementEntity`, `CertificateEntity` are the meaningful candidates —
  `BookEntity`/`LessonEntity`/`VocabWordEntity`/`QuizQuestionEntity` are seeded content, not
  per-user state, and do not need to sync).
- **UI changes:** a sync-status indicator (last synced time, pending/conflict state) somewhere in
  settings/profile; no new primary screen.
- **Dependencies:** a backend is required for this to mean anything — this roadmap does not select
  one (Firebase, a custom REST API, Supabase, etc. are all viable and the choice is a product/cost
  decision outside this codebase's control, not a technical architecture decision this document
  should make unilaterally). On the client: `androidx.work:work-runtime-ktx` for background sync
  scheduling — notably, this exact dependency was **removed** from `app/build.gradle.kts` in an
  earlier phase for having zero call sites (see the `build.gradle.kts` comment explaining the
  removal) — this is the first feature in this roadmap that would legitimately re-justify adding it
  back, and should reference that history rather than silently re-adding a previously-flagged-dead
  dependency.
- **Offline strategy:** this is the crux of the whole tier — every write still goes to Room first
  (unchanged from today), sync is a background reconciliation layer on top, and every 6C screen
  must work with `syncState = PENDING` shown honestly rather than blocking the UI on connectivity.
- **Storage requirements:** negligible on-device beyond the new columns; the real cost is
  server-side, outside this document's scope.
- **Security implications:** this is the single largest security-surface change in the entire
  roadmap — it requires real user authentication (does not exist anywhere in this codebase today;
  biometric login gates *local device access*, not any identity a server could recognize), a
  network security review beyond what Phase 2/3 already did (which explicitly assumed no server
  traffic existed), and a real answer to the still-open "Room database is unencrypted" gap
  (`docs/handoff/05_RELEASE_RISK_REGISTER.md` #5) becoming materially more urgent once that data
  also traverses a network. **Do not build #18, #15, #16, #22, #26, or #29 before this is
  resolved** — they all assume sync/identity exists.
- **Implementation order:** first in 6C, hard blocker for #18/#15/#16/#22/#26/#29.
- **Estimated complexity:** **XL**.

## 18. #18 — Multi-device learning continuity

- **Architecture:** thin layer on top of #17 — once sync exists, "continuity" is simply "open the
  app on device B, `SyncEngine` reconciles, local Room state matches device A." No new engine.
- **Database/UI/Dependencies:** none beyond #17.
- **Offline strategy:** each device remains independently fully-functional offline; continuity is
  purely a sync-time property.
- **Storage/Security:** inherits #17's.
- **Implementation order:** immediately after #17 — effectively a validation/testing milestone for
  #17 more than a distinct feature.
- **Estimated complexity:** **S** (given #17 exists).

## 19. #15 — School dashboard

- **Architecture:** the true multi-student version of #13, now meaningful because #17 provides
  actual cross-device/cross-user data. `ui/screens/school/SchoolDashboardScreen.kt`, backed by a
  new server-side aggregation endpoint (not a local Room query — a school's data spans devices).
- **Database changes:** local: none new beyond #17's sync columns. Server-side schema is outside
  this document's scope (no backend is chosen in this roadmap, per #17).
- **UI changes:** new screen.
- **Dependencies:** none beyond #17.
- **Offline strategy:** requires connectivity to fetch other students' aggregated data by
  definition (this is legitimately the first feature in the whole roadmap that cannot have a
  meaningful offline mode, and should say so plainly in-product rather than pretending otherwise).
- **Storage requirements:** local cache of last-fetched aggregate data, small.
- **Security implications:** real authorization logic needed (a teacher/admin account must only see
  their own school's students) — this is access-control design work, not just a UI screen.
- **Implementation order:** after #17, alongside #16.
- **Estimated complexity:** **L**.

## 20. #16 — Institution dashboard

- Same shape as #15 at a higher aggregation level (multiple schools). Reuses the same server-side
  aggregation approach and the same authorization model, extended with an institution→schools
  hierarchy. `ui/screens/institution/InstitutionDashboardScreen.kt`.
- **Implementation order:** after #15 (shares its aggregation/authorization groundwork).
- **Estimated complexity:** **M** (given #15's groundwork).

## 21. #22 — Classroom mode

- **Architecture:** new `domain/classroom/ClassroomSession.kt` — a teacher-initiated, time-bounded
  session where a set of students' devices are logically grouped (via #17's identity layer) for
  synchronized activity (e.g. everyone doing the same #24 exam at the same time, live progress
  visible to the teacher via #13/#15).
- **Database changes:** new `ClassroomSessionEntity`, server-side primarily, with local
  `activeClassroomSessionId` state.
- **UI changes:** new `ui/screens/classroom/ClassroomHostScreen.kt` (teacher) and a joined-session
  indicator in the student's existing exam/quiz flow.
- **Dependencies:** real-time updates (teacher sees live progress) likely need a push/websocket
  channel, not just periodic sync — a meaningfully different networking primitive from #17's
  batch reconciliation, worth calling out as its own sub-decision rather than assuming #17's sync
  mechanism trivially covers it.
- **Offline strategy:** classroom mode is inherently a connected feature by definition; a
  disconnected student should fail gracefully back to normal solo exam/quiz mode, not block.
- **Storage/Security:** inherits #17's; adds session-membership authorization.
- **Implementation order:** depends on #17, #23, #24.
- **Estimated complexity:** **L**.

## 22. #26 — National leaderboard system

- **Architecture:** the true multi-user version of #25, now meaningful with #17. Server-side
  ranking computation (do not compute a "national" ranking client-side from partial data).
- **Database/UI:** local: a leaderboard view screen; no new local persistence needed (fetched,
  cached, refreshed).
- **Dependencies:** none beyond #17.
- **Offline strategy:** cached last-fetched leaderboard shown with a clear "last updated" timestamp
  when offline; cannot refresh without connectivity, by definition.
- **Security implications:** this is a public-facing ranking of (at minimum) usernames — needs an
  explicit decision on what identity is shown (should not default to real names), and interacts
  with any privacy-policy commitments in `docs/store/PRIVACY_POLICY.md` (currently DRAFT, written
  for a version of this app with no server component at all — will need a real revision once any
  6C feature ships, not just this one).
- **Implementation order:** after #17, alongside #15/#16.
- **Estimated complexity:** **M**.

## 23. #29 — Learning analytics platform

- **Architecture:** new `domain/analytics/` aggregation layer feeding #13/#14/#15/#16/#19-summary
  style views with richer statistics (trend lines, cohort comparisons) computed server-side once
  #17 exists, mirroring the same "local dashboards get richer once sync exists" pattern as #15/#16.
- **Database/UI/Dependencies/Offline/Storage/Security:** same profile as #15/#16 — server-side
  aggregation, local caching, authorization-gated.
- **Implementation order:** last in 6C — it's the synthesis layer over everything else in this
  tier, so building it earlier would mean re-deriving its inputs as they land.
- **Estimated complexity:** **L**.

## 24. #9 — AI English tutor

- **Architecture:** reuses `ai/OnDeviceTutorEngine.kt` from #8 (6B) with a different system prompt
  and target-language framing — genuinely no new engine, which is why this is tiered separately
  from #8 despite being "the same feature in a different language": #8 is core to this app's
  stated purpose (teaching Arabic) and #9 is a lower-priority extension of the same investment,
  consistent with "prioritize by educational value, not novelty."
- **Database/UI/Dependencies/Offline/Storage/Security:** identical to #8's, no new cost beyond a
  second system-prompt configuration.
- **Implementation order:** depends on #8 existing; otherwise independent of the rest of 6C.
- **Estimated complexity:** **S** (given #8 exists).

## 25. #1 — Offline Arabic OCR

- **Architecture:** new `ml/` package (sibling to `tts/`, `stt/`, `ai/`) — `ml/OcrEngine.kt`.
  **Important honesty flag:** Google's ML Kit Text Recognition v2 — the obvious first choice for
  on-device OCR — does **not** support Arabic script; its on-device models cover Latin, Chinese,
  Devanagari, Japanese, and Korean only. A real Arabic OCR path requires **Tesseract** via an
  Android wrapper (e.g. Tesseract4Android) bundled with the `ara.traineddata` language file —
  meaningfully more integration work and a materially lower out-of-the-box accuracy ceiling than
  ML Kit's Latin-script path (#2), which is exactly why this is sequenced after, and is the more
  complex sibling of, #2 within this tier.
- **Database changes:** none required for the engine; if OCR results should feed into e.g.
  vocabulary lookup, reuse the existing `VocabularyRepository` lookup path rather than a new table.
- **UI changes:** new `ui/screens/ocr/CameraOcrScreen.kt` (camera capture via CameraX) +
  a result-review screen before any text is used elsewhere in the app.
- **Dependencies:** `androidx.camera:camera-*` (CameraX, not currently a dependency), Tesseract4Android
  or equivalent.
- **Offline strategy:** fully offline once the `ara.traineddata` file (bundled or downloaded once)
  is present.
- **Storage requirements:** Tesseract Arabic trained data is realistically **~20–30MB**.
- **Security implications:** new `CAMERA` permission — this app currently requests none beyond
  `RECORD_AUDIO`/`USE_BIOMETRIC`, so this is a real, user-visible permission-surface expansion that
  needs its own justification in any Play Store data-safety disclosure
  (`docs/store/DATA_SAFETY_FORM.md`, currently DRAFT and written with no camera use assumed).
- **Implementation order:** after #2 (shares the camera-capture UI scaffold).
- **Estimated complexity:** **L**.

## 26. #2 — Offline English OCR

- **Architecture:** same `ml/OcrEngine.kt` interface as #1, backed by ML Kit Text Recognition v2's
  Latin model instead of Tesseract — genuinely simpler and higher-accuracy than #1 for this reason,
  which is why it's built first within this pair despite sharing a number-order with #1 in the
  original 30-feature list.
- **Database/UI/Offline/Security:** same shape as #1, minus the Tesseract-specific model-bundling
  concern.
- **Dependencies:** `com.google.mlkit:text-recognition` (+ CameraX, shared with #1).
- **Storage requirements:** ML Kit's Latin recognition model is bundled/downloaded by Play Services
  automatically — smaller and simpler than Tesseract's footprint, another reason to sequence this
  first.
- **Implementation order:** before #1; shares the camera scaffold both features need.
- **Estimated complexity:** **M**.

## 27. #12 — Saudi Arabic voice pack

- **Architecture:** not new infrastructure — a specific, real content entry in the `VoicePackEntity`
  catalogue introduced in #11 (6A), pointing at whatever Saudi-dialect-tuned TTS voice becomes
  available through the system TTS engine (this depends on third-party/OEM TTS engine voice
  offerings this app does not control — same OS-boundary honesty note as #11).
- **Database/UI/Dependencies/Offline/Storage/Security:** entirely inherited from #11; this entry
  adds no new mechanism.
- **Implementation order:** depends on #11 (6A) existing; also unlocks a proper Saudi-accent
  reference for #7 (accent detection, 6B) once shipped, per that entry's noted dependency.
- **Estimated complexity:** **S** (a catalogue entry, contingent on voice data actually existing to
  reference — the complexity risk here is external/content availability, not engineering).

---

# Phase 6D — Saudi Flagship Edition

Highest complexity and most novel capability in the roadmap — reserved last per "build on the
current architecture wherever possible" and "prioritize by educational value, not novelty": these
three genuinely are the most novel, least foundational items among the 30 requested.

## 28. #3 — Arabic handwriting recognition

- **Architecture:** new `ml/InkRecognitionEngine.kt` (in the same `ml/` package as #1/#2) wrapping
  **ML Kit Digital Ink Recognition** — unlike Text Recognition, ML Kit's Digital Ink Recognition
  *does* publish an Arabic-script model, so this is a materially better-supported path than #1's
  OCR situation; worth stating plainly since it's the more favorable case in this tier.
- **Database changes:** none required for the engine; if handwriting practice should be scored and
  tracked, a new `HandwritingAttemptEntity` (id, targetWord, recognizedText, score, timestamp)
  follows the same pattern as #6's `PronunciationAttemptEntity`.
- **UI changes:** new `ui/screens/handwriting/HandwritingPracticeScreen.kt` using Compose's own
  drawing/gesture APIs (`Modifier.pointerInput` + `Canvas`) to capture ink strokes, feeding them to
  the ink-recognition model for comparison against a target word from `VocabWordEntity`.
- **Dependencies:** `com.google.mlkit:digital-ink-recognition`.
- **Offline strategy:** fully offline once the Arabic ink-recognition language model (a per-language
  downloadable pack, managed by ML Kit's own `RemoteModelManager`) is downloaded once.
- **Storage requirements:** ML Kit ink-recognition language packs are typically **~20–25MB** each.
- **Security implications:** none new beyond what #1/#2 already introduce (no camera needed here —
  ink is captured directly via touch input, not imaging).
- **Implementation order:** first in 6D — #4 reuses this exact engine.
- **Estimated complexity:** **L**.

## 29. #4 — English handwriting recognition

- Same engine as #28, different ML Kit ink-recognition language pack (`en` instead of `ar`) and a
  target word source from any English content already in `VocabWordEntity.english`.
- **Implementation order:** immediately after #28, effectively free given the shared engine.
- **Estimated complexity:** **S** (given #28 exists).

## 30. #30 — Founder/Administrator control center

- **Architecture:** new `ui/screens/admin/AdminControlCenterScreen.kt` + a
  `domain/admin/AdminCapabilities.kt` gate. This is the most architecturally sensitive item in the
  entire roadmap — it implies a privileged role that can see/act across the multi-tenant data model
  #17 introduces (schools, institutions, users), which does not exist as a concept anywhere in this
  codebase today (today's security model is entirely single-device, single-user: biometric login
  gates *this device*, nothing more). This requires:
  - A real role/permission model server-side (admin/founder role distinct from teacher/parent/
    student), which is a schema and authorization decision on top of whatever #17's backend choice
    turns out to be — cannot be fully specified client-side in this document.
  - Audit logging for any administrative action (view/modify another user's data), given the
    sensitivity of what this role can touch.
- **Database changes:** local: none. Server-side: an `AdminRole`/audit-log schema, outside this
  document's scope per #17's same caveat.
- **UI changes:** new screen, gated behind the admin role check.
- **Dependencies:** none beyond #17.
- **Offline strategy:** inherently connectivity-dependent (it's administering cross-device/
  cross-user state by definition) — same honest framing as #15/#16/#22/#26.
- **Storage requirements:** negligible client-side.
- **Security implications:** this is the single highest-stakes security surface in the entire
  roadmap — a compromised or over-privileged admin credential has blast radius across every other
  user's data. This must not ship without a real security review beyond what any prior phase of
  this project has performed (every prior audit explicitly scoped itself to a single-device, no-
  backend threat model — Phase 6D invalidates that scoping and needs its own dedicated security
  audit before release, not an extension of the existing one).
- **Implementation order:** last in the entire roadmap — hard dependency on #17 and, practically,
  on #15/#16/#22/#26 existing first (there's little for an admin center to administer otherwise).
- **Estimated complexity:** **XL**.

---

# Summary table

| # | Feature | Tier | Complexity | Hard dependency |
|---|---|---|---|---|
| 19 | AI-generated quizzes (rule-based) | 6A | S | — |
| 20 | AI-generated lesson summaries (template-based) | 6A | S | — |
| 21 | AI-generated revision plans (rule-based) | 6A | M | #19 (soft) |
| 10 | Adaptive learning engine | 6A | M | #19 (soft) |
| 27 | Digital library expansion | 6A | M/L | — |
| 11 | Downloadable voice packs | 6A | M | — |
| 5 | Offline speech-to-text | 6A | L | — |
| 13 | Teacher dashboard | 6B | M | #10 |
| 14 | Parent dashboard | 6B | S | #13 |
| 23 | Assignment system | 6B | M | #13 |
| 24 | Examination system | 6B | M | #10, #23 |
| 25 | Student ranking system | 6B | S | #13 |
| 28 | Premium certificate verification | 6B | S | — |
| 6 | Advanced Arabic pronunciation scoring | 6B | L | — |
| 7 | Accent detection | 6B | L | #6 |
| 8 | AI Arabic tutor | 6B | XL | — |
| 17 | Cloud synchronization | 6C | XL | — |
| 18 | Multi-device learning continuity | 6C | S | #17 |
| 15 | School dashboard | 6C | L | #17 |
| 16 | Institution dashboard | 6C | M | #15 |
| 22 | Classroom mode | 6C | L | #17, #23, #24 |
| 26 | National leaderboard system | 6C | M | #17 |
| 29 | Learning analytics platform | 6C | L | #15, #16, #17 |
| 9 | AI English tutor | 6C | S | #8 |
| 1 | Offline Arabic OCR | 6C | L | #2 (shared UI) |
| 2 | Offline English OCR | 6C | M | — |
| 12 | Saudi Arabic voice pack | 6C | S | #11 |
| 3 | Arabic handwriting recognition | 6D | L | — |
| 4 | English handwriting recognition | 6D | S | #3 |
| 30 | Founder/Administrator control center | 6D | XL | #17, #15/#16/#22/#26 (soft) |

## What this roadmap deliberately does not do

- It does not modify any existing architecture, entity, screen, or dependency — everything above
  is additive planning, per this phase's own scoping instruction.
- It does not select a cloud backend for #17 and everything downstream of it — that's a real
  product/cost/vendor decision this document isn't positioned to make unilaterally, and every 6C
  entry above says so rather than picking one arbitrarily to look more concrete.
- It does not treat "AI-generated" as a label that excuses skipping a real technical description —
  every feature above states plainly whether it's rule-based logic or an actual ML/LLM model, and
  names the specific model/library where one is required.
- It does not change this project's current classification. `docs/handoff/07_FINAL_STATUS_REPORT.md`
  still stands as written; the next real milestone for this codebase is still the first successful
  `./gradlew assembleDebug`, independent of anything in this document.
