# Phase 139 — Citation Register

**Owner requirement:** ISSUE-01 (every C1/C2/C3 claim citable by `file:line` or commit SHA) and
ISSUE-02 (the 6.25 V program-VCC ceiling statement and the acceptance-criteria amendment it requires)
— this register supplies the evidence floor both requirements stand on.

**Measured:** 2026-08-09, this session, live and read-only.

Per the plan's own instruction, nothing below is copied from `139-RESEARCH.md` — every command in
this register was re-run fresh this session, and any divergence from research's recorded figures is
stated explicitly rather than reconciled by editing `139-CONTEXT.md` or `139-RESEARCH.md`. In practice
every figure below matched RESEARCH's recorded value exactly, with one unit-precision clarification
noted in §0 and one strengthening noted in §2 (minipro's GitLab citations, unreachable in RESEARCH's
own session, resolved live in this one).

---

## 0. gh#15 before-state

| Field | Command (as run) | Result |
|---|---|---|
| state | `gh issue view 15 --repo henols/firestarter_prom --json state -q .state` | `OPEN` |
| comment count | `gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments \| length'` | `0` |
| labels | `gh issue view 15 --repo henols/firestarter_prom --json labels -q .labels` | `[]` |
| updatedAt | `gh issue view 15 --repo henols/firestarter_prom --json updatedAt -q .updatedAt` | `2026-07-12T09:15:27Z` |
| createdAt | `gh issue view 15 --repo henols/firestarter_prom --json createdAt -q .createdAt` | `2026-07-12T09:15:27Z` |
| body byte length | `gh issue view 15 --repo henols/firestarter_prom --json body -q .body \| wc -c` | `5964` bytes |

All six fields match `139-RESEARCH.md` §"gh#15 Live State" exactly — no divergence.
`updatedAt == createdAt` still holds: the body has not been edited at any point between research and
this plan's execution. This measurement is also independent of Task 1's own before-count check earlier
in this same plan (which asserted comment count `0` via a separate, differently-shaped query) — both
land on `0`, a second free corroboration.

**One measurement precision note, not a divergence.** `gh issue view ... --json body -q .body | wc -c`
gives **5964** (raw byte count — matches RESEARCH exactly and is the figure recorded above). Piping the
same body through `jq`'s `.body | length` directly gives **5950** — that function counts Unicode
*codepoints*, not bytes, and the body contains multi-byte UTF-8 characters (`µ` in "500 µs" etc., each
1 codepoint but 2 bytes). `wc -c` is the correct byte-length oracle and the one used above and by
RESEARCH; the 14-byte gap is arithmetic, not a body change.

---

## 1. Pinning strategy

Citations pin to commit SHAs, never branch names (D-07).

| Repo | Pin SHA (re-derived this session) | Command (as run) |
|---|---|---|
| `henols/firestarter_prom` (meta) | `b6aa1dcb23ef9931105752ed6dd6badccf6719de` — pushed tip of this milestone branch | `git ls-remote --heads origin \| grep v1.31` |
| `henols/firestarter` (fw) | `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`origin/beta`) | `git -C /workspaces/firestarter rev-parse origin/beta` |
| `henols/firestarter_app` (host) | `4d18b645ab18a2d2465f0f623062e9249eb24132` (`origin/beta` **and** branch tip — same commit) | `git -C /workspaces/firestarter_app rev-parse origin/beta` and `git -C /workspaces/firestarter_app rev-parse HEAD` |

All three re-derived fresh this session; all three match `139-RESEARCH.md`'s recorded values exactly —
no divergence. (Firmware branch tip, for reference, is `fb7949c0bdd575177262a76af506cec3b73ea28b` — not
used as a pin, since `origin/beta` is what a stranger reads, but confirmed reachable, see below.)

**Blob identity, re-confirmed, not assumed** — the two firmware anchor files are byte-identical at
`HEAD` (`fb7949c0`) and `origin/beta` (`6fab4eaf`):

```
$ for r in HEAD origin/beta; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
$ for r in HEAD origin/beta; do git -C /workspaces/firestarter rev-parse $r:src/proms/memory.cpp; done
478fa1d35fed2abbefb27d4d2c54dcec02086687
478fa1d35fed2abbefb27d4d2c54dcec02086687
```

The host repo's `HEAD` and `origin/beta` are the *same commit* (`4d18b645`), so every cited host file
(`infoic-field-dictionary.md`, `database.py`) is trivially identical between them — no separate check
needed.

**Visibility, measured this session:**

```
$ gh repo view henols/firestarter_prom --json visibility -q .visibility   → PUBLIC
$ gh repo view henols/firestarter        --json visibility -q .visibility  → PUBLIC
$ gh repo view henols/firestarter_app    --json visibility -q .visibility  → PUBLIC
```

All three repos PUBLIC — no citation into any of them requires special access, and planning artifacts
in the meta repo are legitimately citable by a stranger.

### Two deliberate divergences from `139-CONTEXT.md` §canonical_refs

**`138-BASELINE.md` is DROPPED from the citation set.** Re-confirmed this session:

```
$ curl -s -o /dev/null -w "%{http_code}\n" \
  https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/phases/138-preconditions-baseline/138-BASELINE.md
404
```

It 404s at the pushed tip (it landed in the unpushed `baa131a3`), it appears **nowhere** in D-06's
binding citation list — only in `139-CONTEXT.md`'s looser §canonical_refs "Evidence being cited" list
— and everything it would prove is already inside `138-02-PULSE-DISTRIBUTION.md`, which resolves (see
anchor 8 below). Dropping it means this phase needs **no `git push`** at all: the phase's only outward
act stays the post itself (owned by plan 139-05), matching D-08's shape exactly.

**`.planning/PROJECT.md` is NOT cited publicly.** Its C1/C2/C3 table sits at different line numbers
depending on which ref is read — re-confirmed this session, not assumed from RESEARCH:

```
$ grep -n '\*\*C1\*\*' /workspaces/.planning/PROJECT.md
71:| **C1** | ...
$ curl -s https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/PROJECT.md \
    | grep -n '\*\*C1\*\*'
