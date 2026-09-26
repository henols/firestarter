# Phase 115: Beta Install & Firmware-Flash Bench Validation — Community Onboarding (close) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-10
**Phase:** 115-beta-channel-install-and-firmware-flash-bench-validation-for
**Areas discussed:** Step-0 publish scope, uno328pb inclusion, bench evidence / fresh-machine, community doc shape, doc-vs-publish ordering, release-cut scope

---

## Step-0 publish scope

| Option | Description | Selected |
|--------|-------------|----------|
| Verify-only + halt (recommended) | Publishing stays a manual operator-gated step outside the phase; Step 0 probes both channels and halts on a publish-first blocker. | |
| Phase drives the release cut | Phase authors + runs the full release engineering (bump, lockstep cut, gitlink bump, PyPI dispatch, GitHub prerelease + .hex upload). | ✓ |
| Hybrid: phase preps, operator triggers | Phase does mechanical prep; actual dispatch/publish stays a manual gate. | |

**User's choice:** Phase drives the release cut.
**Notes:** Scoped down in the follow-up to the beta publish only (see Release-cut scope). Irreversible publish steps still get an explicit operator go-ahead at execution time (CONTEXT D-03).

---

## uno328pb inclusion

| Option | Description | Selected |
|--------|-------------|----------|
| Best-effort, not a hard gate (recommended) | Uno + Leonardo are hard gates; uno328pb attempted + recorded but a flaky/failed run doesn't block close. Flash firestarter_uno328pb.hex; if really a plain Uno, note + use firestarter_uno.hex. | ✓ |
| Hard gate for all three | All three must pass to close, incl. uno328pb. | |
| Drop uno328pb from this phase | Validate only Uno + Leonardo; defer uno328pb entirely. | |

**User's choice:** Best-effort, not a hard gate.
**Notes:** Grounded in documented uno328pb bench instability (timeouts, 0xff drift, VPP misread, PROGRAM brownout) and the plain-Uno-wrong-FW correction.

---

## Bench evidence / fresh-machine

| Option | Description | Selected |
|--------|-------------|----------|
| Fresh venv + config-dir isolation, per-board records (recommended) | Throwaway venv + FIRESTARTER_CONFIG_DIR at a clean temp dir; one evidence record per board. | ✓ |
| Container/VM fresh machine | Run install inside a clean container/VM, flash the attached board from there. | |
| Plain run on the dev bench | Just run pip install --pre + fw -i as-is on the bench. | |

**User's choice:** Fresh venv + config-dir isolation, per-board records.
**Notes:** Makes the "stranger on a fresh machine" claim credible without USB-passthrough friction of a container.

---

## Community doc shape

| Option | Description | Selected |
|--------|-------------|----------|
| New standalone doc in firestarter_app/doc/ (recommended) | Focused standalone file (e.g. beta-testing-install.md); README gets a pointer link, not a duplicate. | ✓ |
| Expand the README install section | Fold into README.md install section. | |
| Section inside community-validation.md | Add install/flash as a preamble to the existing taxonomy doc. | |

**User's choice:** New standalone doc in firestarter_app/doc/.
**Notes:** Operator-canonical home (two-layer pattern); hands off into community-validation.md.

---

## Doc-vs-publish ordering

| Option | Description | Selected |
|--------|-------------|----------|
| Draft-first, publish, then finalize from findings (recommended) | Write doc from known facts before the cut so b11 ships with it; validate; fold live findings back as a repo update. | ✓ |
| Publish b11 now, doc lands in next cut | Cut b11 code-complete, validate, write doc last (ships later). | |
| Doc fully first, single clean cut after | Finalize doc entirely before any publish; one clean cut. | |

**User's choice:** Draft-first, publish, then finalize from findings.
**Notes:** b11 is complete at publish; doc still captures what the bench runs reveal.

---

## Release-cut scope

| Option | Description | Selected |
|--------|-------------|----------|
| Beta publish only; tag/final-merge stays at close (recommended) | Phase drives the beta publish enough to make both channels public for Step 0; v1.21 tag + final --no-ff merge + ship ceremony stay a separate operator-gated close step after verification. | ✓ |
| Everything incl. tag + final merge in this phase | Fold the full close ceremony into Phase 115's plan. | |

**User's choice:** Beta publish only; tag/final-merge stays at close.
**Notes:** Preserves the standing operator-gated milestone-close ceremony as a distinct step.

---

## Claude's Discretion

- Smoke-test op default: `firestarter fw` (version+board) + `firestarter hw` (identify) as the minimal live protocol op; planner may pick `id`/identify if more universal. NOT a chip write/verify.
- venv / FIRESTARTER_CONFIG_DIR scaffolding mechanics; evidence-record filename/template; doc filename + section ordering.
- Firmware-repo version-tag-vs-app-b11 lockstep + how beta-build.yml .hex assets attach to the GitHub prerelease — flagged as the likely `--research-phase 115` item.

## Deferred Ideas

- Milestone close ceremony (v1.21 tag, final --no-ff merge to beta, /gsd-ship / /gsd-complete-milestone) — separate operator-gated step after verification.
- uno328pb as a hard gate — future bench session, if the third board stabilizes / its identity is confirmed.
- avrdude MCU-detection fallback — a feature-add to the avrdude recovery path; out of scope for a validation-only phase.
