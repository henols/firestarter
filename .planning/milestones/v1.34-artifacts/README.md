# v1.34 Rig — Pre-Merge Hardware Regression Validation

This milestone benches v1.33's three unmerged PRs (fw#56, app#54, plus the py32 side) against
a control baseline on real hardware, before either sub-repo's PR is merged. The `control` arm
is the pre-v1.33 merge-base; the `v133` arm is the PR head. Both arms are indistinguishable in
every self-reported identity string (`--version`, `fw_board_identity`), so every mechanism in
this directory identifies an arm by absolute path and measured proof, never by a version string
or handshake.

## Directory map

```
.planning/milestones/v1.34-artifacts/
├── README.md              # this file
├── rig-pins.json          # the single machine-readable pin record (SHAs, paths, per-target params)
├── arms-provenance.json   # the two host arms' D-08 proof triple + dependency-set equality
├── PROCEDURE.md           # (plan 06) arm-agnostic per-cell procedure
├── images/                # (plan 02) six committed .hex files + SHA256SUMS.txt
├── tools/                 # rig scripts — stdlib only except touch_1200.py (pyserial)
├── config/                # the one frozen shared FIRESTARTER_CONFIG_DIR for both arms (D-07)
└── bench/
    ├── EVIDENCE.jsonl     # canonical, append-only per-position evidence
    ├── EVIDENCE.md        # rendered from EVIDENCE.jsonl, never hand-edited
    └── cells/<cell-id>/   # per-cell provenance JSON, read-backs, logs
```

## D-16 boundary

Nothing under `.planning/milestones/v1.34-artifacts/` is ever copied into `firestarter/` or `firestarter_app/`. This
phase changes no product code — not firmware, not the host app. Everything here is rig tooling.
A worktree checkout of `firestarter_app` (D-06, below) is the only sub-repo mutation this phase
permits, and it is a detached checkout: no branch is created, advanced, or pushed in either
sub-repo, and no commit lands there from this milestone's rig work.

## The pinned avrdude decision

PlatformIO's own avrdude binary (`~/.platformio/packages/tool-avrdude/avrdude`, measured version
8.1) is pinned for **both** the write chain (`pio run -t upload`) and the independent read-back
chain (D-01). This is a deliberate choice: using the same avrdude binary for both directions
means the write chain and the read chain do not introduce a second avrdude version as a variable
between them. D-01's independence is preserved anyway, because the read is a separate
invocation, on a separate process boundary, judged by a phase-owned script (`judge_readback.py`,
authored in a later plan) rather than by avrdude's own `-U flash:w:...:v` verify pass — the
upload tool never judges its own upload.

The `-A` flag (disable trailing-0xFF truncation on read) was probed before pinning:
`avrdude -A -p atmega328p -c arduino -P /dev/null` failed at port-open
("unable to open port /dev/null for programmer arduino"), not at option-parse — contrasted
against a deliberately invalid `-Z`, which avrdude rejects immediately as `invalid option -- 'Z'`.
`-A` parsed cleanly on the pinned 8.1 binary, so **no fallback substitution was needed**. The
named fallback (`/usr/bin/avrdude` 7.1 + `/etc/avrdude.conf`) is recorded in `rig-pins.json` but
was not used.

## The D-09 non-claim

Both host arms run on the devcontainer's Python 3.12.14 — not the `firestarter_app` CI floor of
Python 3.11. This is stated once, here, as a non-claim: it is not an A/B confound, because both
arms share the identical interpreter, but it means v1.34's bench results were never taken on the
py3.11 floor that app CI targets. Phase 166's honesty ledger carries this forward as a named
line rather than letting it pass unstated.
