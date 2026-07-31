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

**Last updated:** after round 2 of real runs (commit `1d4fbeb`, the fix for round 1's errors).
Every claim below is read directly from actual GitHub Actions job logs via the GitHub API — not
inferred, not predicted.

### Build success

**Real, confirmed — Debug APK Build, round 2 (commit `1d4fbeb`):**
[run 30646062526](https://github.com/ahmadsulaimiy1/My-books/actions/runs/30646062526) — ✅
**success**. This is the first successful compile-and-package of this codebase in its entire
history. Confirmed via the GitHub API, not just the green check: the `app-debug-apk` artifact
exists, is **22,578,453 bytes**, with a real SHA-256 digest
(`48595f8f6011009bd0351a81703ce89d5efae98fa61c07619d65b9b452e0a879`), expiring
2026-08-30. Download it from that run's page → **Artifacts** section.

Release APK/AAB were not yet successful in round 2 — see below.

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

A fresh push containing this fix has been made; this file will be updated again with round 3's
real result once it completes — specifically checking that both release artifacts now build and
that `-dontwarn`-ing these classes didn't silently break anything else, by confirming the
resulting APK/AAB files exist and have plausible non-zero sizes.
