# Phase 172: POLICY — One Tracker, Protected `main` - Pattern Map

**Mapped:** 2026-09-01
**Files analyzed:** 14 file artifacts + 3 API-only artifacts
**Analogs found:** 8 / 14 (6 have no in-repo analog — see "No Analog Found")

This phase writes **no product code**. Every artifact is documentation, GitHub configuration or
CI YAML. The pattern value therefore sits in *procedural* analogs — Phase 171's four plans — and in
the `tools/wiki/` checkers whose exact output strings the verify legs must assert on.

**All analog paths below are git-tracked source** (verified with `git ls-files` in `/workspaces`,
`firestarter/` and `firestarter_app/`). No gitignored mirror paths appear.

---

## Standing constraints that override local style

| Constraint | Where it bites |
|---|---|
| **NO COMMENTS in anything written.** Operator's standing hard rule; a plan cannot override it. | The new `wiki-check.yml` grep leg, both YAML issue forms, `config.yml`, the Markdown template, all three `.github/CONTRIBUTING.md`, the `MIGRATION-TABLE.md` row. **`wiki-check.yml` and `catalog-sync-check.yml` are dense with comments written by earlier phases — do NOT match that local style. Match the rule.** The Pitfall-1 fix is a *deletion* (`--wiki-dir wiki-clone`), so it satisfies the rule trivially. |
| No product code is edited. | `firestarter_app/firestarter/submit.py` is **read-only reference** here. |
| `.planning/` is never swept for dead-tracker links. | The grep leg carries `--exclude-dir=.planning`. |
| Submodule commits land **inside** the submodule on `gsd/v1.35-documentation-consolidation-wiki-migration`; meta commits on the same-named branch in `/workspaces`. | Every task touching `firestarter/` or `firestarter_app/`; gitlink re-pin at phase close. |
| Verify commands are single-line `&&`-chained shell that write an evidence file then assert on it. **Literal `&&`, never `&amp;&amp;`.** | Every `<automated>` leg. |

---

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|---|
| `Contributing.md` (wiki) | `firestarter_prom.wiki.git` | doc page | authored content | live wiki `Shell-Completion.md` (published by Phase 171 plan 01) | exact |
| `_Sidebar.md` (wiki) | wiki | nav | list append | its own current 10-bullet body | exact |
| `Home.md` `## Reference` (wiki) | wiki | nav | list append | its existing `- [Shell-Completion](Shell-Completion) — …` bullet | exact |
| `.github/ISSUE_TEMPLATE/bug-report.yml` | `/workspaces` (prom) | config (issue form) | form-capture | **none in any repo** — use RESEARCH "An issue form that validates" + real filed `[BUG]` issues | none |
| `.github/ISSUE_TEMPLATE/feature-request.yml` | prom | config (issue form) | form-capture | **none** — same | none |
| `.github/ISSUE_TEMPLATE/dev-test-report.md` | prom | config (md template) | routing / hand-off | **none**; differentiate against `submit.py`'s machine body | none |
| `.github/ISSUE_TEMPLATE/config.yml` | prom | config | chooser config | **none** — RESEARCH literal | none |
| `.github/CONTRIBUTING.md` ×3 | prom, fw, app | doc pointer | static link | **none**; nearest are the three README sections being trimmed | none |
| `.github/workflows/wiki-check.yml` (2 fixes + 1 leg) | prom | CI workflow | batch / scheduled | **itself**, plus `.github/workflows/catalog-sync-check.yml` | exact |
| `README.md:33-37` trim | prom | doc | static link | its own current text | exact |
| `firestarter/README.md:73-81` trim | fw | doc | static link | its own current text | exact |
| `firestarter_app/README.md:104-108` trim | app | doc | static link | its own current text | exact |
| `.planning/v1.35/MIGRATION-TABLE.md` (+1 row) | prom | data table | provenance record | the `Home` row + Phase 171's `Shell-Completion` row | exact |
| `evidence/172-NN-*.txt|.json` | prom | evidence | file-I/O | `.planning/phases/171-…/evidence/171-0*.txt` | exact |
| Three GitHub rulesets (API, not files) | — | live config | REST | `gh api /repos/henols/firestarter/rulesets/4998759` | exact |

---

## Pattern Assignments

### 1. `Contributing.md` on the wiki (doc page, authored content)

**Analog:** live wiki `Shell-Completion.md`, published by
`/workspaces/.planning/phases/171-stray-the-root-level-documentation-files/171-01-PLAN.md`.
The wiki is a fourth repository: `git clone https://github.com/henols/firestarter_prom.wiki.git`.

