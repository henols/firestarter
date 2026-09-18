---
phase: 260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/260918-ayh-SUMMARY.md
autonomous: true
requirements:
  - QUICK-260918-ayh
estimate:
  tokens: 22500
  raw_tokens: 45000
  tasks: 3
  confidence: high
must_haves:
  truths:
    - "GitHub pre-release `3.0.0b33` in `henols/firestarter_fw` carries the three AVR install images `firestarter_uno.hex`, `firestarter_uno328pb.hex` and `firestarter_leonardo.hex`, so `firestarter fw --install --pre` resolves an asset for every AVR board instead of failing."
    - "The published asset basenames are the exact names the host's `asset_candidates()` asks for, checked by deriving the expected set from `/workspaces/firestarter_app/firestarter/firmware.py` rather than transcribing it."
    - "`origin/beta` in `henols/firestarter_fw` is still at `11024ee47bdc99dde9308c5179aae608871979bc` after the repair — the dispatch pushed no commit and moved no tag."
    - "Issues #67 and #68 in `henols/firestarter` are CLOSED, each carrying exactly one new comment naming firmware `3.0.0b33` and host `3.0.0b48`, and each labelled `fix:released`."
    - "Issues #2 and #5 in `henols/firestarter` are CLOSED, each carrying exactly one new comment; #2's comment states that the old firmware slug no longer redirects and gives the `git remote set-url` repair."
    - "Issues #15 and #16 are still OPEN with their comment counts unchanged (2 and 0), because the evidence on `origin/beta` contradicts named acceptance criteria in both."
    - "No public comment contains a `.planning/` path, a phase number, a milestone identifier, or any AI or assistant attribution."
    - "No branch was created, switched or pushed in any of the three repositories, and no file under `firestarter_fw/` or `firestarter_app/` was modified."
  artifacts:
    - "Pre-release `3.0.0b33` at https://github.com/henols/firestarter_fw/releases/tag/3.0.0b33 with >= 3 assets"
    - ".planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/260918-ayh-SUMMARY.md"
  key_links:
    - "beta-build.yml workflow_dispatch (ref `beta`, beta_version=3.0.0b33) -> softprops/action-gh-release@v2 -> assets on the existing `3.0.0b33` tag"
    - "published asset basename -> host `asset_candidates(board)` in firestarter_app/firestarter/firmware.py:113-128 -> `_pick_asset` download URL"
    - "assets exist -> `fix:released` on #67/#68 is a true statement"
---

<objective>
Repair the `henols/firestarter_fw` pre-release `3.0.0b33`, which was published against the right
commit but carries zero assets, then close the GitHub issues whose fixes have actually shipped.

Purpose: `firestarter fw --install --pre` is broken for every user on the pre-release channel —
the host finds `3.0.0b33`, finds no `.hex` in it, and fails. Nothing else can honestly be announced
as released until that release carries installable firmware.

Output: three AVR install images attached to the existing `3.0.0b33` tag; four issues closed with
a factual comment each; two issues deliberately left open with their reasons recorded for the
operator.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md

Established by planning on 2026-09-18 — do NOT re-derive, but DO re-assert anything a task's
`<precondition>` names:

- **Measured release state.** `gh release view 3.0.0b33 --repo henols/firestarter_fw` →
  `tagName 3.0.0b33`, `isPrerelease true`, `createdAt 2026-09-17T20:45:50Z`,
  `targetCommitish 11024ee47bdc99dde9308c5179aae608871979bc`, **`assets: 0`**. The upload failed
  with "Error creating asset temp dir". The tag and the release object are correct; only the
  assets are missing.
- **Why the dispatch is safe.** `origin/beta`'s `include/version.h` already reads `3.0.0b33` and
  its tip is `11024ee`. With `beta_version=3.0.0b33`, `update_version.py` writes the same string,
  the diff is empty, `stefanzweifel/git-auto-commit-action@v5` is a no-op, and nothing is pushed
  to `beta`. This is what distinguishes the dispatch from a re-run of the failed run, which
  auto-increments and is rejected non-fast-forward.
- **Never hand-build or hand-upload a `.hex`.** The only permitted repair is the dispatch.
- **`rehearsal` defaults to `false` — do not pass it.** `rehearsal=true` publishes a draft under a
  `rehearsal-<run_id>` tag and repairs nothing.
