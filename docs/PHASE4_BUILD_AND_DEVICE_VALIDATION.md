# Phase 4 — Real-World Compilation & Device Validation

**Method statement:** this phase re-verified every build-configuration file directly against
its actual current content (quoted below, not recalled from memory) and confirmed the Gradle
wrapper mechanism itself works in this environment (`./gradlew --version` succeeds, real output
below). It found **zero configuration defects** — every version pin is internally consistent
with what Phase 1-3 established. Per this phase's instruction ("do not write code unless a
defect is identified"), **no source files were changed in this phase.** The blocker remains
exactly what Phase 3 documented: this sandbox cannot reach Google's Maven repository
(`dl.google.com` → HTTP 403), so no dependency can ever be resolved here, regardless of how
correct the configuration is. Everything below is written for a developer working in an
environment that *does* have that access.

---

## Part A — Build Readiness Package

### A.1 Repository compilation readiness (verified against current file content)

| Item | Value | Verified from | Status |
|---|---|---|---|
| Gradle wrapper | 8.10.2 | `gradle/wrapper/gradle-wrapper.properties` | **Mechanically confirmed working** — `./gradlew --version` in this environment actually reports `Gradle 8.10.2` (real output below). Only dependency resolution fails, not the wrapper itself. |
| Android Gradle Plugin | 8.7.2 | `build.gradle.kts` line 4 | Internally consistent with Gradle 8.10.2 (AGP 8.7.x requires Gradle ≥8.9) |
| Kotlin | 2.0.21 | `build.gradle.kts` line 5 | Consistent |
| Compose compiler plugin | 2.0.21 | `build.gradle.kts` line 6 | **Must equal the Kotlin version exactly** — confirmed identical |
| KSP | 2.0.21-1.0.28 | `build.gradle.kts` line 7 | Correctly prefixed with the Kotlin version it targets |
| Compose BOM | 2024.12.01 | `app/build.gradle.kts` lines 81, 116 | Applied consistently to both `implementation` and `androidTestImplementation` |
| compileSdk / targetSdk | 35 (Android 15) | `app/build.gradle.kts` lines 23, 28 | Consistent |
| minSdk | 26 (Android 8.0) | `app/build.gradle.kts` line 27 | Sufficient for every API actually used (`PdfRenderer`, `BiometricPrompt` DEVICE_CREDENTIAL, `EncryptedSharedPreferences`, adaptive icons) |
| JVM target | 17 | `app/build.gradle.kts` lines 60-61, 65 | Consistent between `sourceCompatibility`/`targetCompatibility`/`kotlinOptions` |
| All other dependency versions | Room 2.6.1, Navigation Compose 2.8.5, Biometric 1.1.0, security-crypto 1.1.0-alpha06, ZXing 3.5.3, Coroutines 1.9.0, core-ktx 1.15.0, core-splashscreen 1.0.1, lifecycle 2.8.7, activity-compose 1.9.3, fragment-ktx 1.8.5 | `app/build.gradle.kts` dependencies block | No version conflicts identified; `security-crypto` remains pinned to an alpha (a known, long-standing upstream situation documented since Phase 2, not a new issue) |
| Signing configuration | Conditional — reads `keystore.properties` (gitignored) if present, else release build is unsigned | `app/build.gradle.kts` lines 15-19, 35-44, 50-52 | Correctly degrades with no crash and no fabricated secrets when the file is absent (true in this repo) |
| Build variants | 2: `debug`, `release`. No product flavors. | `app/build.gradle.kts` lines 46-57; confirmed zero `flavorDimensions`/`productFlavors` blocks exist | Simple, single-dimension variant space |
| NDK / native code | **None required** | Confirmed via repo-wide search — zero `external fun`, `System.loadLibrary`, or `externalNativeBuild`/`ndk {}` blocks anywhere | No NDK installation needed |

Real wrapper verification output from this environment:
```
$ ./gradlew --version
------------------------------------------------------------
Gradle 8.10.2
------------------------------------------------------------
Kotlin:        1.9.24
Launcher JVM:  21.0.10 (Ubuntu 21.0.10+7-Ubuntu-124.04)
Daemon JVM:    /usr/lib/jvm/java-21-openjdk-amd64
OS:            Linux 6.18.5 amd64
```
(The "Kotlin 1.9.24" line is Gradle's *own* embedded Kotlin, unrelated to this project's Kotlin
2.0.21 — not a version conflict, just Gradle-internal tooling.)

### A.2 Complete build package for a developer

