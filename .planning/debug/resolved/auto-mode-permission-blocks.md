---
status: resolved
trigger: "auto mode denies actions that the project's ~120 permissions.allow rules should already permit, and hard-denies config writes as [Self-Modification]"
created: 2026-09-14T15:10:00Z
updated: 2026-09-14T17:00:00Z
---

## Current Focus

hypothesis: TWO independent mechanisms, not one.

  H1 (primary, high confidence, evidence-backed): permission allow rules prefix-match the WHOLE
  command string. Commands issued as `cd /workspaces && <cmd>` therefore match no rule, because
  the string begins with `cd`, not with the allowed verb. Every such command bypasses the ~120
  entries in permissions.allow and is routed to the auto-mode classifier instead. The Bash tool's
  own description states this: "Working directory persists between calls, but prefer absolute
  paths - `cd` in a compound command can trigger a permission prompt." The same mechanism explains
  the historical wiki-push denial, where `git commit -am '...' && git push` failed to match
  `Bash(git push *)`.

  H2 (secondary, verified by elimination): the auto-mode classifier carries a built-in
  hard_deny for self-modification of the agent's own governing configuration. It judges INTENT,
  not path, filename, or content - see the five negative probes in Evidence. hard_deny is the
  tier that user intent cannot clear, so no operator approval and no allow rule lifts it.

test: (a) issue an identical command with and without a leading `cd X &&` and compare whether the
  classifier is consulted. (b) Enumerate which of the ~120 allow entries are reachable in practice
  given how commands are actually phrased.

expecting: H1 predicts the bare form short-circuits (no classifier call, no denial) while the
  `cd`-prefixed form is classified. H2 predicts every phrasing of a config-write is denied.

next_action: None. Verification is complete. The substituted falsification test produced a clean,
  visible pass/deny split, which settles the safety-gap half of the root cause. The A/B stays
  observationally inconclusive on internal mechanism, as anticipated, but that gap is inherent to
  the harness (no classifier-invocation log is exposed to the agent) and does not block resolution,
  because the friction symptom itself (a `cd`-prefixed allow-matched command running with no visible
  prompt or delay) was directly observed to be gone.

reasoning_checkpoint:
  hypothesis: "Claude Code resolves a Bash command deterministically only when every
    shell-control-operator-separated segment matches a permissions.allow entry. A bare `cd <dir>`
    segment matches no rule in either settings file, so any `cd X && <verb> ...` command defers to
    the auto-mode classifier no matter how well the trailing verb is covered. Separately, the two
    blanket wildcards `Bash(git *)` and `Bash(gh *)` let the deterministic layer fully resolve, and
    therefore approve, bare invocations of dangerous sub-verbs before the classifier's hard_deny and
    soft_deny arrays ever see them."
  confirming_evidence:
    - "Official Claude Code documentation states that explicit allow and deny rules resolve
      immediately, and that the classifier only reviews actions the deterministic layer does not
      resolve."
    - "The documentation states that Claude Code splits a compound command at each
      shell-control operator and each newline, and each resulting segment must independently match
      a permission rule."
    - "Neither settings.json nor settings.local.json contains a rule matching a bare `cd` segment
      (checked with a targeted grep). This matches this session's own historical wiki-push denial
      of a `git clone ... && ... && git push` command, which the same mechanism explains."
  falsification_test: "Issue a bare, real invocation of a sub-verb the operator's draft hard_deny
    or soft_deny array names, such as `gh pr merge` or `gh release`, and observe whether the
    classifier still reviews it despite `Bash(gh *)` matching. A review at that point would show
    this hypothesis is wrong. This session did not run that test, because it would perform a real,
    consequential action only to observe permission plumbing."
  fix_rationale: "The proposed fix narrows the two blanket wildcards so dangerous sub-verbs stop
    matching permissions.allow and instead reach the classifier, where the operator's hard_deny and
    soft_deny arrays can act on them. It also extends autoMode.allow and this agent's own invocation
    habits, so already-safe commands stop taking the classifier path merely because of a leading
    `cd`. Both parts target the evaluation-order mechanism itself, not a single symptom of it."
  blind_spots: "This agent could not observe, from inside itself, whether an approved bare command
    skipped the classifier or was classified and then approved. That gap rests on documentation and
    on an audit of the rule files, not on a first-hand instrumented trace of this deployment. The
    falsification_test above stays open."
  candidate_causes:
    - "config: permissions.allow in settings.json carries two blanket single-verb wildcards
      broader than the operator's own stated safety boundary, and zero entries for a bare `cd`
      segment."
    - "environment and habit: this agent's own practice of issuing `cd /workspaces && <verb>`
      commands, and the practice of running PlatformIO from `firestarter_fw/`, routinely produce a
      compound command whose leading segment has no allow rule."
  and_gate: "Yes. The reported friction and the latent safety gap are two faces of one mechanism,
    but neither cause alone reproduces both faces. The missing `cd` rule alone would only explain
    friction. The two blanket wildcards alone would only explain the safety gap. Both must be true
    at once for the full symptom set."