- **The ref MUST be `beta`.** This workflow was once dispatched from a non-default branch (run
  30199560282, 2026-07-26) and published a real public prerelease by accident.
- **Asset expectation.** `.pio/build/**/firestarter_*.hex` for the three AVR envs in
  `platformio.ini` (`uno`, `uno328pb`, `leonardo`), plus `build/py32f071/firestarter_py32f071.hex`
  only if the ARM build succeeds. The ARM step is `continue-on-error: true` by design — a missing
  `py32f071` asset is NOT a failed repair. The three AVR assets are the pass condition.
- **Version strings, read at planning time.** `firestarter_fw` `include/version.h` on `origin/beta`
  → `3.0.0b33`. `firestarter_app` `firestarter/__init__.py` → `3.0.0b48`, already on PyPI.
- **Issue state, read at planning time** (`henols/firestarter` is the single tracker for the whole
  project): #2 OPEN / `enhancement` / 0 comments · #5 OPEN / `enhancement` / 1 comment ·
  #15 OPEN / no labels / 2 comments · #16 OPEN / no labels / 0 comments ·
  #67 OPEN / `bug`,`cause:firmware` / 0 comments · #68 OPEN / `bug`,`cause:firmware` / 1 comment.
- **`gh` needs a writable cache in this devcontainer.** `~/.cache/gh` is unwritable. Prefix every
  `gh` call with
  `XDG_CACHE_HOME=/tmp/claude-1000/-workspaces/9c8dcaa7-65a1-4d19-8d68-aad44c6bea63/scratchpad/ghcache`
  and create that directory once with `mkdir -p` before the first call.
- **Branch and worktree discipline.** HEAD is `quick/260918-ayh-b33-repair-and-issue-closeout`,
  forked from `beta` at `046f1760`, deliberately so nothing lands on `beta`. Do not switch, create,
  rebase or push any branch, here or in either submodule. Do not push at all — GSD pushes at ship
  time only.
- **Pre-existing unrelated dirt that must survive untouched:** modified
  `.devcontainer/devcontainer.json`, `.vscode/c_cpp_properties.json`, `.vscode/extensions.json`,
  `.vscode/launch.json`, `.planning/graphs/.last-build-status.json`,
  `.planning/graphs/GRAPH_REPORT.md`; untracked `anything.txt`, `firestarter.wiki/`,
  `setup-claude-pr-policy.sh`, `tmp/`. Never `git add -A`, `git add .`, `git commit -a` or
  `git clean -Xdf`. Stage only the explicit `.planning/quick/260918-ayh-*/` paths.
- **This task edits no product source.** Write no comments into product source — that covers
  everything under `firestarter_fw/` and `firestarter_app/`, applies to any `#`, `//` or `/* */`
  line for any reason, and is not overridable by this plan, a task, a skill or a subagent
  instruction. No file in either submodule is touched by this plan at all.
- **Forbidden verbs:** never run `gsd-tools query audit-open acknowledge` (it destroys artifact
  content) and never run `state.sync` (it corrupts STATE.md frontmatter). Do not use
  `gsd-tools query commit` — it scrapes ROADMAP prose and has been observed to switch branches.
  Use plain `git` with explicit pathspecs.
- **No ROADMAP edit, no backlog filing.** A quick task is not a roadmap phase. If the release
  pipeline defect deserves a durable record, note it in the SUMMARY for the operator instead.

**Register for every public comment** (matching `.claude/skills/devtest-rootcause` §4): factual;
name the artefact versions that carry the fix; separate what is proven from what is not. A reader
of the issue tracker has no `.planning/` directory — no phase numbers, no milestone identifiers
(`v1.39`, `D-11`, `PAGE-03`), no GSD vocabulary. No AI or assistant attribution anywhere, in a
comment or a commit message.

**Grounding for the #67 / #68 wording, verified in source at planning time — do not restate more
than this:**
- Host `firestarter_app/firestarter/database.py:411-413,544-551` carries the chip's recorded
  `programming.page_size` onto the wire as `page-size`; the firmware reads `handle->page_size` in
  `src/proms/flash_5v_page.cpp:82` and errors with `MSG_ERR_FL4_PAGE_SIZE` on a size it cannot use.
  The derive-from-total-size helper is gone.