**Page opening — copy exactly, all ten live pages share it:**

```markdown
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

---

# Contributing
```

Lines 3-5 are therefore `---`, blank, `# Contributing` — the verify leg asserts exactly this shape
(see the `sed -n '3,5p' … | tr '\n' '|' | grep -qx -- '---||# Title|'` idiom below).

**Navigation — a new page owes BOTH edits in the same push or `wiki.py links` goes red**
(orphan detection + sidebar completeness):

- `_Sidebar.md`: append `- [Contributing](Contributing)` after the `Shell-Completion` bullet.
- `Home.md` `## Reference`: append `- [Contributing](Contributing) — <one clause>`.

Only the bare-stem form counts. `wiki.py:39`:
`LEGAL_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Za-z0-9][A-Za-z0-9-]*)(?:#([A-Za-z0-9_-]*))?\)")` —
an absolute `https://github.com/…/wiki/Contributing` URL in `Home.md` does **not** satisfy
reachability.

**Content:** relocated from gh#9 (three POLICY-01 statements + the four-step cross-repository
protocol) plus D-04's one security sentence. No HTML comments, no claim stamps — Phase 171 plan 01
carried the same prohibition and its verify leg asserted `! grep -q '<!--' "$WIKI/<Page>.md"`.

**Publish mechanics (Phase 171 plan 01 shape):** work in a deterministic scratch clone outside all
three repositories (`171-01` used `/tmp/gsd-171-wiki`; use `/tmp/gsd-172-wiki`), run the pre-push
oracle, then a `checkpoint:human-action` for the push, then re-verify from a **second independent
`--depth 1` clone**.

---

### 2. `.github/workflows/wiki-check.yml` (CI workflow, scheduled batch)

**Analog:** the file itself, `/workspaces/.github/workflows/wiki-check.yml`. Three changes.

**House step shape** (existing, lines ~95-108) — a `run: |` block, the tool invocation, then an
`echo "OK: …"` confirmation line:

```yaml
      - name: WIKI-05 reachability check
        run: |
          python3 meta/tools/wiki/wiki.py links --source-dir wiki-clone
          echo "OK: every wiki page is reachable from Home.md and listed in _Sidebar.md"
```

**Change A — Pitfall 1, a pure deletion.** The dispatch-mirror step passes an argument the script
rejects. `dispatch_mirror.py:157-158` declares only `--app-dir` and `--fw-dir`; the step passes
`--wiki-dir wiki-clone` → `unrecognized arguments`, rc=2, every run. Delete that one line.

**Change B — Pitfall 2, the ref resolver.** `wiki-check.yml:59,64,66`:

```
          CAND="${{ github.head_ref || github.ref_name }}"
              RESOLVED="$CAND"
              RESOLVED="beta"
```

On a `schedule` event `CAND` resolves to `main`, which exists in both sub-repos, so the
`git ls-remote --exit-code --heads` probe succeeds and both legs then run against trees that lack
`chip_database.json` and `PROTOCOLS.md`. Gate `CAND` to the empty string when it equals the meta
default branch before the probe, so scheduled runs fall through to `beta` — which is what the
step's existing (currently false) comment already claims.

**Change C — the LEGACY-01 grep leg (D-13/D-15). NO COMMENTS.** Insert after "Clone the live wiki":

```yaml
      - name: LEGACY-01 dead tracker link check
        run: |
          if grep -rInE 'henols/firestarter(_app)?/issues' meta firestarter firestarter_app wiki-clone --exclude-dir=.git --exclude-dir=.planning; then
            echo "FAIL: a page links to an issue tracker that is disabled"
            exit 1
          fi
          echo "OK: no page links to henols/firestarter/issues or henols/firestarter_app/issues"
```

Do **not** write it as `! grep … && echo …`: under the runner's `bash -e` an inverted status does
not trip errexit and a trailing `echo` resets the step's exit status to 0.

**Registration:** this file is absent from prom's default branch, so it is inert today.
`catalog-sync-check.yml` is the only registered workflow; note its `on:` block pins
`branches: [main]` with a `paths:` filter — the shape prom's registered workflows use.

---

### 3. `.github/ISSUE_TEMPLATE/*.yml` — issue forms (config, form-capture)

**No analog exists in any of the three repositories.** Use RESEARCH's validated shape verbatim as
the skeleton (top-level keys are `name, description, title, labels, projects, assignees, type, body`
with `additionalProperties: false`; `body[].type` ∈
`checkboxes|dropdown|input|markdown|textarea|upload`):

