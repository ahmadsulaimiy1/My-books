# Independent Audit Package

**Purpose of this document:** give an external reviewer — someone with zero prior context on
this project — everything needed to answer six specific questions, using only what's in this
repository. Each answer states the current evidence-backed status and exactly where to find
more detail or how to generate fresh evidence. Read this document standalone; it does not
assume you've read anything else in `docs/`.

**What this project is, in one paragraph:** Sultan Arabic AI is a native Android app (Kotlin +
Jetpack Compose) for learning Arabic offline, built around a bundled textbook. It has never been
compiled or run in any environment used during its development so far (explained below) — this
package exists specifically so a reviewer with real tooling can generate the missing evidence
and answer these questions for real.

---

## Q1: Does it compile?

**Current answer: Unknown in general; confirmed FAILING in the specific sandboxed environment
this project was developed in.**

Real evidence (not a guess): running `./gradlew assembleDebug` in that environment produces:
```
FAILURE: Build failed with an exception.
* What went wrong:
Plugin [id: 'com.android.application', version: '8.7.2', apply: false] was not found...
Failed to get resource: GET. [HTTP HTTP/1.1 403 Forbidden: https://dl.google.com/...]
```
Root cause: that environment's network policy blocks Google's Maven repository outright. The
project's build configuration itself was independently re-verified as internally consistent
(matching Kotlin/Compose-compiler/KSP/AGP/Gradle versions, no NDK requirement, no product
flavors) — see `docs/handoff/03_FIRST_BUILD_PLAYBOOK.md` for the exact setup sequence and
`docs/PHASE4_BUILD_AND_DEVICE_VALIDATION.md` Part A for the full version-consistency table.

**To answer this for real:** run the First Build Playbook (`docs/handoff/
03_FIRST_BUILD_PLAYBOOK.md`) on a machine with normal internet access. It should take under 15
minutes including first-sync download time.

## Q2: Does it run?

**Current answer: Unknown — has never been installed on any device or emulator.**

There is no evidence either way. The First Device Test Playbook (`docs/handoff/
04_FIRST_DEVICE_TEST_PLAYBOOK.md`) is a literal step-by-step script — install, first launch,
every core flow — written from direct source code knowledge with explicit predicted outcomes
for each step, but every prediction is labeled as exactly that: a prediction, not a confirmed
result.

**To answer this for real:** complete Q1 first (you need a build artifact), then work through
the Device Test Playbook and record actual results against each predicted outcome.

## Q3: Does it crash?

**Current answer: Unknown — no execution has occurred to crash or not crash.**

No crash logs exist because nothing has run. `docs/handoff/02_KNOWN_ISSUES_REGISTER.md` #7 is
the single most likely first-crash candidate if one occurs (PDF page bitmaps at ~8MB each with
no recycling, on a low-RAM device/emulator during rapid page-turning) — worth testing that
specific scenario deliberately rather than only casually using the app.

**To answer this for real:** run `adb logcat` capture throughout the Device Test Playbook
session (the playbook already instructs this). Any crash — or explicitly, the absence of one —
is real, reportable evidence either way; "no crashes observed in this session" is a valid and
useful finding, not a non-answer.

## Q4: Is it secure?

**Current answer: Partially verified by code audit; not verified by any dynamic/runtime
security testing (no build exists to test against).**

