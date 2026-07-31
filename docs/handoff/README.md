# Engineering Handoff Package — Sultan Arabic AI

Start here if you're picking up this project for the first time with real Android Studio/SDK/
device access. Read in this order:

1. **[01_ENGINEERING_BRIEFING.md](01_ENGINEERING_BRIEFING.md)** — project purpose, architecture,
   module structure, dependency map, database schema, and how the TTS/PDF/quiz/certificate/
   security subsystems work. Read this first.
2. **[02_KNOWN_ISSUES_REGISTER.md](02_KNOWN_ISSUES_REGISTER.md)** — every unresolved issue found
   across this project's audit history, with severity, impact, recommended fix, and
   release-blocking status for each.
3. **[03_FIRST_BUILD_PLAYBOOK.md](03_FIRST_BUILD_PLAYBOOK.md)** — exact setup sequence to get a
   working build for the first time, plus troubleshooting.
4. **[04_FIRST_DEVICE_TEST_PLAYBOOK.md](04_FIRST_DEVICE_TEST_PLAYBOOK.md)** — step-by-step
   script for the first real device test session, covering every core flow.
5. **[05_RELEASE_RISK_REGISTER.md](05_RELEASE_RISK_REGISTER.md)** — every remaining risk, ranked
   highest to lowest, tagged as Proven / Suspected / Untested.
6. **[06_INDEPENDENT_AUDIT_PACKAGE.md](06_INDEPENDENT_AUDIT_PACKAGE.md)** — standalone document
   for an external reviewer with zero prior context, answering "does it compile / run / crash,
   is it secure / accessible, is it release-ready" directly.
7. **[07_FINAL_STATUS_REPORT.md](07_FINAL_STATUS_REPORT.md)** — current classification
   (**C — Advanced Prototype**) with the evidence trail supporting it and what would move it.

## The one-sentence version

Extensive, coherent, repeatedly-audited source code that has never successfully compiled or run
anywhere — your first job is simply to close that gap (playbooks 3 and 4 exist to make that
fast), and most of what you'll find when you do is probably already predicted somewhere in this
package.

## Related documents elsewhere in this repository

- [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md), [`docs/DESIGN_SYSTEM.md`](../DESIGN_SYSTEM.md),
  [`docs/ROADMAP.md`](../ROADMAP.md) — the original design/architecture/product documentation.
- [`docs/PHASE3_RELEASE_READINESS.md`](../PHASE3_RELEASE_READINESS.md) and
  [`docs/PHASE4_BUILD_AND_DEVICE_VALIDATION.md`](../PHASE4_BUILD_AND_DEVICE_VALIDATION.md) — the
  detailed audit-phase reports this handoff package summarizes and builds on. The RC1 report
  template and Go/No-Go release gate live in the latter.
- [`docs/store/`](../store/) — draft Play Store materials (privacy policy, terms of service,
  data safety form, listing copy), all marked DRAFT pending legal review.