- Host `firestarter_app/firestarter/page_size_gate.py` refuses pre-connect when no page size is
  recorded, when the recorded size is not a power of two ≤ 512, or when `start % page_size` or
  `length % page_size` is non-zero; the firmware refuses again with `MSG_ERR_FL4_PAGE_ALIGN`
  (`src/proms/flash_5v_page.cpp:94`). A zero-length payload is not refused.
- Bench evidence in both issues is a **W29C020 on a Leonardo**. Claim no hardware validation
  beyond that.
</context>

<comment_bodies>

These are the exact bodies to post. Write each to a scratch file and post with
`gh issue comment <n> --repo henols/firestarter --body-file <file>`. Do not compose, reword,
shorten or extend any of them.

**BODY-67** — post on #67 before closing it:

~~~markdown
Fixed. The firmware no longer derives the page size from the device's total size — the page size now comes from the chip's own database record and is sent with the write command, so the parts listed above use their real 128, 256 or 512 byte page. A chip with no recorded page size, or one whose recorded size this protocol cannot use, is refused before anything is written rather than guessed at.

The fix is carried by firmware `3.0.0b33` and host `3.0.0b48`:

```
pip install --pre --upgrade firestarter
firestarter fw --install --pre
```

Verified on a W29C020 on a Leonardo and by the firmware and host test suites. The other affected parts have not been re-checked on hardware — a fresh report on any of them is welcome.
~~~

**BODY-68** — post on #68 before closing it:

~~~markdown
Fixed by refusing the write, not by adding a read-modify-write. A protocol `0x05` write whose start address or payload length is not a whole multiple of the chip's page size is now rejected before any page cycle runs, with a message naming the page size, the start address and the length. Both sides check: the host refuses before it opens the port, and the firmware refuses again on the write command. Whole-page writes are unchanged, so patching part of a page now means supplying the whole page.

The fix is carried by firmware `3.0.0b33` and host `3.0.0b48`:

```
pip install --pre --upgrade firestarter
firestarter fw --install --pre
```

Verified on a W29C020 on a Leonardo and by the firmware and host test suites. No other protocol `0x05` part has been re-checked on hardware.
~~~

**BODY-02** — post on #2 before closing it:

~~~markdown
Done. The repositories are now `henols/firestarter_fw` for the firmware and `henols/firestarter_app` for the host application, and `henols/firestarter` is the project's front door and its issue tracker. The application resolves firmware releases from `henols/firestarter_fw` directly and does not depend on a redirect.

One thing to know if you already have a clone: because `henols/firestarter` is now this repository, the old firmware URL no longer redirects to the firmware — it resolves here instead. Re-point an old firmware clone with:

```
git remote set-url origin https://github.com/henols/firestarter_fw.git
```

Installing or upgrading the application with pip is unaffected.
~~~

**BODY-05** — post on #5 before closing it:

~~~markdown
Done. All project documentation now lives in one place: the wiki of this repository. The firmware and application READMEs are now short and repo-specific and link here, and the wikis on both of those repositories are disabled, so there is no second copy to drift out of date.
~~~

</comment_bodies>

<tasks>

