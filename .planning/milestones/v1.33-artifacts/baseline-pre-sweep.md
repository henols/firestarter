---
title: Pre-sweep baseline — milestone v1.33, Phase 154
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "01"
measured: 2026-08-23
status: AUTHORITATIVE — every "before/after" comparison in Phase 154 is measured against this file
supersedes: >
  All baseline numbers in 154-RESEARCH.md (F8, R5, VALIDATION §Test Infrastructure).
  Those were taken against the DIRTY `size-reduction-survey` working tree and are
  mechanics proofs, not baselines. See §"Reconciliation with RESEARCH.md".
requirements: [SWEEP-05 (before-half), SWEEP-13 (branch anchors)]
---

# Pre-sweep baseline — v1.33 Phase 154

Every number in this file was measured on a **clean** working tree, after D-12
precondition 1 was discharged (task 1) and precondition 2 was discharged (task 2).
Each number carries the verbatim command that produced it. Nothing here is quoted
from research.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `PRE_DIRTY_SHA` | `8695ee52c27a4bee4387c5c489afd5f3d7275e8a` |
| `PRESERVED_SHA` | `a6b46f8b12e81c62d9958945eb0bdbb8c16ae699` |
| preserved branch | `wip/v1.33-size-reduction-survey-preserved` (in `firestarter`) |
| `FW_PRE_SHA` | `8695ee52c27a4bee4387c5c489afd5f3d7275e8a` |
| `APP_PRE_SHA` | `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a` |
| meta branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` @ `717757f368b28fe04c3a5f43e2a0aed1ed06e99c` |
| `firestarter` branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` @ `FW_PRE_SHA` (forked from `beta`) |
| `firestarter_app` branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` @ `APP_PRE_SHA` (forked from `beta`) |

`PRE_DIRTY_SHA` and `FW_PRE_SHA` are the same commit: `beta`'s tip. The dirty tree
was uncommitted work *on top of* `beta` at `8695ee5`, so preserving it added exactly
one commit (`PRESERVED_SHA`) and the milestone branch forks from the same base.

### SWEEP-13 anchoring rule

Plan 12's commit-count criteria are anchored to `FW_PRE_SHA` / `APP_PRE_SHA`, **never**
to `HEAD~1`. `git rev-list --count HEAD ^HEAD~1` is a tautology that always prints `1`
(`reference_git_revlist_head1_tautology`). The correct form is:

```bash
git -C firestarter     rev-list --count 8695ee52c27a4bee4387c5c489afd5f3d7275e8a..HEAD   # must be 1
git -C firestarter_app rev-list --count 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a..HEAD   # must be 1
```

### Recovery path for Phases 155-158

`wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8` is the **only** ref carrying
the already-implemented firmware size-reduction work (11 files, 229 insertions,
231 deletions). It is duplicated at
`.planning/notes/firmware-size-reduction-measured.patch` in the meta repo. Verified
byte-identical to `beta` + that patch by a recursive tree diff (§5). **Do not delete or
force-update this branch during milestone v1.33.**

---

## 2. Byte-identity pair — three AVR targets (SWEEP-05, before-half)

The measured artifact is `.pio/build/<env>/firestarter_<env>.elf` — **not** the default
PlatformIO `PROGNAME`, because `platformio.ini` wires `extra_scripts = pre:name_firmware.py`
at `[env]` scope and that hook does `env.Replace(PROGNAME="firestarter_%s" % board_name)`.

Resolved concretely for the three envs, the measured artifacts are
`.pio/build/uno/firestarter_uno.elf`, `.pio/build/uno328pb/firestarter_uno328pb.elf` and
`.pio/build/leonardo/firestarter_leonardo.elf`, each with its sibling `.hex`. The `uno`
oracle in one line, which is the form plans 06-11 run per swept file (1.2 s):

```bash
cd /workspaces/firestarter && rm -rf .pio/build/uno && pio run -e uno \
  && sha256sum .pio/build/uno/firestarter_uno.elf