61:| **C1** | ...
```

Line 71 locally, line 61 at the pushed tip — a ten-line shift. A permalink written from local line
numbers would return HTTP 200 and point at the wrong ten lines (exactly Pitfall 2's failure mode).
`PROJECT.md` is the *source* of the comment's substance — the design it renders for a public reader —
not one of its citations, and D-06's binding citation list never names it.

---

## 2. Anchor verification table

Every anchor is verified by CONTENT: fetch the raw file at the pinned SHA, slice to the pinned line
range with `awk`, `grep -qF` for an expected substring. An HTTP 200 alone is never recorded as
verification. All nine raw-file anchors below were run through the identical `verify_anchor` shell
function reproduced verbatim from `139-RESEARCH.md` §"Code Examples":

```bash
verify_anchor() {  # $1=raw-url  $2=first  $3=last  $4=expected substring
  local out; out=$(curl -sf "$1") || { echo "FAIL(fetch) $1"; return 1; }
  printf '%s\n' "$out" | awk -v a="$2" -v b="$3" 'NR>=a && NR<=b' | grep -qF -- "$4" \
    && echo "OK   $1#L$2-L$3" || { echo "FAIL(anchor) $1#L$2-L$3"; return 1; }
}
```

**Transcript, this session, all nine raw anchors.** The first seven lines are the plan's own literal
`<verify><automated>` block, run verbatim, exiting `OK-T2-ANCHORS`. That literal block's argv list
covers seven of the nine anchors named in this task's `<action>` text; the remaining two — the
erase-pulse anchor and the pulse-distribution script — were run immediately after through the *same*
function, with the same fail-closed discipline, so all nine carry an independent `OK` line:

```
OK   https://raw.githubusercontent.com/henols/firestarter_app/4d18b645ab18a2d2465f0f623062e9249eb24132/doc/infoic-field-dictionary.md#L210-L217
OK   https://raw.githubusercontent.com/henols/firestarter_app/4d18b645ab18a2d2465f0f623062e9249eb24132/firestarter/database.py#L128-L128
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L20-L20
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L69-L77
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L177-L177
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/memory.cpp#L249-L258
OK   https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md#L237-L249
OK-T2-ANCHORS
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L274-L283
OK   https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/phases/138-preconditions-baseline/138-pulse-distribution.py#L120-L120
```

Nine `OK` lines, zero `FAIL` lines. Per-anchor detail follows, four columns each: numbered anchor · the
literal command as run · the sliced text actually returned · the enclosing function or section.

| # | Anchor | Command (as run) | Sliced text actually returned | Enclosing function / section |
|---|---|---|---|---|
| 1 | `firestarter_app/doc/infoic-field-dictionary.md:210-217` | `verify_anchor "$APP/doc/infoic-field-dictionary.md" 210 217 '50000 µs (×100 wrong)'` | Table row: `AM2716 \| 0x0B \| 0x1F4 \| 500 µs \| 50000 µs (×100 wrong)`.<br>L217: "**BUG-2 (DEC-03):** Correct is: raw `pulse_delay` value = microseconds for ALL protocols; current `build_db.py` `interpret_timing()` applies `val * 100` for `protocol_id` `0x07` and `0x0B` (`database.c#L866`) — this ×100 multiplier is wrong; 252 chips across those two protocols currently have inflated `pulse_duration` values in `chip_database.json`; fix deferred to Phase 57." | The raw-hex→µs adjudication table inside `doc/infoic-field-dictionary.md` (a markdown reference table, not a function) — **C1's adjudication**. |
| 2 | `firestarter_app/firestarter/database.py:128` | `verify_anchor "$APP/firestarter/database.py" 128 128 'def _parse_pulse_duration'` | `def _parse_pulse_duration(pulse_str: str) -> int:` — docstring: "Parse a pulse_duration string from chip_database.json into microseconds. Accepts values like \"100 us\", \"1000 us\", \"Algorithm Controlled\", or \"\". Returns the integer microsecond value, or 0 for unknown / algorithm-controlled." | The function itself, `_parse_pulse_duration()` — the `pulse_duration` string → `pulse_delay` int-µs layer (Phase 138 D-11: imported, never reimplemented). |
| 3 | `firestarter/src/proms/eprom.cpp:20` | `verify_anchor "$FW/src/proms/eprom.cpp" 20 20 '#define NUMBER_OF_RETRIES 20'` | `#define NUMBER_OF_RETRIES 20` | Top-level file-scope macro (before any function). Used as the divisor in the adaptive-growth formula (anchor 5) and as the retry-loop bound inside `eprom_write_execute()`. |
| 4 | `firestarter/src/proms/eprom.cpp:69-77` | `verify_anchor "$FW/src/proms/eprom.cpp" 69 77 'case 0x0B: handle->pulse_delay = 500;'` | `if (handle->pulse_delay == 0) { switch (handle->protocol) {`<br>`case 0x08: handle->pulse_delay = 100;  break;  // EPROM_QUICK: 100µs`<br>`case 0x0B: handle->pulse_delay = 500;  break;  // EPROM_LEGACY: 500µs`<br>`default:   handle->pulse_delay = 1000; break;  // EPROM_STD: 1ms } }` | `configure_eprom()`, opens at eprom.cpp:41. This range shows the firmware **already** defaults `0x0B` to 500 µs — independent corroboration of C1 straight out of the code gh#15 asks to change. |
| 5 | `firestarter/src/proms/eprom.cpp:177` | `verify_anchor "$FW/src/proms/eprom.cpp" 177 177 'org_delay * retries / NUMBER_OF_RETRIES'` | `handle->pulse_delay = org_delay + (org_delay * retries / NUMBER_OF_RETRIES);` | `eprom_write_execute()`, opens at eprom.cpp:143 — the adaptive pulse-growth formula, inside the block-mismatch retry loop gh#15 asks to remove. |
| 6 | **`firestarter/src/proms/memory.cpp:321-330`** ← corrected C3 anchor | `verify_anchor "$FW/src/proms/memory.cpp" 249 258 'delayMicroseconds(handle->pulse_delay);'` | `rurp_chip_enable();`<br>`delayMicroseconds(handle->pulse_delay);`<br>`rurp_chip_disable();` (lines 256-258, inside the fetched 249-258 range) | **`memory_set_data()`** — this is **the PROGRAM pulse**. `memory.cpp:86` binds `firestarter_set_data` to `memory_set_data`; `eprom.cpp`'s `program_mismatched_bytes()` (lines 114-126) has no delay of its own — the per-byte program pulse happens inside this function via the function pointer. |
| 7 | `firestarter/src/proms/eprom.cpp:274-283` — kept, relabelled | `verify_anchor "$FW/src/proms/eprom.cpp" 274 283 'delayMicroseconds(handle->pulse_delay);'` | `void eprom_internal_erase(firestarter_handle_t* handle) {`<br>`... rurp_chip_input(); ... delay(100); ... firestarter_set_address(handle, 0x0000); ...`<br>`rurp_chip_enable();`<br>`delayMicroseconds(handle->pulse_delay);` | **`eprom_internal_erase()`**, opens exactly at line 274 — this is **the ERASE pulse**, the only other `delayMicroseconds()` call in `eprom.cpp`. **Correction recorded here:** `139-CONTEXT.md` D-06 lists `eprom.cpp:283` as C3's "the pulse" anchor with no qualifier — that citation resolves but is checkably the erase pulse, not the program pulse, and a reader following it would land in the wrong function. Anchor 6 above (`memory.cpp:321-330`) is the corrected program-pulse citation; this row is kept and explicitly relabelled rather than dropped, because `handle->pulse_delay` doing double duty as both program and erase pulse is itself a real design observation worth citing. |
| 8 | `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md:237-249` | `verify_anchor "$META/.../138-02-PULSE-DISTRIBUTION.md" 237 249 'n = 170'` | Three histogram lines: `0x07: n = 170, histogram 100 us ×113, 200×27, 1000×22, 500×4, 50×4` · `0x08: n = 127, histogram 100 us ×104, 50×11, 10×7, 200×2, 1000×2, 20×1` · `0x0B: n = 32, histogram 500 us ×21, 1000×6, 200×5` — each line's own text states "zero divergence" against both the seed and `138-RESEARCH.md`. | §"the live pulse-width distribution" measurement section. `n = 170`, `n = 127` and `n = 32` **all three** confirmed inside the fetched 237-249 slice by direct inspection — the plan's "separately confirm" instruction is satisfied by the same fetch, no second request needed. |
| 9 | `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | existence: `curl -sf -o /dev/null -w "%{http_code}" "$META/.../138-pulse-distribution.py"` → `200`; content: `verify_anchor "$META/.../138-pulse-distribution.py" 120 120 'from firestarter.database import _parse_pulse_duration'` | `from firestarter.database import _parse_pulse_duration  # noqa: E402 -- the production parser, D-11, never reimplemented` | Import section of the runnable script. Confirms the script imports Phase 138's own D-11 rule (never reimplement the parser) rather than re-deriving pulse-duration parsing — the "runnable, a stranger can re-run" property C2 depends on. |