<task type="auto">
  <name>Task 1: Repair pre-release 3.0.0b33 by dispatching beta-build.yml on beta</name>
  <files>none — this task creates no file and modifies no repository working tree</files>
  <precondition>`gh release view 3.0.0b33 --repo henols/firestarter_fw --json assets --jq '.assets|length'` still prints `0`, and `git -C /workspaces/firestarter_fw rev-parse origin/beta` (after `git -C /workspaces/firestarter_fw fetch origin beta`) still prints `11024ee47bdc99dde9308c5179aae608871979bc`. If either differs, halt and report — someone has already acted on this release.</precondition>
  <read_first>/workspaces/firestarter_fw/.github/workflows/beta-build.yml (the `files:` list under `softprops/action-gh-release@v2` and the `workflow_dispatch` inputs), /workspaces/firestarter_app/firestarter/firmware.py lines 80-128 (`_BOARD_FLASH_METHODS`, `asset_candidates`)</read_first>
  <reversibility rating="costly">Publishing assets to a public pre-release notifies watchers and is visible immediately; it is undoable only by deleting assets, which is itself public. The dispatch is nonetheless the only sanctioned repair and restores the intended state of an already-public release.</reversibility>
  <action>
    Create the gh cache directory once with `mkdir -p` at the path named in the context, then export
    `XDG_CACHE_HOME` to it for every gh call in this plan.

    Dispatch the repair exactly as written, with no extra inputs:
    `gh workflow run beta-build.yml --repo henols/firestarter_fw --ref beta -f beta_version=3.0.0b33`.
    Do not pass `rehearsal`. Do not use `gh run rerun` on the failed run — it auto-increments the
    version and is rejected non-fast-forward. Do not build or upload a `.hex` by hand under any
    circumstance, including if the dispatched run fails.

    Resolve the new run id with
    `gh run list --workflow=beta-build.yml --repo henols/firestarter_fw --branch beta --limit 5 --json databaseId,status,createdAt,event`
    and pick the newest `workflow_dispatch` entry created after the dispatch. Wait for it with
    `gh run watch <id> --repo henols/firestarter_fw --exit-status`; if that needs a TTY, poll
    `gh run view <id> --repo henols/firestarter_fw --json status,conclusion` in a background command
    instead. The run takes several minutes — a native test suite, a Python test suite, three AVR
    builds and an ARM build. Do not assume it finished.

    When the run ends, read the conclusion. If the ARM job step failed but the three AVR assets
    published, that is a PASS — the ARM step is `continue-on-error: true` by design. If the run
    failed before the release step, or the assets are still absent, halt and report; do not dispatch
    a second time and do not improvise a workaround.

    Finally assert that `beta` did not move: fetch and compare `origin/beta` against the recorded
    SHA. The dispatch is expected to push nothing.
  </action>
  <verify>
    <automated>export XDG_CACHE_HOME=/tmp/claude-1000/-workspaces/9c8dcaa7-65a1-4d19-8d68-aad44c6bea63/scratchpad/ghcache; python3 -c "import re,os,sys,json,subprocess; src=open('/workspaces/firestarter_app/firestarter/firmware.py').read(); tbl=re.search(r'_BOARD_FLASH_METHODS\s*=\s*\{(.*?)\}',src,re.S).group(1); avr=sorted(m.group(1) for m in re.finditer(r'\"([^\"]+)\"\s*:\s*FLASH_METHOD_AVRDUDE',tbl)); assert avr, 'no AVR boards parsed'; assert re.search(r'f\"firestarter_\{board\}\.hex\"',src), 'asset_candidates naming pattern changed'; exp={'firestarter_%s.hex'%b for b in avr}; pub={a['name'] for a in json.loads(subprocess.run(['gh','release','view','3.0.0b33','--repo','henols/firestarter_fw','--json','assets'],capture_output=True,text=True,check=True).stdout)['assets']}; print('avr boards:',avr); print('published:',sorted(pub)); missing=sorted(exp-pub); sys.exit('MISSING ASSETS: %s'%missing if missing else 0)"</automated>
    <automated>git -C /workspaces/firestarter_fw fetch origin beta --quiet; test "$(git -C /workspaces/firestarter_fw rev-parse origin/beta)" = "11024ee47bdc99dde9308c5179aae608871979bc" && echo "beta unmoved OK"</automated>
  </verify>
  <done>Pre-release `3.0.0b33` carries `firestarter_uno.hex`, `firestarter_uno328pb.hex` and `firestarter_leonardo.hex`, every basename matches what the host's `asset_candidates()` asks for, and `origin/beta` is still at `11024ee47bdc99dde9308c5179aae608871979bc`.</done>
</task>

