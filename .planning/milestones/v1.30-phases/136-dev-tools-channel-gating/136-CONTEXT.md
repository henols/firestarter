# Phase 136 — Dev-Tools Channel Gating — CONTEXT

**Authored 2026-08-05 by Claude, not by `/gsd-discuss-phase`.** The operator's standing instruction
is to run 136 → 136.1 → 137 in order without stopping, batching anything undecidable to
`.planning/v1.30-OPERATOR-BATCH.md`. So the gray areas the roadmap flagged are decided here, each
with the evidence it was decided from, rather than left for the planner to guess.

Every decision below was measured against live source at `firestarter_app@HEAD`, not recalled.

---

## Measured baseline

| Fact | Value | How measured |
|---|---|---|
| `dev` subcommands | **8**: `read`, `reg`, `addr`, `consistency-check`, `write-cycle`, `fault-inject`, `validate-family`, `test` | `grep -c '@dev.command'` + the `name=` list |
| Stable keeps | `read`, `test` | Backlog 999.15 / gh#8 channel-split design (2026-07-28) |
| Therefore gated | **6**: `reg`, `addr`, `consistency-check`, `write-cycle`, `fault-inject`, `validate-family` | 8 − 2 |
| Channel detector | `firestarter/channel.py::is_prerelease_build()` — **already exists and already fails closed** | read in full |
| `dev` group site | `cli_handlers.py:1203` `@cli.group(name="dev")` | read |

---

## D-01 — The gate is conditional registration **plus** a `_DevGroup` subclass. Both, not either.

The roadmap frames this as a choice ("invocation-time `_DevGroup` subclass **vs.** import-time
deletion; both satisfy the requirement"). Measured against the requirement texts, that framing is
wrong — neither alone satisfies both CHAN-02 and CHAN-03:

- **CHAN-02** demands the command be gated **by not registering it**. A `hidden=True` flag or a
  runtime refusal inside a registered callback fails this outright.
- **CHAN-03** demands invoking a gated subcommand refuse **informatively** with a specific message.
  Bare non-registration cannot do this: Click emits its generic `No such command 'reg'.`, which is
  indistinguishable from a typo and tells a stable user nothing about channels.

**Decision:** the command is genuinely not registered (CHAN-02 satisfied literally), AND the `dev`
group is a `_DevGroup` subclass that knows the gated *names* and, on resolving one, emits the
channel-specific refusal with a non-zero exit (CHAN-03). The subclass holds names only — never the
callbacks — so a gated command remains genuinely absent and uninvokable.

**Rejected:** `hidden=True` (CHAN-01 explicitly rules it out — a hidden command still runs).

## D-02 — Reuse `channel.is_prerelease_build()`. Do not write a second detector.

It already exists, already fails closed on an unparseable version, and its own docstring records that
a checkout's `2.0.7_dev` parses as a pre-release. A second detector is how two sources of truth drift
apart. **CHAN-07 is satisfied structurally by this choice:** `channel.py` reads the package's own
`__version__` and nothing else — no firmware source, no handshake, no serial. The four host gates
that failed OPEN in Phase 117 did so by scanning firmware source; this one cannot, because it never
opens a file.

## D-03 — The `dev reg` bench override is an explicit, fail-closed environment variable.

This is criterion 4, and it exists because of a recorded near-miss: gating keys off the package
`__version__`, so **at any stable version cut, or between betas, an editable devcontainer install
silently loses `dev reg`** — which is load-bearing bench tooling (the held-erase-rail DMM proxy).

**Decision:** a single environment variable, read host-side only, that **fails closed** — it enables
the full `dev` group only on an exact truthy value, never on mere presence. This is deliberate and
non-negotiable: the firmware side of this same idea (`-D DEV_TOOLS=${sysenv.VAR}`) is recorded as
**fail-OPEN**, because an unset variable still *defines* the macro and every `#ifdef` stays true. The
host override must not repeat that shape. Presence ≠ enabled; only an explicit value enables.

Ship it with a tripwire comment at the `dev reg` definition naming *why* it exists, following the
RETIRE-07 pattern from Phase 132 — so the next person to touch the gate learns about the bench
dependency from the code, not from a broken bench.

## D-04 — Both-channel proof is **subprocess-only**. An in-process test is vacuous.

`is_prerelease_build()` reads the imported package's `__version__`, which in any local test run is
the checkout's own pre-release string. An in-process assertion that "stable hides `reg`" therefore
tests nothing — it can only ever observe the beta branch. Criterion 2 already says this; it is
restated here as a task-level constraint so no plan quietly adds an in-process shortcut.

## D-05 — The `dev` group docstring rewrite is in scope and is a real requirement, not polish.

CHAN-05: the docstring currently warns users away from the very commands (`dev read`, `dev test`)
that are being deliberately kept in stable *for those users*. Leaving it would ship a stable build
whose own help text tells its audience not to use the two commands it exposes.

---

## Deferred to the operator batch — NOT decided here, and NOT blocking

Both are recorded in the gh#8 design as **operator decisions, not implementer guesses**. Neither is
required by any of CHAN-01…07, so Phase 136 proceeds without them:

- **Whether welding beta → dev-tools is acceptable at all.** It protects stable users while leaving
  the beta community fully exposed. That is a policy call about who deserves protection.
- **Whether `dev read` / `dev test` should graduate out of the `dev` namespace.** Deferred by gh#8 §5,
  forced by v1.21, deferred again 2026-07-28. Now deferred a third time.

Filed in `.planning/v1.30-OPERATOR-BATCH.md` §E.

---

## Traps carried in from the record — do not rediscover

- **Only 2 of the 8 subcommands are firmware-gateable, ever.** `reg` and `addr` send dev-only command
  IDs; the other six are built from **production** IDs, so no firmware flag can gate them without
  killing the production feature. Any plan that reaches for a firmware flag is wrong on 6 of 8.
- **`fault-inject` deliberately sends malformed production frames** — gating it firmware-side is
  meaningless by construction.
- **Do not re-derive the channel policy.** Stable = `read` + `test`, full stop; that decision closed
  v1.21's collision and is not this phase's to reopen.