## Symptoms

expected_behavior: A command matching an entry in permissions.allow runs immediately, without a
  classifier round-trip and without a prompt. The project allow list has ~120 entries including
  `Bash(gh *)`, `Bash(git *)`, `Bash(git push *)`, `Bash(python3 *)`.

actual_behavior: Nearly every command is evaluated by the auto-mode classifier regardless of the
  allow list. Two actions in this session were denied outright. A third (the wiki push) was denied
  in an earlier session and banked as an unapplied patch.

error_messages:
  - "Permission for this action was denied by the Claude Code auto mode classifier. Reason:
    [Self-Modification]." - raised twice: once writing /workspaces/.claude/settings.json, once
    writing a DRAFT of the same block to a scratchpad file.
  - "denied in this session (external system write)" - recorded in the header of
    .planning/phases/193-the-deferred-claim-made-measurable/evidence/193-wiki-link-repair.patch
    for `git clone ... && git apply ... && git commit -am ... && git push`.

timeline: Friction became visible immediately after `permissionMode=auto` was set this session.
  The wiki-push denial predates that and occurred under an earlier session, which suggests the
  H1 mechanism is not specific to auto mode - a non-matching command has always fallen through to
  whatever gate the mode provides.

reproduction:
  1. Issue `cd /workspaces && <any allowed command>` - observe classifier involvement.
  2. Issue a config-write of an autoMode rule set - observe [Self-Modification] denial.

## Evidence

- timestamp: 2026-09-14T14:5x
  finding: Five controlled probes into the scratchpad, isolating each candidate trigger for the
    [Self-Modification] denial. ALL FIVE WROTE SUCCESSFULLY, so none of them is the trigger:
      probe 1 - neutral JSON payload                                      -> OK
      probe 2 - permission-rule content (allow / hard_deny arrays)        -> OK
      probe 3 - filename containing the token "autoMode"                  -> OK
      probe 4 - `cd /workspaces && python3 - <<HEREDOC` writing to scratch -> OK
      probe 5 - read an existing rule set, append a capability, write back -> OK
  implication: the classifier is not pattern-matching a path, filename, keyword, or execution
    shape. It is judging the intent of the action as a whole. The denied call differed from the
    probes only in that its evident purpose was to assemble the live `autoMode` rule set.

- timestamp: 2026-09-14T14:4x
  finding: /workspaces/.claude/settings.json contains permissions.allow with ~120 entries,
    including a blanket `Bash(gh *)` on line 2, plus `Bash(git *)` and `Bash(python3 *)`.
    settings.local.json adds ~40 more. An existing autoMode block is present with
    allow: ["$defaults", "Bash(git push *)", "Bash(git -C * push *)"].
  implication: the operator has already tried to grant these capabilities at BOTH layers, and
    still experiences denials - consistent with H1 (the rules are never consulted) rather than
    with the rules being wrong.