<task type="auto">
  <name>Task 2: Close #67 and #68 with the shipped-fix comments and fix:released</name>
  <files>none in any repository — GitHub issue state only</files>
  <precondition>Task 1's asset verify passed. `gh release view 3.0.0b33 --repo henols/firestarter_fw --json assets --jq '.assets|length'` prints 3 or more. Closing these issues announces a released fix; a `fix:released` label on a release with no installable firmware would be a false statement, so this task must not start before the assets exist.</precondition>
  <reversibility rating="costly">A public comment notifies every subscriber the moment it posts and an edit does not un-notify them. The bodies are fixed by this plan precisely so nothing is composed at execution time.</reversibility>
  <action>
    For #67 then #68, in that order: write the matching body from `&lt;comment_bodies&gt;` (BODY-67,
    BODY-68) verbatim to a scratch file under the session scratchpad, post it with
    `gh issue comment &lt;n&gt; --repo henols/firestarter --body-file &lt;file&gt;`, add the label with
    `gh issue edit &lt;n&gt; --repo henols/firestarter --add-label fix:released`, then close with
    `gh issue close &lt;n&gt; --repo henols/firestarter`.

    Post the comment before closing, so the close notification carries the explanation. Post exactly
    one comment per issue. Change no existing label: `bug` and `cause:firmware` stay on both. Do not
    reword, shorten, extend or re-check the body text — it was written and fact-checked against
    source at planning time.

    Use a heredoc or the Write tool for the scratch file. Do not pass the body inline with `--body`,
    where shell expansion would mangle the backticks and the fenced block.
  </action>
  <verify>
    <automated>export XDG_CACHE_HOME=/tmp/claude-1000/-workspaces/9c8dcaa7-65a1-4d19-8d68-aad44c6bea63/scratchpad/ghcache; for n in 67 68; do gh issue view $n --repo henols/firestarter --json state,labels,comments --jq '"#'$n' state=\(.state) labels=\([.labels[].name]|join(",")) comments=\(.comments|length) last=\(.comments[-1].body|.[0:40])"'; done</automated>
    <automated>export XDG_CACHE_HOME=/tmp/claude-1000/-workspaces/9c8dcaa7-65a1-4d19-8d68-aad44c6bea63/scratchpad/ghcache; python3 -c "import json,subprocess,sys; bad=[]; exp={'67':1,'68':2}
for n in ('67','68'):
    d=json.loads(subprocess.run(['gh','issue','view',n,'--repo','henols/firestarter','--json','state,labels,comments'],capture_output=True,text=True,check=True).stdout)
    names=[l['name'] for l in d['labels']]; body=d['comments'][-1]['body'] if d['comments'] else ''
    if d['state']!='CLOSED': bad.append(n+': not CLOSED')
    if 'fix:released' not in names: bad.append(n+': missing fix:released')
    if len(d['comments'])!=exp[n]: bad.append(n+': comment count %d, expected %d'%(len(d['comments']),exp[n]))
    for tok in ('3.0.0b33','3.0.0b48'): 
        if tok not in body: bad.append(n+': last comment omits '+tok)
    for tok in ('.planning','v1.39','D-11','PAGE-03','Claude','Anthropic','AI-assisted'):
        if tok in body: bad.append(n+': last comment leaks '+tok)
sys.exit('; '.join(bad) if bad else 0)"</automated>
  </verify>
  <done>#67 and #68 are CLOSED, each carries exactly one new comment naming both `3.0.0b33` and `3.0.0b48` and leaking no internal identifier, and both are labelled `fix:released` alongside their existing `bug` and `cause:firmware`.</done>
</task>

