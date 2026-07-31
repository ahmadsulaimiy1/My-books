# First Build Playbook

Written for someone who has never seen this project before and is building it for the first
time. Follow the steps in order. Every version number here was re-verified directly against the
current repository files as of Phase 5 — if any step's actual output disagrees with what's
printed here, trust your terminal over this document and check whether the underlying config
file has changed since this was written.

## Prerequisites

1. **Install Android Studio Ladybug (2024.2.1) or newer.** Download from
   `developer.android.com/studio`. This project pins Android Gradle Plugin 8.7.2, which Ladybug
   bundles by default; newer Studio versions also work fine with a pinned-version project like
   this one.
2. During Android Studio's first-run setup wizard, let it install:
   - **Android SDK Platform 35** (the app's `compileSdk`/`targetSdk`)
   - **Android SDK Platform 26** (or at least one emulator system image at API 26, the app's
     `minSdk` floor) if you intend to test against the minimum supported version
   - **Android SDK Build-Tools** (let Studio auto-resolve the version matching AGP 8.7.2)
   - **Android SDK Platform-Tools** (provides `adb`)
   - **Android Emulator** + at least one system image, if you don't have a physical test device
     handy yet
3. JDK: Android Studio bundles a compatible JDK by default — use that unless you have a specific
   reason not to. If configuring manually, this project requires **JDK 17 minimum** (AGP 8.7.x's
   documented floor for running Gradle itself); JDK 21 has also been confirmed to run the Gradle
   wrapper mechanics without issue in prior testing of this exact repository.
4. **NDK: not required.** This project has zero native/JNI code — do not install it unless a
   future feature needs it.
5. Confirm you have normal internet access reaching `dl.google.com` / `maven.google.com` and
   `repo1.maven.org` (or an internal mirror covering both). This is the exact thing that was
   *not* available in the sandboxed environment this project was developed in — if you're
   reading this on a normal developer machine or CI runner, you almost certainly have it, but
   it's worth confirming first if anything below fails at dependency resolution.

## Setup sequence

1. **Clone the repository** and `cd` into it.
2. **Open the project root in Android Studio** (File → Open → select the folder containing
   `settings.gradle.kts`). Do not open the `app/` subfolder directly.
3. **Let Gradle sync run automatically.** Android Studio triggers this on project open. Watch
   the "Build" panel at the bottom. First sync will download the Gradle 8.10.2 distribution
   (already pinned in `gradle/wrapper/gradle-wrapper.properties`) plus every dependency listed
   in `docs/handoff/01_ENGINEERING_BRIEFING.md`'s dependency map — this can take several minutes
   on first run depending on connection speed.
4. **If sync succeeds:** proceed to step 5. **If it fails:** see Troubleshooting below before
   doing anything else — do not start editing code to "fix" a sync failure that's actually an
   environment/tooling issue.
5. From a terminal at the repo root (or use Android Studio's Gradle panel / Run button
   equivalently):
   ```bash
   ./gradlew assembleDebug
   ```
   Expect a signed, installable APK at `app/build/outputs/apk/debug/app-debug.apk` (debug builds
   are auto-signed by AGP using a default debug keystore — no setup needed for this step).
6. **Confirm the build actually produced a file:**
   ```bash
   ls -la app/build/outputs/apk/debug/app-debug.apk
   ```
7. Proceed to `docs/handoff/04_FIRST_DEVICE_TEST_PLAYBOOK.md` once step 6 succeeds.

## Release / signed build (only once debug build is confirmed working)

1. Copy `keystore.properties.example` (repo root) to `keystore.properties`.
2. Generate a real keystore if you don't have one:
   ```bash
   keytool -genkeypair -v -keystore sultan-release.keystore -alias sultan-release \
     -keyalg RSA -keysize 2048 -validity 10000
   ```
3. Fill in `keystore.properties` with the real `storeFile` (absolute path), `storePassword`,
   `keyAlias`, `keyPassword`. **Never commit this file or the keystore** — both are already
   gitignored; double check `git status` shows neither before any commit.
4. ```bash
   ./gradlew assembleRelease bundleRelease
   ```
   Expect `app/build/outputs/apk/release/app-release.apk` (signed) and
   `app/build/outputs/bundle/release/app-release.aab`.

## Troubleshooting

**Gradle sync fails with a plugin/dependency resolution error mentioning `dl.google.com` or
similar (403, timeout, or "could not resolve"):**
This is the exact failure mode documented throughout this project's audit history
(`docs/PHASE3_RELEASE_READINESS.md` §1) — but there, it was a genuine network policy block in a
sandboxed environment. On a normal machine, the same symptom usually means a corporate
proxy/firewall, VPN, or DNS issue is blocking Maven repository access. Check:
- Can you `curl -I https://dl.google.com` (or your organization's Maven mirror) successfully
  from the same machine/network?
- Does Android Studio have proxy settings configured correctly (Settings → Appearance & Behavior
  → System Settings → HTTP Proxy)?
- Is a corporate VPN required to reach internal Maven mirrors, and is it connected?

**"SDK location not found" / `local.properties` missing:**
Android Studio normally generates `local.properties` (gitignored, machine-specific) automatically
on first sync pointing at your SDK install. If it's missing, create it manually:
```
sdk.dir=/path/to/your/Android/sdk
```

**"You have not accepted the license agreements":**
Run `sdkmanager --licenses` from the SDK's `cmdline-tools/latest/bin/` directory, or accept
licenses through Android Studio's SDK Manager UI (Settings → Languages & Frameworks → Android
SDK → SDK Tools tab prompts this automatically for missing components).

**KSP or Compose-compiler version mismatch errors:**
This project pins Kotlin 2.0.21, the Compose compiler plugin at exactly 2.0.21, and KSP at
2.0.21-1.0.28 (`build.gradle.kts`). If you've modified any of these independently, they must
stay in lockstep — the Compose compiler plugin version must equal the Kotlin version exactly,
and KSP's version must be prefixed with the Kotlin version it targets.

**Gradle daemon / cache issues after a partial or interrupted first sync:**
```bash
./gradlew --stop        # kill any stuck Gradle daemons
rm -rf ~/.gradle/caches  # last resort — forces a clean re-download of everything
```

**Build succeeds but the app crashes immediately on launch:**
This has never been observed (no build has ever run to see it) — if it happens, capture
`adb logcat` output immediately and start with `docs/handoff/02_KNOWN_ISSUES_REGISTER.md` to see
if it matches a documented risk (the PDF bitmap sizing item is the most likely first-crash
candidate on a low-RAM emulator/device) before assuming it's something new.

**Everything above succeeds and you have a working debug APK:** congratulations — this
repository's audit trail (Phases 2 through 4) never got this far in any of its own development
environments. You are now in a position to generate actual evidence instead of code-review
analysis. Please update `docs/PHASE4_BUILD_AND_DEVICE_VALIDATION.md`'s Part B checklist and Go/
No-Go gate with real results.
