# Google Play Data Safety Form — Draft Answers

**Status: DRAFT.** These are draft answers for Play Console's Data Safety questionnaire, mapped
directly to the app's actual current permissions and code (verified by reading
`AndroidManifest.xml` and the data-handling code, not assumed). **Re-verify against the actual
app version being submitted** — this form is legally binding when submitted to Google Play and
must be re-done if the app's data behavior changes (e.g. when cloud sync ships per the roadmap).

## Does your app collect or share any of the required user data types?

Based on current app behavior: **No data is collected or shared**, in Play Console's specific
sense of "collected" (transmitted off the device). Rationale:

- The app requests no `INTERNET` permission (confirmed absent from `AndroidManifest.xml` as of
  the Phase 2.5 stabilization pass) and has zero networking code anywhere in the codebase — it
  is technically incapable of transmitting data off the device.
- Google's own Data Safety guidance states that data processed and stored only locally, never
  transmitted off-device, does not need to be declared as "collected" for this form's purposes.

If Play Console's specific wording requires declaring on-device processing anyway, use the
following mapping:

| Data type | Collected? | Shared? | Purpose | Notes |
|---|---|---|---|---|
| Audio recordings (voice) | On-device only | No | App functionality (Speaking Lab playback/comparison) | Recorded via `RECORD_AUDIO`, saved to app-private cache, overwritten per take, never transmitted |
| Personal info — name | On-device only | No | App functionality (certificate recipient name) | User-typed, stored locally, embedded in a locally-generated PDF |
| App activity | On-device only | No | App functionality (learning progress, quiz results, achievements) | Stored in a local database |
| App info and performance | Not collected | No | — | No crash reporting, no analytics SDK integrated |
| Device or other identifiers | Not collected | No | — | No advertising ID, no device fingerprinting |
| Location | Not collected | No | — | No location permission requested |
| Financial info | Not collected | No | — | No payment features exist |

## Is all of the user data collected by your app encrypted in transit?

Not applicable — no data leaves the device.

## Do you provide a way for users to request that their data be deleted?

Yes, functionally: uninstalling the app removes all app-private data (the local database,
cache, and encrypted preferences). [DEVELOPER NOTE: Play Console may still require an explicit
in-app or web-based data-deletion mechanism/link depending on current policy at submission
time — confirm current Play Console requirements, as these have changed over time and this
draft cannot guarantee it reflects the policy version in effect when you submit.]

## Security practices section

- Data is encrypted in transit: N/A (no transmission occurs).
- Data is encrypted at rest: **Partially.** Session/authentication flags are encrypted
  (AES-256-GCM via `EncryptedSharedPreferences`). The main learning-progress/certificate
  database is **not** encrypted at rest as of this version — answer this question accurately
  (not "yes") until that changes; see `docs/ROADMAP.md`'s database-encryption entry.
- Users can request data deletion: see above.
- Independent security review: [DEVELOPER NOTE: state truthfully whether one has occurred —
  this repository's own audit history (docs/PHASE2 findings, this Phase 3 document) is an
  internal code-level review, not a substitute for a third-party penetration test if Play
  Console's question specifically asks about that.]

## Target audience / children's section

[DEVELOPER/LEGAL NOTE: this cannot be answered generically — it requires a real decision about
the app's intended age range, which affects both this form and the Privacy Policy's children's
section. Do not submit a Data Safety form with a placeholder answer here.]