<task type="auto">
  <name>Task 3: Close #2 and #5; re-verify #15 and #16 and leave both open</name>
  <files>.planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/260918-ayh-SUMMARY.md</files>
  <precondition>`gh issue view 15 --repo henols/firestarter --json comments --jq '.comments|length'` prints `2` and the same call for #16 prints `0` — the counts recorded at planning time, which the verify asserts are unchanged.</precondition>
  <reversibility rating="costly">Same public-notification cost as Task 2 for #2 and #5. Leaving #15 and #16 open is fully reversible and is the deliberate outcome.</reversibility>
  <action>
    **Close #2 and #5.** For each, in order: write BODY-02 / BODY-05 from `&lt;comment_bodies&gt;`
    verbatim to a scratch file, post with
    `gh issue comment &lt;n&gt; --repo henols/firestarter --body-file &lt;file&gt;`, then
    `gh issue close &lt;n&gt; --repo henols/firestarter`. Leave the existing `enhancement` label on both
    and add no label — neither is a bug fix, so `fix:released` does not apply.

    **#15 and #16 stay OPEN. Post nothing on either.** Planning assessed both against `origin/beta`
    in `/workspaces/firestarter_fw` and found the evidence mixed in both cases. Re-assert that
    finding with the commands in `&lt;verify&gt;` rather than trusting it, then record it in the SUMMARY
    for the operator:

    - **#15 — protocol-specific EPROM programming algorithms.** Substantial work shipped: a const,
      `protocol_id`-keyed parameter table (`src/proms/eprom_params.cpp`, rows for 0x07/0x08/0x0B
      carrying max-pulse counts, an energy cap, a verify mode and a VPP path), a per-byte pulse
      count with the pulse width never grown, and the block-level adaptive retry loop gone. But at
      least three of the issue's own acceptance criteria are demonstrably unmet on `origin/beta`:
      there is one `eprom_write_execute`, not the three separate handlers the issue's required
      design names and the table's design note explicitly forbids a second dispatch selector;
      `overprogram_factor` is `0` in all three rows, so the final overprogram pulse the issue asks
      for is inert; and 0x0B still keeps the 500 µs fallback default and a max-pulse ceiling of 255
      where the issue asks for a long fixed pulse with one attempt and no 500 µs default. Mixed
      evidence on a two-month-old community request closes to a wrong answer. Leave it open.
    - **#16 — prepare HAL for PY32F071.** The HAL work is present on `origin/beta`
      (`include/rurp_platform.h`, `include/rurp_platform_compat.h`, board headers under
      `include/boards/`, the `platform/py32f071/` tree with its own timing, dual-slot flash config
      storage and native USB CDC, a CMake/`arm-none-eabi` build and a `py32f071.yml` workflow). But
      `platform/py32f071/CMakeLists.txt` sets `RURP_HAS_VPP_DAC=0` and the tree's own notes route
      the closed DAC loop and its calibration out of scope, so the issue's DAC-VPP acceptance
      criterion is unmet; the pin map is marked `[ASSUMED]` with no schematic confirming it; the
      workflow publishes only the `.hex`, not the BIN and ELF the issue asks CI to publish; and no
      PY32F071 board has ever been flashed. Leave it open.

    If either re-assertion contradicts the finding above — for instance three separate write
    handlers now exist — do not close the issue on the strength of that alone. Halt, and record the
    contradiction in the SUMMARY for the operator to decide.

    **Then write the SUMMARY** at the path in `&lt;files&gt;`, recording: the dispatched run id, url and
    conclusion; the exact published asset list for `3.0.0b33`; the four closed issues with their
    comment urls; the two issues left open with the reasons above stated in full; and — as an
    operator note, not a backlog filing — that `beta-build.yml` published a release object whose
    asset upload failed without failing the run, so a zero-asset release can reach users silently,
    and that the failed run cannot be re-run to fix it because the version auto-increments.

    Commit the SUMMARY with plain `git` from `/workspaces`, staging only
    `.planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/`. Never `git add -A` or
    `git add .`. Do not touch either submodule, do not stage a gitlink, do not switch branches and
    do not push. The commit message must carry no attribution line, no `Co-Authored-By` trailer and
    no identifier beyond the quick id `260918-ayh`.
  </action>
  <verify>
    <automated>export XDG_CACHE_HOME=/tmp/claude-1000/-workspaces/9c8dcaa7-65a1-4d19-8d68-aad44c6bea63/scratchpad/ghcache; python3 -c "import json,subprocess,sys; bad=[]
for n,exp in (('2',1),('5',2)):
    d=json.loads(subprocess.run(['gh','issue','view',n,'--repo','henols/firestarter','--json','state,comments'],capture_output=True,text=True,check=True).stdout)
    if d['state']!='CLOSED': bad.append(n+': not CLOSED')
    if len(d['comments'])!=exp: bad.append(n+': comment count %d, expected %d'%(len(d['comments']),exp))
    b=d['comments'][-1]['body'] if d['comments'] else ''
    for tok in ('.planning','v1.35','v1.38','Claude','Anthropic','AI-assisted'):
        if tok in b: bad.append(n+': comment leaks '+tok)
