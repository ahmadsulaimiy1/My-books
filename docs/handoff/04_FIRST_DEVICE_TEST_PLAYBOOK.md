# First Device Test Playbook

A literal step-by-step script for the first person to actually run this app. Written from exact
knowledge of the current UI code (not a guess) — but since no build has ever run, **every
"expected result" below is a prediction from source, not a confirmed behavior.** Where reality
diverges from what's written here, that divergence is itself the most important thing to record
— log it against `docs/handoff/02_KNOWN_ISSUES_REGISTER.md`'s format immediately.

Have `adb logcat` running and captured to a file for this entire session:
```bash
adb logcat > first_run_session.log &
```

## 1. Install the APK

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```
**Expected:** `Success` in the terminal. **If it fails:** capture the exact `adb` error — a
signature mismatch means an older version is already installed under a different signing key
(`adb uninstall com.sultan.arabicai` first); anything else, check the device's Android version
against `minSdk 26`.

## 2. First launch

1. Open the app from the launcher (icon: navy field, gold eight-pointed star).
2. **Expected:** a splash screen appears briefly, then the Onboarding screen — "A Flagship
   Standard of Arabic Mastery" headline, Royal Navy/Gold theme, "Begin Your Journey" button.
3. Tap **Begin Your Journey**.
4. **Expected:** if the device has enrolled biometrics, a biometric prompt screen appears next
   (see step 8 for that flow in detail); otherwise, you land directly on the **Executive
   Overview** (Dashboard) screen with all-zero stats (0-day streak, 0 XP).
5. **Record:** did the app crash or ANR at any point in this sequence? This is the single
   highest-value data point in this whole playbook, since first-launch behavior has literally
   never been observed before.

## 3. Creating progress (baseline for later steps)

1. From the bottom navigation bar, tap **Library**.
2. **Expected:** one book listed — "SULTAN: Intermediate Book 2" by Ahmad Sulaimiy, with **Read**
   and **Lessons** buttons.
3. Tap **Lessons**.
4. **Expected:** 3 seeded lessons listed ("At the Airport", "Shopping at the Market", "Daily
   Life"), each showing a unit number and estimated minutes.
5. Tap the first lesson.
6. **Expected:** Lesson detail screen with Arabic dialogue text, an English/Arabic title, a
   "Tap any word..." hint, and the dialogue rendered as individually-tappable Arabic word
   tokens inside a wrapping layout.
7. Tap any Arabic word that has a matching vocabulary entry (e.g. "جواز" in the airport lesson).
8. **Expected:** a dialog opens showing translation, transliteration, root letters, part of
   speech.
9. Dismiss the dialog, return to Dashboard (bottom nav → Overview).
10. **Record:** does the Dashboard still show all-zero stats at this point? (It should — nothing
    in steps 3-9 awards XP or logs a study session yet; that starts in step 5 below.)

## 4. Running TTS

1. Return to the lesson detail screen from step 3.6 above.
2. Scroll to the **Speaking Practice** card.
3. Tap the **Play** button (default reading mode: Sentence).
4. **Three possible outcomes — record which one actually happens:**
   - **(a)** Arabic speech is audible. This is Scenario A from
     `docs/PHASE3_RELEASE_READINESS.md` §5 — confirms the TTS pipeline works end to end for the
     first time ever.
   - **(b)** A "Voice Data Needed" dialog appears instead, offering "Download Voice" / "Open TTS
     Settings" / "Learn more." This is Scenario B or D — expected on a device/emulator with no
     Arabic voice data installed. Tap **Download Voice** and confirm it actually opens the
     system's voice-data manager (not a crash, not nothing).
   - **(c)** Nothing happens at all — no sound, no dialog. **This would be a Critical/High
     regression** relative to what Phases 2.5/3 specifically fixed (the "Play button does
     nothing" defect) — if this happens, it's the single most important finding to report,
     since it means a previously-fixed-and-reverified defect somehow reappeared.
5. Try the **Word** and **Paragraph** reading-mode chips, and the speed slider — confirm each
   audibly changes chunking/pace if (a) above was the outcome.
6. Try the **Loop** toggle — confirm the same chunk repeats rather than advancing.

## 5. Opening the PDF reader

1. From Library, tap **Read** on the SULTAN book.
2. **Expected:** the first page of the actual bundled PDF renders within the reader view.
3. Tap the forward-navigation arrow several times, then the back arrow — confirm both directions
   work and the page counter ("Page X of Y") updates correctly.
4. **Deliberately stress-test:** tap the forward arrow rapidly ~15-20 times in a row.
   **Record:** does the app stay responsive, or does it stutter/freeze/crash? This directly
   tests the unresolved bitmap-sizing risk (`docs/handoff/02_KNOWN_ISSUES_REGISTER.md` #7) — do
   this specifically on the lowest-RAM device available, not just a high-end one.
5. Navigate back to Library, then reopen the same book. **Expected:** it opens without re-
   triggering a full asset copy the second time (should be near-instant on reopen).

## 6. Completing a quiz

1. Return to the lesson detail screen, scroll down, tap **Start Quiz for This Lesson**.
2. **Expected:** the Assessment Centre screen, difficulty chips (Easy/Medium/Hard/Scholar), and
   a **Generate Quiz** button.
3. Tap **Generate Quiz** at the default (Medium) difficulty.
4. **Expected:** a multiple-choice question appears with 4 answer options in Arabic-prompt form.
5. Answer several questions (mix of correct and incorrect on purpose) through to the end.
6. **Expected:** an Assessment Complete screen with an accurate `X / Y correct` score.
7. Navigate to **Profile** (bottom nav) — **expected:** total XP is now non-zero, reflecting the
   quiz just completed.

## 7. Generating a certificate

1. From Profile, tap **View Certificates of Honour**.
2. Enter a recipient name, pick a level from the dropdown (confirm the dropdown itself opens and
   is tappable at a reasonable touch target — this was a specific fix target in Phase 3).
3. Tap **Issue Certificate**.
4. **Expected:** a new certificate entry appears in the list below, showing the title, recipient
   name, and a verification code.
5. Tap **Share PDF** on that certificate.
6. **Expected:** the system share sheet opens; hand it off to any app that can open a PDF (a
   file manager, email draft, etc.) and confirm the PDF actually opens and displays the
   certificate layout (Royal Navy/Gold, the eight-pointed star seal, and a scannable QR code).
7. If a QR scanner is available, scan the certificate's QR code and confirm it encodes the same
   verification code shown in the app.

## 8. Testing biometrics

**On a device/emulator with biometrics enrolled:**
1. Go to Profile, enable the **Biometric Lock** switch.
2. Fully close the app (swipe away from recent apps, not just background it).
3. Relaunch. **Expected:** the biometric login screen appears before Dashboard, prompting for
   fingerprint/face.
4. Authenticate successfully. **Expected:** proceeds to Dashboard.
5. Relaunch again, this time **cancel** the biometric prompt. **Expected:** handled gracefully
   (offers a retry or a "use passcode" fallback per the on-screen "Use passcode instead" option)
   — should not crash or hang.

**On a device/emulator with no enrolled biometrics:**
6. Confirm the Biometric Lock switch is either disabled/hidden or, if enabled anyway, that
   relaunching the app skips straight to Dashboard rather than getting stuck on an unusable
   biometric screen.

**Specifically flagged in `docs/PHASE3_RELEASE_READINESS.md` §2:** if an Android 10 (API 29)
device is available, run this entire section on it first — that's the one specific version
where the `BIOMETRIC_STRONG | DEVICE_CREDENTIAL` authenticator combination has an unconfirmed
compatibility question.

## After this session

Fill in `docs/handoff/06_INDEPENDENT_AUDIT_PACKAGE.md`'s answers with real results, and use
`docs/PHASE4_BUILD_AND_DEVICE_VALIDATION.md`'s RC1 Report Template (Part E) to write up
everything observed — bugs found, crash logs (even "none observed" is a real, required entry),
memory/battery observations if you profiled the session, and update the Go/No-Go gate checklist
with real checkmarks for whichever items this session actually satisfied.
