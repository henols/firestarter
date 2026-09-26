---
status: resolved
trigger: "the /devtest-triage are bloating and puts to deep tecnichal information in to the issues. It is the /devtest-rootcause job to work on the tecnichal details"
created: 2026-09-20T00:00:00Z
updated: 2026-09-20T00:00:00Z
---

## Current Focus

status: root cause confirmed, applying fix.

reasoning_checkpoint:
  hypothesis: "devtest-triage's §5d template contains an all-MATCH framing sentence
    ('so the failure is in how that sequence is *executed*, not in the data describing
    it') that poses an unanswered mechanism question with no stop instruction, and a
    'Most likely cause: <...> and why' field with no depth ceiling or prohibition — the
    combination causes a competent agent to answer 'how' by reading and quoting
    firestarter_app/firestarter_fw source, producing devtest-rootcause's deliverable
    (file:line root cause) instead of triage's (layer + cause label)."
  confirming_evidence:
    - "5 live comments (#66, #70, #71, #83, #86) all follow cross-check table -> all-MATCH
      framing sentence -> full code-level mechanism proof, in that order"
    - "Two comments echo the template's exact framing phrase almost verbatim ('the failure
      is in how that sequence is *executed*, not in the data describing it' / 'the failure
      is in how the write is executed, not in the data describing it') immediately before
      diverging into source-code analysis — direct textual causation, not just topical
      similarity"
    - "SKILL.md full-file read confirms no prohibition on file:line/source-quoting/
      function-names/proposed-fixes exists anywhere in the 539 lines, while an equivalent
      enforceable prohibition exists for a different concern at §4"
  falsification_test: "If the bloat passages did NOT cluster around the all-MATCH sentence
    and the 'most likely cause... and why' field — e.g. if they instead answered §5c
    checklist rows directly, or appeared in PASS/closing comments, or appeared before the
    cross-check table — the template-affordance hypothesis would be wrong and the driver
    would be elsewhere (description, handoff section, or agent-inherent behavior)."
  fix_rationale: "Adding an explicit stop/prohibition at the exact point the template
    currently dangles an open question addresses the mechanism (the missing enforceable
    boundary), not the symptom (comment length) — a length cap alone would not stop an
    agent from packing file:line citations into a shorter comment; the fix targets both
    the unbounded field and the unanswered question that invites the deep-dive in the
    first place."
  blind_spots: "Cannot execute the skill in this session to confirm the revised prompt
    actually produces shorter comments — verification is re-derivation (re-reading the
    revised prose against real transcripts) only, not a live run. Also have not tested
    whether a differently-phrased model instruction would be equally or more effective;
    this is one plausible fix among several, chosen for being minimal and for mirroring
    an existing, working pattern (§4) already in this file."
  candidate_causes:
    - "code/template category: the §5d all-MATCH framing sentence + unbounded 'and why'
      field (confirmed — see confirming_evidence)"
    - "environment/agent-behavior category: generic LLM helpfulness/thoroughness bias
      independent of skill wording (checked and eliminated — see Eliminated: real comments
      echo the template's own specific phrasing verbatim, which a generic-bias hypothesis
      does not predict)"
  and_gate: "No. Single category (skill-definition prose) produces the whole effect; the
    environment/agent-behavior alternative was checked and eliminated rather than found to
    co-occur. No AND-gate — one textual defect, in two co-located spots in the same file,
    is sufficient to explain all 5 observed instances."

next_action: edit .claude/skills/devtest-triage/SKILL.md §5d (template, all-MATCH prose,
  worked example clause, §5c intro) per Resolution.fix, then verify by re-derivation
  against the real #66 comment.

## Symptoms

expected: a `devtest-triage` comment stays at the datasheet-vs-database layer — the
  cross-check table, which rows MATCH / MISMATCH / UNCHECKED, a short "most likely
  cause" pointer, and the `cause:*` label that says which repo owns the fix. Code-level
  mechanism (file:line, call paths, which function drops a field) is `devtest-rootcause`'s
  deliverable, posted later as a "### Fix —" comment.

actual: triage comments carry full root-cause analyses. Measured on the live tracker
  (henols/firestarter, 2026-09-20), triage comments run 3.5-6 KB, e.g.:
    - #66 MBM27C4001 — 5968 chars
    - #70 MBM27C1000 — 5309 chars
    - #71 MBM27128    — 4858 chars
    - #83 62256       — 4717 chars
    - #86 SST39SF040  — 4655 chars
  The #66 comment is the clearest case: past its cross-check table it walks
  `build_db.py`'s decode of `vdd_mv`, quotes the firmware acceptance test as
  `eprom.cpp`: `vpp_mv > handle->vpp_mv + 500`, traces `database.py::_map_data` and
  `convert_to_programmer` field-by-field to show VCC is never emitted, and inspects the
  `firestarter.h` handle struct for a missing member. That is a completed root cause
  with file:line evidence — `devtest-rootcause` §4's deliverable — published under a
  "### Datasheet cross-check" heading and with no artefact/version table.

errors: none. Nothing fails or errors; the skill produces a wrong-shaped, oversized
  artifact. This is a specification/boundary defect in the skill, not a runtime bug.

reproduction: run the `devtest-triage` skill on any open FAIL issue in
  henols/firestarter and read the §5d comment it drafts. Read-only; no hardware, no
  writes to the tracker needed to reproduce the drafting behaviour.

started: not pinned. Present in comments from at least 2026-09-10 (#66) through
  2026-09-20 (#71/#70/#66 follow-ups).

## Context

skill under investigation: `/workspaces/.claude/skills/devtest-triage/SKILL.md` (539 lines)
sibling that owns the technical layer: `/workspaces/.claude/skills/devtest-rootcause/SKILL.md` (336 lines)

The two skills already declare the split:
  - triage SKILL.md:15 — "It never edits the chip database — see `devtest-rootcause` for the fix side."
  - triage SKILL.md:511 — "Comments left here are the input to `devtest-rootcause`, which investigates the code."
  - rootcause SKILL.md:8 — "Takes the datasheet findings `devtest-triage` left on an issue and turns them into a fix"

Suspect surfaces in triage SKILL.md (starting points, not conclusions):
  - §5d template line "Most likely cause: <the one you actually believe, and why>" — the
    "and why" is an open invitation to justify with code.
  - §5d prose "**Not a pin-map fault, and not a missing-SDP-config fault.** ... so the
    failure is in how that sequence is *executed*, not in the data describing it." — a
    template example that itself reasons about execution.
  - The worked example (§ "Worked example — issue #21") ends by pointing at the SDP
    unlock sequence "not taking effect on the wire" and cross-linking a code issue.
  - §5c's checklist has 10 rows; several ("Program algorithm", "Pulse timing",
    "Write protection") have no hard datasheet-vs-DB answer without reading code.
  - No stated length or depth ceiling for the comment anywhere in the skill.
  - No stated prohibition on `file:line` / function-name citations, unlike the explicit
    prohibition that exists for GSD references in the ledger Notes (§4).

Scope decision (orchestrator, at session creation): the deliverable is a change to the
skill definition(s) so future comments stay in their lane. Retro-editing the community
comments already posted to henols/firestarter is OUTWARD-FACING and is NOT in scope —
if the investigation concludes it is warranted, raise it as a checkpoint rather than
doing it.

Constraint: `devtest-triage` is self-contained and stdlib-only (SKILL.md:19-22). Its
scripts must not import from `firestarter_app`. Any fix that adds a check must respect
that, and must ship with its own tests under `scripts/tests/` per
[[feedback_skills_must_own_their_scripts]].

## Evidence

- timestamp: 2026-09-20 (orchestrator, pre-spawn)
  observation: comment sizes on the live tracker, measured via
    `gh issue view <n> --repo henols/firestarter --json comments --jq '.comments[] | "\(.author.login) \(.createdAt) chars=\(.body|length)"'`
    Triage-authored (henols) comments: 5968, 5309, 4858, 4717, 4655, 3486, 3039 chars.
    Community-authored report bodies for comparison: 694, 853, 993, 1302, 1331 chars.
  reading: triage comments are routinely 4-6x the size of the report they answer.

- timestamp: 2026-09-20 (orchestrator, pre-spawn)
  observation: #66's triage comment contains, after its cross-check table, five prose
    blocks of code-level analysis naming `build_db.py`, `eprom.cpp`, `database.py::_map_data`,
    `convert_to_programmer`, `ic_layout.py`, `rurp_read_vcc_mv()` and `firestarter.h`.
  reading: the content is `devtest-rootcause` §2/§4 material — "Decide which layer is at
    fault" and "Root cause: <the mechanism, in the code, at file:line>" — published from
    the triage skill instead.

- timestamp: 2026-09-20
  checked: full comment bodies on #66 (both the original cross-check and the follow-up
    after the reporter supplied the real datasheet), #70, #71, #83, #86, read verbatim via
    `gh issue view <n> --json comments --jq`.
  found: every one of the five reproduces the same shape — cross-check table, then an
    "All-MATCH"/mismatch framing sentence that echoes the SKILL.md template's own wording
    near-verbatim ("the failure is in how that sequence is *executed*, not in the data
    describing it" in #66 vs. "the failure is in how the write is executed, not in the
    data describing it" in #86), then a full mechanism proof: quoted C source
    (`configure_sram()`'s entire body verbatim in #83), function names
    (`memory_write_execute`, `memory_verify_execute`, `_map_data`, `resolve_pinout_key`),
    a byte-format decode of `MSG_ERR_VERIFY` down to argument order, a proposed fix location
    ("the fix belongs in an override table next to `NMOS_TRUE_VPP_MV`", #70/#71), and in one
    case a bisect recommendation ("a b22...b31 firmware bisect is the cheapest next step",
    #86). This is `devtest-rootcause` §1/§2/§4 territory (upstream-decode tracing, layer
    classification via source, `Root cause: <mechanism, at file:line>`), not §5c/§5d's
    datasheet-vs-database table.
  implication: the "Most likely cause: <...> and why" hypothesis is confirmed as the
    strongest driver, but the trigger sentence is specifically the template's own
    all-MATCH framing line ("so the failure is in how that sequence is *executed*, not in
    the data describing it") — real comments pick up that exact phrase and then answer the
    unasked question "how", which requires reading source. The Worked Example (§ Worked
    example — issue #21) is comparatively restrained (no file:line, no quoted source) and
    ends correctly ("hand it to `devtest-rootcause`"), so the worked example is not itself
    a major driver — the reusable *template* block lacks the equivalent closing/prohibition
    the worked example demonstrates only informally.

- timestamp: 2026-09-20
  checked: whether `devtest-triage` SKILL.md states anywhere that comments must NOT carry
    file:line citations, quoted source, function names, or proposed fixes — searched full
    539-line file.
  found: no such statement exists. §4 (ledger Notes) has a hard, explicit prohibition ("No
    GSD process references in Notes — ever") of the same rhetorical shape this bug needs;
    §5 has no equivalent. No length/depth ceiling exists anywhere either (confirmed by
    full-file read, not just grep).
  implication: the boundary is stated only as aspirational prose at the top of the file
    ("This skill only inspects firestarter code... see `devtest-rootcause` for the fix
    side") and in the Handing-off section, never as an enforceable rule at the point where
    the bloat is actually produced (§5d). This is the gap to close.

- timestamp: 2026-09-20
  checked: reverse direction — does `devtest-rootcause` SKILL.md rely on triage's deep
    code walkthrough as an input, such that trimming triage would create a gap rootcause
    has to re-fill (moving the bloat rather than removing it)?
  found: no. `devtest-rootcause` §1 re-derives upstream facts independently via its own
    `infoic_lookup.py` (explicitly never imports the generator, to stay standalone) and
    §2's layer classification is driven by `eprom_ledger.py family` plus its own file
    table, not by parsing prose out of the triage comment. The skill's stated input from
    triage is "the datasheet findings" (i.e., the cross-check table + `cause:*` label),
    consumed as human-readable context, not as a formal contract on comment depth.
  implication: trimming triage's comment to table + layer + one-line pointer removes
    duplicated work (rootcause was always going to re-derive the mechanism itself via §1/§2)
    rather than creating a new gap. No change to `devtest-rootcause/SKILL.md` is required.

## Eliminated

- hypothesis: the Worked Example (§ Worked example — issue #21) is the primary source of
  the bloat, since it is the one place the skill demonstrates a full investigation.
  evidence: the worked example never cites file:line, never quotes source, and explicitly
  ends by handing off to `devtest-rootcause`. The five real over-bloat comments go
  measurably further than the worked example models (quoted C function bodies, `_map_data`/
  `convert_to_programmer` field tracing, a bisect recommendation) — behavior the worked
  example does not demonstrate at all. The worked example is a minor contributor at most.
  timestamp: 2026-09-20

- hypothesis: the bloat is generic LLM-agent thoroughness/helpfulness bias, independent of
  the skill's wording, and no textual fix in SKILL.md would change it.
  evidence: real comments echo the template's own all-MATCH framing sentence near-verbatim
  ("the failure is in how that sequence is *executed*, not in the data describing it" /
  "the failure is in how the write is executed, not in the data describing it") before
  diverging into code analysis. That specific, repeated echo is direct evidence the
  template text itself is the proximate trigger, not undifferentiated agent thoroughness —
  a textual fix that removes the dangling "how is it executed" question and replaces it
  with an explicit stop/handoff instruction is falsifiable and targeted.
  timestamp: 2026-09-20

## Resolution

root_cause: `devtest-triage/SKILL.md` §5d's comment template contains an unbounded
  affordance for code-level analysis with no enforceable stop rule. Two specific textual
  causes, both in the same file/category (skill-definition prose — no AND-gate; a single
  category with two co-located defects):
  (1) the all-MATCH prose model — "...so the failure is in how that sequence is *executed*,
  not in the data describing it" — poses an unanswered "how is it executed" question with
  no accompanying instruction to stop there; real comments answer that question by reading
  and quoting `firestarter_app`/`firestarter_fw` source (the exact material
  `devtest-rootcause` §1/§2/§4 exists to produce), and
  (2) the template's own "Most likely cause: <the one you actually believe, and why>" field
  has no depth ceiling and no prohibition on file:line citations, function names, quoted
  source, proposed fixes, or bisect recommendations, unlike the explicit, enforceable
  prohibition the skill already writes for a different concern at §4 ("No GSD process
  references in Notes — ever"). Confirmed against 5 live over-bloat comments (#66, #70,
  #71, #83, #86); the worked example and generic agent-thoroughness were both considered
  and eliminated as the primary driver (see Eliminated).
fix: added an explicit, `cause:*`-label-mirroring stop/prohibition to §5d (no file:line
  citations, no quoted source, no function/variable names from either sub-repo, no proposed
  fix or bisect recommendation — name the layer and stop), reworded the all-MATCH template
  sentence and its surrounding prose to end in a handoff instead of an open "how" question,
  narrowed "Most likely cause: <...> and why" to "the layer ... in one sentence. Not the
  mechanism", added a comment-size guideline anchored to the measured community-report size
  (700-1300 chars) so a bloated comment is self-evidently out of bounds, tightened the §5c
  checklist intro to say those rows are settled from `firestarter info` + the datasheet only
  (never by reading source), and added one clarifying clause to the worked example so
  "keep going" reads as "through the datasheet's own rows", not into source. No code/script
  change; `devtest-rootcause/SKILL.md` is unchanged (see Evidence, reverse-direction check).
verification: re-derivation only (this skill cannot be executed in this session — posting
  to the live tracker is outward-facing and out of scope). Verified by re-reading the
  revised §5 end to end as the triaging agent and by walking the real #66 comment
  passage-by-passage against the revised instructions (see final summary for the mapping).
files_changed:
  - .claude/skills/devtest-triage/SKILL.md
  - .planning/debug/devtest-triage-bloat.md

Archival note: this session's brief substituted re-derivation for the standard
human-verify checkpoint (the fix cannot be run against the live tracker without violating
the outward-facing-edit constraint) and its Return/Commit steps did not request moving
this file to `resolved/` or appending `knowledge-base.md`. Left undone deliberately —
those are cheap to do in a follow-up once a human has actually watched a real triage
comment come out short, which is the stronger confirmation a spec-level fix like this one
still lacks.

Recommendation for the operator (not executed — outward-facing, out of scope): none of
the 5 already-posted bloated comments need editing or retraction. They are accurate and
their depth did no harm; the fix only prevents new ones. No retro-edit is warranted.
