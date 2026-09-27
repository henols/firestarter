---
created: 2026-08-30T20:57:55Z
title: Add a `dev test` flag that files the issue automatically when the run finishes
area: host app
files:
  - firestarter_app/firestarter/cli_handlers.py:2329-2345
  - firestarter_app/firestarter/submit.py:590-760
  - firestarter_app/firestarter/submit.py:62
  - firestarter_app/firestarter/diagnostic_report.py:150
---

## Problem

Operator ask (2026-08-30): a flag on `dev test` that auto-creates the GitHub issue when
the run is done, with no prompt.

Today there is no way to get there. `dev test` takes exactly one option, `--fast`
(`cli_handlers.py:2329-2345`); the `--submit` flag it carried through v1.21 was
**removed**, and the comment block at `cli_handlers.py:2292` records it as now erroring
as an unknown option. Every run still ends by handing the report to `submit_report`
(`submit.py:590`), which forks two ways and files on neither automatically:

- **On a TTY** — Step 5 asks `Submit this report to henols/firestarter_prom?` with
  `default=False`. A human has to answer every single run.
- **Off a TTY** — Step 4 prints the prefilled issue URL and returns *without* calling
  `confirm_fn`, `submit_via_gh` or `comment_via_gh_fn`. Filing nothing there is
  deliberate: it is v1.21 SUB-01's ban on silent off-TTY submission, which survived the
  removal of the explicit flag precisely because no flag was left to carry the consent.

So an unattended sweep files nothing at all, and an attended one costs a prompt per chip.
A flag is the missing piece of consent the off-TTY ban was written around — it makes
scripted multi-chip sweeps (e.g. Backlog 999.42, six chips × two shields) able to file
their own reports.

**This is outward-facing:** the flag creates public issues in `henols/firestarter_prom`
(`submit.py:62`) with no human in the loop, so the gate must be provably unable to fire
on a run the operator did not opt into.

## Solution

Add one flag; keep every existing safety property of `submit_report` intact. Points to
settle at discuss-phase:

- **Name.** `--submit` reads naturally and matches the docs/history, but that exact
  spelling was deliberately retired and is currently documented as an unknown option;
  `--auto-submit` or `-y/--yes` avoid re-animating a removed surface. Whichever wins, the
  removal note at `cli_handlers.py:2292` must be corrected in the same change, not left
  contradicting the code.
- **Refuse gate stays.** The flag consents to *filing*; it must never bypass
  `is_submittable` (`diagnostic_report.py:150`) — a report missing
  `chip`/`protocol`/`host_version` still refuses with the named fields.
- **Dedup outcome drives the action.** Step 3 already runs on every path before any ask.
  Under the flag, a found prior issue should comment (the `comment_via_gh_fn` path)
  rather than file a second issue. When the dedup check *could not run* (gh absent,
  unauthenticated, offline), the interactive path asks anyway — unattended, refusing
  loudly is the safer default, because a duplicate public issue is not undoable by the
  tester.
- **Tier.** `gh` only. `submit_via_browser` is meaningless without a human at the tab
  (nothing is filed until someone presses Submit there), so a `gh`-absent run under the
  flag should fail with a stated reason, never open a browser.
- **Interaction with `--fast`.** A fast run's `repeat_policy_tag` already re-keys
  `dedup_fingerprint` so it cannot join an accurate run's N≥2 promotion group. Whether
  auto-filing *weaker* reports at scale is wanted needs an explicit decision — possibly
  refuse the combination.
- **Tests.** Prove the auto-path is unreachable without the flag (TTY and off-TTY), that
  the refuse gate and dedup-comment branch still hold under it, and that no browser tier
  is reachable from it.