What's been checked (via direct code reading, independently re-audited multiple times across
this project's history rather than trusting any single pass):
- ✅ Biometric login correctly restricted to `BIOMETRIC_STRONG`/`DEVICE_CREDENTIAL` authenticators only
- ✅ Session/auth flags encrypted at rest (`EncryptedSharedPreferences`, Keystore-backed)
- ✅ No cleartext network traffic possible (network security config blocks it; moot since the app requests no `INTERNET` permission at all)
- ✅ Manifest permissions minimized (only `RECORD_AUDIO`, `USE_BIOMETRIC` remain, confirmed unused ones removed)
- ✅ Exported components correctly scoped (only the launcher `Activity` is exported, as required; `FileProvider` is not exported)
- ⚠️ **Open, documented gap:** the main Room database is unencrypted plaintext, holding some PII (certificate recipient names). A compensating control (excluded from Android backup) is in place; full encryption was deliberately deferred rather than implemented unverified. See `docs/ROADMAP.md`'s "Security debt: database encryption" section.
- ⚠️ **Open, documented gap:** certificate verification codes have no cryptographic tamper-binding to their content.
- ⚠️ **Characteristic, not a bug:** biometric lock is a launch-time convenience gate, not enforced access control elsewhere in the app — accurate to describe, inaccurate to market as "securing your data."

Full detail: `docs/handoff/01_ENGINEERING_BRIEFING.md`'s Security subsystem section,
`docs/handoff/02_KNOWN_ISSUES_REGISTER.md` items #1-4, and the original Phase 2/Phase 3 security
audits referenced there.

**To answer this more completely:** a real penetration test / dynamic security review against
an actual running build would be the natural next step this project has never had access to.

## Q5: Is it accessible?

**Current answer: Statically analyzed at ~78/100 WCAG-AA-adjacent (independent code-audit
score, Phase 3); never tested with a real screen reader.**

What's been checked via code audit (re-verified independently, not just trusted from an earlier
pass): color contrast ratios (computed via the real WCAG relative-luminance formula against
actual hex values — one failing pair was found and fixed), `contentDescription` coverage on
icons, touch-target sizing (two real sub-48dp targets found and fixed, one initially-flagged
case re-classified as a legitimate WCAG exception for inline text links), font-scaling (100%
`sp`-based, confirmed compliant), semantic roles on custom clickable components (added where
missing). Full detail in `docs/PHASE3_RELEASE_READINESS.md` §7 and
`docs/handoff/02_KNOWN_ISSUES_REGISTER.md` #8-9.

**What's explicitly not been checked:** an actual TalkBack pass reading through every screen, an
actual switch-access or D-pad-only navigation session, and real-world behavior on any assistive
technology. Static analysis catches a meaningful subset of accessibility issues but not all of
them (focus order and announcement timing in particular need a live session to verify).

**To answer this more completely:** enable TalkBack on a test device, navigate every screen in
the Device Test Playbook using only TalkBack gestures, and record what's actually announced vs.
expected.

## Q6: Is it ready for release?

**Current answer: No — see `docs/handoff/07_FINAL_STATUS_REPORT.md` for the full classification
and evidence.** In short: a large, coherent, repeatedly-audited codebase with real, working
architecture (verified by extensive manual code reading, not by execution) that has never
successfully compiled or run anywhere. The Go/No-Go gate in
`docs/PHASE4_BUILD_AND_DEVICE_VALIDATION.md` Part F is 0 of 8 items checked, for that reason.

---

## What to do with this package

1. Work through `docs/handoff/03_FIRST_BUILD_PLAYBOOK.md` to get Q1 (compile) answered for real.
2. Work through `docs/handoff/04_FIRST_DEVICE_TEST_PLAYBOOK.md` to get Q2/Q3 (run/crash) answered.
3. Cross-reference `docs/handoff/02_KNOWN_ISSUES_REGISTER.md` and
   `docs/handoff/05_RELEASE_RISK_REGISTER.md` while testing — most of what you find will already
   be predicted there; anything you find that *isn't* predicted is the most valuable kind of new
   information, since it means the static-analysis-only verification process this project relied
   on missed something real.
4. Fill in `docs/PHASE4_BUILD_AND_DEVICE_VALIDATION.md`'s RC1 Report Template (Part E) with real
   results.
5. Revisit `docs/handoff/07_FINAL_STATUS_REPORT.md`'s classification once real evidence exists —
   it should almost certainly move, likely upward, once even one real successful build-and-run
   cycle completes.