```

Verbatim command, per env:

```bash
cd /workspaces/firestarter
rm -rf .pio/build/<env> && pio run -e <env>
sha256sum .pio/build/<env>/firestarter_<env>.elf .pio/build/<env>/firestarter_<env>.hex
```

| env | `.elf` sha256 | `.hex` sha256 | Flash: | RAM: |
|---|---|---|---|---|
| uno | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | 26026 / 32768 (79.4%) | 1575 / 2048 (76.9%) |
| uno328pb | `6650baecf09ca0fb5ffbf7a377e0528b021568c1ab7f9c4afdafc4254ed98d8c` | `7b86c1aac5642b968bd9604bde249b7d68643ebe135f0d05690e56e43e20ebba` | 26074 / 32768 (79.6%) | 1581 / 2048 (77.2%) |
| leonardo | `fcca68e967798a1a133149fa5736dd0d5dd04384d5cf02feeff861f8672d7aef` | `2b9ad44e23dd6dc88e76a5aeb9105050f56c84d470a14b9a9d2597feffb0ee88` | 28170 / 32768 (86.0%) | 2016 / 2560 (78.8%) |

Per Ruling E both forms are recorded: the hash pair (strictly stronger, and proven
comment-immune) **and** the `Flash:`/`RAM:` figures SWEEP-05 literally asks for. The
`.hex` is corroboration only — `avr-objcopy -O ihex` drops non-loadable sections, so a
`.hex` match would mask a debug-section change that the `.elf` catches.

**Leonardo Caterina headroom:** `28672 - 28170 = 502 B`. This is the figure v1.33's
Phases 155-158 exist to widen (the preserved work measures it at 3440 B, 6.9x).

### Per-env `-g` absence — measured, not assumed

Research assumption A2 verified the `-g`-absent compile line for `uno` only. Measured
here for all three envs. The probe is run on a **cold** tree, because `pio run -v` on an
already-built target prints no compile lines at all and the grep would be vacuously `0`:

```bash
cd /workspaces/firestarter
rm -rf .pio/build/<env> && pio run -v -e <env> > /tmp/gsd-154-logs/<env>-verbose.log 2>&1
grep -cE 'avr-g(\+\+|cc) .*-c .*(src/|\.pio/build/<env>/src)' /tmp/gsd-154-logs/<env>-verbose.log  # denominator
grep -c ' -g ' /tmp/gsd-154-logs/<env>-verbose.log                                                 # numerator
```

| env | project-source compile lines (denominator) | lines carrying ` -g ` | verdict |
|---|---|---|---|
| uno | 25 | **0** | oracle safe |
| uno328pb | 25 | **0** | oracle safe |
| leonardo | 25 | **0** | oracle safe |

The denominator is recorded so the `0` cannot be read as a vacuous grep. A2 is now
discharged for all three envs, not extrapolated from `uno`.

### Bonus reproducibility evidence

Each env was cold-built **twice** — once as `pio run -e <env>`, once as
`pio run -v -e <env>` — and both builds hashed **identically** on both `.elf` and `.hex`
for all three envs. Verbosity does not perturb the artifact, and the cold-build
convention is reproducible on this tree.

---

## 3. Suite baselines — taken on the clean tree

### Firmware CI legs (all three, per `reference_v131_firmware_native_gate_gotchas`)

| Leg | Command (verbatim, from `/workspaces/firestarter`) | Result | Wall |
|---|---|---|---|
| native | `pio test -e native` | **172 passed / 0 failed** (172 test cases, 172 succeeded) | 52.4 s |
| native_nodevtools | `pio test -e native_nodevtools` | **172 passed / 0 failed** (172 test cases, 172 succeeded) | 64.4 s |
| firmware gates | `python3 -m pytest tests/ -q` | **323 passed / 0 failed** | 11.2 s |

### Host suite — CPython 3.11 ONLY

The devcontainer's system interpreter is **3.12** and app CI is **3.11 only**; 3.12
masks app CI defects (`reference_devcontainer_py312_masks_ci_py39`). Provisioning and
run, verbatim:

```bash
export UV_CACHE_DIR=/tmp/gsd-154-uvcache          # ~/.cache/uv is unwritable: os error 13
uv venv --python 3.11 /tmp/gsd-154-venv311        # -> CPython 3.11.16
cd /workspaces/firestarter_app
uv pip install --python /tmp/gsd-154-venv311/bin/python -e '.[test]'
FIRESTARTER_FW_ROOT=/workspaces/firestarter /tmp/gsd-154-venv311/bin/python -m pytest tests/ -o addopts="" -q
```

| Leg | Result | Wall |
|---|---|---|
| full host suite | **1970 passed / 0 failed** (32 snapshots passed, 1 warning) | 263.3 s |

`-o addopts=""` is mandatory: `firestarter_app/pyproject.toml` sets `addopts = "-ra -q"`,
and that plus a command-line `-q` suppresses the count line
(`reference_pytest_addopts_q_suppresses_count_line`).

Editable-install sanity check (the sibling-worktree trap): the venv resolves
`firestarter.__file__` to `/workspaces/firestarter_app/firestarter/__init__.py`, i.e. the
live tree, not a stale copy.

### The four F3 blob-sha gates — green starting point for plan 07

```bash
cd /workspaces/firestarter && python3 -m pytest \
  tests/test_eprom_params_citations.py tests/test_protocol_branch_inventory.py \
  tests/test_golden_trace_identity.py tests/test_golden_trace_identity_eprom_v131.py -q
