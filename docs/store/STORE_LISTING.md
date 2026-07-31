# Play Store Listing — Draft Copy & Asset Checklists

**Status: DRAFT copy**, written to accurately describe what the app actually does today (per
the codebase), not aspirational marketing beyond that. Revise before publishing if features
change. **The screenshot and feature-graphic checklists are checklists, not delivered
assets** — no images can be produced without a running app on a real device, which does not
exist yet (see `docs/PHASE3_RELEASE_READINESS.md` §1).

## Short description (max 80 characters for Play Store)

> Offline Arabic learning: lessons, TTS, flashcards, quizzes & speaking practice.

(79 characters — leaves no room for "AI" branding claims that the app can't fully back up yet;
adjust once/if the Phase 3+ roadmap items land.)

## Full description (draft)

```
Sultan Arabic AI — Learn Arabic, Fully Offline

Built around SULTAN: Saudi Ultimate Language Training of Arabic for Non-Natives (Intermediate
Book 2) by Ahmad Sulaimiy, Sultan Arabic AI is a premium, offline-first Arabic learning
companion for Android.

WHAT YOU GET
• A digital library with the bundled SULTAN textbook, readable entirely offline
• Interactive lessons — tap any Arabic word for its translation, root letters, and grammar
• Offline Arabic text-to-speech with word, sentence, and paragraph reading modes, adjustable
  speed, and loop/repeat controls for pronunciation practice
• A spaced-repetition vocabulary bank and flashcard system that adapts to what you find hard
• On-device quiz generation from your own vocabulary — no internet connection required
• A Speaking Lab to record yourself, compare against native pronunciation, and practice
• Gamified progress — XP, a nine-tier rank system from Beginner to Grand Scholar, streaks, and
  achievements
• Luxury certificates with QR verification as you complete milestones
• Biometric login and encrypted session storage

WORKS WITHOUT THE INTERNET
Every core feature — lessons, vocabulary, quizzes, text-to-speech, and progress tracking —
works with no network connection at all. The app requests no internet permission.

WHO IT'S FOR
Intermediate learners of Arabic as a foreign language working through structured, curriculum-
based lessons rather than casual phrasebook apps.

[DEVELOPER NOTE: do not publish superlative claims ("world's most advanced," "AI-powered
tutor," etc.) that the current build doesn't substantiate — see docs/ROADMAP.md for exactly
what's implemented vs. planned. Overclaiming in a store listing is a Play Store policy risk,
not just a marketing judgment call.]
```

## Keywords / search terms (for ASO — not a Play Store form field, but useful for the
description and metadata)

`arabic learning`, `learn arabic offline`, `arabic vocabulary`, `arabic flashcards`, `arabic
text to speech`, `arabic pronunciation`, `arabic quiz`, `intermediate arabic`, `arabic reading`,
`spaced repetition arabic`, `arabic speaking practice`

Avoid: `AI tutor`, `handwriting recognition`, `OCR`, `Quran memorization` — none of these are
built features as of this version; using them as keywords risks a misleading-listing policy
flag from Play Store review, independent of any marketing intent.

## Screenshot checklist (assets do not exist — none can be captured without a running build)

Play Store requires 2-8 phone screenshots minimum (plus optional 7"/10" tablet screenshots).
Once a real build exists and runs on a device/emulator, capture:

- [ ] Onboarding / welcome screen (shows the Royal Navy/Gold design identity)
- [ ] Executive Overview (Dashboard) with real (non-empty) progress data
- [ ] Digital Library showing the bundled book
- [ ] Lesson detail screen with the tap-word dictionary popup open
- [ ] Speaking Practice controls (reading mode + delivery preset chips) mid-interaction
- [ ] Vocabulary Bank or Flashcard review screen
- [ ] Quiz in progress, showing a question with answer options
- [ ] Scholar Profile showing rank badge + achievements
- [ ] A generated certificate (the actual PDF render, or the in-app certificate card)
- [ ] Arabic-locale (RTL) versions of at least 2-3 of the above, since the app is bilingual —
      Play Store supports localized screenshots per listing locale

## Feature graphic checklist (1024×500px banner — asset does not exist)

- [ ] Design incorporating the Royal Navy Blue (#082A66) / Royal Gold (#C9A961) palette and the
      eight-pointed star (khatim) seal motif already used for the launcher icon and certificates
      (see `docs/DESIGN_SYSTEM.md`), so the store presence matches the in-app identity
- [ ] App name + a short tagline, legible at small/thumbnail size
- [ ] No screenshot-in-a-phone-frame collage — Play Store's current design guidance favors a
      clean, simple graphic over a busy composite
- [ ] Export at exactly 1024×500px, JPG or 24-bit PNG (no alpha), per current Play Console specs
      at time of upload — verify against Play Console's live requirements, which can change

## App icon

Already exists in the codebase (`res/mipmap-anydpi-v26/ic_launcher.xml` — an adaptive icon using
the eight-pointed star seal on a Royal Navy field). Play Store requires a 512×512px PNG export
of this for the listing itself, separate from the in-app adaptive icon — generate this from the
vector source once a build toolchain is available (Android Studio's Image Asset tool or a
manual vector-to-PNG export at that resolution).

## Content rating questionnaire

[DEVELOPER NOTE: complete Play Console's content rating questionnaire honestly based on actual
app content — this app has no violence, no user-generated public content, no in-app purchases
in its current form, and is educational. Expected to rate very permissively (e.g. "Everyone"),
but the actual questionnaire must be completed in Play Console directly, not assumed here.]