| Requirement | Version | Notes |
|---|---|---|
| Android Studio | **Ladybug (2024.2.1) or newer** | Ladybug is the first stable Studio release bundling AGP 8.7.x by default, matching this project's pin. Newer Studio versions (Meerkat/Narwhal and later) also work — Studio's Gradle/AGP integration is decoupled from the IDE version for an already-pinned project like this one. |
| JDK | **17 minimum** (required by AGP 8.7.x to run Gradle itself) | This environment confirmed the Gradle *wrapper mechanism* also runs cleanly on JDK 21 (see A.1) — 17 is the documented floor, 21 is not excluded, but only 17 has been treated as the target here since that's what `sourceCompatibility`/`kotlinOptions.jvmTarget` are pinned to. Android Studio bundles its own compatible JDK by default; using that is the simplest path. |
| Android SDK Platform | **API 35** (compileSdk/targetSdk) — install via SDK Manager | Also install **API 26** (or an AVD system image at/above it) as the practical minimum test target, matching `minSdk`. |
| Android SDK Build-Tools | Matching AGP 8.7.2's default (34.x or 35.x, whichever Studio/SDK Manager resolves automatically for this AGP version) | Let Android Studio auto-resolve this — do not pin manually unless a specific CI reproducibility need arises. |
| Android SDK Platform-Tools | Latest available | Provides `adb`, required for device installation/testing (Part C below). |
| Android Emulator + a system image | Optional, only if testing on a virtual device rather than / in addition to physical hardware | Recommend at minimum one API 26 image (minSdk floor) and one API 35 image (targetSdk ceiling) per Phase 3's compatibility matrix. |
| NDK | **Not required** — confirmed no native code exists in this project (A.1). Do not install unless a future feature needs it. |
| Network access | Must reach `dl.google.com` / `maven.google.com` and `repo1.maven.org` (or an internal mirror of both) | This is the exact blocker Phase 3 hit in the sandboxed environment; any normal developer machine or CI runner with standard internet access will not have this problem. |

**Build commands:**
```bash
# Debug build — produces an installable, debug-signed APK automatically
# (AGP auto-generates/uses ~/.android/debug.keystore; no setup needed)
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk

# Release build — UNSIGNED unless keystore.properties exists (see below)
./gradlew assembleRelease
# Output: app/build/outputs/apk/release/app-release-unsigned.apk (no keystore.properties)
#      or app/build/outputs/apk/release/app-release.apk (signed, keystore.properties present)

# Android App Bundle (AAB) — the format Play Store requires for new submissions
./gradlew bundleRelease
# Output: app/build/outputs/bundle/release/app-release.aab
```

**To produce a signed, distributable release build:**
```bash
cp keystore.properties.example keystore.properties   # then fill in real values
# NEVER commit keystore.properties or the keystore file itself — both are gitignored
./gradlew assembleRelease bundleRelease
```

