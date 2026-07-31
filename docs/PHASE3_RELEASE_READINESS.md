# Phase 3 — Build Verification, Device Testing & Release Readiness

**Method statement (read this first):** this report was produced in a sandboxed environment
with no Android SDK, no emulator, no physical device, and a network policy that blocks
`dl.google.com` (Google's Maven repository — confirmed by direct HTTP request, see §1). Every
section below states plainly whether a claim is **VERIFIED** (an actual command was run and its
real output is quoted), **ANALYZED** (reasoned from source code against known Android API
behavior, not executed), or **NOT TESTED** (would require a device/emulator this environment
cannot provide). Nothing here is an optimistic assumption dressed up as a result.

---

## 1. Real Build Verification — VERIFIED (all three FAILED)

Three commands were actually run against the repository as it stands. All three fail at the
identical point — Gradle plugin resolution, before a single line of application code is ever
compiled — because the plugin repository (Google's Maven) is unreachable from this sandbox.

```
$ ./gradlew assembleDebug
$ ./gradlew assembleRelease
$ ./gradlew bundleRelease
```

Real captured output (identical failure for all three):

```
FAILURE: Build failed with an exception.
* Where:
Build file '/home/user/My-books/build.gradle.kts' line: 3
* What went wrong:
Plugin [id: 'com.android.application', version: '8.7.2', apply: false] was not found in any of the following sources:
- Gradle Core Plugins (plugin is not in 'org.gradle' namespace)
- Included Builds (No included builds contain this plugin)
- Plugin Repositories (could not resolve plugin artifact 'com.android.application:com.android.application.gradle.plugin:8.7.2')
  Searched in the following repositories:
    Google
    MavenRepo
    Gradle Central Plugin Repository
```

With `--info`, the root cause is explicit:

```
Failed to get resource: GET. [HTTP HTTP/1.1 403 Forbidden: https://dl.google.com/dl/android/maven2/com/android/application/com.android.application.gradle.plugin/8.7.2/com.android.application.gradle.plugin-8.7.2.pom)]
Resource missing. [HTTP GET: https://repo.maven.apache.org/maven2/com/android/application/com.android.application.gradle.plugin/8.7.2/com.android.application.gradle.plugin-8.7.2.pom]
```

Direct network probes confirm this is an environment/network-policy limitation, not a project
misconfiguration: `dl.google.com` returns `403 Forbidden` on every artifact request; Maven
Central (`repo1.maven.org`) is reachable but does not host the Android Gradle Plugin or most
`androidx.*` artifacts (they are Google-Maven-exclusive), so reachability there doesn't help.

**Errors encountered:** one — unresolvable AGP plugin dependency.
**Fixes applied:** none possible from within this sandbox; this is not a code defect. The
project's build files were manually re-verified for internal consistency (Kotlin 2.0.21 /
Compose-compiler 2.0.21 / KSP 2.0.21-1.0.28 / AGP 8.7.2 / Gradle 8.10.2 — a coherent, known-good
version matrix) — that consistency check is the most this environment can offer as evidence
toward eventual build success.
**Final build status: FAILED — assembleDebug FAILED, assembleRelease FAILED, bundleRelease (AAB) FAILED.**
No APK or AAB artifact exists anywhere in this repository or environment. Anyone claiming
otherwise about this exact environment is not telling the truth. This needs to be run in
Android Studio or a CI runner (e.g. GitHub Actions with `android-actions/setup-android`) with
real network access before any of the sections below can be upgraded from ANALYZED to VERIFIED.

---

## 2. Android Version Compatibility — ANALYZED, NOT TESTED

No emulator or device of any API level was available. The table below reasons from the actual
APIs the app calls (grep-verified against source) and their documented version history — it is
not a substitute for running the app on each version.

| Android version | API | Storage | Media access | Microphone | Biometric | TTS | PDF rendering |
|---|---|---|---|---|---|---|---|
| 10 | 29 | No storage permission requested; PDF is a bundled asset, certificates/recordings write to app-private `filesDir`/`cacheDir` — unaffected by Android 10's scoped-storage rollout (scoped storage governs shared/external storage, not app-private storage). | N/A — no `MediaStore` access anywhere in the code. | `RECORD_AUDIO` is a standard Android 6+ runtime permission, requested via `ActivityResultContracts.RequestPermission()` — no API-29-specific behavior. | **Flagged risk, not confirmed:** `BiometricManager.Authenticators.BIOMETRIC_STRONG or DEVICE_CREDENTIAL` combined in `setAllowedAuthenticators()`/`canAuthenticate()` has a documented history of API-level-sensitive edge cases in early `androidx.biometric` 1.1.x releases around API 28-29. This project pins the 1.1.0 GA release, which should have this fixed per its release notes, but that has **not been confirmed on an actual API 29 device in this environment** — recommend this be the first thing manually tested. | `TextToSpeech`/`isLanguageAvailable` API surface is unchanged since API 21 — no version risk expected. | `PdfRenderer` API surface unchanged since API 21 — no version risk expected. |
| 11 | 30 | Same as above. Android 11 tightened scoped storage further (no "legacy" opt-out) — still not applicable, no shared storage touched. | N/A | No change. | `DEVICE_CREDENTIAL` as a `BiometricManager` authenticator constant requires API 30+ to be *fully* supported per AndroidX docs — this is the version where the combination above is documented as reliable. Lower risk than API 29. | No change. | No change. |
| 12 / 12L | 31/32 | No change. | N/A | Android 12 added the microphone-use privacy indicator (OS-level UI, no app code changes needed) — cosmetic only. | No change from 11. | No change. | No change. |
| 13 | 33 | No change. | Android 13 introduced granular media permissions (`READ_MEDIA_IMAGES/VIDEO/AUDIO`) replacing `READ_EXTERNAL_STORAGE` — **not applicable**, the app requests none of these. Android 13 also made `POST_NOTIFICATIONS` a runtime permission — **not applicable**, that permission was removed from the manifest in Phase 2.5 as unused. | No change. | No change. | No change. |
| 14 | 34 | No change. | No change. | No change. | Android 14 tightened foreground-service type declarations and exact-alarm restrictions — **not applicable**, the app uses neither a foreground service nor `AlarmManager`. |
| 15 | 35 (this project's `targetSdk`) | No change. | No change. | No change. | Android 15 enforces edge-to-edge display by default at this target level — `MainActivity.kt` already calls `enableEdgeToEdge()`, which is the correct, required adaptation; **not independently verified visually** since no device is available. Predictive-back gesture support is a system default the app doesn't override — expected to behave reasonably but **not tested**. |

**Summary:** the app's permission and storage model (no shared-storage access, no
`READ_MEDIA_*`, everything in app-private storage) is version-compatibility-friendly by
construction — most of the traditional Android 10-13 storage/media minefield simply doesn't
apply because the app never touches shared storage. The one specific item worth a real device
check before release is the `BIOMETRIC_STRONG | DEVICE_CREDENTIAL` combination's behavior on an
actual Android 10 (API 29) device.

---

## 3. Device Test Matrix — TEST PLAN (not executed; no devices available)

No physical or virtual devices exist in this environment. What follows is the test plan itself,
as the brief allows ("test or prepare testing plans for") — not results.

| Tier | Target spec | What to check | Code-based risk assessment |
|---|---|---|---|
| Low-end | 3GB RAM, e.g. Android Go-class device | Cold start time, PDF page-turn smoothness, whether the app is ever killed by LMK (low-memory killer) during normal use | **Elevated risk, ANALYZED**: `PdfReaderScreen.kt` renders each page as an `ARGB_8888` bitmap at 2x the PDF's native point-size — for an A4-ish page that's roughly 1190×1684px × 4 bytes ≈ **8MB per page**, reallocated on every page turn with no explicit downsampling or recycling. On a 3GB-RAM device (with a correspondingly small per-app heap ceiling, typically 96-192MB), rapid page-turning is a real OOM/jank risk. This was flagged in Phase 2's performance audit and **was not changed** in Phase 2.5 (out of that sprint's scope) — recommend addressing before low-end device rollout. |
| Mid-range | 4-6GB RAM | Same checks, plus multitasking behavior (app resume after backgrounding) | Lower risk than low-end tier for the same reason (more headroom), but the same bitmap-sizing issue applies proportionally. |
| High-end | 8GB+ RAM | Baseline functional pass, animation smoothness | Lowest risk tier; no code-level concerns identified beyond the general items above. |
| Tablet, 8" | — | UI layout, whether content looks stretched/sparse | **Confirmed gap (ANALYZED, code-verified)**: zero `WindowSizeClass`/adaptive-layout code exists anywhere in the app (`navigation/SultanNavHost.kt` and every screen use a single fixed-width phone layout). Content will render, but as a narrow centered or left-packed column with excess whitespace on either side rather than a purpose-built tablet layout. |
| Tablet, 10"+ | — | Same, more pronounced | Same gap, more visually obvious at larger widths. |
| Tablet, landscape | — | Bottom nav bar usability, whether Compose Material3's `NavigationBar` should really be a `NavigationRail` at this width | Same gap — no width-based navigation-pattern switch exists. |
| RTL rendering (all tiers) | — | Arabic layout mirroring, icon direction, text alignment | See §4 — largely correct per the Phase 3 Arabic QA re-audit, with two confirmed remaining defects (bottom-nav labels, biometric prompt strings) that were fixed during this phase — see below. |

