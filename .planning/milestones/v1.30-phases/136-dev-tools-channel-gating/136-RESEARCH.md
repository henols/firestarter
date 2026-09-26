# Phase 136 — Dev-Tools Channel Gating — RESEARCH

**Authored inline by the orchestrator, 2026-08-05.** The `gsd-phase-researcher` subagent was spawned
twice and terminated both times on a transient server-side **API 529 Overloaded**, writing nothing
and leaving nothing salvageable in its transcript. Rather than block the run on a flaky spawn, the
six research questions were measured directly. Everything below marked **VERIFIED** was executed and
its real output pasted. Everything marked **UNVERIFIED** is reasoning the planner must confirm.

Locked decisions in `136-CONTEXT.md` (D-01…D-05) were **not** reopened. **Nothing measured here
contradicts any of them** — one measurement (§2) actively confirms D-04.

---

## 1. Click version and the subclass hook — VERIFIED

```
$ python3 -c "import click; print(click.__version__)"
8.3.3
```

Hooks confirmed present on `click.Group`: `get_command`, `resolve_command`, `list_commands`,
`parse_args`, `invoke`.

**Use `click.Group`, never `click.MultiCommand`.** Measured deprecation warning:

```
DeprecationWarning: 'MultiCommand' is deprecated and will be removed in Click 9.0. Use 'Group' instead.
```

`MultiCommand` still exists in 8.3.3 but subclassing it would ship a construct with a known removal
date. (Separately, `click.__version__` itself warns it is deprecated and removed in 9.1 — use
`importlib.metadata.version("click")` if the phase needs a version assertion in a test.)

**Recommended hook split for D-01 — UNVERIFIED, the planner must confirm against Click 8.3.3's actual
resolution order:**

- `list_commands()` — controls what `dev --help` enumerates. Filtering here satisfies CHAN-01's
  "lists only `read` and `test`".
- `get_command(ctx, name)` — returns `None` for a gated name. Returning `None` is what makes the
  command genuinely unresolvable (CHAN-02), rather than hidden-but-runnable.
- The informative refusal (CHAN-03) must come from whichever of `get_command` / `resolve_command`
  Click consults *before* it raises its own `UsageError`. **This is the single most important thing
  for the planner to verify empirically**, because the difference between the two determines whether
  the tailored message appears at all or is swallowed by Click's generic
  `Error: No such command 'reg'.`

**Design constraint restated from D-01:** the subclass holds *names only*, never callbacks. A gated
command must not exist as an invokable object anywhere in the stable process.

## 2. Subprocess harness — VERIFIED, and it confirms D-04

The question was whether a subprocess can be forced onto the **stable** channel, given
`is_prerelease_build()` reads the imported package's `__version__`. It can:

```
$ cat force_stable.py
import sys, firestarter
firestarter.__version__ = "3.0.0"          # bare X.Y.Z => stable
from firestarter.channel import is_prerelease_build
print("is_prerelease_build() ->", is_prerelease_build())

$ python3 force_stable.py
is_prerelease_build() -> False

$ python3 -c "import firestarter; from firestarter.channel import is_prerelease_build; \
              print('version=',firestarter.__version__,'-> is_prerelease_build() ->', is_prerelease_build())"
version= 3.0.0b15 -> is_prerelease_build() -> True
```

Two things are now measured fact rather than assumption:

1. **The channel is flippable in a subprocess** by assigning `firestarter.__version__` before the
   channel module reads it. `is_prerelease_build()` does `import firestarter as _pkg` at call time,
   so a pre-import assignment is observed. The harness is buildable.
2. **D-04's vacuity claim is confirmed.** This checkout is `3.0.0b15`, which parses as a pre-release,
   so an in-process test can only ever observe the beta branch. Any in-process assertion that
   "stable hides `reg`" tests nothing.

**Existing subprocess precedent** — 8 test modules already shell out, so this is house style, not a
new pattern: `test_check_mypy_watermark.py`, `test_gen_test_image.py`, `test_characterization.py`,
`test_skip_census.py`, `test_check_no_community_support_status_write.py`, `test_update_version.py`,
`test_check_dispatch_invariants.py`, `test_audit_coverage_matrix.py`.

## 3. The fail-closed env override (D-03) — VERIFIED precedent, UNVERIFIED rule

**Precedent is strong.** Eight `FIRESTARTER_*` variables already exist, so the name fits the house
style rather than inventing an axis:

```
FIRESTARTER_BASELINE_FILE      FIRESTARTER_CLAIMSCAN_TARGETS   FIRESTARTER_CMD_ADMISSION_SRC
FIRESTARTER_CONFIG_DIR         FIRESTARTER_DB_FILE             FIRESTARTER_DEVTEST_HANDLER
FIRESTARTER_DEVTEST_SRC        FIRESTARTER_DEVTEST_SUBMIT
```

**Proposed — UNVERIFIED, planner to implement and prove:** `FIRESTARTER_DEV_TOOLS`, enabling the full
`dev` group **only** on an explicit allow-value (e.g. exactly `"1"`). The required proof is a test
matrix showing the gate stays **CLOSED** for: unset, empty string, `"0"`, `"false"`, and arbitrary
garbage. Presence alone must never enable.

