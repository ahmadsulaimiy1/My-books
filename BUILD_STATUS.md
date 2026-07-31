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

**As of the commit that introduced this pipeline, no workflow run has completed yet — this
section will be updated with the real result of the first run once GitHub Actions has actually
executed it**, following this project's standing rule of never reporting an untested outcome as
if it were verified. Do not treat the sections below as predictions of success; they're the
categories this file will be filled in against once real run data exists.

### Build success

*(To be filled in from the actual run.)* A successful run means: the job completed with a green
check, the named artifact appears in the run's Artifacts section, and downloading it produces a
valid, non-empty `.apk`/`.aab` file.

### Build failure

*(To be filled in from the actual run, if it occurs.)* A failed run means the job stopped with a
red X before producing an artifact — the Gradle command's `--stacktrace` output (enabled in all
three workflows) will be in that step's log.

### Errors encountered

*(To be filled in with the exact error text from the first real run, if any — not a guess.)*

### Required fixes

*(To be filled in with the exact fix applied for each error above, once diagnosed against real
CI output — this project's whole prior audit history was static-analysis-only precisely because
no real compiler output existed anywhere; this is the first opportunity to close that gap for
real.)*
