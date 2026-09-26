---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 05
type: execute
wave: 4
depends_on: [09-02-atomic-legacy-deletion-and-version-bump, 09-03-host-comment-refresh, 09-04-host-stubs-trim]
files_modified:
  - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md
autonomous: false
requirements:
  - LFW-03
  - LFW-04
  - LMIG-04
requirements_addressed:
  - LFW-03
  - LFW-04
  - LMIG-04
tags:
  - logging
  - measurement
  - bench-verification
  - phase-close
user_setup: []
must_haves:
  truths:
    - "SC#1: 09-MEASUREMENT.md contains a PROGMEM exemption audit list enumerating every remaining PROGMEM hit, separated into two distinct category tables: (a) named-symbol PROGMEM declarations (the SC#1 audit target — must match the documented exemption list: MAGIC_PREAMBLE, CRC8_TABLE, json_parser keys + key_parsers[] table) AND (d) inline F(\"...\") Arduino-macro literal sites (anonymous compiler-generated PROGMEM — exempt by definition per CONTEXT.md D-01 + RESEARCH.md Risk #8). The SC#1 acceptance applies ONLY to category (a); category (d) is documented for completeness but does not gate acceptance."
    - "SC#2: legacy macros grep gate returns 0 hits in firestarter/src/ + firestarter/include/ + firestarter/lib/ (excluding rurp_log_id survivors and comment-only lines)"
    - "SC#3: pytest tests/test_fwguard.py reports 4 PASS; bench-side `firestarter -p <port> fw` (no FIRESTARTER_DEV_ALLOW_PRE_V12 prefix) returns `OK: FW: 3.0.0-dev:<board>, ...` on both Uno and Leonardo, exercising the native-pass guard path"
    - "SC#4: Leonardo Flash reported below 90% with measurable headroom vs the v1.1 baseline of 98.7%; exact percentage + byte count + bytes-free recorded in the anchor table"
    - "SC#5: Uno Flash recorded alongside Leonardo for the milestone-close comparison"
    - "09-MEASUREMENT.md extends the 5-column anchor table from 08-MEASUREMENT.md lines 308-319 with the Phase 9 close row replacing the TARGET/TBD placeholders"
    - "09-MEASUREMENT.md includes a 4-delta attribution table per 09-RESEARCH.md §\"Deltas to compute and record\" (v1.1→Phase 9, Phase 6→Phase 9, Phase 7→Phase 9, Phase 8→Phase 9)"
    - "Bench wire-protocol matrix re-run on Uno + Leonardo post-3.0.0-bump per 08-MEASUREMENT.md §\"Bench Verification — Chipless Wire-Protocol Validation\" (lines 322-384), with the FIRESTARTER_DEV_ALLOW_PRE_V12=1 prefix dropped to exercise the SC#3 native-pass path"
    - "Phase 8 SC#2 (chip-seated W27C512 end-to-end write on Uno + Leonardo) closed inside 09-MEASUREMENT.md per CONTEXT.md Claude's-Discretion bundle"
    - "Phase 8 SC#3 (byte-identical W27C512 readback on Uno + Leonardo) closed inside 09-MEASUREMENT.md per CONTEXT.md Claude's-Discretion bundle"
  artifacts:
    - path: ".planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md"
      provides: "Phase 9 close measurement artifact: extended anchor table + 4-delta attribution + PROGMEM exemption audit (separate named-symbol vs inline-F() tables) + bench-verification transcripts + Phase 8 SC#2/SC#3 closure"
      min_lines: 100
      contains: "Phase 9 close (LMIG-04)"
  key_links:
    - from: ".planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md"
      to: ".planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md"
      via: "extends the anchor table from lines 308-319; cites the Phase 8 close row (Leonardo 85.6% / Uno 69.2%) as the immediate predecessor"
      pattern: "85.6.*24,?538\\|69.2.*22,?330"
    - from: ".planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md"
      to: ".planning/ROADMAP.md"
      via: "cites the v1.1 close baseline (98.7%) as the LMIG-04 milestone comparison point"
      pattern: "98.7"
---

<objective>
Produce the Phase 9 close measurement artifact `09-MEASUREMENT.md` and run the bench-verification step that closes (a) Phase 9 SC#1 (PROGMEM exemption audit), (b) Phase 9 SC#3 (firmware FW-version handshake reports 3.0.0-dev on both boards via the native-pass guard path), (c) Phase 9 SC#4 (Leonardo Flash < 90% with measurable headroom recorded), (d) Phase 9 SC#5 (Uno Flash recorded alongside), and (e) the carried Phase 8 SC#2 / SC#3 chip-seated UAT items per CONTEXT.md Claude's-Discretion bundle.

This plan is **non-autonomous** because the bench step requires the operator at the bench with both Uno and Leonardo boards connected, plus at least one W27C512 chip (or substitute) for the Phase 8 SC#2/SC#3 carry-over. Task 1 (the artifact) and Task 2 (the chipless bench matrix) and Task 3 (the chip-seated UAT) form a single phase-close ritual; the operator's transcripts feed back into 09-MEASUREMENT.md.

Per project memory `[[feedback_always-mirror-uno-leonardo-tests]]`: every Uno bench command is paired with a Leonardo run as the control. Per project memory `[[project_leonardo-shield-socket-wonky]]`: if Leonardo readback differs from Uno on the chip-seated steps, suspect chip contact first before declaring a regression. Per project memory `[[feedback_ic-removal-autonomy]]`: chip-swap cycles between boards do not require per-cycle operator confirmation.