This asymmetry is deliberate and is the whole reason D-03 exists: the firmware-side analogue
`-D DEV_TOOLS=${sysenv.VAR}` is on record as **fail-OPEN**, because an unset variable still *defines*
the macro and every `#ifdef` stays true. The obvious implementation is the broken one.

## 4. `dev --help` pinning — VERIFIED, with a consequence the planner must handle

**A `dev --help` snapshot already exists**: `tests/__snapshots__/test_characterization.ambr` contains
`name: test_help_dev` (syrupy; 8 `dev` matches in that file).

Two consequences:

- **It is an in-process pin, so it only ever sees the beta channel.** It satisfies nothing in
  criterion 2 on its own — criterion 2 explicitly wants *both* channels via subprocess.
- **It WILL change when the gate lands** and must be re-baselined. Per the roadmap's own warning
  about Backlog 999.28 (`write --sdp-relock` would change `write --help`), a help pin must be updated
  **deliberately, with the change named and justified**, never silently re-recorded by running
  `--snapshot-update` and committing whatever appears.

## 5. Blast radius — VERIFIED

Test files referencing each gated command:

| Gated command | Test files |
|---|---|
| `reg` | 1 |
| `addr` | 1 |
| `consistency-check` | 2 |
| `write-cycle` | 1 |
| `fault-inject` | 1 |
| `validate-family` | 3 |

Small, and **none of them should break**: every test runs under this checkout, whose `3.0.0b15`
version keeps the gate open (§2). The planner should still confirm each explicitly rather than
assume — a test that constructs the group directly rather than going through the CLI could behave
differently.

## 6. CHAN-05's target — VERIFIED

`cli_handlers.py:1203`:

```python
@cli.group(name="dev")
@map_typed_errors
def dev() -> None:
    """Debug command for development purposes.

    USR button will break command and return.
    """
```

This is exactly the defect CHAN-05 names: a stable install would expose `dev read` and `dev test`
*to end users* under a group whose own help text calls itself "for development purposes" and warns
about a USR button most users do not have. The rewrite is a real requirement, not polish.

## 7. NOT RESEARCHED

- **CHAN-06 / `dev reg 0 0 0x86 -f` runtime semantics.** The command's signature was read (`msb`,
  `lsb`, `ctrl` arguments plus `-i/--input-enable`, `-d/--chip-disable` flags), but its held-rail
  behavior was **not** traced through to the hardware layer. The bench role is documented externally
  as the held-erase-rail DMM proxy; the planner should confirm the override preserves the exact
  invocation rather than trusting this note.
- **mypy/ruff impact of the new constructs.** The subagent died mid-type-check and no result was
  observed. Do **not** inherit a number from this document — there is none. Measure it as the first
  task, via `tools/ci_replica_venv.sh`, never the devcontainer python. Standing headroom entering
  this phase is 2 (33 against watermark 35); `cli_handlers.py` is inside the strict island
  (`disallow_untyped_defs = true`), so a new subclass there needs full annotations.

---

## Pitfalls

1. **`hidden=True` is not a gate.** A hidden command still runs. CHAN-01 rules it out explicitly.
2. **Bare non-registration cannot satisfy CHAN-03.** Click's generic `No such command 'reg'.` is
   indistinguishable from a typo. This is the whole reason D-01 pairs two mechanisms.
3. **In-process channel tests are vacuous** — measured in §2, not theorised.
4. **Do not write a second channel detector.** `channel.py::is_prerelease_build()` exists and already
   fails closed. Two detectors drift.
5. **Do not reach for a firmware flag.** Only 2 of the 8 `dev` subcommands (`reg`, `addr`) send
   dev-only command IDs; the other six are built from production IDs, so a firmware flag cannot gate
   them without killing the production feature. Any plan that reaches for one is wrong on 6 of 8.
6. **Do not silently re-baseline the `test_help_dev` snapshot** (§4).
7. **CHAN-07 is satisfied structurally, and cheaply** — `channel.py` reads the package's own
   `__version__` and opens no file at all. The four Phase-117 host gates that failed OPEN did so by
   scanning firmware source. Keep it that way; do not add a firmware read "for robustness".

## Per-requirement touch notes

| Req | What implementing it touches |
|---|---|
| CHAN-01 | `_DevGroup.list_commands` filter + the subprocess both-channel help proof |
| CHAN-02 | Conditional registration of the 6 gated commands at the `@dev.command` sites |
| CHAN-03 | The refusal path — hook TBD per §1, plus its exit-code assertion |
| CHAN-04 | New subprocess test module; re-baseline `test_help_dev` deliberately (§4) |
| CHAN-05 | The `dev` group docstring at `cli_handlers.py:1203` |
| CHAN-06 | `FIRESTARTER_DEV_TOOLS` override + tripwire comment at the `dev reg` site (RETIRE-07 pattern) |
| CHAN-07 | Satisfied by construction via D-02; needs an explicit no-firmware-read assertion to be provable |