c2=json.loads(subprocess.run(['gh','issue','view','2','--repo','henols/firestarter','--json','comments'],capture_output=True,text=True,check=True).stdout)['comments']
if not c2 or 'git remote set-url' not in c2[-1]['body']: bad.append('2: last comment missing, or omits the git remote set-url repair')
for n,exp in (('15',2),('16',0)):
    d=json.loads(subprocess.run(['gh','issue','view',n,'--repo','henols/firestarter','--json','state,comments'],capture_output=True,text=True,check=True).stdout)
    if d['state']!='OPEN': bad.append(n+': must stay OPEN')
    if len(d['comments'])!=exp: bad.append(n+': comment count %d, expected unchanged %d'%(len(d['comments']),exp))
sys.exit('; '.join(bad) if bad else 0)"</automated>
    <automated>cd /workspaces/firestarter_fw && git fetch origin beta --quiet; python3 -c "import subprocess,sys
def sh(a): return subprocess.run(a,cwd='/workspaces/firestarter_fw',capture_output=True,text=True).stdout
bad=[]
h=sh(['git','grep','-nE','eprom_(regular|quick|legacy)_write_execute','origin/beta','--','src','include'])
print('#15 variant handlers found:'); print(h or '  (none)')
if h.strip(): bad.append('#15: separate per-protocol write handlers now exist — the planner finding is stale, HALT and report')
rows=[l for l in sh(['git','show','origin/beta:src/proms/eprom_params.cpp']).splitlines() if '/* 0x0' in l]
print('#15 param table rows:'); [print(' ',r.strip()) for r in rows]
if len(rows)!=3: bad.append('#15: expected 3 param rows, found %d'%len(rows))
dac=[l for l in sh(['git','show','origin/beta:platform/py32f071/CMakeLists.txt']).splitlines() if 'RURP_HAS_VPP_DAC' in l]
print('#16 DAC seam:'); [print(' ',d.strip()) for d in dac]
if not any('RURP_HAS_VPP_DAC=0' in d for d in dac): bad.append('#16: the DAC seam is no longer 0 — the planner finding is stale, HALT and report')
ci=[l.strip() for l in sh(['git','show','origin/beta:.github/workflows/py32f071.yml']).splitlines() if 'firestarter_py32f071.' in l]
print('#16 CI artifact lines:'); [print(' ',c) for c in ci]
if any(c.endswith('.bin') or c.endswith('.elf') for c in ci if c.startswith('path:')): bad.append('#16: CI now publishes bin/elf — the planner finding is stale, HALT and report')
sys.exit('; '.join(bad) if bad else 0)"</automated>
    <automated>cd /workspaces && python3 -c "import subprocess,sys,os
bad=[]
p='.planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/260918-ayh-SUMMARY.md'
if not os.path.isfile(p): bad.append('SUMMARY.md missing')
msg=subprocess.run(['git','log','-1','--format=%B'],capture_output=True,text=True,check=True).stdout
for tok in ('Co-Authored-By','Claude','Anthropic','Generated with','AI-assisted'):
    if tok in msg: bad.append('commit message carries '+tok)