Purpose: deliver the LMIG-04 acceptance number that Phase 10's DOC-02 will cite verbatim into `MILESTONES.md`.
Output: `09-MEASUREMENT.md` published with all 5 SCs covered + Phase 8 carry-over UAT closed.
</objective>

<execution_context>
@/workspaces/firestarter_prom/.claude/get-shit-done/workflows/execute-plan.md
@/workspaces/firestarter_prom/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-VALIDATION.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-02-SUMMARY.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-03-SUMMARY.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-04-SUMMARY.md
@.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md
@firestarter/CLAUDE.md
@firestarter/platformio.ini

<interfaces>
<!-- Source: 09-PATTERNS.md §"Pattern Assignment 8" — 08-MEASUREMENT.md is the structural template. -->

Anchor table to extend (from `08-MEASUREMENT.md:310-316`, current Phase 9 row is `TARGET / TBD`):

| Snapshot | Leonardo Flash | Uno Flash | SRAM (Uno) | Notes |
|----------|----------------|-----------|------------|-------|
| **v1.1 close** | 98.7% (~28,299 / 28,672) | not formally recorded | — | ROADMAP-pinned baseline; per-byte derived from %. |
| **Phase 6 close** | 98.7% (28,292 / 28,672), 380 B free | 80.9% (26,100 / 32,256), 6,156 B free | 1,683 B / 2,048 B (Uno) | LMIG-01: new ID infrastructure alongside legacy text; no call-sites converted yet. |
| **Phase 7 close** | 94.3% (27,026 / 28,672), 1,646 B free | 77.0% (24,838 / 32,256), 7,418 B free | 1,587 B / 2,048 B (Uno) | LMIG-02: all ERROR/WARN/INFO call-sites converted; dead-code deleted. |
| **Phase 8 close** | 85.6% (24,538 / 28,672), 4,134 B free | 69.2% (22,330 / 32,256), 9,926 B free | 1,497 B / 2,048 B (Uno) | LMIG-03: OK/INIT/MAIN/END state-machine acks + MSG_DATA_CHUNK streaming + R-01 SRAM win. |
| **Phase 9 close (LMIG-04)** | XX.X% (NNNNN / 28,672), NNNN B free | XX.X% (NNNNN / 32,256), NNNN B free | NNNN B / 2,048 B (Uno) | LMIG-04: legacy macro tower deletion (send_ack/send_ack_const/rurp_log*/_firestarter_log_*/LOG_OK_MSG/debug_setup/log_debug); inline `OK: FW: ` bootstrap (D-01); FW version → 3.0.0-dev. |

4-delta attribution (Phase 9 row needs all four — per 09-RESEARCH.md §"Deltas to compute and record"):
- v1.1 (98.7%) → Phase 9 close — **LMIG-04 acceptance number**, Phase 10 DOC-02 cites verbatim
- Phase 6 close → Phase 9 close — "pure migration recovery"
- Phase 7 close → Phase 9 close — "state-machine + cleanup contribution"
- Phase 8 close → Phase 9 close — "logging.h macro tower deletion, isolated" (the Phase 9 surface win)

Measurement recipe (per 09-RESEARCH.md §"Flash Measurement Recipe"):
```
cd firestarter && pio run -e leonardo -t clean && pio run -e uno -t clean
cd firestarter && pio run -e leonardo  # grep '^Flash:' for percentage + bytes
cd firestarter && pio run -e uno       # grep '^Flash:' for percentage + bytes
```