```yaml
name: Bug report
description: Something in the CLI or firmware behaves incorrectly
title: "[BUG] "
labels: ["bug", "needs:report"]
body:
  - type: input
    id: app-version
    attributes:
      label: firestarter version
      placeholder: 3.0.0b22
    validations:
      required: true
  - type: dropdown
    id: board
    attributes:
      label: Board
      options:
        - uno
        - uno328pb
        - leonardo
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
    validations:
      required: true
```

**Field oracle — D-03's four migrating bullets, verbatim from `firestarter/README.md:76-81`:**

```
- the firmware version, from `firestarter fw` or `include/version.h`
- your board: `uno`, `uno328pb` or `leonardo`
- the chip's part number and manufacturer, for hardware-specific issues
- steps to reproduce
```

These four become required fields on the bug form; they are moved, not deleted.

**Title prefixes** adopt what people already type: `[BUG] `, `[Feature Request] `.
**Labels** are drawn from prom's live set (`bug, enhancement, feature, dev-test, needs:report,
cause:*, chip:validated, fix:*, intermittent`). Template-declared `labels:` apply server-side for
any filer — unlike the `labels=` query param, which GitHub drops for filers without write access.

**Validation before it can merge** (Pitfall 7 — "it parses as YAML" is not validation):
`check-jsonschema --builtin-schema vendor.github-issue-forms .github/ISSUE_TEMPLATE/*.yml`.
The package is flagged `[SUS]` in RESEARCH — the planner must either gate its install behind a
`checkpoint:human-verify` or use the inline-assertion fallback.

---

### 4. `.github/ISSUE_TEMPLATE/dev-test-report.md` (config, routing)

**No analog.** Markdown front-matter keys: `name, about, title, labels, assignees`.

**What it must differ from** — `firestarter_app/firestarter/submit.py`, read-only:

- `build_title` (line 155-165): `f"[dev test] {chip} — {verdict} ({shorthash})"`
- `build_body` (line 227+): a `| Step | Verdict | Runs | Took | Reason |` table followed by
  ```` ```json ```` … `json.dumps(sanitized_dict, indent=2)` … ```` ``` ````
- `build_issue_url` (line 273-284): `f"https://github.com/{SUBMIT_REPO}/issues/new?{query}"`,
  `SUBMIT_REPO = "henols/firestarter_prom"` (line 62), `labels` deliberately omitted.

`devtest-triage` keys on the `[dev test]` title marker **plus** the fenced-JSON `schema_version`
block that only the CLI emits. A hand-filled report carrying the marker without parseable JSON is
picked up and then found unparseable — worse than not being picked up. **The template's `title:`
must therefore NOT be `[dev test]`** (D-06); it routes the reader to
`firestarter dev test <chip> --submit`, and its hand-fill fallback uses a different marker.
Verify leg: `! grep -q '\[dev test\]' .github/ISSUE_TEMPLATE/<devtest>.md`.

---

### 5. `.github/ISSUE_TEMPLATE/config.yml`

**No analog.** D-07 keeps blank issues on so `submit.py`'s browser prefill tier survives:

```yaml
blank_issues_enabled: true
contact_links:
  - name: Firestarter wiki
    url: https://github.com/henols/firestarter_prom/wiki
    about: Installation, chip testing, protocols and pin maps.
```

Validate with `--builtin-schema vendor.github-issue-config`.

---

### 6. `.github/CONTRIBUTING.md` ×3 (doc pointer)

**No analog** — no `CONTRIBUTING.md` exists anywhere in the three repos. The nearest existing text
is the three README sections these files replace. Each file is a **link, not a restatement**, so
POLICY-01's "stated once" holds by construction. Keep every cross-repo link mechanically greppable
(Backlog 999.9's rename sweep will re-sweep this phase).

---

### 7. README trims ×3 (doc, static link)

**Analog:** the current text of each, all three already pointing at the correct tracker. What D-03
changes is the *duplication*, not the destination.

`/workspaces/README.md:33-37` (prom, 37 lines — Phase 169 kept it deliberately short):

```markdown
## Reporting a problem

**[Open an issue here](https://github.com/henols/firestarter_prom/issues)**,
whichever part it concerns. The firmware and CLI repositories do not have their
own trackers.
```

`/workspaces/firestarter/README.md:73-81` — heading, one sentence, then the four "Include:" bullets
quoted in §3 above (those bullets **move** into the bug form).

`/workspaces/firestarter_app/README.md:104-108`:

```markdown
## Contributing

Issues and pull requests are welcome.
**[Report a problem here](https://github.com/henols/firestarter_prom/issues)** — the tracker for
all three Firestarter repositories.
```

Each trims to a single link at the canonical `Contributing` wiki page.

---

### 8. `.planning/v1.35/MIGRATION-TABLE.md` — one authored-page row

**Analog:** the `Home` row (an authored, never-migrated page) at line 12, and Phase 171's
`Shell-Completion` row at line 20:

```
| firestarter_prom | — | Home | Home | — | 167 |
| firestarter_app | firestarter_app/autocomplete.md | Shell-Completion | Shell Completion | d56424e1979edf7245cffb9ec3111c0469f5b23f | 171 |
```

**The row to add:** `| firestarter_prom | — | Contributing | Contributing | — | 172 |`

The em dash is load-bearing. `honest01_claims.py:49` sets `NO_SHA_MARKER = "—"` (U+2014) and line 93
filters `rows if row.get("Pre-deletion SHA", NO_SHA_MARKER) != NO_SHA_MARKER`, so an authored row
with `—` keeps the count at **8** and preserves Phase 171's assertion `rows with a SHA: 8`. Any
other value in that column silently changes what the provenance checker counts.

Add a prose note beneath the table recording that the page was **authored from gh#9, not migrated**
— matching the existing notes for `How-To-Edit-This-Wiki` and the two renames, per Phase 171 D-06.

---

### 9. Three GitHub rulesets (live config, REST)

**Analog:** the incumbent, `gh api /repos/henols/firestarter/rulesets/4998759`.

**Order (D-12, rulesets last; prom first as an `Integration`-acceptance canary):**

```bash
gh api /repos/henols/firestarter/rulesets/4998759 > "${PHASE_DIR}/evidence/172-ruleset-4998759-pre-delete.json"
gh api --method POST   /repos/henols/firestarter_prom/rulesets --input /tmp/ruleset.json
gh api --method DELETE /repos/henols/firestarter/rulesets/4998759
gh api --method POST   /repos/henols/firestarter/rulesets      --input /tmp/ruleset.json
gh api --method POST   /repos/henols/firestarter_app/rulesets  --input /tmp/ruleset.json
```

The pre-delete capture is not optional: D-10 is one-way and the API has no undelete.

The one canonical body, the read-back normaliser, and the full POLICY-03 verify leg are in
`172-RESEARCH.md` §"Architecture Patterns" Patterns 1-2 and §"Code Examples" — copy them literally.
Key assertions the leg makes that a naive existence check would not: exactly **one** ruleset per
repo (so the incumbent is really gone), `enforcement == active`, rule set exactly
`deletion,non_fast_forward,pull_request`, bypass list exactly `Integration:15368:always`
(catches Pitfall 3's silent-drop case), `ref_name.include == ~DEFAULT_BRANCH`.

**Anti-pattern:** asserting a ruleset merely exists. `henols/firestarter` has had a ruleset named
`Protect main` since 2025-04-22 with `"enforcement": "disabled"`.

---

### 10. Evidence files

**Analog:** `/workspaces/.planning/phases/171-stray-the-root-level-documentation-files/evidence/`
— `171-01-wiki-links-prepush.txt`, `171-01-wiki-links-postpush-freshclone.txt`,
`171-03-migration-table-parse.txt`, `171-04-gitlink-equality.txt`, `171-04-validation-sweep.txt`.

Path pattern for this phase:
`/workspaces/.planning/phases/172-policy-one-tracker-protected-main/evidence/172-NN-<slug>.txt`
(`.json` for the ruleset capture). Each is committed to meta with a path-scoped
`git commit -- <path>`.

---

## Shared Patterns

### Verify-command house style

**Source:** `171-01-PLAN.md:206`, `171-03-PLAN.md:278`, `171-04-PLAN.md:150`
**Apply to:** every `<automated>` block in this phase.

Single line. Literal `&&`. Write the evidence file, then assert on it. Canonical example
(`171-01-PLAN.md:206`):

```
WIKI=/tmp/gsd-171-wiki; EV=/workspaces/.planning/phases/171-.../evidence/171-01-wiki-links-prepush.txt; cd /workspaces && python3 tools/wiki/wiki.py links --source-dir "$WIKI" > "$EV" 2>&1; echo "exit $?" >> "$EV"; grep -q '^OK: 10 pages,' "$EV" && grep -qF 'Shell-Completion -> "Shell Completion"' "$EV" && grep -qx 'exit 0' "$EV" && sed -n '3,5p' "$WIKI/Shell-Completion.md" | tr '\n' '|' | grep -qx -- '---||# Shell Completion|' && ! grep -q '<!--' "$WIKI/Shell-Completion.md" && test "$(git -C "$WIKI" show --stat --format="" HEAD | grep -cE 'Home\.md|_Sidebar\.md|Shell-Completion\.md')" -eq 3
```

Reusable idioms in that one line, all of which Phase 172 needs:

- `> "$EV" 2>&1; echo "exit $?" >> "$EV"` then `grep -qx 'exit 0' "$EV"` — capture *and* assert rc.
- `sed -n '3,5p' … | tr '\n' '|' | grep -qx -- '---||# Title|'` — the wiki page-shape assertion,
  reusable verbatim with `# Contributing`.
- `! grep -q '<!--'` — the no-comments prohibition, made mechanical.
- `git -C "$WIKI" show --stat --format="" HEAD | grep -cE …` — the "all three files in one push"
  assertion.

Fresh-clone re-verification (`171-01-PLAN.md:287`): `V=$(mktemp -d); git clone --depth 1
https://github.com/henols/firestarter_prom.wiki.git "$V/wiki" …` — never trust the working clone.

**Counting for `wiki.py links`:** the expected string becomes `OK: 11 pages,` once `Contributing`
lands. `_Sidebar.md` is excluded from the page count by `NAV_EXCLUDED_PAGES`.

### The three `tools/wiki/` checkers — invocation, exit codes, output lines

**Apply to:** the workflow legs and every verify block that asserts on them.

| Checker | Invocation | rc=0 output line |
|---|---|---|
| `tools/wiki/wiki.py links` | `python3 tools/wiki/wiki.py links --source-dir <clone>` (`--source-dir` is `required=True`, no default) | per-page `Stem -> "Rendered Title"` lines, then `OK: N pages, all reachable from Home.md by some link path, all internal links resolve, all filenames legal, and all listed in _Sidebar.md.` |
| `tools/wiki/honest02_truth.py` | `--wiki-dir <clone> --db <app>/firestarter/data/chip_database.json --allowlist tools/wiki/claim-allowlist.json` (all three `required=True`) | `OK: leg1 stamp-present …, leg2 claims-resolve …, leg3 stamp-freshness 6 checked/0 stale.` |
| `tools/wiki/dispatch_mirror.py` | `--app-dir <app> --fw-dir <fw>` — **and nothing else** (`:157-158`) | `OK: 12 protocols compared across firmware doc, host tool and firmware.` |

Failures: `cmd_links` prints `ERROR: <message>` to stderr and returns 1; the other two return 2 on
argument/load errors.

`honest01_claims.parse_migration_table` is used by import, not CLI — Phase 171's pattern
(`171-03-PLAN.md:278`):

```
python3 -c "import sys; sys.path.insert(0,'tools/wiki'); from pathlib import Path; from honest01_claims import parse_migration_table; rows=parse_migration_table(Path('.planning/v1.35/MIGRATION-TABLE.md')); print('rows with a SHA:', len(rows)); [print(' ', r['Source path'], '->', r['Wiki page'], r['Moved in']) for r in rows]" > "$EV"
```

**Do not run `tools/wiki/selftest.sh`** — it mutates Phase 168 evidence.

**The "full suite" recipe** (fresh wiki clone + `beta` clones of both sub-repos, `dispatch_mirror.py`
without `--wiki-dir`) is in `172-RESEARCH.md` §"Validation Architecture". Never substitute the local
working trees and call it "as CI would".

### Plan frontmatter and task shape

**Source:** `171-01-PLAN.md:1-56`
**Apply to:** every plan in this phase.

Frontmatter carries `phase`, `plan`, `wave`, `depends_on`, **`commits_land_in`** (name the actual
repository — Phase 171 plan 01 used `firestarter_prom.wiki.git (live public wiki) — plus one meta
commit for this plan's evidence files under …/evidence/`), `files_modified`, `autonomous`,
`requirements`, then a `must_haves` block of `truths` / `artifacts` (with `provides` and
`min_lines`) / `key_links` (with `from`/`to`/`via`/`pattern`) / `prohibitions` (with `statement`,
`status`, `verification`).

Task types in use: `<task type="auto">`, `<task type="checkpoint:human-action" gate="blocking-human">`
(the wiki push, the ruleset calls, the PR merges), `<task type="checkpoint:human-verify" gate="blocking">`.
Each task carries `<files>`, `<verify><automated>…</automated></verify>`, `<acceptance_criteria>`.

Note: this project runs GSD with `--chain`, which **auto-approves `human-verify` and `decision`
gates** — only `human-action` genuinely stops. Anything that must not proceed unattended (the
ruleset DELETE, the three merges) needs `human-action`.

**No bare `<!--` anywhere in a PLAN.md** — it swallows the frontmatter's closing `---` and breaks the
decision-coverage gate.

### Gitlink re-pin at phase close

**Source:** `171-04-PLAN.md:150`
**Apply to:** the closing plan.

```
cd /workspaces && EV=…/evidence/172-NN-gitlink-equality.txt; ok=1; for m in firestarter firestarter_app; do rec=$(git ls-tree HEAD "$m" | awk '{print $3}'); act=$(git -C "$m" rev-parse HEAD); printf "%-16s recorded=%s actual=%s %s\n" "$m" "$rec" "$act" "$([ "$rec" = "$act" ] && echo OK || echo STALE)"; [ "$rec" = "$act" ] || ok=0; done | tee -a "$EV"; test "$ok" = 1 && …
```

### The `.github` pull requests (Pitfall 4)

**Source:** `172-RESEARCH.md` Pitfall 4. Author on the milestone branch, then per repo cut a branch
from `origin/main` and take only the wanted paths onto it:

```bash
git -C firestarter fetch origin main
git -C firestarter switch -c policy/contributing-pointer origin/main
git -C firestarter checkout gsd/v1.35-documentation-consolidation-wiki-migration -- .github/CONTRIBUTING.md
git -C firestarter commit -m "docs: point contributors at the project wiki" && git -C firestarter push -u origin HEAD
gh pr create --repo henols/firestarter --base main --head policy/contributing-pointer --title "..." --body "..."
```

**Never** `--head gsd/v1.35-…` — that PR carries 531-781 commits.

Before merging the firmware PR, read the head commit's checks
(`gh api /repos/henols/firestarter/commits/<sha>/check-runs --jq '[.check_runs[].name]'`): if
`Firestarter CI` is present the merge will cut a stable release (`build.yml` has no `.github/**` in
its `paths-ignore`; `firestarter_app/.github/workflows/release.yml:6-14` does).

---

## No Analog Found

Files with no close match anywhere in the three repositories. The planner should use
`172-RESEARCH.md`'s validated literals rather than hunt for a local precedent.

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `.github/ISSUE_TEMPLATE/bug-report.yml` | config | form-capture | No `.github/ISSUE_TEMPLATE/` has ever existed in any of the three repos. Use RESEARCH's schema-validated skeleton; field oracle is `firestarter/README.md:76-81` and real filed `[BUG]` issues. |
| `.github/ISSUE_TEMPLATE/feature-request.yml` | config | form-capture | Same. Title prefix `[Feature Request] ` is what filers already type. |
| `.github/ISSUE_TEMPLATE/dev-test-report.md` | config | routing | Same. The only reference point is `submit.py`'s machine-generated title/body, which this template must be recognisably **different** from (D-06). |
| `.github/ISSUE_TEMPLATE/config.yml` | config | chooser config | Same. RESEARCH gives the validated two-key literal. |
| `.github/CONTRIBUTING.md` ×3 | doc pointer | static link | No `CONTRIBUTING.md` or `CODE_OF_CONDUCT.md` in any repo. Nearest text is the README sections being trimmed. |
| Throwaway-repo `GITHUB_TOKEN` bypass probe (Pitfall 3) | test harness | REST | Nothing like it has been done in this project. Repository creation is an account mutation — gate as `checkpoint:human-verify`. |

---

## Metadata

**Analog search scope:** `/workspaces/.planning/phases/171-*/`, `/workspaces/.github/workflows/`,
`/workspaces/tools/wiki/`, `/workspaces/README.md`, `firestarter/README.md`,
`firestarter/.github/workflows/`, `firestarter_app/README.md`,
`firestarter_app/.github/workflows/`, `firestarter_app/firestarter/submit.py`, and the live wiki
contents as recorded in `172-RESEARCH.md`.
**Tracked-source gate:** every analog path verified with `git ls-files` in its owning repository.
No gitignored mirror paths (`.gsd/capabilities/**`) appear in this document.
**Pattern extraction date:** 2026-09-01