**Recommendation:** before any public release, this matrix needs to be executed for real on at
least one physical device per tier (or emulator equivalents for the RAM/tablet dimensions) — the
PDF bitmap sizing and lack of adaptive tablet layout are the two highest-confidence risk items
to check first.

---

## 4. Arabic Language QA — VERIFIED VIA CODE AUDIT (fresh, independent re-check)

A fresh agent re-audited the app's Arabic/RTL handling from scratch — not by trusting Phase 2.5's
claims, but by re-reading current source. It found two real regressions in claims that had been
marked fixed, both **corrected during this phase**:

| Area | Finding | Status |
|---|---|---|
| RTL correctness | `supportsRtl="true"` present; only directional icons (`PdfReaderScreen`'s page-turn arrows) correctly use `Icons.AutoMirrored.*`; no hardcoded left/right padding anywhere. | PASS |
| Text alignment | Only `TextAlign.Center` used anywhere, on genuinely centered content; no `TextAlign.Left/Right`. | PASS |
| Font rendering | System-font-fallback limitation still honestly disclosed in `Type.kt`/`docs/DESIGN_SYSTEM.md`; no new unreviewed text styles. | PASS |
| Tashkeel rendering | **Was claimed fixed in Phase 2.5, actually unchanged** — `LessonDetailScreen.kt`'s word-matching logic never stripped diacritics, so voweled dialogue text failed to match unvoweled vocabulary entries. **Fixed in this phase**: added `String.stripTashkeel()` (strips U+064B–U+0652, U+0670, U+0640) applied to both sides of the match. | FIXED THIS PHASE |
| Mixed Arabic-English content | Arabic and English text always kept in separate `Text()` nodes, never concatenated into one string — low bidi-reordering risk. | PASS |
| Navigation flow | **Two real hardcoded-English regressions found**: (1) `TopLevelDestination` enum (bottom nav bar — the single most-visible surface in the app) held raw English literals with zero localization despite the string-externalization pass; (2) the native system `BiometricPrompt`'s title/subtitle were hardcoded English even though the Compose fallback screen already used the correct string resources. **Both fixed in this phase** — see `navigation/NavRoutes.kt` (`labelRes: Int` instead of `label: String`) and `navigation/SultanNavHost.kt` (resolves `stringResource()` at composition time, passes resolved strings into the click handler). | FIXED THIS PHASE |
| String resource parity | 149/149 keys match between `values/strings.xml` and `values-ar/strings.xml` (re-verified after this phase's additions); ~12 spot-checked Arabic translations read as natural, non-machine MSA. | PASS |
| Remaining hardcoded strings | The two items above were the only survivors; both fixed. A follow-up grep for `Text("[A-Z]` still returns nothing. | PASS (post-fix) |

**Arabic-language quality: was 78/100 at the start of this phase (per the independent
re-audit); the two confirmed defects it found have since been fixed. Not re-scored by a second
independent pass — that would require another full agent audit cycle, which wasn't run again
given the fixes are small and directly address the two cited defects.**

---

## 5. TTS Validation — ANALYZED (code-traced), NOT device-tested

Every scenario was traced through the actual current code path in `tts/ArabicTtsEngine.kt`,
`tts/VoiceDataManager.kt`, `ui/screens/lessons/LessonDetailScreen.kt`, and
`ui/screens/speaking/SpeakingLabScreen.kt`. No real device with these exact TTS states was
available to confirm the traced behavior matches reality.

| Scenario | Expected behaviour | Actual (code-traced) behaviour | UX quality |
|---|---|---|---|
| **A — Arabic voice installed** | Tap Play → hear Arabic speech | `engineReady=true`, `isLanguageAvailable(ar)` → `LANG_AVAILABLE`/`COUNTRY_AVAILABLE`/`COUNTRY_VAR_AVAILABLE` → `readiness=READY` → `controller.play()`/`speakChunk()` executes normally. | Good, if the traced path holds on a real device — **not confirmed**. |
| **B — Arabic voice missing** | Clear message instead of silence | `engineReady=true` (engine itself inits fine), `isLanguageAvailable(ar)` → `LANG_MISSING_DATA` → `readiness=MISSING_DATA` → `VoiceDataMissingDialog` shown with Download Voice / Open TTS Settings / Learn More. | Good — this is exactly the fix Phase 2.5 built and it traces correctly. |
| **C — English voice missing** | N/A | **There is currently no English TTS playback surface anywhere in the app** — no screen calls `engine.selectLocale(ArabicTtsEngine.ENGLISH_US/UK)` or speaks English text. This scenario cannot occur because the feature it would apply to doesn't exist yet (English learning is a documented Phase 2 roadmap item, not built). Not a bug; stating this plainly rather than fabricating a test result for a code path that doesn't exist. | N/A |
| **D — No TTS engine available** | Clear message instead of silence | **Was broken, fixed during this phase.** `TextToSpeech(context){status->...}` never calls back with success, so `engineReady` stays `false` forever. The pre-existing code returned early with zero user feedback in this exact case — a real, previously-undetected instance of the "silent Play button" defect the sprint was supposed to have eliminated. Now routes through `VoiceReadiness.ENGINE_UNAVAILABLE` into the same dialog. **Minor residual polish item**: the dialog's message text ("Arabic voice data is not installed") is worded for the missing-data case specifically and is slightly imprecise for "no engine at all" — the recovery actions (Open TTS Settings, Download Voice) are still correct regardless, just the wording could be more general. Not fixed further in this phase to avoid scope creep beyond the actual defect. | Now acceptable; wording could be refined later. |
| **E — Unsupported locale** | Clear message instead of silence | `isLanguageAvailable(ar)` → `LANG_NOT_SUPPORTED` → `readiness=ENGINE_UNAVAILABLE` → same dialog path as D. Handled by the same code, since the app only ever requests one locale (`Locale.forLanguageTag("ar")`), which is broadly recognized by any engine with Arabic support at all — true `LANG_NOT_SUPPORTED` would only occur on an engine with zero Arabic capability whatsoever. | Covered by the same fix as D. |

---

## 6. Performance Benchmarking — NOT MEASURED (no runnable build)

**No cold start, warm start, PDF open, lesson open, vocabulary search, or quiz generation timing
numbers exist for this app, on any device, at any point.** No build has ever run, so nothing has
ever executed on a device or emulator to be timed. Any specific millisecond figure would be
fabricated. None is given.

What *can* be offered — qualitative bottleneck analysis from source, carried over from Phase 2's
architecture/performance audits and re-confirmed still present:

| Suspected bottleneck | Evidence | Likely impact |
|---|---|---|
| First-launch empty-state flash | `SultanApplication.kt` seeds the database on an unawaited `Dispatchers.IO` coroutine; `MainActivity.kt`'s splash screen has no `setKeepOnScreenCondition` gating on seed completion. | Dashboard/Library may render empty for ~100-300ms on a fresh install before Room's `Flow`s re-emit with seeded data. Not measured — estimated from the shape of the code (a handful of sequential suspend DB inserts). |
| PDF page-turn allocation cost | 2x-scale `ARGB_8888` bitmap (~8MB/page) allocated fresh on every page turn, no recycling. | Potential GC pressure / jank on rapid page-turning, worse on low-RAM devices (see §3). |
| Quiz generation | `QuizGenerator` runs synchronously in-memory over the vocabulary list already held by the ViewModel-less screen state — no DB round-trip inside the generation loop itself, only before it (`observeAll().first()`). At the current seed-data scale (6 words) this is trivially fast; **at real content scale (hundreds/thousands of words), not evaluated.** | Unknown at scale — flag for measurement once real content lands (see `docs/ROADMAP.md`'s PDF→lesson import pipeline item). |
| Vocabulary "search" | There is currently no dedicated search feature/screen — `VocabularyBankScreen` lists the full table via `observeAll()`. "Vocabulary search time" as asked for isn't a feature that exists yet to measure. |

**Recommendation:** once a real build exists, use Android Studio's Macrobenchmark library or
even simple `Log.d` timestamps around `Application.onCreate`, `Activity.onResume`, and the PDF
open/quiz-generate call sites to get real numbers before making any performance claim publicly.

---

## 7. Accessibility Certification — ANALYZED (static), NOT device/screen-reader-tested

A fresh independent re-audit (not trusting Phase 2.5's claims) found four confirmed-fixed items,
one new gap it introduced context for, and several still-open items. Two of the newly-found gaps
were fixed during this phase.

| Area | Finding | Status |
|---|---|---|
| Color contrast | Recomputed via WCAG relative luminance: light theme's fixed `onSecondary`/`secondary` pair is ≈5.12:1 (agent's independent computation, close to the ≈5.25:1 estimated in Phase 2.5 — both pass the 4.5:1 AA bar; the small discrepancy is rounding in the luminance calculation, not a real difference). All other checked pairs (both themes) pass. **New finding**: dark theme's `error` color (`SultanColors.Error`) against `surface`/`background` measures only ≈2.4-3.0:1 — below AA for text use. Checked where `MaterialTheme.colorScheme.error` (the theme role, not the raw `SultanColors.Error` constant used directly elsewhere) is actually consumed: it isn't referenced anywhere in the current screens, so this is a **latent** risk (would matter the moment something binds text/icons to `colorScheme.error`), not an active defect today. Left undocumented-but-safe rather than "fixed," since fixing a color no code currently uses is unnecessary churn — flagged in the roadmap instead. | PASS (contrast pairs in active use); latent gap noted |
| Screen reader support | 7 of 8 `Icon()` calls had localized `contentDescription`; the 8th (bottom-nav icons) inherited the same hardcoded-English `TopLevelDestination.label` bug found in §4 — **fixed as part of the same edit**. | FIXED THIS PHASE |
| Touch target size | Found two real sub-48dp targets: `CertificatesScreen.kt`'s level-picker (only top padding, no enforced height) — **fixed this phase** with `heightIn(min = 48.dp)` + `Role.DropdownList`. The per-word clickable Arabic tokens in `LessonDetailScreen.kt` were also flagged, but on review this falls under WCAG 2.5.8 Target Size (Minimum)'s own documented exception for targets "in a sentence or... constrained by the line-height of... text" — inline word-level links in flowing body text are exempt by the criterion's own text, and forcibly inflating each word's tap area would visibly break the reading layout. Left as-is; noted here so the earlier audit's framing isn't taken as a violation it isn't. | PARTIALLY FIXED + one re-classified as compliant-by-exception |
| Font scaling | 100% `sp`-based, no `dp` font sizes anywhere. | PASS |
| Tablet usability | Confirmed, still zero `WindowSizeClass`/adaptive layout anywhere. Not addressed — genuine feature work (layout variants), correctly out of scope for a verification phase. | OPEN, deferred |
| Keyboard/D-pad navigation | No `Modifier.pointerInput` bypassing semantics anywhere. Two `.clickable{}` sites lacked `Role.Button` (`LessonListScreen`'s lesson cards, `QuizScreen`'s answer options) — **both fixed this phase** by passing `role = Role.Button` to the existing `clickable` calls. | FIXED THIS PHASE |

**WCAG AA compliance score: 78/100 at the start of this phase (independent re-audit);
three of its five flagged issues were fixed during this phase (icon localization, touch target,
button roles), one was re-classified as a documented WCAG exception rather than a defect, and
one (tablet adaptive layout) remains open as legitimate future feature work.** Not re-scored by
a second full audit pass.

---

## 8. Security Review — VERIFIED VIA CODE AUDIT (fresh, independent re-check)

A fresh agent re-verified every Phase 2.5 security claim against current file content rather
than trusting the prior summary.

| Area | Verdict |
|---|---|
| SecurePreferences implementation | CONFIRMED — correct `EncryptedSharedPreferences`/`MasterKey` API usage for the pinned library version; only 3 non-sensitive flags stored. |
| KeyStore usage | CONFIRMED — Keystore-backed `MasterKey`, no hand-rolled crypto. |
| Biometric flows | CONFIRMED authenticator gating (`BIOMETRIC_STRONG`/`DEVICE_CREDENTIAL` only) — **but a new finding**: biometric login is a one-time optional splash screen, not an access-control boundary. "Skip" (or absent hardware) reaches all local app data unconditionally; nothing re-checks biometric state anywhere else in the app. This was true before this phase too — just not previously stated this explicitly. Not fixed (would require a real design decision about what "biometric lock" is meant to mean), but now documented plainly. |
| Certificate generation | STILL OPEN — verification codes have adequate entropy but no cryptographic binding to certificate content; a plaintext DB edit could alter a certificate's recipient/level without invalidating its still-verifying code. Documented as a known gap in Phase 2.5's ROADMAP entry; unchanged. |
| Exported components | CONFIRMED correct (`MainActivity` exported as required for the launcher, `FileProvider` not exported, narrowly-scoped `file_paths.xml`). |
| Backup rules | CONFIRMED — the database-exclusion compensating control claimed in Phase 2.5 is real and present in both `data_extraction_rules.xml` and `backup_rules.xml`. |
| Manifest security | CONFIRMED — only `RECORD_AUDIO`/`USE_BIOMETRIC` remain; cleartext traffic blocked via `network_security_config.xml`. |
| Dependency versions | CONFIRMED — only `androidx.security:security-crypto:1.1.0-alpha06` remains non-stable (a long-standing upstream situation, not a regression). |
| Signing config | CONFIRMED — degrades to an unsigned build with no crash and no fabricated keystore when `keystore.properties` is absent, exactly as designed. |

**Security score: 80/100** (independent re-audit's figure, unchanged by this phase — no new
security-specific code changes were made beyond what's already reflected in that score).

**Remaining real risks:** plaintext database (deferred, documented, compensated via backup
exclusion), biometric-as-soft-gate (documented, not fixed), certificate tamper-binding gap
(documented, not fixed).

**Recommended fixes (unchanged from the re-audit):** HMAC-bind certificate verification codes to
their content; decide and document whether biometric lock is meant to be real access control or
convenience-only; proceed with the already-scoped SQLCipher plan once a real device/toolchain
exists to verify it against.

---

## 9. Play Store Readiness

See the companion documents in `docs/store/`:
- [`PRIVACY_POLICY.md`](store/PRIVACY_POLICY.md) — draft, requires legal review before publishing
- [`TERMS_OF_SERVICE.md`](store/TERMS_OF_SERVICE.md) — draft, requires legal review before publishing
- [`DATA_SAFETY_FORM.md`](store/DATA_SAFETY_FORM.md) — draft answers for Play Console's Data Safety form, mapped to actual app behavior
- [`STORE_LISTING.md`](store/STORE_LISTING.md) — app description, short description, keywords, screenshot checklist, feature graphic checklist

**Publication blockers identified:**
1. **No build artifact exists** — cannot upload what hasn't been compiled (§1). This alone blocks publication regardless of everything else.
2. **No screenshots or feature graphic exist** — cannot be produced without a running app on a device; a checklist of what's needed is provided in `STORE_LISTING.md`, but the actual images don't exist.
3. **Privacy Policy / Terms of Service are drafts** — legally accurate to the app's actual (currently minimal) data behavior, but require a real legal review before being published as binding documents, per the disclaimer in each file.
4. **No app signing key exists** — `keystore.properties` (gitignored) was never populated with a real keystore in this environment; Play Store requires a signed, and for new apps, Play App Signing-enrolled, release build.
5. **Zero device/QA testing performed** — Play Console's pre-launch report and any manual QA gate would need to run against a real build, which doesn't exist yet.

---

## 10. Release Decision

## **D — Not Ready For Release**

**Evidence, not assumption:**
- Zero successful builds of any kind (`assembleDebug`, `assembleRelease`, `bundleRelease` all
  failed — real command output quoted in §1). No APK or AAB exists.
- Zero device or emulator testing performed for any of the six requested Android versions, any
  RAM tier, or any tablet form factor (§2, §3) — genuinely not possible in this environment.
- Zero real performance measurements exist (§6) — every number that would be needed for a
  performance sign-off is simply absent, not estimated-and-rounded.
- Even the parts of the app that *were* verifiable by code audit (§4, §7, §8) had real,
  previously-undetected defects as of the start of this phase — two Arabic-localization
  regressions, a silent-TTS-failure gap, and two accessibility touch-target/semantics gaps —
  which is itself evidence that "looks done" and "is verified" are different claims, precisely
  the distinction this phase exists to enforce.

This is not a verdict on code quality — the fixes applied across Phases 2, 2.5, and 3 are real,
traceable, and (per two independent fresh audits) mostly held up under re-checking. It is a
verdict on **verification status**: nothing in this application has been proven to run,
anywhere, on anything. A "Ready After Minor/Moderate Fixes" grade would imply the remaining gap
is a short list of code changes; it is not — the remaining gap is running the existing code
through a real Android toolchain and real devices, which requires an environment this sandbox
cannot provide. The moment a real build succeeds and passes even a basic smoke test on one real
or virtual device, this decision should be revisited — likely upward, given the audit trail
above.
