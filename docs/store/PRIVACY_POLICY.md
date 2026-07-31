# Privacy Policy — Sultan Arabic AI (DRAFT)

**Status: DRAFT.** This document was generated from a direct reading of the app's actual code —
every claim below is grounded in what the app's manifest, permissions, and data-handling code
actually do as of this writing, not aspirational language. It has **not** been reviewed by a
lawyer and must not be published as-is. Have qualified counsel review it — particularly the
jurisdiction, contact information, and children's-privacy sections — before it goes live.

_Last updated: [DATE — fill in at publication]_

## Summary

Sultan Arabic AI is designed to work entirely offline. As of this version, **the app has no
internet permission and cannot transmit any data anywhere** — everything it stores stays on your
device.

## Information We Collect

The app processes the following categories of information, all of it stored locally on your
device only:

- **Voice recordings.** If you use the Speaking Lab feature, your microphone recording is saved
  to the app's private, app-only storage area on your device. It is used only for local
  playback so you can compare it to a reference pronunciation. It is overwritten each time you
  record again and is never transmitted anywhere.
- **Learning progress and content data.** Lesson completion, vocabulary review history, quiz
  results, achievement/rank progress, and any notes or bookmarks you create are stored in a
  local database on your device.
- **Certificate information.** If you generate a certificate, the recipient name you enter is
  stored locally and embedded in the certificate PDF file saved to your device.
- **Biometric authentication.** If you enable fingerprint/face unlock, authentication is handled
  entirely by your device's operating system (Android's BiometricPrompt system). The app never
  receives, stores, or has access to your actual fingerprint or facial data — only a
  success/failure signal from the operating system.
- **App preferences.** A small number of settings (whether biometric lock is enabled, whether
  onboarding is complete) are stored in encrypted local storage on your device.

## Information We Do Not Collect

The app does not collect, and has no technical capability to collect (it does not request
Internet access), any of the following: your name or contact details (other than a certificate
recipient name you choose to type in, which stays on-device), location data, contacts, camera
data, advertising identifiers, analytics/usage telemetry, or crash reports.

## How Your Information Is Used

All information listed above is used exclusively to provide the app's core functionality on
your device: tracking your learning progress, letting you review your own vocabulary and
recordings, and generating certificates you request. None of it is used for advertising,
profiling, or any purpose beyond delivering the feature you directly interacted with.

## Data Sharing

We do not share, sell, rent, or transmit any of your data to any third party, because the app
has no network access with which to do so.

## Data Storage and Security

- Session and authentication flags are stored using Android's encrypted storage (AES-256-GCM
  `EncryptedSharedPreferences`, backed by the Android Keystore).
- Learning-progress and certificate data are stored in a local database that is **not**
  currently encrypted at rest. [DEVELOPER NOTE: correct this section if/when database
  encryption ships — see `docs/ROADMAP.md`'s "Security debt: database encryption" entry.]
- Voice recordings are stored unencrypted in the app's private cache directory, inaccessible to
  other apps under normal Android sandboxing.
- The database is excluded from Android's automatic backup system as a precaution.

## Your Choices

- You can decline microphone permission; the Speaking Lab feature simply won't be available.
- You can decline biometric enrollment; the app remains fully usable without it.
- Uninstalling the app removes all locally stored data.

## Children's Privacy

[DEVELOPER/LEGAL NOTE: this section needs a deliberate decision, not a default. If the app is
marketed to or likely to be used by children under 13 (or the relevant age in your
jurisdiction), you likely need a COPPA-compliant policy (US) and/or equivalent under
applicable Saudi/GCC or other regional child-data regulations, potentially including parental
consent flows before any microphone-recording feature is used by a child. As shipped, the app
does not ask the user's age and does not gate any feature by age. Do not publish this section
without a legal determination on your actual target audience.]

## Changes to This Policy

We may update this policy as the app's features change — most notably if a future version adds
network connectivity, cloud sync, or an account system (see the app's public roadmap). Material
changes will be reflected with an updated "Last updated" date above.

## Contact

[DEVELOPER NOTE: insert a real, monitored contact email/address before publishing — Play Store
requires a working contact method for privacy inquiries.]