**Installing to a connected device/emulator:**
```bash
./gradlew installDebug            # builds + installs the debug variant in one step
# or, once an APK exists:
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

**Supporting commands referenced elsewhere in this doc:**
```bash
./gradlew lint                    # Android Lint report → app/build/reports/lint-results-*.html
./gradlew clean                   # wipe build outputs before a clean-room verification run
```

---

## Part B — Compilation Checklist

Every item below is a real pass/fail check to run in a real environment. None of these have
been checked in this sandbox (Part A already explains why); check them for real before treating
any of Part C onward as applicable.

- [ ] Gradle sync completes in Android Studio with no errors
- [ ] `./gradlew clean` succeeds
- [ ] `./gradlew assembleDebug` succeeds
- [ ] `app-debug.apk` exists at `app/build/outputs/apk/debug/`
- [ ] `./gradlew assembleRelease` succeeds (with `keystore.properties` present, for a real distributable build)
- [ ] `app-release.apk` exists at `app/build/outputs/apk/release/` and is signed (verify with `apksigner verify app-release.apk`)
- [ ] `./gradlew bundleRelease` succeeds
- [ ] `app-release.aab` exists at `app/build/outputs/bundle/release/`
- [ ] `./gradlew lint` completes and the report contains no new `Fatal`/`Error`-severity findings beyond what's already documented in Phase 2/3
- [ ] Debug APK installs on at least one physical device via `adb install` or `./gradlew installDebug`
- [ ] Debug APK installs on at least one emulator (API 26 image)
- [ ] Debug APK installs on at least one emulator (API 35 image)
- [ ] Release APK installs on at least one physical device (confirms real signing works, not just debug-signing)
- [ ] App launches to the onboarding screen with no crash on first install
- [ ] App launches directly to the Dashboard with no crash on a second launch (onboarding already complete)

---

## Part C — Device Test Checklist

One checklist per core flow. Run this on every device in Phase 3's device/version matrix that
actually becomes available; do not extrapolate a pass on one device to "verified" for others.

**First launch**
- [ ] Splash screen displays and dismisses without hanging
- [ ] Onboarding screen renders correctly (Royal Navy/Gold theme, no layout clipping)
- [ ] "Begin Your Journey" proceeds to either biometric login (if available) or Dashboard
- [ ] No crash, no ANR dialog, during the entire first-launch sequence

**Lesson reading**
- [ ] Library screen lists the bundled SULTAN book
- [ ] Lessons screen lists seeded lessons
- [ ] Lesson detail screen renders Arabic dialogue text correctly (no mojibake, no reversed text)
- [ ] Tapping a vocabulary word inside the dialogue opens the word-detail dialog with correct data
- [ ] Grammar focus section renders both Arabic and English text correctly

**PDF reader**
- [ ] Opening the bundled book from Library loads without crashing
- [ ] First page renders visibly within a reasonable time (no numeric target exists yet — see Phase 3 §6; just confirm it isn't hung or blank)
- [ ] Page-forward and page-back navigation both work
- [ ] Rapid repeated page-turning does not crash or visibly stall the UI (this is the specific low-RAM-device risk flagged in Phase 3 §3 — test deliberately, not just casually)
- [ ] Reopening the same book on a second visit doesn't crash (validates the asset-cache-copy logic runs correctly on repeat)

**Vocabulary lookup**
- [ ] Vocabulary Bank screen lists all seeded words
- [ ] Favorite toggle persists after navigating away and back
- [ ] "Mark difficult" toggle persists after navigating away and back
- [ ] Flashcard review flow presents due cards and accepts all four grade levels (Again/Hard/Good/Easy) without crashing

**Quiz generation**
- [ ] Selecting a difficulty and tapping "Generate Quiz" produces a non-empty quiz
- [ ] Multiple-choice answers can be selected, and correct/incorrect feedback displays with the correct color coding
- [ ] Completing a quiz reaches the results screen with an accurate score
- [ ] XP/rank progress updates after quiz completion (visible on Profile screen after navigating there)

**Speaking Lab**
- [ ] Microphone permission prompt appears and both Allow/Deny paths are handled without crashing
- [ ] "Hear Native Voice" triggers TTS playback (or the voice-missing dialog — see TTS checklist below) rather than doing nothing
- [ ] "Record My Voice" / "Stop Recording" cycle completes and produces a playable recording
- [ ] "Play My Recording" plays back the just-recorded audio
- [ ] Backgrounding the app mid-recording and returning does not leave the mic silently active (validates the Phase 2.5 lifecycle fix — check the system mic-in-use indicator disappears on backgrounding)

**TTS playback** (cross-reference Phase 3 §5's five scenarios — confirm each for real)
- [ ] Case A (Arabic voice installed): speech is audible and reasonably intelligible
- [ ] Case B (Arabic voice missing): the voice-missing dialog appears with working Download Voice / Open TTS Settings actions, not silence
- [ ] Case D (no TTS engine at all — hard to stage on a normal device, but check if a suitable test device/emulator config is available): dialog still appears, does not silently no-op
- [ ] Word / Sentence / Paragraph reading-mode chips each produce audibly different chunking
- [ ] Speed slider audibly changes playback rate
- [ ] Loop toggle causes the current chunk to repeat rather than advancing

**Certificate generation**
- [ ] Selecting a level and tapping "Issue Certificate" produces a new certificate entry
- [ ] The generated PDF opens correctly outside the app (via the Share action) and displays the expected layout, seal, and QR code
- [ ] The QR code scans successfully with a generic QR reader and encodes the expected verification code
- [ ] "Share PDF" opens a real share sheet and successfully hands off the file to at least one other app (e.g. a file manager or email client)

**Biometric authentication**
- [ ] On a device with enrolled biometrics, enabling "Biometric Lock" in Profile and relaunching the app prompts for biometric auth
- [ ] Successful authentication proceeds to Dashboard
- [ ] Cancelling/failing authentication is handled gracefully (does not crash, offers a retry or passcode fallback)
- [ ] On a device with **no** enrolled biometrics, the biometric login screen is skipped entirely rather than getting stuck
- [ ] Test specifically on one Android 10 (API 29) device per Phase 3 §2's flagged compatibility risk for the `BIOMETRIC_STRONG | DEVICE_CREDENTIAL` combination

---

## Part D — Bug Triage Framework

| Severity | Definition | Examples from this project's own audit history |
|---|---|---|
| **Critical** | Crashes, data loss, security exposure, or a core flow (Part C) that cannot be completed at all on a supported device/OS version. | The achievement-reset-on-every-launch bug (Phase 2, fixed) — silent data loss on every session. A hypothetical crash on PDF open would also be Critical. |
| **High** | A core flow completes but produces visibly wrong behavior, or a defect that affects a large share of users/devices even if a workaround exists. | The TTS silently-no-oping when voice data is missing (Phase 2/3, fixed) — the feature appears broken with no explanation. |
| **Medium** | A real defect confined to a secondary flow, an edge case, or a specific device/locale segment, with a viable workaround. | The tashkeel-matching gap (Phase 3, fixed) — degrades word-lookup accuracy for fully-voweled text but doesn't block the flow. |
| **Low** | Cosmetic, minor inconsistency, or a defect with negligible real-world impact. | The `PdfReaderScreen` header showing only `titleEn` and not `titleAr` (Phase 3, noted, not fixed) — inconsistent with `LibraryScreen`'s treatment but not user-blocking. |

**Release-blocking criteria:**
- **Any open Critical defect blocks release**, unconditionally.
- **Any open High defect in a Part C core flow blocks release** unless a product owner explicitly accepts the risk in writing (name + date), and even then only for a defect confirmed to affect a narrow, named device/OS segment.
- Medium and Low defects do not block release by default, but must be logged and triaged into a post-release fix plan — "logged" means an actual issue tracker entry exists, not just a mention in a chat transcript.
- A defect found only via static/code-audit (as in Phases 2-3 here) and never actually reproduced on a device is not yet triage-able by this framework at all — it must first be confirmed to reproduce for real (or explicitly marked "unable to reproduce — code path may be unreachable in practice") before a severity assignment means anything.

---

## Part E — Release Candidate (RC1) Report Template

Copy this template and fill it in after a real build + device test pass. Every field is
mandatory; "N/A" is only acceptable with a one-line reason.

```markdown
# Sultan Arabic AI — Release Candidate Report