Bench commands (per 09-RESEARCH.md §"Bench Verification Matrix Re-use" — note: DROP `FIRESTARTER_DEV_ALLOW_PRE_V12=1` to exercise the SC#3 native-pass):
```
# Flash both boards
cd firestarter
pio run -t upload -e uno --upload-port /dev/ttyACM0
pio run -t upload -e leonardo --upload-port /dev/ttyACM1

# Full chipless wire-protocol matrix (no env-var prefix)
firestarter -p /dev/ttyACM0 fw       # expect: OK: FW: 3.0.0-dev:uno, ...
firestarter -p /dev/ttyACM1 fw       # expect: OK: FW: 3.0.0-dev:leonardo, ...
firestarter -p /dev/ttyACM0 hw       # P-02 sentinel
firestarter -p /dev/ttyACM1 hw       # P-02 sentinel
firestarter -p /dev/ttyACM0 config   # P-03 sentinel
firestarter -p /dev/ttyACM1 config   # P-03 sentinel
firestarter -p /dev/ttyACM0 vpp      # MSG_DATA_VPP_VOLTAGE
firestarter -p /dev/ttyACM1 vpp
firestarter -p /dev/ttyACM0 vpe      # MSG_DATA_VPE_VOLTAGE
firestarter -p /dev/ttyACM1 vpe
firestarter -p /dev/ttyACM0 id W27C512   # exercises INIT_DONE
firestarter -p /dev/ttyACM1 id W27C512
```

Chip-seated UAT carry-over (per 09-RESEARCH.md §"Phase 8 UAT Carry-over"):
- Phase 8 SC#2: `firestarter -p <port> write -e W27C512 <hex>` on Uno + Leonardo; success message + INIT/MAIN/END id-frame rendering
- Phase 8 SC#3: `firestarter -p <port> read -e W27C512 -o out.bin && diff baseline.bin out.bin` on Uno + Leonardo; zero diff on both
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Run automated SC#1, SC#2, SC#4, SC#5 — measure dual AVR Flash + capture PROGMEM exemption audit (separate named-symbol vs inline-F() categories)</name>
  <read_first>
    - firestarter/platformio.ini (lines 1-67 to confirm no -D SERIAL_DEBUG override is active and DATA_BUFFER_SIZE=512 still applies to Leonardo)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"Flash Measurement Recipe" + §"Risks & Landmines" #5, #7, #8
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 8" (08-MEASUREMENT.md structural template)
    - .planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md (full file — copying the anchor table + bench matrix format)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-02-SUMMARY.md (the Plan 02 acceptance gate output is the source of truth for the post-deletion Flash numbers if Task 1 chooses to reuse them; otherwise Task 1 re-runs from a cold-cache clean to ensure measurement determinism)
  </read_first>
  <files>.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md</files>
  <behavior>
    - Creates `09-MEASUREMENT.md` with the following section structure (mirroring 08-MEASUREMENT.md):
      1. Header / frontmatter
      2. `## Anchor Table` — extended with the Phase 9 close row (real numbers replace TARGET/TBD)
      3. `## 4-Delta Attribution`
      4. `## Build Output Excerpts` — verbatim `pio run -e leonardo` and `pio run -e uno` output blocks
      5. `## SC#1 — PROGMEM Exemption Audit` — TWO distinct category tables: (a) named-symbol PROGMEM declarations (the SC#1 acceptance target) AND (d) inline `F("...")` literal sites (exempt by definition, documented for completeness only)
      6. `## SC#2 — Legacy Macro Grep Gate` — command + output (expect 0 hits)
      7. Empty placeholder sections for bench transcripts (Task 2 fills these)
      8. Empty placeholder sections for chip-seated UAT (Task 3 fills these)
    - Leonardo Flash percentage MUST be below 90% per LMIG-04 acceptance
    - All 4 deltas computed (v1.1 → Phase 9, Phase 6 → Phase 9, Phase 7 → Phase 9, Phase 8 → Phase 9)
    - PROGMEM audit SEPARATES (a) named-symbol declarations from (d) inline F() literal sites — no double-counting between the categories
  </behavior>
  <action>
    1. From a clean tree, run the measurement recipe:
       ```
       cd /workspaces/firestarter_prom/firestarter && pio run -e leonardo -t clean && pio run -e uno -t clean
       cd /workspaces/firestarter_prom/firestarter && pio run -e leonardo 2>&1 | tee /tmp/ph9-leonardo.log
       cd /workspaces/firestarter_prom/firestarter && pio run -e uno 2>&1 | tee /tmp/ph9-uno.log
       ```
       Extract from each log: the `Flash:` line (percentage + bytes-used + bytes-max + bytes-free) and the `RAM:` line (SRAM usage). Per 09-RESEARCH.md §"Risks & Landmines #6" use the byte count as the authoritative number; the percentage is human-readable.

    2. Run the LFW-03 grep gate from 09-VALIDATION.md row 9-02:
       ```
       grep -rn 'send_ack\|rurp_log\b\|rurp_log_P\|_firestarter_log_\|LOG_OK_MSG\|log_info_const\|log_error_format\|log_warn\b\|debug_setup\|log_debug\b' firestarter/src firestarter/include firestarter/lib 2>/dev/null | grep -v 'rurp_log_id' | grep -v '^[^:]*:[[:space:]]*//' > /tmp/ph9-grep-legacy.txt
       wc -l /tmp/ph9-grep-legacy.txt
       ```
       Expect: 0 lines. Save the (empty) output to embed in the artifact.

    3. Run the SC#1 PROGMEM exemption survey — **two separate greps** that produce **two distinct category lists** (per RESEARCH.md Risk #8: F() literals are anonymous compiler-generated PROGMEM, NOT named-symbol PROGMEM, and must not be double-counted):

       3a. **Category (a) — named-symbol PROGMEM declarations** (the SC#1 acceptance target):
       ```
       bash -c "grep -rn 'PROGMEM' firestarter/src firestarter/include" 2>/dev/null > /tmp/ph9-progmem-named.txt
       wc -l /tmp/ph9-progmem-named.txt
       ```
       This is the SC#1 audit target. Every line in this file must be a documented exemption: MAGIC_PREAMBLE (frame infra), CRC8_TABLE (frame infra), json_parser key strings + the `key_parsers[]` table (parser infra). Any hit NOT in those three categories is an SC#1 violation — STOP and flag.

       3b. **Category (d) — inline F("...") Arduino-macro literal sites** (exempt by definition per CONTEXT.md D-01 + RESEARCH.md Risk #8; documented for completeness, NOT a gate):
       ```
       bash -c "grep -rn 'F(\"' firestarter/src firestarter/include" 2>/dev/null > /tmp/ph9-progmem-inline-f.txt
       wc -l /tmp/ph9-progmem-inline-f.txt
       ```
       The `F("...")` macro yields a pointer to an anonymous compiler-generated PROGMEM literal — it does NOT produce a named symbol grep can match via `'PROGMEM'`. These sites are exempt by definition (CONTEXT.md D-01 inline LFW-05 bootstrap uses `F("OK: FW: ")`; frame-emit helpers use `F("...")` for inline labels). Document the count and the sites but do not gate on it.

    4. Create `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` with the following structure (mirroring 08-MEASUREMENT.md):

       - Header: title, date, "Boards flashed at: firestarter HEAD <hash> (Phase 9 close)", "Host at: firestarter_app HEAD <hash>"
       - `## Anchor Table` — copy the 5-row table from 08-MEASUREMENT.md lines 310-316 verbatim and replace the Phase 9 row's `TARGET / TBD` placeholders with the real numbers from step 1. Per 09-PATTERNS.md §"Pattern Assignment 8 (a)" the row's Notes column reads: "LMIG-04: legacy macro tower deletion (send_ack, send_ack_const, rurp_log*, _firestarter_log_*, LOG_OK_MSG, debug_setup, log_debug); inline `OK: FW: ` bootstrap (D-01); FW version → 3.0.0-dev."
       - `## 4-Delta Attribution` — compute and tabulate each delta:
         - **v1.1 (98.7%) → Phase 9 close** — LMIG-04 acceptance number. Cite the v1.1 Leonardo baseline of `28,299 / 28,672 = 98.7%` (per anchor row 1). Compute bytes-saved + percentage-point delta. **This is the row Phase 10 DOC-02 cites verbatim.**
         - **Phase 6 close (98.7%, 28,292 B) → Phase 9 close** — "pure migration recovery"
         - **Phase 7 close (94.3%, 27,026 B) → Phase 9 close** — "state-machine + cleanup contribution"
         - **Phase 8 close (85.6%, 24,538 B) → Phase 9 close** — "logging.h macro tower deletion, isolated" — the Phase 9 surface win
       - `## Build Output Excerpts` — verbatim paste the relevant section of `/tmp/ph9-leonardo.log` (the `Linking ... .pio/build/leonardo/firmware.elf` through `Flash:` lines) and same for `/tmp/ph9-uno.log`. Per 08-MEASUREMENT.md lines 15-44 + 59-88 format.
       - `## SC#1 — PROGMEM Exemption Audit` — render TWO separate sub-tables with explicit category labels:
         - **Table (a): Named-symbol PROGMEM declarations** (the SC#1 acceptance gate). Embed `/tmp/ph9-progmem-named.txt` content. Categorize each hit into one of: (a1) `MAGIC_PREAMBLE` (frame infra), (a2) `CRC8_TABLE` (frame infra), (a3) `json_parser` keys + `key_parsers[]` table (parser infra). Per LFW-04 acceptance every named-symbol hit MUST fall in (a1)-(a3). Any uncategorized named-symbol PROGMEM declaration is an SC#1 violation — STOP and flag the contradiction; do not declare LFW-04 satisfied.
         - **Table (d): Inline F("...") literal sites** (informational only; exempt by definition). Embed `/tmp/ph9-progmem-inline-f.txt` content. Expected sites: (d1) `hardware_operations.cpp` `fw_get_version()` `F("OK: FW: ")` per D-01, (d2) frame-emit helper inline labels (if any), (d3) any other Arduino-macro F() use. These are anonymous compiler-generated PROGMEM literals; they do NOT count toward the SC#1 named-symbol budget. The two tables are mutually exclusive — a site appears in (a) OR (d), never both.
         - Add an explicit note: "Category (a) named-symbol PROGMEM declarations gate SC#1; category (d) inline F() literals are exempt per CONTEXT.md D-01 + RESEARCH.md Risk #8 and are documented for completeness only. No site is double-counted."
       - `## SC#2 — Legacy Macro Grep Gate` — embed the grep command + output (expected: empty / 0 lines)
       - `## SC#3 — Host fw-guard Regression` — embed `pytest tests/test_fwguard.py -v` output (4 PASS) + note that the bench-side native-pass exercise is captured in Task 2
       - `## SC#4 + SC#5 — Flash Recorded` — repeats the Phase 9 anchor row inline for readability
       - `## Bench Verification — Chipless Wire-Protocol Validation` — empty section header with the bench command list pre-populated (Task 2 fills in the observed outputs)
       - `## Phase 8 SC#2 (carried) — Chip-Seated Write` — empty section header (Task 3 fills it)
       - `## Phase 8 SC#3 (carried) — Byte-Identical Readback` — empty section header (Task 3 fills it)

    5. Validate: per 09-VALIDATION.md row 9-05 the Leonardo Flash percentage MUST be `< 90.0%`. If not, STOP and flag — Phase 9 has not delivered LMIG-04.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom &amp;&amp; test -f .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; grep -q 'Phase 9 close (LMIG-04)' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; grep -qE '8[0-9]\.[0-9]%|7[0-9]\.[0-9]%|6[0-9]\.[0-9]%|5[0-9]\.[0-9]%|4[0-9]\.[0-9]%' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; grep -q 'PROGMEM Exemption Audit' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; grep -q 'Named-symbol PROGMEM declarations' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; grep -q 'Inline F.*literal sites' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; grep -q '4-Delta Attribution' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; cd /workspaces/firestarter_prom/firestarter &amp;&amp; LEONARDO_PCT=$(pio run -e leonardo 2>&amp;1 | grep '^Flash:' | grep -oE '[0-9]+\.[0-9]+%' | head -1 | tr -d '%') &amp;&amp; awk -v p="$LEONARDO_PCT" 'BEGIN { exit !(p &lt; 90.0) }'</automated>
  </verify>
  <acceptance_criteria>
    - `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` exists with ≥ 100 lines
    - Anchor table contains exactly 5 rows (v1.1 close, Phase 6 close, Phase 7 close, Phase 8 close, Phase 9 close) — verifiable by `grep -c '^|.*close' 09-MEASUREMENT.md` returning ≥ 5
    - Phase 9 row's Leonardo Flash is below 90.0% — verifiable by extracting the percentage and asserting `< 90.0` (LMIG-04 gate)
    - 4-delta attribution table is present (`grep -q '4-Delta Attribution' 09-MEASUREMENT.md`)
    - PROGMEM exemption audit section contains **two distinct labeled sub-tables**: (a) `Named-symbol PROGMEM declarations` (SC#1 acceptance gate) AND (d) `Inline F("...") literal sites` (informational, exempt by definition). Both labels are grep-verifiable in the artifact.
    - Every hit in category (a) is assigned to one of (a1) MAGIC_PREAMBLE, (a2) CRC8_TABLE, (a3) json_parser keys + key_parsers[]; zero hits in an "uncategorized / leftover log PROGMEM" bucket
    - Category (d) is documented but NOT used to gate SC#1 acceptance (the explicit note from step 4 above must appear in the artifact)
    - SC#2 grep gate section shows 0 hits
    - SC#3 section shows `pytest tests/test_fwguard.py -v` output with 4 PASS
    - Build output excerpts include `Flash:` + `RAM:` lines for both Leonardo and Uno
  </acceptance_criteria>
  <done>
    - 09-MEASUREMENT.md published with the anchor row + 4 deltas + PROGMEM audit (two-table form: named-symbol vs inline F()) + SC#2 + SC#3 sections complete
    - Leonardo Flash measurement confirmed below 90% (LMIG-04 gate green)
    - Uno Flash recorded (SC#5)
    - Empty bench-transcript section headers in place for Task 2 to fill
    - Empty chip-seated UAT section headers in place for Task 3 to fill
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Bench wire-protocol re-run post-3.0.0-bump on Uno + Leonardo (SC#3 native-pass + Phase 8 chipless matrix)</name>
  <read_first>
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"Bench Verification Matrix Re-use" (the chipless matrix from 08-MEASUREMENT.md re-run post-bump)
    - .planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md §"Bench Verification — Chipless Wire-Protocol Validation" (lines 322-384 — the canonical bench matrix)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md (the artifact created in Task 1 — Task 2 fills the empty bench section)
  </read_first>
  <what-built>
    Task 1 produced `09-MEASUREMENT.md` with all automated SCs covered. The bench section is currently empty; Task 2 fills it with the observed outputs from running the chipless wire-protocol matrix on both boards post-Phase-9 firmware upload.
  </what-built>
  <how-to-verify>
    Operator runs the bench matrix on both Uno (`/dev/ttyACM0`) and Leonardo (`/dev/ttyACM1` — actual port may differ; resolve via `firestarter --list-ports`). Per project memory `[[feedback_always-mirror-uno-leonardo-tests]]` every Uno command is paired with a Leonardo run as the control.

    1. **Flash both boards with the Phase 9 firmware:**
       ```
       cd /workspaces/firestarter_prom/firestarter
       pio run -t upload -e uno --upload-port /dev/ttyACM0
       pio run -t upload -e leonardo --upload-port /dev/ttyACM1
       ```
       Expected: both uploads succeed.

    2. **SC#3 native-pass verification (no FIRESTARTER_DEV_ALLOW_PRE_V12 prefix):**
       ```
       firestarter -p /dev/ttyACM0 fw
       firestarter -p /dev/ttyACM1 fw
       ```
       Expected output (Uno): `OK: FW: 3.0.0-dev:uno, HW: Rev1, Cmd: 0x0b` (no `FirmwareOutdatedError`)
       Expected output (Leonardo): `OK: FW: 3.0.0-dev:leonardo, HW: Rev1, Cmd: 0x0b`
       Significance: per 09-RESEARCH.md §"Bench commands re-used" — dropping the env-var prefix exercises the SC#3 native-pass guard path. If `FirmwareOutdatedError` is raised, the firmware did NOT bump to major=3 and SC#3 fails.

    3. **Full chipless matrix re-run** (per 08-MEASUREMENT.md lines 322-384):
       ```
       firestarter -p /dev/ttyACM0 hw       # P-02 sentinel
       firestarter -p /dev/ttyACM1 hw
       firestarter -p /dev/ttyACM0 config   # P-03 sentinel
       firestarter -p /dev/ttyACM1 config
       firestarter -p /dev/ttyACM0 vpp      # MSG_DATA_VPP_VOLTAGE
       firestarter -p /dev/ttyACM1 vpp
       firestarter -p /dev/ttyACM0 vpe      # MSG_DATA_VPE_VOLTAGE
       firestarter -p /dev/ttyACM1 vpe
       firestarter -p /dev/ttyACM0 id W27C512   # exercises INIT_DONE; ERROR may fire on Leonardo if VPP overshoots, as observed in Phase 8 — that is expected and validates ERROR-band rendering
       firestarter -p /dev/ttyACM1 id W27C512
       ```
       Expected: every command produces output matching the Phase 8 baseline at 08-MEASUREMENT.md lines 332-342 (severity-band frame coverage table). The ONLY observable that should differ is the `fw` output (FW-version string changes from `2.0.11-dev` to `3.0.0-dev`).

    4. **Operator transcribes** the observed output of each command into the empty `## Bench Verification — Chipless Wire-Protocol Validation` section of `09-MEASUREMENT.md`. Format mirrors 08-MEASUREMENT.md lines 332-342 (Severity band | Frame | Uno result | Leonardo result).

    5. **Operator commits** the updated `09-MEASUREMENT.md`.

    Expected outcome: the chipless matrix validates the LFW-05 inline bootstrap (D-01) + the version bump (D-06) preserve byte-identical wire shape on both boards.
  </how-to-verify>
  <resume-signal>Type "bench-chipless-approved" with the observed outputs transcribed into 09-MEASUREMENT.md, OR describe issues (e.g. "Leonardo fw timed out", "Uno config returned unexpected R1/R2"). If any issue surfaces, the operator should pause and report it — per project memory `[[project_leonardo-shield-socket-wonky]]` Leonardo socket can be wonky; but the chipless matrix does NOT seat a chip so socket issues should not apply.</resume-signal>
  <verify>
    <automated>cd /workspaces/firestarter_prom &amp;&amp; grep -q 'OK: FW: 3.0.0-dev:uno' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; grep -q 'OK: FW: 3.0.0-dev:leonardo' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md</automated>
  </verify>
  <acceptance_criteria>
    - `09-MEASUREMENT.md` contains a populated `## Bench Verification — Chipless Wire-Protocol Validation` section with observed outputs for `fw`, `hw`, `config`, `vpp`, `vpe`, `id W27C512` on BOTH boards
    - The `fw` output for Uno contains the substring `OK: FW: 3.0.0-dev:uno`
    - The `fw` output for Leonardo contains the substring `OK: FW: 3.0.0-dev:leonardo`
    - No `FirmwareOutdatedError` raised on either board (confirms SC#3 native-pass)
    - Every other command produces output matching the Phase 8 baseline severity-band coverage table at 08-MEASUREMENT.md lines 332-342 (allowing for board-specific differences — e.g., Uno may exercise sentinel `Rev1` branch and Leonardo the non-sentinel `Rev1, Override HW: Rev2` branch)
  </acceptance_criteria>
  <done>
    - Chipless bench matrix transcribed into 09-MEASUREMENT.md for both boards
    - SC#3 native-pass confirmed (firmware reports 3.0.0-dev without env-var workaround)
    - LFW-05 wire shape confirmed byte-identical (the `OK: FW: ...` line still parses via the host `_probe_port` regex)
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 3: Phase 8 SC#2 + SC#3 chip-seated UAT carry-over on Uno + Leonardo (W27C512 write + readback)</name>
  <read_first>
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"Phase 8 UAT Carry-over" (lines 612-656)
    - .planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md §"SC#2 Manual Verification Plan" + §"SC#3 Manual Verification Plan" (lines 200-227)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md §"Phase 8 pending UAT (SC#2/SC#3) carry-over"
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md (the artifact in progress — Task 3 fills the chip-seated UAT sections)
  </read_first>
  <what-built>
    Task 1 + Task 2 produced 09-MEASUREMENT.md with all automated + chipless-bench SCs complete. Task 3 closes the Phase 8 carry-over: chip-seated W27C512 end-to-end write (SC#2) + byte-identical readback (SC#3) on BOTH boards. Per CONTEXT.md Claude's-Discretion bundle, Phase 9 is the closure venue because (a) the firmware version bump invalidates any prior chip-seated tests and (b) both boards are already on the operator's bench for Task 2.
  </what-built>
  <how-to-verify>
    Operator runs the chip-seated UAT on both Uno (`/dev/ttyACM0`) and Leonardo (`/dev/ttyACM1`). Per project memory `[[feedback_ic-removal-autonomy]]` the operator does NOT need to ask for per-cycle chip-removal confirmation — chip swaps between boards proceed autonomously.

    Per project memory `[[project_leonardo-shield-socket-wonky]]`: if Leonardo readback differs from Uno on SC#3, **suspect chip contact first** before declaring a regression. Re-seat the chip in the Leonardo socket and re-run before flagging.

    1. **Prepare a test hex file** (e.g., a known-good W27C512 image; if the operator has a pre-Phase-8 baseline binary on the bench, use it as the SC#3 reference. Otherwise capture a fresh baseline from `3.0.0-dev` as the new v1.2+ reference per 09-RESEARCH.md §"Phase 8 UAT Carry-over").

    2. **Phase 8 SC#2 — Write end-to-end on Uno:**
       - Seat W27C512 in Uno shield socket
       - Run:
         ```
         firestarter -p /dev/ttyACM0 write -e W27C512 <test.hex>
         ```
       - Expected: command completes with a success message (no ERROR-band frame). INIT / MAIN / END acks render as decoded id-frame text (NOT raw `INIT:` / `MAIN:` / `END:` text prefixes). The bootstrap `OK: FW: 3.0.0-dev:uno, ...` line is the only text line.

    3. **Phase 8 SC#2 — Write end-to-end on Leonardo:**
       - Move W27C512 to Leonardo shield socket (per `[[feedback_ic-removal-autonomy]]` no confirmation needed)
       - Run:
         ```
         firestarter -p /dev/ttyACM1 write -e W27C512 <test.hex>
         ```
       - Expected: same success criteria as Uno. If Leonardo write fails or behaves erratically, re-seat the chip first (per `[[project_leonardo-shield-socket-wonky]]`).

    4. **Phase 8 SC#3 — Byte-identical readback on Uno:**
       - Move W27C512 back to Uno shield (or leave on Leonardo and reverse order; operator chooses)
       - Run:
         ```
         firestarter -p /dev/ttyACM0 read -e W27C512 -o /tmp/ph9-uno-readback.bin
         diff <baseline.bin> /tmp/ph9-uno-readback.bin
         ```
       - Expected: `diff` returns zero output (byte-identical).

    5. **Phase 8 SC#3 — Byte-identical readback on Leonardo:**
       - Move W27C512 to Leonardo shield
       - Run:
         ```
         firestarter -p /dev/ttyACM1 read -e W27C512 -o /tmp/ph9-leonardo-readback.bin
         diff <baseline.bin> /tmp/ph9-leonardo-readback.bin
         ```
       - Expected: `diff` returns zero output. If non-zero on Leonardo only, re-seat chip and re-run (per `[[project_leonardo-shield-socket-wonky]]`).

    6. **Operator transcribes** the observed write + read outputs into the `## Phase 8 SC#2 (carried)` and `## Phase 8 SC#3 (carried)` sections of `09-MEASUREMENT.md`. Format mirrors 08-MEASUREMENT.md §"SC#2 Manual Verification Plan" / §"SC#3 Manual Verification Plan".

    7. **Operator commits** the updated `09-MEASUREMENT.md`.

    If the operator does NOT have a W27C512 chip on the bench (or a substitute supported chip), they may report "no chip available" — Phase 9 would then ship without Phase 8 SC#2/SC#3 closure (those would remain carried into Phase 10 or a later resumption window). The operator's call.
  </how-to-verify>
  <resume-signal>Type "chip-uat-approved" with the observed write + read transcripts embedded in 09-MEASUREMENT.md (or "no chip available — carrying Phase 8 SC#2/SC#3 to Phase 10"). If a readback diff is non-zero AFTER re-seating, type "readback-regression" and stop for operator investigation — this could indicate Phase 9 broke the wire format despite Task 2's chipless validation.</resume-signal>
  <verify>
    <automated>cd /workspaces/firestarter_prom &amp;&amp; grep -qE 'Phase 8 SC#2 \(carried\)|no chip available' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md &amp;&amp; grep -qE 'Phase 8 SC#3 \(carried\)|no chip available' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md</automated>
  </verify>
  <acceptance_criteria>
    - `09-MEASUREMENT.md` `## Phase 8 SC#2 (carried)` section is either (a) populated with write transcripts for Uno + Leonardo showing success + no INIT/MAIN/END text prefixes (id-frame decode only) OR (b) annotated "no chip available — carrying Phase 8 SC#2 to Phase 10"
    - `09-MEASUREMENT.md` `## Phase 8 SC#3 (carried)` section is either (a) populated with read + `diff` transcripts for Uno + Leonardo showing zero diff OR (b) annotated "no chip available — carrying Phase 8 SC#3 to Phase 10"
    - If readback diff non-zero on Leonardo: at least one re-seat attempt is documented per `[[project_leonardo-shield-socket-wonky]]` before declaring a regression
  </acceptance_criteria>
  <done>
    - Phase 8 SC#2 + SC#3 either closed (with transcripts) or explicitly carried forward (with rationale)
    - `09-MEASUREMENT.md` is the single source of truth for Phase 9 close; Phase 10 DOC-02 will quote it directly
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| firmware ↔ host (post-bump) | Bench step exercises the LFW-05 byte-identical wire shape across the version bump. If the inline emit in Plan 02 changed the wire output by even one byte, Task 2 catches it. |
| chip ↔ shield socket | Chip-seated UAT in Task 3 reaches the physical chip-contact layer; per project memory `[[project_leonardo-shield-socket-wonky]]` Leonardo socket can be unreliable. |
| measurement determinism | Flash measurement requires cold-cache rebuilds (per 09-RESEARCH.md §"Risks & Landmines #5/#7") — Task 1 enforces `pio run -t clean` before measuring. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-09-05-01 | Tampering | Inline LFW-05 wire shape regression — Plan 02's `F("OK: FW: ")` + `println(FW_VERSION)` produces a different byte sequence than the pre-Phase-9 `send_ack_const(FW_VERSION)` chain | mitigate | Task 2 bench step on BOTH boards explicitly exercises the host `_probe_port` regex via `firestarter -p <port> fw`. If the host can parse the `FW: <digits>` substring, the wire shape is operationally byte-identical (the regex is the load-bearing observable, not exact byte equality). Failure surfaces as `FirmwareOutdatedError` or a parse miss. |
| T-09-05-02 | Denial of Service | Chip-seated readback diverges on Leonardo due to wonky socket, masquerading as a Phase 9 regression | mitigate | Project memory `[[project_leonardo-shield-socket-wonky]]` is documented as Task 3's first investigation step. Re-seat before declaring a regression. |
| T-09-05-03 | Information Disclosure | PROGMEM exemption audit (SC#1) misses a leftover log-purposed PROGMEM string by double-counting an inline F() site as a named-symbol declaration, declaring LFW-04 satisfied when it is not | mitigate | Task 1 uses TWO separate greps producing TWO mutually-exclusive category tables: (a) `grep -rn 'PROGMEM' ...` finds named-symbol PROGMEM declarations (the SC#1 acceptance gate; must match a documented exemption: MAGIC_PREAMBLE / CRC8_TABLE / json_parser keys); (d) `grep -rn 'F("' ...` finds inline F() literal sites (exempt by definition per CONTEXT.md D-01 + RESEARCH.md Risk #8). The two greps look for different syntactic patterns, so no site is double-counted. Any uncategorized named-symbol PROGMEM hit STOPS the task and surfaces a contradiction. |
| T-09-05-04 | Denial of Service | Build-cache stale objects from Plan 02 file deletions leave dangling links that pass `pio run` but fail on cold checkout | mitigate | Task 1 prefixes both AVR measurements with `pio run -t clean`. The measurement is from a cold-cache rebuild. |
| T-09-05-05 | Operator-side automation script breakage from `OK: ` → `OK: Ready` change in dev_tools acks (RESEARCH.md Risk #4) | accept | Already accept-dispositioned in Plan 01 / Plan 02 threat models; bench step re-confirms (any `firestarter -p <port> dev` invocation in Task 2/3 would surface the change if it broke). |
| T-09-05-06 | Tampering | Operator transcription error in bench section (Task 2) or chip-seated section (Task 3) — observed output mis-typed into the artifact | mitigate | Task 2/3 acceptance criteria pin specific grep substrings (`OK: FW: 3.0.0-dev:uno`, `OK: FW: 3.0.0-dev:leonardo`). The grep gate catches obvious transcription errors. For chip-seated transcripts, the operator + Phase 10 reviewer cross-check the SUMMARY against the artifact. |
</threat_model>

<verification>
### Plan-level acceptance gate (run after all 3 tasks complete)

```bash
# 1. Artifact exists with all required sections (including the two-table PROGMEM audit form)
test -f .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md || { echo "FAIL: artifact missing"; exit 1; }
for SECTION in 'Anchor Table' '4-Delta Attribution' 'PROGMEM Exemption Audit' 'Named-symbol PROGMEM declarations' 'Inline F' 'Legacy Macro Grep Gate' 'Bench Verification — Chipless Wire-Protocol Validation' 'Phase 8 SC#2 (carried)' 'Phase 8 SC#3 (carried)'; do
  grep -q "$SECTION" .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md || { echo "FAIL: section $SECTION missing"; exit 1; }
done

# 2. LMIG-04 acceptance — Leonardo Flash < 90%
LEONARDO_PCT=$(grep -E '\*\*Phase 9 close' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md | grep -oE '[0-9]+\.[0-9]+%' | head -1 | tr -d '%')
awk -v p="$LEONARDO_PCT" 'BEGIN { exit !(p < 90.0) }' || { echo "FAIL: Leonardo Flash >= 90% ($LEONARDO_PCT%)"; exit 1; }

# 3. SC#3 native-pass — both boards report 3.0.0-dev on the bench
grep -q 'OK: FW: 3.0.0-dev:uno' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md || { echo "FAIL: Uno fw"; exit 1; }
grep -q 'OK: FW: 3.0.0-dev:leonardo' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md || { echo "FAIL: Leonardo fw"; exit 1; }

# 4. Phase 8 SC#2 + SC#3 sections populated (or explicitly carried)
grep -qE 'Phase 8 SC#2 \(carried\)' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md || { echo "FAIL: SC#2 carry"; exit 1; }
grep -qE 'Phase 8 SC#3 \(carried\)' .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md || { echo "FAIL: SC#3 carry"; exit 1; }

echo "PLAN 05 GREEN — Phase 9 ready for /gsd-verify-work"
```
</verification>

<success_criteria>
- `09-MEASUREMENT.md` exists in the phase directory with all required sections
- SC#1: PROGMEM exemption audit complete in TWO distinct labeled sub-tables — (a) Named-symbol PROGMEM declarations: every hit categorized into MAGIC_PREAMBLE / CRC8_TABLE frame infra OR json_parser keys + key_parsers[] parser infra; zero uncategorized log-purposed PROGMEM strings. (d) Inline F("...") literal sites: documented for completeness; exempt by definition per CONTEXT.md D-01 + RESEARCH.md Risk #8; does NOT gate SC#1 acceptance. No site appears in both tables.
- SC#2: legacy macros grep gate returns 0 hits
- SC#3: pytest tests/test_fwguard.py 4 PASS + bench `firestarter fw` returns `OK: FW: 3.0.0-dev:<board>` on both Uno and Leonardo with no env-var prefix (native-pass guard path exercised)
- SC#4: Leonardo Flash percentage in the Phase 9 anchor row is `< 90.0%` (LMIG-04 acceptance)
- SC#5: Uno Flash recorded in the same anchor row
- Anchor table extended with the Phase 9 close row; 4-delta attribution table present
- Phase 8 SC#2 + SC#3 sections either populated with chip-seated transcripts (both boards) OR explicitly annotated as carried forward (with rationale)
- All three project-memory directives observed during the bench step: Uno-Leonardo pairing, Leonardo socket caution, IC-removal autonomy
</success_criteria>

<output>
After completion, create `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-05-SUMMARY.md` recording:
- Path to `09-MEASUREMENT.md` (the phase-close artifact)
- Leonardo Flash percentage + byte count + bytes free (the LMIG-04 acceptance number)
- Uno Flash percentage + byte count + bytes free
- The 4 deltas (v1.1 → Phase 9, Phase 6 → Phase 9, Phase 7 → Phase 9, Phase 8 → Phase 9) — bytes saved + percentage-point delta for each
- PROGMEM exemption audit summary: count of hits per category, with explicit separation of (a) named-symbol declarations (the SC#1 acceptance gate) vs (d) inline F() literal sites (informational only)
- Bench section status: chipless matrix complete on both boards (yes/no)
- Chip-seated UAT status: Phase 8 SC#2 + SC#3 closed on both boards (yes/no/carried)
- Notes (optional): any operator observations (Leonardo socket re-seat events, unexpected output, etc.)

This SUMMARY is the input to Phase 10 DOC-02; it must be precise enough that the milestone-close documentation can quote it without re-running anything.
</output>