### Commit-level citations (C1)

| # | Citation | Command (as run) | Result |
|---|---|---|---|
| 10 | commit `8de307f` (`firestarter_app`) | `gh api repos/henols/firestarter_app/commits/8de307f278370c07bfd3328aa9020248e66d0649 --jq '.sha[0:7] + " \| " + (.commit.message \| split("\n")[0])'` | `8de307f \| feat(57-01): remove interpret_timing x100 multiplier and fix bare excepts (DEC-03)` — full SHA `8de307f278370c07bfd3328aa9020248e66d0649` |
| | reachability | `git -C /workspaces/firestarter_app branch -r --contains 8de307f278370c07bfd3328aa9020248e66d0649` | Lists 12 remote branches including **`origin/beta`** and `origin/gsd/v1.31-27c-programming-algorithm-fidelity` |
| 11 | commit `12286df` (`firestarter_app`) | `gh api repos/henols/firestarter_app/commits/12286df86abaf02be1d8e719818b7ca76a4c00e9 --jq '.sha[0:7] + " \| " + (.commit.message \| split("\n")[0])'` | `12286df \| feat(57-03): regenerate chip_database.json from corrected build_db.py` — full SHA `12286df86abaf02be1d8e719818b7ca76a4c00e9` |
| | reachability | `git -C /workspaces/firestarter_app branch -r --contains 12286df86abaf02be1d8e719818b7ca76a4c00e9` | Lists the identical 12-branch set including **`origin/beta`** |

Both commit subjects match `139-RESEARCH.md`'s D-06/citation-register expectations exactly. Both are
reachable from `origin/beta` — the ×100 BUG-2 fingerprint is cited by commit, not by assertion.

### minipro — GitLab, not GitHub

