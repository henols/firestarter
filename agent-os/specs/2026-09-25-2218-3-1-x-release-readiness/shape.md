# 3.1.x Release Readiness — Shaping Notes

## Scope

Make the first stable 3.x release possible without making it happen. The stable channel has been
frozen since 2025-11 at firmware `2.0.6` and CLI `2.0.9`, while all work lives on `beta`, now
`3.1.0b2`. `beta` leads `main` by 1140 commits in `firestarter_app`, 640 in `firestarter_fw` and
2316 in the meta repository — and `main` leads `beta` by 20, 6 and 18, so a promotion is a real
merge, not a fast-forward.

**Nothing in this spec publishes.** No push to `beta` or `main`, no tag, no GitHub release, no PyPI
upload. The product is that the publish decision, when the operator takes it, is a runbook
execution and not a discovery exercise.

The work has two halves. The first is code: a pre-flash gate that refuses a firmware release whose
feature version is above the CLI's. The second is documentation: a promotion runbook, a CHANGELOG,
three wiki pages, an honest annotation of the validation ledger, and a staleness sweep over
`agent-os/product/` and the root `CLAUDE.md`.

## What the investigation found

Three facts changed the shape of the work and are recorded here because each contradicts something
the project currently believes.

- **The stable release path is already broken, and has been since 2026-09-01.** In
  `firestarter_app` run `34784468070` (a push to `main`) the *Create new patch release* step
  succeeded, the *Commit updated version* step **failed** with `GH013: Repository rule violations
  found for refs/heads/main — Changes must be made through a pull request`, and the *Release* step
  was skipped. All three repositories carry an identical active `Protect main` ruleset whose only
  bypass actor is `DeployKey`; `current_user_can_bypass` is `never`, so the owner cannot push
  directly either. `2.0.9` was cut by hand — its release author is the user `henols`, twelve
  minutes after the failed run.

  This **inverts** a standing hazard. A push to `main` in `firestarter_fw` publishes *nothing*
  today, because the auto-commit is upstream of `pio run`, the dev-tools assertion and the
  `Release` step, and its failure aborts the job. The old warning — "any push to `main` cuts a
  stable release, there is no dry run" — is false now, and **re-arms the instant the bump is
  unblocked**.

- **`3.1.0` is unreachable by the automation.** `update_version.py` on `main` takes the stable
  path, discards the pre-release suffix and emits `major.minor.(patch+1)`. From `3.1.0b2` that is
  `3.1.1`. `--set-version` cannot rescue it: it forces beta mode and validates against a regex that
  demands a `b` or `rc` suffix.

- **The `2.0.9` exposure cannot be closed from the host side.** A `2.0.10` guard release would
  protect almost nobody. `pip install --upgrade firestarter` resolves to the newest stable, so once
  a stable 3.x is on PyPI every upgrading user lands there directly, and a user who never upgrades
  never receives `2.0.10` either. What does protect the installed base is already in the firmware:
  retired ordinals 4 and 6 fall through `default: LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd)`
  in `firestarter_fw/src/firestarter.cpp`, so a `2.0.9` host's verify and standalone blank check
  fail **loudly**, not silently. The README's blanket "fail quietly" wording overstates the hazard.

## Decisions

- **D-1. Readiness prep only.** Nothing publishes. The verification section proves this: after the
  work, `gh api repos/henols/firestarter_fw/releases/latest` must still return `2.0.6`.
- **D-2. The version guard is the forward half only.** It refuses a firmware release whose
  `(major, minor)` is above the CLI's. It protects a 3.1.x user from a future 3.2.x firmware. It
  does **not** protect a `2.0.9` user from a stable 3.x firmware, and the spec says so rather than
  implying coverage it does not have.
- **D-3. No `2.0.10` backport.** Unreachable by `pip install --upgrade` once a stable 3.x ships.
  Reversed from the 2026-09-20 analysis, which had it as the central mitigation.
- **D-4. No new bench validation.** The release rests on 3.0.x evidence, annotated honestly in the
  ledger rather than presented as evidence for 3.1.x.
- **D-5. Open chip FAILs ship as documented known issues**, on a new wiki page, not as release
  blockers.
- **D-6. The first stable is `3.1.1`** — recommended, because it is what the automation produces
  and costs nothing. Recorded as an open decision in the runbook. Not acted on here.
- **D-7. The override flag is `--allow-newer-firmware`, not `--force`.** `--force` is a wire flag
  (`FLAG_FORCE` reaches `command_dict["flags"]`), it already waives the hardware-revision gate, and
  its documented meaning is "reinstall even if up to date". One flag waiving two unrelated hazards
  is what `host/gate-polarity` warns against.
- **D-8. The guard's authoritative call site is the service layer**, in
  `FirmwareManager.manage_firmware_update` immediately after `fetch_release_info`, not in the CLI
  handler. It guards where the release tag is born, so "a refused release reaches the flasher"
  becomes unrepresentable rather than covered on four downstream branches. A second, earlier call
  in `cli_handlers.fw` covers the `--firmware-version` path, where the answer is knowable with no
  port open and no HTTP request.
- **D-9. A `None` release version does not refuse.** There is no release, so nothing flashes, and
  the existing failed-fetch diagnostic is the honest message. Turning a GitHub outage into a
  version-mismatch refusal would be a lie. This is the one place the gate looks fail-open and is
  not; the module docstring says so.

## Context

- **Visuals:** none. This is process and policy work.
- **References:** see `references.md`. Three documents from 2026-09-20 survive only on
  `origin/beta` under the deleted `.planning/` tree and are re-homed by this spec.
- **Product alignment:** `mission.md` §"Honest claims" governs the ledger annotation and the
  known-issues page — a chip counts as validated only after a real write→read→verify on silicon,
  and limits the hardware cannot meet are stated, not hidden. `roadmap.md` carries the planned item
  this spec discharges: "A path for the stable-release version bump."

## Standards Applied

- **host/pre-serial-gates** — the pure-module shape: `is_*` returns a bool, `require_*` raises. One
  recorded deviation, in D-8: the authoritative call runs after the release-metadata fetch, because
  the release tag is not known before it. It still runs before the download and before any byte
  reaches avrdude.
- **host/gate-polarity** — fail closed on an unparseable version on either side. The escape is a
  CLI option, never an environment variable. D-9 records the single documented fail-open edge and
  why its worst case is only lost availability.
- **host/typed-refusals** — `FirmwareReleaseRefusedError` under `FirmwareOperationError`, which
  renders with no prefix. No new arm in `map_typed_errors`; the standard says existing verbatim
  arms are the exception and not to add more.
- **host/refusal-text** — module-level `_REFUSAL_FORMAT` and `_UNREADABLE_FORMAT`. Tests import the
  constants and never copy the text. ASD-STE100.
- **host/command-skeleton, host/help-docstrings** — the `--allow-newer-firmware` option and its
  help string. No test pins `--help` text.
- **testing/non-vacuity** — both sides of the threshold, violating input, and absent-evidence cases
  for the fail-closed arm.
- **testing/standalone-checkout** — the suite is verified from a fresh clone on Python 3.11,
  because the devcontainer's editable install points at `/workspaces` and masks CI-only defects.
- **protocol/retired-ordinals** — read, not changed. Its tombstones are what make a stale host's
  verify and blank check fail loudly, which is the finding behind D-3.