RC version: RC1
Report date:
Reported by:

## Build status
- assembleDebug:            [ PASS / FAIL ] —
- assembleRelease:          [ PASS / FAIL ] —
- bundleRelease (AAB):      [ PASS / FAIL ] —
- Build tool versions used: AGP __, Gradle __, JDK __, Android Studio __

## Device(s) tested
| Device | Android version | RAM | Form factor | Result |
|---|---|---|---|---|

## Core flow results (Part C checklist)
| Flow | Result | Notes |
|---|---|---|
| First launch | | |
| Lesson reading | | |
| PDF reader | | |
| Vocabulary lookup | | |
| Quiz generation | | |
| Speaking Lab | | |
| TTS playback | | |
| Certificate generation | | |
| Biometric authentication | | |

## Bugs found
| ID | Severity | Flow | Description | Reproducible? |
|---|---|---|---|---|

## Crash logs
(Paste real `adb logcat` stack traces or attach files. "None observed" is a valid, real entry —
do not omit this section even if empty.)

## Memory observations
(Real numbers from Android Studio Profiler or `adb shell dumpsys meminfo <package>` — device,
peak RSS during PDF reading, any OOM/LMK events observed. "Not measured" if genuinely not done.)

## Battery observations
(Real numbers from `adb shell dumpsys batterystats` or on-device battery usage screen after a
timed usage session — device, session length, % drain, whether the mic/TTS lifecycle fix
(Phase 2.5) actually prevents background drain in practice.)

## Accessibility observations
(Real TalkBack pass results — which screens were tested with TalkBack enabled, what was
announced correctly vs. not, whether the static-analysis findings from Phase 3 §7 held up when
actually using a screen reader.)

## Final recommendation
[ ] Promote to RC2 candidate for wider testing
[ ] Ready for release pending Critical/High fixes listed above
[ ] Not ready — [reason]
```

---

## Part F — Go / No-Go Release Gate

The application **cannot** be considered released until every item below is checked, and every
check is backed by real evidence (a build log, an install confirmation, a completed device test
checklist, or a bug tracker query) — not a status update asserting it happened.

- [ ] **APK built successfully** — `assembleDebug` and `assembleRelease` both pass (Part B)
- [ ] **AAB built successfully** — `bundleRelease` passes (Part B)
- [ ] **Installed on at least one physical Android device** — not an emulator substitute for this specific gate item
- [ ] **Core learning flow completed successfully** — First launch → Lesson reading → Quiz generation, end to end, on the physical device above
- [ ] **TTS verified** — at minimum Case A and Case B from Part C's TTS checklist confirmed on a real device
- [ ] **PDF reader verified** — book opens, pages turn, survives rapid page-turning without crashing
- [ ] **Certificate generation verified** — a real certificate PDF was generated, opened, and its QR code scanned successfully
- [ ] **No Critical defects remain open** — per Part D's definition, verified against a real issue tracker, not this document's memory

**Current status of this gate, as of this phase: 0 of 8 items checked.** Every item requires a
real build and real device, neither of which exist yet in any environment this project has been
developed in so far (see Part A's opening note). This is the same conclusion as Phase 3's
Release Decision (D — Not Ready For Release), restated here in the specific checklist form this
phase asked for — the underlying evidence hasn't changed because the underlying blocker
(network access to build the project at all) hasn't changed.