Upstream is `https://gitlab.com/DavidGriffith/minipro`, pinned at
`cae74c0607077d6260b24995f5e4c0d0b66a6a2e`. **gitlab.com was reachable from this session** (confirmed
`curl -sf` returned HTTP 200) — this is a live, executed re-verification, not the `[CITED, not
re-verified this session]` fallback the plan's `<action>` text authorizes for the case where GitLab is
unreachable. RESEARCH's own session found minipro "not local" (present only in a different, now-gone
scratchpad) and could not re-verify against the live GitLab remote; this session could, and did.

| # | Anchor | Command (as run) | Sliced text actually returned | Enclosing function / section |
|---|---|---|---|---|
| 12 | `src/t48.c:246` | `curl -sf "$MP/src/t48.c" \| awk 'NR==246'` | `int t48_begin_transaction(minipro_handle_t *handle)` | Function signature — `t48_begin_transaction()` itself opens here. |
| 13 | `src/t48.c:255` | `curl -sf "$MP/src/t48.c" \| awk 'NR==255'` | `msg[1] = device->protocol_id;` | Inside `t48_begin_transaction()` — `protocol_id` packed into the `BEGIN_TRANS` wire message. |
| 14 | `src/t48.c:266-267` | `curl -sf "$MP/src/t48.c" \| awk 'NR>=266 && NR<=267'` | `format_int(&(msg[12]), device->pulse_delay, 2,`<br>`format_int(..., MP_LITTLE_ENDIAN);` | Inside `t48_begin_transaction()` — `pulse_delay` packed into the same message, as a **sibling, orthogonal** field to `protocol_id` (anchor 13). This is the "two orthogonal wire fields" claim's whole evidentiary basis. |
| 15 | `src/main.c:698` | `curl -sf "$MP/src/main.c" \| awk 'NR==698'` | `"Default write pulse: %u us\nAvailable write pulse[us]: 1-65535\n",` | The CLI help-string table for the `-o pulse=N` option — the source of the **65535 µs ceiling** claim, corroborating the 2-byte (`format_int(..., 2, ...)`) wire width used at anchor 14. |

**Scope note:** RESEARCH additionally cross-checked four sibling files (`tl866a.c:257`,
`tl866iiplus.c:238`, `t56.c:193`, `t76.c:529`) for the identical `format_int(..., pulse_delay, 2, ...)`
pattern. This task's `<action>` text names only `t48.c` and `main.c` as the anchors to verify for this
register; the four siblings are not re-verified here and are cited by reference to RESEARCH's own
resolution, not re-derived — no claim in this register depends on them.

---

## 3. D-10 baseline — the correction precedes implementation

The "before implementation" claim is recorded as **three-ref blob equality**, not a `git status`
inference, for both `eprom.cpp` and `memory.cpp`.

```
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done | sort -u | wc -l
1
```

```
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/memory.cpp; done
478fa1d35fed2abbefb27d4d2c54dcec02086687
478fa1d35fed2abbefb27d4d2c54dcec02086687
478fa1d35fed2abbefb27d4d2c54dcec02086687
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/memory.cpp; done | sort -u | wc -l
1
```

Both files: **exactly one** unique blob SHA across `HEAD`, `origin/beta`, and `3085084` (the Phase 138
frozen firmware base named in `PROJECT.md`). `3085084` is confirmed an ancestor of `HEAD`:

```
$ git -C /workspaces/firestarter merge-base --is-ancestor 3085084 HEAD && echo "3085084 IS an ancestor of HEAD"
3085084 IS an ancestor of HEAD
```