files=[f for f in subprocess.run(['git','show','--name-only','--format=','HEAD'],capture_output=True,text=True,check=True).stdout.split() ]
print('committed paths:',files)
stray=[f for f in files if not f.startswith('.planning/quick/260918-ayh-')]
if stray: bad.append('commit touched paths outside the quick dir: %s'%stray)
br=subprocess.run(['git','rev-parse','--abbrev-ref','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
if br!='quick/260918-ayh-b33-repair-and-issue-closeout': bad.append('branch changed to '+br)
sys.exit('; '.join(bad) if bad else 0)"</automated>
  </verify>
  <done>#2 and #5 are CLOSED with one new comment each and their `enhancement` label intact; #15 and #16 are still OPEN with comment counts of 2 and 0 and no comment posted by this run; the SUMMARY records the run, the published assets, the four closes, the two deliberate non-closes with their evidence, and the operator note about the silent zero-asset release; the commit sits on `quick/260918-ayh-b33-repair-and-issue-closeout` touching only the quick directory.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| this session → `henols/firestarter_fw` Actions and Releases | a `workflow_dispatch` runs CI with repository credentials and publishes public artifacts |
| this session → `henols/firestarter` issue tracker | comments and closes are public, outward-facing product, and notify every subscriber |
| this repository's working tree → `beta` / `main` | a stray push or branch switch publishes; a `beta` push in a sub-repo is a release, not a merge |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-260918-ayh-01 | Tampering | `beta-build.yml` dispatch inputs | high | mitigate | Exactly one dispatch, `--ref beta`, only `beta_version=3.0.0b33`; `rehearsal` never passed; `gh run rerun` forbidden by the action; Task 1's second verify asserts `origin/beta` is still `11024ee47bdc99dde9308c5179aae608871979bc`, proving nothing was pushed. |
| T-260918-ayh-02 | Tampering | firmware install image | critical | mitigate | Hand-building or hand-uploading a `.hex` is forbidden outright; the only permitted image is the one the workflow builds from `origin/beta`. Task 1's verify checks published basenames against the host's own `asset_candidates()` source, so a wrongly-named or foreign asset fails the gate. |
| T-260918-ayh-03 | Repudiation | public issue comments | high | mitigate | Every body is fixed verbatim in `<comment_bodies>`; nothing is composed at execution time. Task 2 and Task 3 verifies grep each posted body for internal identifiers and AI attribution and fail on any hit. |
| T-260918-ayh-04 | Information disclosure | `.planning/` vocabulary leaking to the public tracker | high | mitigate | Bodies carry no `.planning/` path, phase number or milestone identifier; both comment verifies assert their absence against an explicit token list. |
| T-260918-ayh-05 | Elevation of privilege | closing a community issue on mixed evidence | medium | mitigate | #15 and #16 are left OPEN by design; Task 3's second verify re-asserts the planner's evidence from `origin/beta` and turns RED if the finding is stale, forcing a halt rather than a close. |
| T-260918-ayh-06 | Tampering | unrelated dirty and untracked working-tree paths | medium | mitigate | `git add -A`, `git add .`, `git commit -a` and `git clean -Xdf` are forbidden; only `.planning/quick/260918-ayh-*/` is staged; Task 3's verify asserts the commit's changed-path set and the branch name. |
| T-260918-ayh-07 | Denial of service | announcing a fix with no installable firmware | high | mitigate | Task 2's precondition blocks on an asset count of 3 or more, so `fix:released` cannot be applied before the release is installable. |
| T-260918-ayh-SC | Tampering | npm/pip/cargo installs | low | accept | This plan installs no package and runs no package manager. The `pip install` line inside BODY-67/BODY-68 is instruction text for a reader, never executed here. |
</threat_model>

<verification>
- `gh release view 3.0.0b33 --repo henols/firestarter_fw` lists at least the three AVR install
  images, and every basename is one the host's `asset_candidates()` asks for.
- `git -C /workspaces/firestarter_fw rev-parse origin/beta` is unchanged at
  `11024ee47bdc99dde9308c5179aae608871979bc`; no tag moved.
- #67, #68, #2 and #5 are CLOSED, one new comment each, `fix:released` on #67 and #68 only.
- #15 and #16 are OPEN with comment counts still 2 and 0.
- No posted comment contains a `.planning/` path, a phase or milestone identifier, or AI
  attribution.
- `git -C /workspaces/firestarter_fw status --porcelain` and
  `git -C /workspaces/firestarter_app status --porcelain` are byte-identical to their state before
  this plan ran — no product source was touched, in either sub-repo.
- The meta repository is still on `quick/260918-ayh-b33-repair-and-issue-closeout`, unpushed, with
  every pre-existing dirty and untracked path still exactly as dirty or untracked.
</verification>

<success_criteria>
- Pre-release `3.0.0b33` is installable: `firestarter fw --install --pre` resolves a `.hex` for
  `uno`, `uno328pb` and `leonardo`.
- The repair was made by one `workflow_dispatch` on ref `beta` and by nothing else; no asset was
  built or uploaded by hand.
- Four issues closed with a factual, version-naming comment; two issues left open with their
  evidence recorded in the SUMMARY.
- No commit in either sub-repo, no push anywhere, no branch created or switched, no ROADMAP edit,
  no backlog filing.
</success_criteria>

<output>
Create `/workspaces/.planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/260918-ayh-SUMMARY.md`
when done, recording the dispatched run id and url, the published asset list, the four closed
issues with comment urls, the two issues left open with their full reasons, and the operator note
about `beta-build.yml` publishing a release whose asset upload failed without failing the run.
</output>