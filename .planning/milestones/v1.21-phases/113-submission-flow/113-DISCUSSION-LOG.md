# Phase 113: Submission Flow - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-03
**Phase:** 113-submission-flow
**Areas discussed:** Target repo, Sanitization, Dedup fingerprint, Submit guardrails

---

## Target repository (SUB-01)

| Option | Description | Selected |
|--------|-------------|----------|
| henols/firestarter_app (hardcoded) | Host-CLI repo where the ONBOARD-04 doc lives and gsd-inbox triage runs; hardcoded constant, no cwd-remote inference | ✓ |
| henols/firestarter (firmware) | Route to the firmware repo since chip support is firmware-rooted; hardcoded constant | |
| Configurable (const default + override) | Hardcoded default overridable via flag/env | |

**User's choice:** henols/firestarter_app (hardcoded)
**Notes:** Fixed maintainer-repo target both tiers; a tester's fork must never receive their own report → no cwd git-remote inference. (D-01)

---

## Sanitization strategy (SUB-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Whitelist-rebuild + scrub free-text | Build body from a re-whitelisted field set + scrub reason/mismatch/`.md` Reason column for home paths, usernames, /dev/tty* | |
| Regex-scrub the existing body | Run PII/path regexes over the already-produced body verbatim | |
| You decide | Planner chooses within SUB-02's whitelist + path/PII-scrub + hex/base64 constraints | ✓ |

**User's choice:** You decide (Claude's discretion)
**Notes:** Captured as Claude's Discretion in CONTEXT.md with the recommended "whitelist is the guarantee, free-text scrub is the backstop" shape; exact regex set is planner's call. (D-02 discretion)

---

## Dedup fingerprint (SUB-03)

| Option | Description | Selected |
|--------|-------------|----------|
| chip + protocol + per-step verdicts → short hash, in JSON + title | Stable fields only; excludes timestamp/host-version/voltages | |
| chip + protocol + verdicts + fingerprint classes | Also folds in byte-mismatch fingerprint classifications so different failure modes get distinct ids | ✓ |
| chip identity only | Hash just chip name/ID; all reports for a chip collide | |

**User's choice:** chip + protocol + verdicts + fingerprint classes
**Notes:** Finer grain is deliberate — two runs that fail differently get distinct dedup ids. Degrades cleanly (non-destructive runs carry no verify-fingerprints → collapse to chip+protocol+verdicts). Volatile fields excluded. Short hash in JSON field + issue title. (D-02)

---

## Submit guardrails — awkward cases (SUB-01/SUB-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Refuse non-submittable; require TTY; drop JSON then guide | Refuse if !is_submittable; off-TTY prints body/URL but does not auto-send; oversize drops fenced JSON + points to saved report; hard-stop before ~8KB | ✓ |
| Warn-but-allow non-submittable | Same TTY/oversize handling but submits an incomplete report after an extra confirm | |
| You decide | Planner chooses within SUB-01 cap + SUB-02 explicit/interactive-only + preview | |

**User's choice:** Refuse non-submittable; require TTY; drop JSON then guide
**Notes:** Three locked sub-behaviors → D-03 (refuse non-submittable, print failing fields), D-04 (interactive-only; off-TTY prints but never auto-opens/`gh create`), D-05 (oversize URL body drops JSON, keeps table + points to always-saved `dev-test-<chip>.json`, hard-stops before ~8KB).

---

## Claude's Discretion

- **Sanitization mechanism** (SUB-02) — operator chose "you decide"; recommended whitelist-first + free-text scrub of `reason`/`chip_id_mismatch_reason`/`.md` Reason column for home paths, usernames, serial device names; hex/base64 any byte dump.
- **Issue title format** — surface dedup short-hash + chip + overall verdict.
- **`gh` auth detection** — `shutil.which("gh")` + `gh auth status` exit 0; injectable for tests.
- **Preview rendering** — reuse `rich`/`Confirm.ask` (firmware.py precedent).
- **`submit.py` internal decomposition + test-seam injection** — planner's call within SAFE-02.

## Deferred Ideas

- Fully-wired gist/attachment tier for verbose failure logs → v2 (SUB-F1); v1.21 only reserves it (D-05 drops JSON rather than attaching).
- Auto-merge/PR of community-confirmed DB entries → v2 (SUB-F2, human-gated).
- `gsd-inbox` triage-side auto-parse + DB-diff surfacing (INBOX-01) and the no-auto-graduate taxonomy lock (DISP-01/GRAD-01) → Phase 114.