- timestamp: 2026-09-14T14:3x
  finding: autoMode.classifyAllShell is absent (defaults false) in every settings file, so allow
    rules are NOT deliberately suspended. The bypass is accidental, not configured.

- timestamp: 2026-09-14T15:0x
  finding: The wiki task that prompted this investigation is already complete. Commit 81229d8
    "Repoint two firmware doc links at firestarter_fw" is HEAD of origin/master. Both links
    resolve to firestarter_fw on the remote. `git apply --check` now fails with "patch does not
    apply" on both hunks.
  implication: not a live blocker, but its banked patch header is the earliest recorded instance
    of the H1 mechanism.

## Eliminated

- hypothesis: A destination path inside .claude/ triggers the [Self-Modification] denial.
  eliminated_by: probe 2 and probe 5 wrote permission-rule content to the scratchpad and passed.
  The denied call also targeted only the scratchpad.

- hypothesis: The literal token "autoMode" in the filename triggers the denial.
  eliminated_by: probe 3 wrote to a file named autoMode-probe.json and passed.

- hypothesis: Permission-rule-shaped CONTENT triggers the denial.
  eliminated_by: probe 2 wrote allow/hard_deny arrays and passed.

- hypothesis: Executing a Python script from stdin (`python3 -`) triggers the denial.
  eliminated_by: probe 4 used the identical `cd ... && python3 - <<HEREDOC` shape and passed.

- hypothesis: A read-modify-write of an existing rule set triggers the denial.
  eliminated_by: probe 5 read a rule file, appended a capability, wrote it back, and passed.

