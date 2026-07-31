# Build Status

This file tracks the real, evidence-based status of the automated GitHub Actions build pipeline
for Sultan Arabic AI. It exists specifically to replace guesswork with actual CI run results —
see the "Current status" section below for what's actually been observed, and "How to read a run"
for how to interpret any run yourself. This is a living document: it gets updated with real
findings after CI runs, not written once and left stale.

## Why this file exists

Every environment this project was previously developed in had no Android SDK and no network
access to Google's Maven repository (`dl.google.com`), so `./gradlew assembleDebug` had never
actually succeeded anywhere — see `docs/handoff/07_FINAL_STATUS_REPORT.md` for the full audit
trail behind that. GitHub Actions runners have normal, unrestricted internet access and a
preconfigured Android toolchain, which removes that specific blocker entirely. The three
workflows in `.github/workflows/` (`debug-apk.yml`, `release-apk.yml`, `release-aab.yml`) exist to
get this project its first real, independently-verifiable compilation result — on every push, not
just once.

## The three workflows

| Workflow file | What it builds | Gradle task | Artifact name (as uploaded) |
|---|---|---|---|
| `.github/workflows/debug-apk.yml` | Debug APK (auto-signed with AGP's built-in debug keystore) | `./gradlew assembleDebug` | `app-debug-apk` → `app/build/outputs/apk/debug/app-debug.apk` |
| `.github/workflows/release-apk.yml` | Release APK (signed if secrets configured, otherwise unsigned) | `./gradlew assembleRelease` | `app-release-apk` → `app/build/outputs/apk/release/*.apk` |
| `.github/workflows/release-aab.yml` | Release Android App Bundle (for Play Store upload) | `./gradlew bundleRelease` | `app-release-aab` → `app/build/outputs/bundle/release/*.aab` |

All three trigger on **every push to every branch** and can also be run manually
(`workflow_dispatch`) from the Actions tab. All three use JDK 17 (Temurin), the Gradle wrapper
already committed in this repository (Gradle 8.10.2, matching `gradle/wrapper/gradle-wrapper.properties`),
and install Android SDK Platform 35 + Build-Tools 35.0.0 — matching this project's pinned
`compileSdk`/`targetSdk = 35` in `app/build.gradle.kts` exactly, not just "whatever's latest."
Gradle dependency caching is enabled via `actions/setup-java`'s built-in `cache: gradle` option.

### Where to find the downloadable files after a run

GitHub Actions → this repository → the workflow run in question → scroll to the **Artifacts**
section at the bottom of the run summary page. Each artifact is a zip containing the one file
named in the table above. Artifacts are retained for 30 days per run.

Direct paths (adjust `<owner>/<repo>` and branch as needed):
`https://github.com/ahmadsulaimiy1/My-books/actions/workflows/debug-apk.yml`
`https://github.com/ahmadsulaimiy1/My-books/actions/workflows/release-apk.yml`
`https://github.com/ahmadsulaimiy1/My-books/actions/workflows/release-aab.yml`
— each page lists every run of that workflow; click a run to reach its Artifacts section.

## Signing status (release APK / AAB)

`app/build.gradle.kts` already contains conditional signing logic from earlier in this project's
history: if a `keystore.properties` file exists at the repo root, the release build type is
signed with it; if it doesn't, the release build type gets no `signingConfig` at all and Gradle/
AGP produce an **unsigned** artifact instead. The two release workflows extend that exact same
logic into CI, unmodified — they don't add a new signing mechanism, they just optionally
materialize `keystore.properties` from repository secrets before the existing Gradle logic runs.

**To add real signing** (once a real release keystore exists), add these four **Actions secrets**
(Settings → Secrets and variables → Actions → New repository secret) on this repository:

| Secret name | Value |
|---|---|
| `KEYSTORE_BASE64` | Your `.keystore`/`.jks` file, base64-encoded: `base64 -w0 your-release.keystore` (Linux) or `base64 -i your-release.keystore \| tr -d '\n'` (macOS) |
| `KEYSTORE_PASSWORD` | The keystore's store password |
| `KEY_ALIAS` | The signing key's alias inside that keystore |
| `KEY_PASSWORD` | The signing key's password (often the same as the store password) |

All four must be present for either release workflow to attempt signing — if even one is missing,
both workflows fall back to an unsigned build automatically rather than failing. Never commit the
keystore file or these values anywhere in the repository itself — Actions secrets are the only
place they should live. This mirrors `keystore.properties.example`'s local-build equivalent
(`docs/handoff/03_FIRST_BUILD_PLAYBOOK.md`'s "Release / signed build" section) — same four values,
different delivery mechanism.

## Current status

**Last updated:** after round 3 of real runs (commit `dc9d72a`, the fix for round 2's R8 error).
**All three workflows are green.** Every claim below is read directly from actual GitHub Actions
job logs and artifact metadata via the GitHub API — not inferred, not predicted.

### Build success

**Real, confirmed — all three workflows, round 3 (commit `dc9d72a`):**

| Workflow | Run | Artifact | Size | SHA-256 |
|---|---|---|---|---|
| Debug APK Build | [run 30646718591](https://github.com/ahmadsulaimiy1/My-books/actions/runs/30646718591) | `app-debug-apk` | 22,578,451 bytes | `3c7a1ca93bac46f37ed83ae9a00e1f1fe4358b50adbb00c1e4ee6ab14892d950` |
| Release APK Build | [run 30646720410](https://github.com/ahmadsulaimiy1/My-books/actions/runs/30646720410) | `app-release-apk` | 5,697,383 bytes | `d99b90e77342a82ba10a757adc74e57d1661a525966ab56f320cfea858011866` |
| Release AAB Build | [run 30646718605](https://github.com/ahmadsulaimiy1/My-books/actions/runs/30646718605) | `app-release-aab` | 8,370,745 bytes | `e00bb1e88cd01eafb023ebb4e464dc19c0dda6f7532f2850161df78f53e79230` |

This is the first time in this project's entire history that a complete, real
compile-shrink-package cycle has succeeded for all three build variants. All artifacts expire
2026-08-30 (30-day retention) — download from each run's page → **Artifacts** section before then,
or just push again to regenerate them.

**Signing status:** the release APK/AAB are **unsigned** — no `KEYSTORE_BASE64`/
`KEYSTORE_PASSWORD`/`KEY_ALIAS`/`KEY_PASSWORD` secrets have been added to this repository (see
"Signing status" section above for exactly how to add them). This is expected, not an error —
`app/build.gradle.kts`'s existing conditional logic falls back to unsigned automatically when
`keystore.properties` doesn't exist, and the same is true here.

It took three rounds of real, evidence-based fixes to get here — each one a genuine defect this
project's years of static-analysis-only audits could describe as *possible* but never *confirm*:

### Build failure

**Round 1 (commit `2e03ab0`) — all three workflows failed identically** at
`:app:compileDebugKotlin` / `:app:compileReleaseKotlin` with two real Kotlin errors (unresolved
`TextToSpeech.Engine.ACTION_TTS_SETTINGS` and an invalid `import
androidx.compose.foundation.lazy.item`) — full detail in git history of this file, fixed in commit
`1d4fbeb`.

**Round 2 (commit `1d4fbeb`) — Release APK and Release AAB still failed, Kotlin compilation now
passes cleanly on all three:**

| Workflow | Run | Conclusion |
|---|---|---|
| Debug APK Build | [run 30646062526](https://github.com/ahmadsulaimiy1/My-books/actions/runs/30646062526) | ✅ success |
| Release APK Build | [run 30646060542](https://github.com/ahmadsulaimiy1/My-books/actions/runs/30646060542) | ❌ failure |
| Release AAB Build | [run 30646061495](https://github.com/ahmadsulaimiy1/My-books/actions/runs/30646061495) | ❌ failure |

Both release workflows got past Kotlin compilation this time and failed at a later step,
`:app:minifyReleaseWithR8` — real, measurable progress from round 1, not a new unrelated problem.

### Errors encountered

Exact text from the real job logs (identical in both Release APK and Release AAB runs):

```
> Task :app:minifyReleaseWithR8 FAILED
ERROR: Missing classes detected while running R8. Please add the missing classes or apply
additional keep rules that are generated in .../app/build/outputs/mapping/release/missing_rules.txt.
ERROR: R8: Missing class com.google.errorprone.annotations.CanIgnoreReturnValue (referenced from:
  com.google.crypto.tink.KeysetManager ... and 52 other contexts)
Missing class com.google.errorprone.annotations.CheckReturnValue (referenced from:
  com.google.crypto.tink.InsecureSecretKeyAccess and 1 other context)
Missing class com.google.errorprone.annotations.Immutable (referenced from:
  com.google.crypto.tink.InsecureSecretKeyAccess and 40 other contexts)
Missing class com.google.errorprone.annotations.RestrictedApi (referenced from:
  com.google.crypto.tink.aead.AesEaxKey$Builder ... and 6 other contexts)
Missing class javax.annotation.Nullable (referenced from:
  java.lang.Object com.google.crypto.tink.PrimitiveSet$Entry.fullPrimitive and 86 other contexts)
Missing class javax.annotation.concurrent.GuardedBy (referenced from:
  com.google.crypto.tink.proto.Keyset$Builder ... and 3 other contexts)
com.android.tools.r8.CompilationFailedException: Compilation failed to complete
```

**Root cause:** `androidx.security:security-crypto` (used for `EncryptedSharedPreferences`, see
`security/` in `01_ENGINEERING_BRIEFING.md`) pulls in Google Tink as a transitive dependency, and
Tink's own code references several compile-time-only annotation classes
(`com.google.errorprone.annotations.*`, `javax.annotation.Nullable`,
`javax.annotation.concurrent.GuardedBy`) that are never actually present at runtime and are not a
real dependency of this app. R8 treats any referenced-but-absent class as a hard error unless
told it's safe to ignore. This is a well-documented, standard caveat of shipping Tink through R8
— not a bug introduced by this project — but `app/proguard-rules.pro` never had the corresponding
`-dontwarn` rules, because (per that file's own header comment) **it had never been run through a
real R8 pass until this CI run**. This is exactly the gap that comment predicted, now closed with
real evidence instead of a guess.

### Required fixes

Applied directly (commit following `1d4fbeb`):

1. **`app/proguard-rules.pro`**: added
   `-dontwarn com.google.errorprone.annotations.**`, `-dontwarn javax.annotation.**`, and
   `-dontwarn javax.annotation.concurrent.**` — telling R8 these specific missing annotation
   classes are safe to ignore (they're never invoked at runtime, only referenced in Tink's source
   for static analysis tooling that isn't present here either).

**Round 3 (commit `dc9d72a`) confirmed the fix worked** — see "Build success" above. The
`-dontwarn` rules didn't silently break anything else: both release artifacts exist with
plausible, non-trivial sizes (5.7MB APK, 8.4MB AAB), not zero-byte or truncated files.

## What this proves, and what it still doesn't

**Proven, for real, for the first time in this project's history:** this codebase compiles, its
Kotlin is valid, its Compose UI graph resolves, its R8/minification configuration is complete
enough to produce a real shrunk release build, and its Gradle/AGP/dependency configuration is
internally consistent end to end on a normal, unrestricted-network machine (a GitHub-hosted
runner). That directly answers the open question at the top of
`docs/handoff/06_INDEPENDENT_AUDIT_PACKAGE.md` Q1 ("Does it compile?") — yes, confirmed, with a
real artifact and a real SHA-256 digest as evidence, not an estimate.

**Still not proven — CI compiling successfully is not the same as the app working:** nothing
here confirms the app installs, launches, or behaves correctly on a device or emulator (Q2/Q3 in
that same document), nor does it touch accessibility, performance, or security testing status
(Q4/Q5). `docs/handoff/07_FINAL_STATUS_REPORT.md`'s classification should be revisited in light of
this — compiling for the first time is real, positive evidence, but the report's own bar for
reclassifying to **D (Production Candidate)** is "one clean install-and-launch on a physical
device," which this CI pipeline does not and cannot provide (GitHub Actions runners have no
Android device/emulator attached in this configuration). That remains the next real milestone.
