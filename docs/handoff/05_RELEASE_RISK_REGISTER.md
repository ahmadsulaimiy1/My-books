# Release Risk Register

Ranked highest to lowest overall risk (severity × likelihood × how much of the release this
would affect). Each row is tagged with one of three evidence categories:

- **Proven** — confirmed by direct evidence: an actual command run with captured output, an
  actual computed value (e.g. a WCAG contrast ratio from real hex codes), or an actual grep/read
  of current source confirming a pattern exists. Not a guess.
- **Suspected** — reasoned from known Android/library behavior and this project's actual code,
  but not directly confirmed against this exact build on this exact device/version. A informed
  hypothesis, not a measurement.
- **Untested** — genuinely unknown. No execution has ever occurred, so there is no way to have
  evidence one way or the other yet.

| Rank | Risk | Category | Why it's ranked here |
|---|---|---|---|
| 1 | **The project has never been confirmed to build successfully anywhere with real tooling.** | Proven (fails in every sandboxed environment used so far, root-caused to a network policy blocking Google's Maven repo) / Untested (whether it builds cleanly on a normal developer machine — the configuration itself was independently re-verified as internally consistent in Phase 4, which is a positive signal, but consistency isn't proof of a clean build) | Everything else on this list is conditional on this resolving. Highest possible rank by definition. |
| 2 | **Zero device execution has ever occurred — the app's actual runtime behavior (crashes, hangs, rendering) is completely unknown.** | Untested | Direct consequence of #1. This is the single largest unknown in the entire project. |
| 3 | PDF page bitmaps are ~8MB each at the current 2x render scale, reallocated on every page turn with no recycling or downsampling cap. | Proven (the size is a real arithmetic fact from `page.width*2 * page.height*2 * 4 bytes` in `PdfReaderScreen.kt`) for the *cause*; Suspected for the *consequence* (jank/OOM on low-RAM devices — plausible and specifically flagged three separate times across Phases 2/3, but never actually observed since nothing has run) | High-probability, high-visibility failure mode on exactly the device tier (low-RAM/budget) most likely to matter for broad Arabic-learner reach. |
| 4 | No automated tests exist anywhere in the repository. | Proven (confirmed absence of `src/test`/`src/androidTest`) | Not a runtime risk itself, but it means every other item on this list has to be re-verified by hand after every future change, indefinitely, until this is fixed. |
| 5 | The Room database is unencrypted and holds PII (certificate recipient names, full learning history). | Proven (confirmed no encryption wrapper anywhere in `AppDatabase.kt`) | Real exposure on a rooted/debuggable device or an unintended backup path; deliberately deferred with a documented compensating control (backup exclusion), not an oversight — but still a real open exposure. |
| 6 | The `BIOMETRIC_STRONG \| DEVICE_CREDENTIAL` authenticator combination may have unresolved edge-case behavior on Android 10 (API 29) specifically, per `androidx.biometric`'s documented history around that API level. | Suspected | Narrow version-specific scope keeps this from ranking higher, but biometric failures are high-visibility when they do occur (a broken launch-time gate blocks the whole app for affected users). |
| 7 | First-launch database seeding is unawaited and the splash screen isn't gated on its completion — the Dashboard/Library may render visibly empty for a brief window on a fresh install before data appears. | Suspected (the race condition is real and traceable in code; the actual visible duration/severity has never been observed) | Cosmetic-to-moderate first-impression risk, self-corrects within the same session. |
| 8 | Seeded lesson/vocabulary content is placeholder/representative, not the real SULTAN Book 2 curriculum. | Proven (explicitly documented in `ContentSeeder.kt` and `docs/ROADMAP.md`) | Not a crash/security risk, but a real gap between "what the app claims to teach" and "what it actually contains" today — release-blocking specifically for any release positioned as delivering the real curriculum. |
| 9 | Real-world performance (cold start, warm start, PDF/lesson/quiz open times) is completely unmeasured. | Untested | Can't be ranked by severity because there's no data — ranked here on the assumption that *something* in a Compose+Room+PdfRenderer app this size is likely to need tuning, not because a specific problem is known. |
| 10 | Real-world accessibility (actual TalkBack screen-reader pass, actual keyboard/switch-access navigation) has only been evaluated by static code analysis, never with a real assistive-technology session. | Untested (a WCAG-AA-adjacent static score of ~78/100 exists from Phase 3's independent re-audit, but that is not the same claim as "verified accessible in practice") | Real screen-reader behavior regularly surfaces issues static analysis misses (focus order, announcement timing, custom-component semantics gaps). |
| 11 | OEM-specific TTS engine behavior (Samsung TTS, Huawei TTS, or other non-Google engines) is unverified — the code targets the standard `android.speech.tts.TextToSpeech` API generically, but voice-availability detection and quality vary by OEM engine in ways this project's `VoiceDataManager` can only detect, not control. | Suspected/Untested | Affects a meaningful share of the real Android device population (non-Pixel/non-stock devices), but the detection-and-recovery path (Phase 2.5/3's dialog fix) should at minimum prevent a silent failure even where TTS quality varies. |
| 12 | No tablet-adaptive layout exists (`WindowSizeClass` or equivalent) — every screen is a fixed phone-width column. | Proven (confirmed zero adaptive-layout code anywhere) | Real but scoped: affects visual polish on tablets specifically, not core functionality, and correctly deferred as feature work across every "no new features" phase since Phase 2.5. |
| 13 | Certificate verification codes have no cryptographic binding to certificate content. | Proven | Low likelihood of exploitation today (no public verification surface exists to exploit), so ranked low despite being a real gap. |
| 14 | `androidx.security:security-crypto` is pinned to a long-standing alpha release with no stable alternative currently available. | Proven | Supply-chain/policy concern for some organizations; functionally stable in practice for years. Lowest-ranked open risk. |

## By category (same items, regrouped for quick scanning)

**Proven (7):** #3 (cause only), #4, #5, #8, #12, #13, #14
**Suspected (4):** #3 (consequence), #6, #7, #11 (partial)
**Untested (4):** #1 (partial), #2, #9, #10, #11 (partial)

(Some items legitimately span two categories, as noted inline in the table — that's an honest
reflection of "we know the mechanism is real but not its real-world consequence," not
double-counting.)