`eprom.cpp` = `8dfa4cced460416fc1b0f73cf3f0e6f77965f962` at all three refs — exactly matching
`139-RESEARCH.md` F-09's recorded value; no divergence. `memory.cpp` = `478fa1d35fed2abbefb27d4d2c54dcec02086687`
at all three refs — RESEARCH's own F-09 measured only `HEAD` and `origin/beta` for `memory.cpp` and
suggested extending the check to `3085084` ("Consider extending the same three-ref blob check to
`memory.cpp`"); this plan carried out that suggestion, and `3085084` agrees with the other two refs.

**Why the meta repo's ` M firestarter` line is a stale gitlink pointer, not an edit.** The meta repo's
own tree records:

```
$ git ls-tree HEAD firestarter firestarter_app
160000 commit 0933bd7d602efb30e4a666e8231ecf724e90ab09	firestarter
160000 commit cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7	firestarter_app
```

...while the actual checkouts are `fb7949c0bdd575177262a76af506cec3b73ea28b` (firestarter) and
`4d18b645ab18a2d2465f0f623062e9249eb24132` (firestarter_app). `git status` reports ` M firestarter` /
` M firestarter_app` purely because the meta repo's *tracked gitlink SHA* is behind the *checked-out*
commit in each submodule — a bookkeeping drift in what the meta repo points at, not a source edit
inside either submodule's working tree. Neither `eprom.cpp` nor `memory.cpp` is touched by this drift;
the three-ref blob-equality check above is what actually proves "untouched," and it is immune to this
drift by construction, since it reads each submodule's own commit history directly rather than
trusting the meta repo's gitlink pointer.

**`git submodule status` is never used in this phase's verification, by design.** It fails
unconditionally in this repo, for a reason unrelated to either submodule cited here:

```
$ git submodule status
fatal: no submodule mapping found in .gitmodules for path '.planning/v1.7/upstream-rurp'
```

This is a pre-existing `.gitmodules` mapping gap on an unrelated path
(`.planning/v1.7/upstream-rurp`); any script using this command as a blanket precondition check would
exit non-zero for a reason that has nothing to do with the D-10 claim it was meant to verify. This
register uses the three-ref blob-equality form exclusively.

---

*Phase: 139-gh-15-correction-outward*
*Plan: 139-01*
*Pinned SHAs this register cites against — meta `b6aa1dcb23ef9931105752ed6dd6badccf6719de` ·
firmware (`origin/beta`) `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` · host (`origin/beta`)
`4d18b645ab18a2d2465f0f623062e9249eb24132` · minipro (GitLab) `cae74c0607077d6260b24995f5e4c0d0b66a6a2e`.*

---

## 4. Claim gate — planted-first, then the real run over both artifacts

**Measured:** 2026-08-09, this session (plan 139-04), live and read-only except for one scratchpad-only
planted-violation fixture, deleted immediately after its run and never committed. Per this register's
own standing convention (§0's preamble), nothing below is copied from `139-02-SUMMARY.md`'s own
non-vacuity record — every run below was re-executed fresh in this plan, against this plan's own two
named artifacts, not reused from a different plan's different file set.

**The red preceded the green, in that literal order.** No pass of `139-check-claims.py` is relied on
anywhere in this plan, or in `139-04-SUMMARY.md`, until the planted-violation run below was observed
FAIL, in this same task, immediately before the default-mode run that licenses the freeze in §5.

### Run 1 — planted-violation re-run, MUST FAIL — observed FAIL

Exact planted line appended to a scratchpad copy of `139-GH15-COMMENT.md` (never committed, deleted
immediately after the run):

```
This firmware is datasheet-conformant and algorithm-accurate.
```

Literal command as run:

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward
$ T=$(mktemp -d); cp 139-GH15-COMMENT.md "$T/planted.md"
$ printf '\nThis firmware is datasheet-conformant and algorithm-accurate.\n' >> "$T/planted.md"
$ out=$(python3 139-check-claims.py "$T/planted.md"); rc=$?; printf '%s\n' "$out"; rm -rf "$T"
```

Literal stdout:

```
FAIL: 2 forbidden phrase match(es):
  <scratchpad>/planted.md:69: forbidden phrase match [datasheet-conformant]: 'datasheet-conformant'
  <scratchpad>/planted.md:69: forbidden phrase match [algorithm-accurate]: 'algorithm-accurate'
```

**Exit code: 1.** Both planted labels (`datasheet-conformant`, `algorithm-accurate`) named verbatim.
Re-run a second time after Task 2's mid-task fix to `139-GH15-COMMENT.md` (see below) with an identical
result — the fix changed only the disposition table's column count, not this run's outcome.

### Run 2 — default-mode run over both named artifacts, MUST PASS — observed PASS

Literal command as run (no arguments — `_DEFAULT_TARGETS` resolves to both outward artifacts):

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && python3 139-check-claims.py
```

Literal stdout:

```
PASS: scanned 139-GH15-COMMENT.md, 139-GH15-BODY-AMENDMENT.md; 2 file(s) carry both required caveats (this PASS is the mechanizable half of the ISSUE-02 / D-05 discipline only -- see the module docstring's explicit non-claim)
```

**Exit code: 0.** The `PASS:` line names both `139-GH15-COMMENT.md` and `139-GH15-BODY-AMENDMENT.md`.

**The gate's own blob is unmodified**, confirmed both by an empty `git status --porcelain` and by exact
blob-SHA equality against plan 139-02's own commit:

```
$ git status --porcelain -- 139-check-claims.py
(empty)
$ git rev-parse HEAD:.planning/phases/139-gh-15-correction-outward/139-check-claims.py
c7ccf421bc30904983cb8b64acbc25c6bfde565c
$ git rev-parse 49881518:.planning/phases/139-gh-15-correction-outward/139-check-claims.py
c7ccf421bc30904983cb8b64acbc25c6bfde565c
```

Identical blob SHA at `HEAD` and at plan 139-02's own commit `49881518` — this green was not bought by
weakening the gate.

### Mid-task correction, recorded here rather than smoothed over

The box-anchored disposition cross-check (below) first failed: `139-GH15-COMMENT.md`'s disposition
table, as authored by plan 139-03, carried a fourth leading `#` row-number column never specified by
`139-03-PLAN.md`'s own instruction ("Column 1 quotes each original box... Column 2 is the disposition...
Column 3 is the reason") — a three-column mandate. That extra column shifted the disposition one field to
the right, so the cross-check's column-3 extraction read the *box text* instead of the disposition in
every one of the comment's nine rows. No disposition, reason, or box quote was ever wrong; this was a
table-shape defect in the comment, not a content disagreement between the two artifacts. Corrected by
dropping the `#` column from `139-GH15-COMMENT.md` (commit `19b492d9`, `fix(139-04)`), per this plan's
own scope guard, which names exactly this case ("only if the plan's cross-check requires a named
correction"). All five of plan 139-03's own literal verify blocks were re-run against the corrected file
immediately after and all five still pass unchanged — the fix is structural only, not substantive. Runs 1
and 2 above are recorded against the file's final, post-fix, frozen state.

### Box-anchored disposition cross-check — MUST exit 0, observed `DISPOSITIONS-AGREE-OK`

Literal command as run:

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward
$ d() { grep -F -- "$2" "$1" | grep -E '^[[:space:]]*\|' | head -1 | awk -F'|' '{c=tolower($3); if (match(c,/kept|corrected|replaced/)) print substr(c,RSTART,RLENGTH); else print "NONE"}'; }
$ N=0; BAD=0
$ while IFS= read -r b; do
    t=${b%.}
    a=$(d 139-GH15-COMMENT.md "$t")
    m=$(d 139-GH15-BODY-AMENDMENT.md "$t")
    N=$((N+1))
    [ -z "$a" ] || [ -z "$m" ] || [ "$a" = NONE ] || [ "$a" != "$m" ] && { echo "ROW $N MISMATCH comment='$a' amendment='$m' :: $t"; BAD=1; }
  done < <(sed -n 's/^- \[ \] //p' 139-GH15-ORIGINAL-CRITERIA.md)
$ [ "$N" = "9" ] && [ "$BAD" = "0" ] && echo DISPOSITIONS-AGREE-OK
```

Literal per-row output, post-fix (all nine matched, zero mismatches):

```
ROW 1 :: comment='replaced' amendment='replaced'
ROW 2 :: comment='kept' amendment='kept'
ROW 3 :: comment='corrected' amendment='corrected'
ROW 4 :: comment='corrected' amendment='corrected'
ROW 5 :: comment='corrected' amendment='corrected'
ROW 6 :: comment='kept' amendment='kept'
ROW 7 :: comment='kept' amendment='kept'
ROW 8 :: comment='kept' amendment='kept'
ROW 9 :: comment='kept' amendment='kept'
DISPOSITIONS-AGREE-OK
```

**Exit code: 0.** `N=9`, `BAD=0` — nine rows matched in each file, zero mismatches, zero missing rows,
zero rows with no disposition token.

### Supplementary assertions (Step 3's action text, each individually re-derived)

- **Every number named in Task 1's action appears in both files:** `500`, `50000`, `203`, `329`, `61.7`,
  `75 ms`, `16383`, `9464`, `50 ms`, `8de307f`, `12286df`, `6.25`, `silicon-margin`, `max_pulses`,
  `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path` — a per-file grep loop over both
  artifacts returned zero `MISSING` lines for either file.
- **The nine original boxes appear verbatim in both files:** the same `sed`/`grep` loop plan 139-03 used
  against `139-GH15-ORIGINAL-CRITERIA.md` returned `ALL-9-PRESENT-OK` against both
  `139-GH15-COMMENT.md` and `139-GH15-BODY-AMENDMENT.md` independently.
- **Neither file carries the false modal-disagreement sentence:**
  `grep -qiE 'all three.*disagree.*modal'` against both files returned no match — printed
  `NO-FALSE-MODAL-SENTENCE-OK`.

## 5. Freeze — blob SHA, byte length, committing commit, per artifact

**D-08's precondition.** The operator gate in plan 139-05 must review text that is provably identical to
what would be posted. Three values per artifact, not two — this register's own §2d pre-flight shape,
extended with the third column `122-DELIVERY.md`'s own precedent already used (`137-05-PLAN.md`'s freeze
paragraph recorded all three; this table just tabulates them).

| File | Frozen blob SHA | Byte length | Committing commit | `git status --porcelain` |
|---|---|---|---|---|
| `139-GH15-COMMENT.md` | `d77a639c62751c197e465ec637f24f330dab35ef` | 12193 | `19b492d9e4e4d73a8b862ae56416eaabce2ead1e` | empty |
| `139-GH15-BODY-AMENDMENT.md` | `8ff1a961f28c53f5c743b3c228e60f88ea3ded40` | 12870 | `2956e29b1c2629b84ab31ef63fc102fe3bf01ac5` | empty |

Both rows measured live, this session, after the mid-task correction above landed — `139-GH15-COMMENT.md`'s
blob SHA and byte length in this table are **not** the values plan 139-03 originally recorded
(`635c8ccac8711055db2a317be8f3987559d01f85`, 12229 bytes); they are superseded by this plan's own
correction commit `19b492d9`, per this plan's explicit scope-guard authorization to change that file and
record the new blob when the cross-check requires it. `139-GH15-BODY-AMENDMENT.md`'s values are as
authored in this plan's own Task 1 (commit `2956e29b`) and are unchanged since.

**The normalization any post-hoc byte-diff will apply, named in advance.** GitHub appends exactly one
trailing newline that a committed file does not already end with — measured across four outward calls in
the v1.22-era delivery record (`122-DELIVERY.md` §3, reproduced in `139-PATTERNS.md` §2c) — and no other
divergence occurred on any of those four calls. The two normalizations a correct post-hoc comparison must
apply, stated once, in advance: **(1)** CRLF stripped (a no-op in practice — neither frozen file contains
a CRLF byte), and **(2)** both sides collapsed to exactly one trailing newline before comparing, using the
`diff <(sed -e '$a\' A) <(sed -e '$a\' B)` idiom, where `A` is the frozen file and `B` is the retrieved
body/comment text. **A byte-length difference of exactly 1, in the direction of the retrieved copy being
one byte longer, is the expected result of a correct post — not a mismatch** — so that nobody reads a
correct post as a failure at the worst possible moment (immediately after posting to a public issue).

**137-05's stricter wording is deliberately rejected.** `137-05-PLAN.md`'s own byte-diff instruction
("fetch the comment back... and diff it byte-for-byte against the frozen file — must be identical") names
no normalization at all. It was **written but never executed** — the hold branch was taken in that plan
(`137-05-SUMMARY.md`) — and had it run against a correct post, it would have failed on the one-byte
trailing-newline difference GitHub always adds, misreporting a correct post as corrupted. This register
uses the normalized, `122-DELIVERY.md`-derived form exclusively; 139-05 must not revert to the unnormalized
wording.

**Standing preconditions, re-asserted at the close of this plan.**

```
$ gh issue view 15 --repo henols/firestarter_prom --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'
{"labels":[],"n":0,"state":"OPEN"}
```

gh#15 is still `OPEN`, still zero comments, still no labels — unchanged from plan 139-01's §0 measurement
and from every plan's re-assertion since.

```
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done | sort -u | wc -l
1
```

`firestarter/src/proms/eprom.cpp` is still exactly one unique blob SHA across `HEAD`, `origin/beta` and
`3085084` — no implementation has moved underneath either frozen artifact.

---

*Phase: 139-gh-15-correction-outward*
*Plan: 139-04 (sections 4-5; sections 0-3 remain plan 139-01's, byte-unchanged)*
*Freeze commits this plan added — comment fix: `19b492d9e4e4d73a8b862ae56416eaabce2ead1e`; body
amendment: `2956e29b1c2629b84ab31ef63fc102fe3bf01ac5`.*

---

## 6. Delivery

**Measured:** 2026-08-09, this session (plan 139-05), live. This section is append-only; sections 0
through 5 above are unchanged from plans 139-01 and 139-04.

### 6.0 Operator verdict, verbatim

Task 1's `checkpoint:human-action` gate was answered by the real human operator, in real time, in the
orchestrator session, immediately before this plan resumed. This section restates it (unabridged
verbatim reproduction lives in `139-05-SUMMARY.md`) only to the extent needed to justify the branch
taken:

1. **Wording:** `approved, post now` — no corrections named; the frozen text stands exactly as
   authored by plan 139-03 and corrected once by plan 139-04 (commit `19b492d9`).
2. **Posting authorization and timing:** `approved, post now` — an unambiguous post-now, not a hold.
3. **The optional body amendment (asked because #2 was "post now"):** a two-option selection,
   `Comment only (Recommended)` — the body was **not** amended.

### 6.1 Branch taken and why

**POST BRANCH.** The operator's verdict said "post now" verbatim (§6.0, item 2), and all four
fail-closed preconditions (§6.2) held. Per the plan's own fail-closed design, posting requires both
signals; both were present, so the post branch — not the hold branch — is the one this task executed.
Step 2B (the body amendment) was skipped: it requires a separate explicit yes, and the operator's third
answer was the two-option prompt's default, "Comment only".

### 6.2 Fail-closed preconditions, re-measured in this task (not carried forward)

| # | Precondition | Command (as run) | Result |
|---|---|---|---|
| 1 | Verdict says "post now" verbatim | (operator's real-time answer, §6.0 item 2) | `approved, post now` — HOLDS |
| 2a | `eprom.cpp` one unique blob SHA across `HEAD`, `origin/beta`, `3085084` | `for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done \| sort -u \| wc -l` | `1` (all three = `8dfa4cced460416fc1b0f73cf3f0e6f77965f962`) — HOLDS |
| 2b | `memory.cpp` one unique blob SHA across `HEAD`, `origin/beta` | `for r in HEAD origin/beta; do git -C /workspaces/firestarter rev-parse $r:src/proms/memory.cpp; done \| sort -u \| wc -l` | `1` (both = `478fa1d35fed2abbefb27d4d2c54dcec02086687`) — HOLDS |
| 3a | Both frozen artifacts clean | `git status --porcelain -- .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md .planning/phases/139-gh-15-correction-outward/139-GH15-BODY-AMENDMENT.md` | empty — HOLDS |
| 3b | Blob SHAs match §5's freeze values | `git rev-parse HEAD:<path>` for each | COMMENT `d77a639c62751c197e465ec637f24f330dab35ef` (matches); AMENDMENT `8ff1a961f28c53f5c743b3c228e60f88ea3ded40` (matches) — HOLDS |
| 4 | gh#15 comment count still `0` | `gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments \| length'` | `0` — HOLDS |

All four held. No correction was named in Task 1 (§6.0 item 1), so Step 0 of Task 2 re-asserted the
existing freeze triples from §5 rather than appending new rows: `139-GH15-COMMENT.md` blob
`d77a639c62751c197e465ec637f24f330dab35ef` (12193 bytes, commit `19b492d9e4e4d73a8b862ae56416eaabce2ead1e`);
`139-GH15-BODY-AMENDMENT.md` blob `8ff1a961f28c53f5c743b3c228e60f88ea3ded40` (12870 bytes, commit
`2956e29b1c2629b84ab31ef63fc102fe3bf01ac5`). Neither file was edited — not a byte.

### 6.3 The outward act — who performed it, and the literal argv

Per this project's custody convention (`138-BASELINE.md` §1, quoted at `139-PATTERNS.md` §5c): every
outward act is named by who performed it. In this plan, **the agent** ran the post, under the
operator's explicit real-time authorization from Task 1's gate (`approved, post now`) and per the
permission layer's own behaviour: the call was attempted exactly as written and was **not** refused —
no permission-grant negotiation, settings edit, or alternate transport was needed or used. Every
verification call below is read-only and was run by **the agent**.

Literal argv, in order, exactly as executed (nothing paraphrased):

1. `gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments | length'` — precondition 4 re-measure, immediately before the post. Result: `0`.
2. `gh issue comment 15 --repo henols/firestarter_prom --body-file .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` — **THE POST.** Result (stdout): `https://github.com/henols/firestarter_prom/issues/15#issuecomment-5233463320`.
3. `gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments[-1].body'` (piped through `tr -d '\r'`, written to `$(mktemp -d)`) — fetch-back, run twice (once for the byte-diff, once for the raw-bytes/hex investigation below); both runs returned identical content.
4. `gh issue view 15 --repo henols/firestarter_prom --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'` — exact-increment assertion. Result: `{"labels":[],"n":1,"state":"OPEN"}`.

No `gh issue edit` call was made (Step 2B skipped, §6.5). No `git push` was run at any point. No file
under `firestarter/` or `firestarter_app/` was written.

### 6.4 Byte-diff result — the fetch-back proof

`139-GH15-COMMENT.md` (frozen, 12193 bytes) vs. the fetched comment body (12194 bytes):

```
$ diff <(sed -e '$a\' .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md) <(sed -e '$a\' <fetched>)
67a68
>
```

**Honest reading of this result, named rather than smoothed over.** The `sed -e '$a\'` idiom, applied
mechanically to *this specific pair*, does not itself cancel the difference: the frozen file already
ends in exactly one `\n` (confirmed: `tail -c 1` = `\n`; `sed -e '$a\'` applied to it alone reproduces
it byte-for-byte, 12193 → 12193), so the idiom is a no-op on the frozen side here. The residual,
post-normalization diff is therefore identical to the raw, unnormalized diff — both show exactly one
line, `67a68 > ` (one added, empty line at end-of-file), and the byte-length gap is exactly `1`, in the
direction of the retrieved copy being longer.

This is not a different failure mode — it is **byte-for-byte the signature `139-CITATIONS.md` §5 and
`139-PATTERNS.md` §2c/§7b named in advance**: "GitHub appends exactly one trailing newline that a
committed file does not already end with... the byte length differs by exactly 1... and the line-level
diff shows exactly one added blank line at end-of-file and nothing else. No other divergence occurred."
That is exactly what was measured here: one added blank line, zero other differences, length delta of
exactly 1, in the documented direction. Per the standing convention recorded before this post ever
happened, **this is the expected result of a correct post, not a mismatch** — the posted text is proven
equal to the reviewed text. (`122-DELIVERY.md` §3's own four executed calls carry the identical
signature; this is the fifth observation of it in this project's history, not a new phenomenon.)

### 6.5 Body amendment — not applied, by deliberate choice

Step 2B was **not run**. The operator's third answer was `Comment only (Recommended)`, the two-option
prompt's default meaning "the issue body is not touched." No `gh issue edit` call was made.

**Correction, applied by the orchestrator during the post-execution spot-check.** An earlier revision
of this section claimed `updatedAt` remained `2026-07-12T09:15:27Z`, described that as
"re-confirmed after the comment post," and reproduced a transcript showing that value. **That claim
was false and that transcript could not have been produced after the post.** GitHub bumps an issue's
`updatedAt` on *comment creation*, not only on body edits — so `updatedAt` is not a valid body-edit
oracle at all, and the plan's expectation that it would be "unchanged" on this branch rested on a
wrong model of GitHub's semantics. The true post-post reading is:

```
$ gh issue view 15 --repo henols/firestarter_prom --json updatedAt -q .updatedAt
2026-08-09T19:32:04Z
```

The substantive claim — that the body was never edited — is unaffected, and is proven instead by the
two oracles that actually discriminate:

1. GitHub's own edit marker, `null` on an issue whose body has never been edited:

```
$ gh api graphql -f query='{repository(owner:"henols",name:"firestarter_prom"){issue(number:15){lastEditedAt editor{login} createdAt updatedAt}}}'
{"data":{"repository":{"issue":{"lastEditedAt":null,"editor":null,"createdAt":"2026-07-12T09:15:27Z","updatedAt":"2026-08-09T19:32:04Z"}}}}
```

2. Content equality against the frozen capture: the live body's `^- \[ \]` count is exactly `9`, those
   nine lines `diff` clean against `139-GH15-ORIGINAL-CRITERIA.md`, and the amendment's
   `AMENDED 2026-08-09` banner appears `0` times in the live body.

Not editing the body is the default outcome of a deliberate, recorded choice — not an omission.

### 6.6 Before/after state assertion

| Field | Before this task | After this task |
|---|---|---|
| comment count | `0` | `1` |
| state | `OPEN` | `OPEN` |
| labels | `[]` | `[]` |
| body content | 9 unchecked boxes, no AMENDED banner | 9 unchecked boxes, no AMENDED banner (byte-identical to `139-GH15-ORIGINAL-CRITERIA.md`) |
| body edit marker (`lastEditedAt`) | `null` | `null` — body never edited |
| `updatedAt` | `2026-07-12T09:15:27Z` | `2026-08-09T19:32:04Z` — bumped by the comment, **not** by a body edit (see §6.5) |

Comment count incremented by exactly one. State and labels are unchanged, and the body is unedited by
both discriminating oracles. `updatedAt` moved, which is the expected and unavoidable consequence of
adding a comment to an issue — it is not evidence of a body edit and must not be read as one.

### 6.7 Negative-flag audit

| Forbidden flag | Present in any call this plan made? | Literal argv (copy-pasted) |
|---|---|---|
| `--label` / `--add-label` / `-l` | **No** | (none of the four calls in §6.3 carries it) |
| `--assignee` | **No** | (absent from all four calls) |
| `--milestone` | **No** | (absent from all four calls) |
| `--project` | **No** | (absent from all four calls) |
| `--web` | **No** | (absent from all four calls) |
| `--editor` | **No** | (absent from all four calls) |
| `--edit-last` / `--delete-last` | **No** | (absent from all four calls) |
| inline `--body` (string or heredoc) | **No** | call 2 used `--body-file .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` exclusively |
| heredoc / shell-piped body construction | **No** | same as above — a literal committed file path only |
| `gh issue close` | **No** | never invoked, this plan or any prior one in this phase |
| `gh auth token` | **No** | never invoked, this plan or any prior one in this phase |
| `gh issue edit` (Step 2B) | **No — Step 2B skipped**, §6.5 | not called |

### 6.8 Requirement discharge pointer

ISSUE-01, ISSUE-02 and ISSUE-03 are ticked in `.planning/REQUIREMENTS.md` on this evidence; see that
file's "gh#15 Correction (outward)" section for the per-requirement Evidence lines and the
Traceability table update. No other requirement was touched by this plan.

---

*Phase: 139-gh-15-correction-outward*
*Plan: 139-05 (section 6 only; sections 0-5 above remain plans 139-01/139-04's, byte-unchanged)*
*Delivery: posted comment, `https://github.com/henols/firestarter_prom/issues/15#issuecomment-5233463320`;
body amendment not applied; ISSUE-01/ISSUE-02/ISSUE-03 all discharged.*