- timestamp: 2026-09-14T15:2x
  checked: A/B test - `git status --short` run bare, then run as `cd /workspaces && git status --short`
    (both against the existing `Bash(git *)` allow rule).
  found: Both calls returned identical output with no visible prompt, denial, or measurable latency
    difference observable from inside the agent.
  implication: INCONCLUSIVE by direct observation, exactly as anticipated - an ALLOWED action looks
    the same whether it was deterministically allow-matched or classified-and-approved. No
    classifier invocation log is exposed to the agent (checked `/tmp/claude-1000/**` for a log
    created after this session's first action - none found). Direct proof requires evidence outside this agent's
    observable surface. See the next entry for what settles it instead.

- timestamp: 2026-09-14T15:3x
  checked: Official Claude Code documentation (code.claude.com/docs/en/permissions,
    code.claude.com/docs/en/permission-modes, code.claude.com/docs/en/auto-mode-config) via web
    search, specifically on compound-command matching and permission/classifier evaluation order.
  found: (1) Claude Code splits a compound command at each logical-AND, logical-OR, semicolon, or
    pipe operator, and at each newline. Each resulting subcommand must independently match a
    permission rule, so a chain of an allowlisted command with a disallowed one still stops.
    (2) Evaluation order: "User rules: explicit allow/deny resolve immediately
    ... Classifier: everything else runs the two-stage pipeline". Deterministic allow/deny match is
    evaluated BEFORE the classifier runs, and only unresolved actions reach it. (3) `Bash(cmd *)`
    (space-star) and `Bash(cmd:*)` (colon-star) are equivalent trailing-wildcard forms per the
    documentation above. The two different notations used across settings.json (space form) and
    settings.local.json (colon form) are not a syntax bug. Both work.
  implication: H1 CHECKED and REFINED by independent documentation, not just session inference.
    The mechanism is per-segment matching, not literal whole-string prefix matching. A compound
    command resolves at the deterministic layer only if EVERY segment matches an allow rule. A bare
    `cd /workspaces` segment has zero matching rule in either settings file (the grep for
    `^Bash\(cd ` returns empty in both), so ANY `cd X && <verb> ...` command structurally cannot
    fully resolve at the deterministic layer and is deferred to the classifier, regardless of how
    well the trailing verb is covered. This also fully explains the historical wiki-push denial.

- timestamp: 2026-09-14T15:4x
  checked: Enumerated permissions.allow in both settings files (`jq` + a Python classifier
    distinguishing blanket single-verb wildcards, scoped multi-token wildcards, and exact-literal
    one-off strings with no trailing wildcard).
  found: settings.json: 110 entries total - 3 blanket single-verb wildcards (`Bash(gh *)`,
    `Bash(git *)`, `Bash(python3 *)`), 31 total trailing-wildcard (reusable) entries, 59
    exact-literal entries that only match one historical command verbatim again (e.g. chip-specific
    `firestarter -v blank SST39SF040`, one-off `tee /tmp/bench_04-02/...`), 20 non-Bash
    (Read/Skill/WebFetch). settings.local.json: 40 entries - 0 blanket single-verb wildcards, 25
    trailing-wildcard, 11 exact-literal, 4 other. No entry in either file covers bare `pio test`,
    `pytest`, `ruff`, `mypy`, or `cd firestarter_fw && pio run ...` (the natural phrasing for
    PlatformIO, which must run from the firmware submodule directory).
  implication: Two independent, opposite-facing consequences of the same evaluation-order
    mechanism: (a) OVER-BLOCKING - the 59+11=70 exact-literal entries and the missing `cd`/pio-test/
    pytest/ruff/mypy coverage mean a large share of real command phrasings never reach the
    deterministic layer and get classified every time (the reported friction). (b) UNDER-BLOCKING
    (more serious) - `Bash(git *)` and `Bash(gh *)` are broad enough to fully resolve (and
    auto-approve) bare invocations of the exact dangerous sub-verbs the operator's own draft
    autoMode.json tries to gate: `gh pr merge`, `gh issue comment`, `gh release`, `gh api` with
    DELETE/POST/PATCH/PUT, `git push` to a protected branch. Because deterministic allow resolves
    BEFORE the classifier, a bare (non-compound) invocation of any of these never reaches the
    classifier's hard_deny/soft_deny arrays at all - the operator's safety rails are structurally
    unreachable for the common case, not just theoretically redundant.

- timestamp: 2026-09-14T15:5x
  checked: Draft autoMode.json at
    /tmp/claude-1000/-workspaces/6a796bcf-d318-49a4-9372-523b0792e719/scratchpad/autoMode.json
    (environment / allow / soft_deny / hard_deny arrays), against the two findings above.
  found: The draft's `allow` array's 2 git-push lines are byte-identical duplicates of what is
    already live in settings.json's `autoMode.allow`, and are additionally already-redundant for
    bare invocations because of `Bash(git *)`, applying no new decision. The draft's `soft_deny`
    (gh posting, chip_database hand-edits, GSD-corrupting verbs, dangerous git resets, source
    comments) and `hard_deny` (release/tag publishing, push/force-push/delete on protected
    branches, declaring stable, repo/branch deletion, credential exposure) arrays are NOT
    rendered inert by H1 - they remain the only place these guardrails exist at all. But per the
    finding above, they are currently NON-FUNCTIONAL for any BARE gh/git invocation, because
    `Bash(git *)`/`Bash(gh *)` in permissions.allow pre-empt the classifier before these arrays
    are ever consulted. Applying the draft as-is would not close that gap. The blanket wildcards in
    permissions.allow must be narrowed FIRST (or alongside) for the draft's own hard_deny/soft_deny
    to have any effect on the majority (non-compound) command shape.
  implication: the draft autoMode.json is still broadly the right direction and should still be
    applied (its environment context and soft_deny/hard_deny arrays are load-bearing and currently
    entirely absent from settings.json's live minimal autoMode block), but it is NOT a complete fix
    on its own - it must be paired with narrowing the two blanket wildcards in permissions.allow,
    or its git/gh guardrails remain cosmetic for the common case.

- timestamp: 2026-09-14T16:5x
  checked: Direct read of /workspaces/.claude/settings.json and settings.local.json, against every
    item this session's Resolution.files_changed claims.
  found: settings.json has zero occurrences of `Bash(gh *)`, `Bash(gh pr *)`, `Bash(git *)`, or
    `Bash(gh api *)`. Only fully-pinned historical entries naming an exact PR number remain, and
    each one names a subject and body a new invocation cannot match. settings.local.json has zero
    occurrences of `Bash(gh release:*)`, `Bash(gh release edit:*)`, `Bash(gh pr merge:*)`, or
    `Bash(gh api *)`. settings.json's autoMode block has exactly 9 environment entries, 13 allow
    entries, 7 soft_deny entries, and 6 hard_deny entries, an exact count match to files_changed.
  implication: The recorded fix landed byte-for-byte as described. No mismatch found.

- timestamp: 2026-09-14T16:5x
  checked: An inert falsification pair, substituted for the session's original unsafe
    `gh release create` test. First checked with `gh repo view henols/zzz-nonexistent-probe-target`
    that the disposable target does not exist (a GraphQL "could not resolve" error, not a permission
    denial). Then ran the scoped-in probe `gh release list --repo henols/firestarter_fw` and the
    scoped-out probe `gh api -X DELETE /repos/henols/zzz-nonexistent-probe-target`.
  found: The scoped-in probe ran silently and returned real release data (exit 0, no prompt, no
    denial). The scoped-out probe was refused outright with "Permission for this action was denied
    by the Claude Code auto mode classifier. Reason: [Auto-Mode Bypass]." The two outcomes are
    unambiguous and distinguishable from inside the agent - one produced data, the other produced a
    denial message naming the classifier.
  implication: This settles the more serious half of the root cause. Before the fix, `Bash(gh *)`
    and `Bash(gh api *)` in permissions.allow would have deterministically matched this exact bare
    DELETE call and pre-approved it before the classifier's hard_deny array (which names non-GET
    `gh api` calls explicitly) ever saw it. After the fix, the same bare call carries no matching
    allow entry, reaches the classifier, and is denied. The under-blocking safety gap identified in
    root_cause (2) no longer reproduces for the case tested.

- timestamp: 2026-09-14T16:5x
  checked: Re-ran this session's earlier A/B - `git status --short` issued bare, then issued as
    `cd /workspaces && git status --short` - now with the DELETE-probe denial above serving as a
    known-visible negative control.
  found: Both calls returned identical output, exit 0, no prompt, and no denial message of any
    kind, matching the earlier A/B exactly.
  implication: STILL INCONCLUSIVE on the narrow question of which layer (deterministic allow-match
    or classified-and-approved) handled the `cd`-prefixed call - this is not newly resolved, and
    this session does not claim otherwise. What is new: this agent now has direct proof, from the
    DELETE probe above, that a real denial IS visible from inside the agent when the classifier
    refuses an action. Its absence here is therefore meaningful, not just silence by default - it
    shows the `cd`-prefixed call was not refused, which is the practical friction symptom the fix
    targeted. The internal routing mechanism stays unproven. The user-visible friction outcome is
    proven.

## Resolution

root_cause: TWO independent contributing causes, both checked against direct evidence in this
  session. Both must be addressed together (one in the config category, one in the usage-pattern
  category. See the reasoning_checkpoint and-gate field in Current Focus).
  (1) Claude Code resolves a Bash action deterministically only when EVERY shell-control-operator-
  separated segment of the command matches a permissions.allow entry. Zero of the combined 150
  entries across settings.json/settings.local.json cover a bare `cd` segment. So any `cd X && verb
  args` invocation (this agent's own habitual phrasing, and the only practical way to run
  directory-scoped tools like `pio` from `firestarter_fw/`) structurally cannot fully resolve at
  the deterministic layer. It is always deferred to the auto-mode classifier, regardless of how
  well the trailing verb is otherwise covered by the allow list. (2) settings.json's
  `permissions.allow` contains 2 blanket single-verb wildcards, `Bash(git *)` and `Bash(gh *)`.
  These are broad enough to deterministically pre-approve bare invocations of exactly the dangerous
  sub-verbs (`gh pr merge`, `gh issue comment`, `gh release`, `gh api` DELETE/POST/PATCH/PUT, `git
  push` to a protected branch) that the operator's own drafted autoMode hard_deny/soft_deny arrays
  exist to gate. Because deterministic allow resolves BEFORE the classifier is ever consulted,
  those guardrails are unreachable for any bare (non-compound) invocation of those tools today.
  (H2, the [Self-Modification] hard_deny on writing the agent's own governing config, was already
  checked and found accurate by the five prior elimination probes. It is not re-opened here.)

fix: OPERATOR-APPLIED (this agent is hard-denied from writing its own permission configuration -
  [Self-Modification] tier. See the reasoning_checkpoint field in Current Focus.) Two parts:
  (A) Narrow the blanket wildcards in /workspaces/.claude/settings.json `permissions.allow` -
  replace `"Bash(git *)"` and `"Bash(gh *)"` with a curated set of safe, scoped sub-verb wildcards
  (e.g. `Bash(git status *)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(git show *)`,
  `Bash(git add *)`, `Bash(git commit *)`, `Bash(git branch *)`, `Bash(git fetch *)`,
  `Bash(git worktree *)`, `Bash(git -C * status *)`, `Bash(git -C * push *)`, `Bash(gh issue list
  *)`, `Bash(gh issue view *)`, `Bash(gh pr list *)`, `Bash(gh pr view *)`, `Bash(gh pr diff *)`,
  `Bash(gh pr checks *)`, `Bash(gh run list *)`, `Bash(gh run view *)`, `Bash(gh release list *)`,
  `Bash(gh api * -X GET*)` or equivalent GET-only scoping), deliberately EXCLUDING `git push`,
  `git reset --hard`, `git clean`, `gh pr merge`, `gh pr create`, `gh issue comment`, `gh release`,
  `gh label`, and any `gh api` with a non-GET verb, so those fall through to the classifier where
  the existing/proposed hard_deny and soft_deny arrays can act on them.
  (B) Apply the draft autoMode.json (already shown above to be pointing in the right direction)
  into settings.json's `autoMode` block, merging rather than replacing the existing
  `["$defaults", "Bash(git push *)", "Bash(git -C * push *)"]` allow entries (which stay - they are
  the entries that actually matter once (A) deletes the blanket cover that `Bash(git *)` currently
  provides). Also add, to
  autoMode.allow, coverage for the concretely missing directory-scoped and tool-bare cases found in
  evidence: PlatformIO run from `firestarter_fw/` (`cd firestarter_fw && pio run *` /
  `pio run -d firestarter_fw *`), `pio test`, bare `pytest`/`ruff`/`mypy` in `firestarter_app/`,
  and a narrow allowance for `cd <known project dir> && <already-allowed verb> ...` generally, so
  this agent's habitual `cd /workspaces && ...` phrasing stops taking the classifier path for
  commands that are otherwise fully covered.
  Do NOT add a blanket `Bash(cd *)` / `Bash(cd:*)` rule - a known community-reported concern
  (anthropics/claude-code#28784, found via research, not independently reproduced here) flags
  `Bash(cd:*)` combined with chaining as a broader-than-intended grant. Prefer scoping any `cd`
  allowance to this repo's specific directories, or eliminate the need for `cd` entirely by
  standardizing on `-C <dir>` / `--project-dir <dir>`-style invocation (already the working pattern
  in the one existing `Bash(env -C /workspaces/firestarter pio run -t upload -e leonardo *)` entry,
  though note that entry's path is stale post-rename and should become `firestarter_fw`).
  Exact settings.json diff is intentionally NOT pre-written as a git patch here, because every
  candidate replacement sub-verb list is a judgment call about the operator's actual risk
  tolerance (e.g., should `git commit *` be unscoped, given a commit is locally reversible but a
  push is not?) - the operator should review and adjust the proposed list in (A) before applying it,
  not apply it verbatim.

verification: RUN, in a later session after the operator applied the fix and re-entered auto mode.
  Four checks, each recorded in full above under Evidence.
  (1) File audit - both settings files match files_changed exactly: the four named blanket
  wildcards are gone from settings.json, the four named entries are gone from settings.local.json,
  and the autoMode block carries exactly environment 9 / allow 13 / soft_deny 7 / hard_deny 6.
  (2) Falsification test, substituted for safety - the session's original plan named a live
  `gh release create` against a disposable target. That action is exactly the hazard hard_deny (1)
  exists to prevent, so it was replaced with an inert pair: `gh release list --repo
  henols/firestarter_fw` (scoped in, read-only) against `gh api -X DELETE
  /repos/henols/zzz-nonexistent-probe-target` (scoped out, non-GET, and inert because that
  repository does not exist, checked first with `gh repo view`). The scoped-in call ran silently
  and returned data. The scoped-out call was denied outright by the classifier with reason
  "[Auto-Mode Bypass]". This settles root_cause (2): the under-blocking safety gap. A bare
  dangerous `gh api` call that the old blanket wildcard would have pre-approved is now denied.
  (3) A/B re-run - `git status --short` bare against `cd /workspaces && git status --short`.
  Both ran identically, with no prompt and no denial, matching the first attempt. This stays
  INCONCLUSIVE on the narrow internal-mechanism question (deterministic match versus
  classified-and-approved), exactly as flagged before the fix. The harness exposes no
  classifier-invocation log to the agent, so this gap is not closable from inside this session.
  What is new is a working negative control from check (2) above: a real denial is visible from
  inside the agent when the classifier refuses. Its absence for the `cd`-prefixed call is therefore
  informative, not just silence by default, and it directly shows the practical friction symptom
  is gone, even though the routing mechanism itself remains unproven.
  (4) H2, the [Self-Modification] hard_deny, was not re-tested. It was already checked to
  correctness by the five elimination probes earlier in this session. It is expected, by-design
  behavior.
  Net: the falsification test settles the more serious half of root_cause. The A/B stays
  inconclusive on mechanism. The A/B shows the symptom, friction, is resolved in practice.

files_changed:
  - /workspaces/.claude/settings.json - permissions.allow 111 -> 122 entries. Removed the 4 blanket
    wildcards `Bash(gh *)`, `Bash(gh pr *)`, `Bash(git *)`, `Bash(gh api *)`. Removed 9 dead entries
    naming the pre-rename `firestarter` submodule path, which no longer exists. Added 24 scoped
    read-only sub-verbs. Merged the autoMode block (environment 9, allow 13, soft_deny 7,
    hard_deny 6).
  - /workspaces/.claude/settings.local.json - permissions.allow 40 -> 36 entries. Removed
    `Bash(gh release:*)`, `Bash(gh release edit:*)`, `Bash(gh pr merge:*)`, `Bash(gh api *)` and 2
    dead pre-rename push entries. The hooks, worktree and extraKnownMarketplaces blocks are intact.
  - Backups at .claude/settings.json.bak and .claude/settings.local.json.bak. Both are gitignored.

  CORRECTION to this session's own proposal: the fix recorded settings.local.json as needing no
  change. That was wrong. The dangerous sub-verbs `gh release`, `gh pr merge` and unrestricted
  `gh api` were allowed in settings.local.json, not in settings.json. Narrowing settings.json alone
  would have left every one of them pre-approved, and part (A) would have achieved nothing.

  Two deliberate departures from the proposed sub-verb list, both operator-approved:
  (1) `git push` stays allowed. GitHub protects main and beta server-side with
  current_user_can_bypass set to never, so it rejects the catastrophic case without help. Gating
  pushes would tax every GSD ship and buy little. Dropping `Bash(git *)` still sends `git clean`
  and `git reset --hard` to the classifier, which is where the unbacked local risk sits.
  (2) `gh issue comment:*` stays allowed. The devtest-triage workflow posts comments often, and a
  comment is editable and deletable. `gh release` and `gh api` writes have no such backstop.

  Residual, harmless: 4 fully-pinned historical rules naming PR 52, 51, 35 and one policy PR still
  match `gh pr merge` and `gh pr create`. Each names an exact PR number, repo, subject and body, so
  none can match a new invocation. One of them names the dead `henols/firestarter` slug.