```

**29 passed / 0 failed**, exit 0. Plan 07's sidecar regeneration therefore starts from a
proven-green state, and any redness after regeneration is attributable to the
regeneration.

---

## 4. Reconciliation with RESEARCH.md — every delta explained, none silently adopted

Research finding F8 said no baseline is meaningful until the tree is clean. It was right,
and the clean numbers reconcile its dirty-tree numbers **exactly**. Both sides are
printed here; neither was silently adopted.

| Quantity | RESEARCH.md (dirty tree) | This file (clean tree) | Delta | Explanation |
|---|---|---|---|---|
| uno Flash | 23088 / 32768 | 26026 / 32768 | **+2938 B** | Exactly the preserved work's measured `-2938 B` flash. Research measured the *reduced* firmware. |
| uno RAM | 1562 / 2048 | 1575 / 2048 | **+13 B** | Exactly the preserved work's measured `-13 B` RAM. |
| uno `.elf` sha256 | `64df1d2f…456141` | `1cfa946f…31ecca` | differs | Different source content (see the two rows above), not a reproducibility failure. |
| firmware gates | 317 pass / 6 fail | **323 pass / 0 fail** | 317+6 = 323 | All 6 failures were the dirt. Total case count identical. |
| host suite | 1963 pass / 7 fail | **1970 pass / 0 fail** | 1963+7 = 1970 | All 7 failures were the dirt. Total test count identical. |
| native | 172 / 172 | 172 / 172 | none | Unaffected by the dirt. |

**Research assumption A5 is discharged.** A5 ("the 7 host + 6 firmware baseline failures
are *all* caused by the dirty tree", confidence Medium, established by mechanism plus one
direct check) is now proven by a full clean-tree run of both suites: 13 failures, 13
recoveries, and identical totals on both sides. Confidence: **VERIFIED**.

The survey note's own baseline figures (`.planning/notes/firmware-size-reduction-survey.md`
§"Measurement baseline": `uno flash=26026 ram=1575`, `leonardo flash=28170 ram=2016`)
match this file's clean measurements to the byte on both targets, independently
corroborating that this is the pre-reduction `beta` state.

---

## 5. Preservation verification (task 1, step 3)

Tree comparison, not patch-text comparison — patch texts differ in `index` lines even
when content is identical:

```bash
cd /workspaces/firestarter
git archive beta    | tar -x -C /tmp/gsd-154-preserve/beta_plus
git archive a6b46f8 | tar -x -C /tmp/gsd-154-preserve/preserved
cd /tmp/gsd-154-preserve/beta_plus && git apply /workspaces/.planning/notes/firmware-size-reduction-measured.patch
diff -r /tmp/gsd-154-preserve/beta_plus /tmp/gsd-154-preserve/preserved
```

| Check | Result |
|---|---|
| `git apply --verbose` of the recovery patch onto clean `beta` | all 11 patches "Applied … cleanly", rc 0 |
| `diff -r beta_plus preserved` | **no output, exit 0** |
| `git diff --name-only beta..PRESERVED \| wc -l` | 11 |
| `git diff --shortstat beta..PRESERVED` | `11 files changed, 229 insertions(+), 231 deletions(-)` |
| `git status --porcelain` after the branch switch | empty |

**No destructive git command ran.** The reflog for this work contains exactly three
entries — two `checkout: moving from …` and one `commit:` — and no `reset --hard`,
`checkout --`, `restore`, `clean` or `stash` entry. (Two older `reset: moving to HEAD`
entries dated 2026-08-22 predate this plan and were not created by it.)

---

## 6. Environment facts and traps recorded for downstream plans

| Fact | Value |
|---|---|
| PlatformIO Core | 6.1.19 (`/usr/local/bin/pio`) |
| `uv` | 0.12.5 |
| system `python3` | **3.12.13** — do NOT use for host gates |
| host-gate interpreter | `/tmp/gsd-154-venv311/bin/python` (CPython 3.11.16) |
| `UV_CACHE_DIR` | `/tmp/gsd-154-uvcache` (required; `~/.cache/uv` is unwritable, os error 13) |
| git | 2.55.0 |
| build logs | `/tmp/gsd-154-logs/` |
| preservation scratch trees | `/tmp/gsd-154-preserve/{beta_plus,preserved}` |

### TRAP — `pio` must never be invoked with cwd `/workspaces`

`/workspaces/platformio.ini` exists as an **untracked, gitignored** 21 KB stray
(`.gitignore:20` ignores `platformio.ini`) and it is **malformed**: duplicate
`[platformio]` section at line 26. Any `pio` invocation whose cwd is the meta root dies
with `InvalidProjectConfError`, including a bare `pio --version`. Every byte-identity
oracle invocation in plans 06-11 must therefore be `cd /workspaces/firestarter` first.
This is a pre-existing condition, out of this phase's scope; logged to
`.planning/phases/154-…/deferred-items.md`.

### CONSTRAINT — path-scoped `git add` only in `firestarter_app` (T-154-03)

The `firestarter_app` working tree carries **7** untracked entries that are NOT this
phase's work:

```
?? .planning/config.json
?? SECURITY.md
?? datasheets/M27C1001.pdf
?? datasheets/M27C512.pdf
?? datasheets/W27C512.pdf
?? datasheets/W27E257.pdf
?? write_test_port.sh
```

(The plan's action text named 3 of these; the measured count is 7 — `datasheets/` holds
four PDFs and `write_test_port.sh` was unlisted. Recorded as measured.)

These are **harmless to every gate**: all porcelain assertions target the *firmware*
repo, verified by grep this session — `_git_porcelain(FW_ROOT)` in 4 app modules
(`test_cap03_ack_layout_parity.py:746,786`, `test_py32_flash_map_host.py:391`,
`test_json_key_parity.py:453,491`, `test_py32_asset_name_host.py:323`) and
`_git_porcelain(_REPO_ROOT)` / `_git_porcelain(_FW_REPO_ROOT)` in 3 firmware modules
(`test_requirement_case_mapping_v131.py:753,802`,
`test_trace_segment_exhaustiveness_v131.py:1144,1275`,
`test_flash_path_record_sync.py:1247`). Measured total: **7 modules**, not F7's stated 9 —
recorded as a delta, not corrected in either direction.

**But** every `git add` in `firestarter_app` throughout this phase MUST be path-scoped.
`git add -A` / `git add .` would sweep all 7 unrelated items into the SWEEP-13 commit.
The firmware tree is clean, so the same constraint there is prudence rather than
necessity — apply it anyway.

---

## 7. What this file does NOT do

It is **not committed by this plan.** Per D-11 the meta-repo deliverables
(`.planning/milestones/v1.33-artifacts/` manifest + tool + marker + this record) land in **one** meta commit,
made by plan 12. This file exists on disk from plan 01 onward and is read by every
intervening plan.
