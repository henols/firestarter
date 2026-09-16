#!/usr/bin/env python3
"""List and parse community `dev test` chip-validation issues.

Self-contained: stdlib only, plus the `gh` CLI for GitHub access. This skill
owns this parser outright — it does not import or shell out to any script in
firestarter_app or firestarter, so it keeps working if those repos move.

    devtest_issues.py list                  # open [dev test] issues + verdicts
    devtest_issues.py list --state all
    devtest_issues.py show 32               # parse one issue
    devtest_issues.py show --body-file b.txt --title "$T"   # offline
    devtest_issues.py fold                  # group issues by EPROM (dry run)
    devtest_issues.py fold --apply          # close superseded, fold the rest
    devtest_issues.py labels                # create the label taxonomy

UNTRUSTED INPUT. Every issue body is community-authored and treated as hostile:
the body is size-bounded before parsing, never `eval`/`exec`d, never shelled
out, never interpolated into a command. Every extraction fails soft (returns
None / skips) rather than raising.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

import firmware_messages

REPO = "henols/firestarter"
def _repo_root() -> str:
    """Locate the checkout from this file: <root>/.claude/skills/<s>/scripts/.

    Falls back to the current directory when the skill is installed outside a
    checkout, where an explicit flag or env override is the only sane source.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, *[os.pardir] * 4))
    return root if os.path.isdir(os.path.join(root, "firestarter_app")) else os.getcwd()


DEFAULT_DB = os.environ.get(
    "FIRESTARTER_DB",
    os.path.join(_repo_root(), "firestarter_app", "firestarter", "data",
                 "chip_database.json"),
)

# Cap before parsing — a hostile body must not be able to exhaust memory.
MAX_BODY = 1_000_000

# Same VALUE as the `NOT_REPORTED` in firestarter/diagnostic_report.py and in
# firestarter_app/tools/parse_devtest_issue.py, but defined here rather than
# imported: this skill owns its scripts and this file lives in a different
# repo, so an import would break the moment either repo moves. Keep the three
# in step by hand if the wording ever changes.
NOT_REPORTED = "not reported"

# One action-oriented clause, true whether the identity is absent because the
# reporting host never captured it or because capture failed. No schema
# ordering logic is inferred from its absence.
NOT_ATTRIBUTABLE = (
    "NOT attributable to a firmware version -- ask the reporter for a "
    "fresh dev test run on a current host build"
)

# submit.py:build_title — "[dev test] <chip> — <VERDICT> (<fingerprint>)".
# Accepts an em dash or a plain hyphen so a hand-edited title still parses.
TITLE_RE = re.compile(
    r"^\[dev test\]\s+(?P<chip>\S+)\s+[—-]\s+(?P<verdict>[A-Za-z]+)"
)
FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)

BAD = {"BAD", "FAIL"}
SOFT = {"MARGINAL", "INCONCLUSIVE"}
OK = {"OK", "NA", "SKIPPED"}

# Version strings this tool must order: host `3.0.0b27`, firmware identity
# `3.0.0b22:leonardo`, and a final release `3.0.0`. The board suffix is
# deliberately outside the capture — it is an identity, not a version.
VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:[._-]?b(\d+))?", re.IGNORECASE)

# The taxonomy this skill applies, shared with `devtest-rootcause` (which
# owns the `fix:*` pair). `labels --ensure` creates them idempotently
# so a fresh clone of the tracker gets the same set. Outcome labels are
# mechanical and applied by `fold --apply`; `cause:*` encodes a triage
# judgement no parser can derive, so it is applied by hand after the
# datasheet or root-cause work (triage SKILL.md, "Labels").
LABELS: list[tuple[str, str, str]] = [
    ("dev-test", "1d76db",
     "Community `dev test` chip-validation report"),
    ("chip:validated", "0e8a16",
     "Every applicable step passed; chip logged in the validated-EPROM ledger"),
    ("fixed:superseded", "c2e0c6",
     "Closed: a later qualifying PASS report supersedes this failure"),
    ("intermittent", "fbca04",
     "A later PASS exists but the software did not move — flaky, not fixed"),
    ("needs:report", "fef2c0",
     "Waiting on a fresh `dev test` run from the reporter"),
    ("fix:committed", "bfd4f2",
     "A fix exists in a branch or PR but no released artefact carries it yet"),
    ("fix:released", "0052cc",
     "A released firmware or host version carries the fix; re-test to close"),
    ("cause:harness", "d93f0b",
     "Defect in the `dev test` harness itself"),
    ("cause:firmware", "d93f0b",
     "Defect in the Arduino firmware"),
    ("cause:database", "d93f0b",
     "Wrong field in the generated chip database"),
    ("cause:rig", "d876e3",
     "Operator wiring, socket or voltage fault — not a software defect"),
]


def gh(args: list[str]) -> str:
    """Run gh with a fixed argv list. Never uses a shell."""
    try:
        r = subprocess.run(
            ["gh", *args], capture_output=True, text=True, timeout=120, check=False
        )
    except FileNotFoundError:
        sys.exit("error: `gh` not found — install the GitHub CLI")
    except subprocess.TimeoutExpired:
        sys.exit("error: `gh` timed out")
    if r.returncode != 0:
        sys.exit(f"error: gh {' '.join(args)} failed: {r.stderr.strip()[:400]}")
    return r.stdout


def parse_title(title: str) -> dict | None:
    m = TITLE_RE.match((title or "").strip())
    return m.groupdict() if m else None


def extract_report(body: str) -> dict | None:
    """Return the embedded diagnostic report.

    Detection requires a fenced block whose parsed object carries
    `schema_version` — accepted by PRESENCE, not by exact value, so a schema
    bump does not need a code change here. Defensive against unrelated fenced
    blocks elsewhere in the issue: every block is tried, the first qualifying
    one wins.
    """
    if not body:
        return None
    for block in FENCE_RE.findall(body[:MAX_BODY]):
        try:
            obj = json.loads(block)
        except (json.JSONDecodeError, ValueError, RecursionError):
            continue
        if isinstance(obj, dict) and "schema_version" in obj:
            return obj
    return None


def is_devtest(title: str, body: str) -> bool:
    """Both markers required: the title marker AND a schema_version report."""
    return parse_title(title) is not None and extract_report(body) is not None


def fingerprint(report: dict | None, body: str) -> str:
    if isinstance(report, dict):
        fp = report.get("dedup_fingerprint")
        if isinstance(fp, str) and re.fullmatch(r"[0-9a-f]{4,32}", fp):
            return fp
    m = re.search(r'"dedup_fingerprint"\s*:\s*"([0-9a-f]{4,32})"', body or "")
    return m.group(1) if m else "-"


def cmd_list(args: argparse.Namespace) -> int:
    raw = gh([
        "issue", "list", "--repo", args.repo, "--state", args.state,
        "--limit", str(args.limit), "--json", "number,title,body",
    ])
    try:
        issues = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit("error: gh returned unparseable JSON")

    rows = []
    for i in issues:
        t = parse_title(i.get("title", ""))
        if not t:
            continue
        body = i.get("body") or ""
        rep = extract_report(body)
        rows.append((
            i.get("number", 0), t["verdict"].upper(), t["chip"],
            fingerprint(rep, body), "" if rep else "  (no JSON report)",
        ))

    rows.sort(key=lambda r: -r[0])
    for n, verdict, chip, fp, note in rows:
        print(f"#{n:<5}{verdict:<15}{chip:<15}{fp}{note}")
    if not rows:
        print("no [dev test] issues found")
    return 0


def load_alias_map(db_path: str) -> dict[str, str]:
    """chip token -> canonical EPROM key, from the chip database if readable.

    Two issues can name one EPROM differently (`w27c020` / `w27e020` are the
    same DB entry). Without this, folding is only string-deep. Degrades to {}
    when the database is absent — the caller then falls back to normalisation.
    Reads the JSON as DATA; imports nothing.
    """
    try:
        with open(db_path, encoding="utf-8") as f:
            db = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[str, str] = {}
    for mfg, chips in (db.items() if isinstance(db, dict) else []):
        if not isinstance(chips, list):
            continue
        for entry in chips:
            if not isinstance(entry, dict):
                continue
            pn = entry.get("part_number", "")
            key = f"{mfg}/{pn.split(',')[0].strip()}"
            for tok in pn.split(","):
                norm = re.sub(r"[^a-z0-9]", "", tok.strip().lower())
                if norm:
                    out.setdefault(norm, key)
    return out


def eprom_key(chip: str, aliases: dict[str, str]) -> str:
    norm = re.sub(r"[^a-z0-9]", "", chip.lower())
    return aliases.get(norm, norm)


def _summarize(issue: dict) -> dict | None:
    t = parse_title(issue.get("title", ""))
    if not t:
        return None
    body = issue.get("body") or ""
    rep = extract_report(body) or {}
    steps = rep.get("steps") or []
    failing = [str(s.get("op")) for s in steps if isinstance(s, dict)
               and str(s.get("verdict", "")).upper() in BAD | SOFT]
    auto = rep.get("auto_capture") or {}
    # op -> verdict, so the supersede test can ask whether a specific step
    # came back OK rather than trusting the title's overall verdict.
    step_verdicts = {str(s.get("op")): str(s.get("verdict", "")).upper()
                     for s in steps if isinstance(s, dict)}
    return {
        "number": issue.get("number", 0),
        "chip": t["chip"],
        "verdict": t["verdict"].upper(),
        "fp": fingerprint(rep, body),
        "host": auto.get("host_version") or "?",
        "fw": auto.get("fw_board_identity") or "",
        "generated": (rep.get("generated") or "?")[:10],
        "generated_full": rep.get("generated") or "",
        "steps": step_verdicts,
        "failing": failing,
    }


def version_key(raw: str) -> tuple[int, int, int, float] | None:
    """Sortable key for `3.0.0b27`, `3.0.0b22:leonardo` or `3.0.0`.

    A final release outranks every prerelease of the same triple, so the
    prerelease slot is +inf when absent. Returns None when nothing parses;
    callers must treat that as NOT COMPARABLE, never as equal.
    """
    if not raw:
        return None
    m = VERSION_RE.search(str(raw))
    if not m:
        return None
    major, minor, patch, pre = m.groups()
    return (int(major), int(minor), int(patch),
            float(pre) if pre is not None else float("inf"))


def supersedes(fail: dict, ok: dict) -> tuple[bool, list[str]]:
    """Does PASS report `ok` supersede failing report `fail`?

    Three legs, all required. Returns (False, why) naming the leg that
    blocked, so a dry run can explain itself. Anything short of all three
    leaves the failure OPEN — a close is outward-facing and must not rest on
    a guess.
    """
    notes: list[str] = []

    # Leg 1 — later by the report's own `generated` stamp, never by issue
    # number or creation date: an old run can be filed late.
    if not (ok["generated_full"] and fail["generated_full"]
            and ok["generated_full"] > fail["generated_full"]):
        return False, ["not later than the failure by report timestamp"]

    # Leg 2 — the software must have moved forward. A later PASS on the same
    # or older build is intermittency, which is a different (worse) finding.
    fh, oh = version_key(fail["host"]), version_key(ok["host"])
    if fh is None or oh is None:
        return False, ["host version not comparable"]
    if oh < fh:
        return False, [f"ran an OLDER host ({ok['host']} < {fail['host']}) "
                       "— intermittent, not fixed"]
    ff, of = version_key(fail["fw"]), version_key(ok["fw"])
    if ff is not None and of is not None and of < ff:
        return False, [f"ran OLDER firmware ({ok['fw']} < {fail['fw']}) "
                       "— intermittent, not fixed"]
    advanced = oh > fh or (ff is not None and of is not None and of > ff)
    if not advanced:
        return False, ["same host and firmware as the failure "
                       "— intermittent, not fixed"]
    if ff is None or of is None:
        notes.append("firmware not comparable on both sides — the close rests "
                     "on host-version evidence alone")

    # Leg 3 — every step that failed must come back OK. NA does NOT count: it
    # means the step stopped running, not that it started passing. Closing on
    # an NA would hide a live defect behind a green title.
    for op in fail["failing"]:
        got = ok["steps"].get(op)
        if got != "OK":
            return False, [f"step `{op}` is {got or 'absent'} in the PASS, "
                           "not OK — the failing step did not pass"]

    return True, notes


def ensure_labels(repo: str) -> int:
    """Create this skill's label taxonomy. Idempotent — `--force` updates an
    existing label's colour and description rather than failing."""
    for name, colour, desc in LABELS:
        gh(["label", "create", name, "--repo", repo, "--color", colour,
            "--description", desc, "--force"])
        print(f"  {name}")
    return 0


def add_labels(repo: str, number: int, *names: str) -> None:
    """Apply labels to one issue. Names come from LABELS only — never from
    issue text, which is untrusted."""
    known = {n for n, _, _ in LABELS}
    wanted = [n for n in names if n in known]
    if wanted:
        gh(["issue", "edit", str(number), "--repo", repo,
            "--add-label", ",".join(wanted)])


def cmd_labels(args: argparse.Namespace) -> int:
    print(f"ensuring {len(LABELS)} labels on {args.repo}:")
    return ensure_labels(args.repo)


def cmd_fold(args: argparse.Namespace) -> int:
    """Group open issues by EPROM, close the failures a later PASS supersedes,
    and fold what is left of each group into one canonical issue."""
    raw = gh([
        "issue", "list", "--repo", args.repo, "--state", "open",
        "--limit", str(args.limit), "--json", "number,title,body",
    ])
    try:
        issues = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit("error: gh returned unparseable JSON")

    aliases = load_alias_map(args.db)
    if not aliases:
        print("note: chip database not readable — grouping by chip NAME only; "
              "alias-different names for one EPROM will not group\n", file=sys.stderr)

    groups: dict[str, list[dict]] = {}
    for i in issues:
        s = _summarize(i)
        if s:
            groups.setdefault(eprom_key(s["chip"], aliases), []).append(s)

    multi = {k: sorted(v, key=lambda r: r["number"])
             for k, v in groups.items() if len(v) > 1}
    if not multi:
        print("nothing to fold — every open EPROM has a single issue")
        return 0

    planned = []
    for key, members in sorted(multi.items()):
        passes = [m for m in members if m["verdict"] == "PASS"]
        actionable = [m for m in members if m["verdict"] != "PASS"]

        names = sorted({m["chip"] for m in members})
        print(f"\n{key}   ({', '.join(names)})")

        if not actionable:
            print("  ALL PASS — do not fold. Close each and log the chip "
                  "(triage §4); a fold would bury a clean result.")
            continue

        # Supersede pass, before any folding: a failure a later qualifying
        # PASS has answered is closed against that PASS, not folded into a
        # canonical that no longer describes anything live.
        superseded: dict[int, tuple[dict, list[str]]] = {}
        blocked: dict[int, list[str]] = {}
        for f in actionable:
            best: tuple[dict, list[str]] | None = None
            why: list[str] = []
            for p in passes:
                ok, notes = supersedes(f, p)
                if ok:
                    if best is None or p["generated_full"] > best[0]["generated_full"]:
                        best = (p, notes)
                else:
                    why.extend(f"#{p['number']}: {r}" for r in notes)
            if best:
                superseded[f["number"]] = best
            elif why:
                blocked[f["number"]] = why

        remaining = [m for m in actionable if m["number"] not in superseded]
        canonical = remaining[0] if remaining else None
        if args.canonical:
            match = [m for m in remaining if m["number"] == args.canonical]
            if match:
                canonical = match[0]
        dupes = [m for m in remaining
                 if canonical and m["number"] != canonical["number"]]

        if canonical:
            print(f"  canonical #{canonical['number']}"
                  + (f"   fold in: {', '.join('#' + str(m['number']) for m in dupes)}"
                     if dupes else "   (nothing left to fold in)"))
        else:
            print("  every failure superseded — no canonical needed")

        for m in members:
            same = [o["number"] for o in members
                    if o["fp"] == m["fp"] and o["number"] != m["number"]
                    and m["fp"] != "-"]
            tags = []
            if same:
                tags.append("same fingerprint as "
                            + ", ".join(f"#{n}" for n in same))
            if m["verdict"] == "PASS":
                tags.append("PASS — closes via §4 as chip:validated; fold "
                            "never closes it as a duplicate")
            elif m["number"] in superseded:
                p, notes = superseded[m["number"]]
                tags.append(f"SUPERSEDED by #{p['number']} — CLOSE as "
                            "fixed:superseded"
                            + (f" ({'; '.join(notes)})" if notes else ""))
            elif m["number"] in blocked:
                tags.append("later PASS does NOT supersede — "
                            + "; ".join(blocked[m["number"]])
                            + " — stays open, label intermittent")
            mark = "*" if canonical and m["number"] == canonical["number"] else " "
            print(f"   {mark}#{m['number']:<4} {m['verdict']:<13}{m['fp']}  "
                  f"host {m['host']}  fw {m['fw'] or NOT_REPORTED}  "
                  f"{m['generated']}  "
                  f"failing: {', '.join(m['failing']) or '-'}"
                  + (f"   [{'; '.join(tags)}]" if tags else ""))
        if passes:
            print("   note: PASS issues above are NOT touched by fold — close "
                  "each via §4 and log the chip.")
        planned.append((key, names, canonical, dupes, members,
                        superseded, blocked))

    if not planned:
        return 0
    if not args.apply:
        n_sup = sum(len(p[5]) for p in planned)
        print(f"\nDRY RUN — {len(planned)} group(s); {n_sup} failure(s) would "
              "close as superseded. Re-run with --apply to comment, label and "
              "close.")
        return 0

    ensure_labels(args.repo)
    for key, names, canonical, dupes, members, superseded, blocked in planned:
        # 1. Failures a later PASS has answered: close against that PASS.
        for f in members:
            hit = superseded.get(f["number"])
            if not hit:
                continue
            p, notes = hit
            caveat = ("\n\n" + "\n".join(f"- Caveat: {n}" for n in notes)
                      if notes else "")
            body = (
                f"### Closed — superseded by a later PASS (#{p['number']})\n\n"
                f"This failure is answered by a later `dev test` report on the "
                f"same database entry, and the close is mechanical against "
                f"three tests:\n\n"
                "| Test | This issue | #%d | " % p["number"] + "Result |\n"
                "|---|---|---|---|\n"
                f"| Report is later | {f['generated']} | {p['generated']} | later |\n"
                f"| Software moved forward | host {f['host']}, fw "
                f"{f['fw'] or NOT_REPORTED} | host {p['host']}, fw "
                f"{p['fw'] or NOT_REPORTED} | advanced |\n"
                f"| Failing step now OK | {', '.join(f['failing']) or '—'} | "
                f"all OK | passed |\n\n"
                "A PASS whose software had not moved, or that reported the "
                "failing step `NA` rather than `OK`, would NOT have closed "
                "this — that is intermittency or a step that stopped running, "
                f"not a fix.{caveat}\n\n"
                f"If {f['chip']} fails again on a current build, please open a "
                "fresh `dev test` report rather than reopening this one."
            )
            gh(["issue", "comment", str(f["number"]), "--repo", args.repo,
                "--body", body])
            add_labels(args.repo, f["number"], "dev-test", "fixed:superseded")
            gh(["issue", "close", str(f["number"]), "--repo", args.repo,
                "--reason", "completed"])
            print(f"closed #{f['number']} — superseded by #{p['number']}")

        # 2. Whatever failure survives: fold the rest of the group into it.
        if canonical:
            add_labels(args.repo, canonical["number"], "dev-test")
            if canonical["number"] in blocked:
                add_labels(args.repo, canonical["number"], "intermittent")
        if canonical and dupes:
            live = [m for m in members
                    if m["verdict"] != "PASS" and m["number"] not in superseded]
            rows = "\n".join(
                f"| #{m['number']} | {m['verdict']} | `{m['fp']}` | {m['host']} | "
                f"{m['fw'] or NOT_REPORTED} | {m['generated']} | "
                f"{', '.join(m['failing']) or '—'} |"
                for m in live
            )
            summary = (
                f"### Consolidated reports for {' / '.join(names)}\n\n"
                f"{len(live)} open `dev test` reports describe this EPROM. "
                f"Folding them here so it is triaged once.\n\n"
                "| Issue | Verdict | Fingerprint | Host | Firmware | Report date "
                "| Failing steps |\n"
                "|---|---|---|---|---|---|---|\n" + rows + "\n\n"
                "Issues sharing a fingerprint are the same failure re-reported.\n"
            )
            gh(["issue", "comment", str(canonical["number"]), "--repo",
                args.repo, "--body", summary])
            print(f"commented on #{canonical['number']}")
            for m in dupes:
                gh(["issue", "close", str(m["number"]), "--repo", args.repo,
                    "--comment",
                    f"Folded into #{canonical['number']} — same EPROM "
                    f"({m['chip']}). This report is preserved in the "
                    f"consolidated table there. Continue the discussion on "
                    f"#{canonical['number']}."])
                add_labels(args.repo, m["number"], "dev-test")
                print(f"  closed #{m['number']} -> #{canonical['number']}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    if args.number is not None:
        title = gh(["issue", "view", str(args.number), "--repo", args.repo,
                    "--json", "title", "-q", ".title"]).strip()
        body = gh(["issue", "view", str(args.number), "--repo", args.repo,
                   "--json", "body", "-q", ".body"])
    else:
        if not args.body_file:
            sys.exit("error: pass an issue NUMBER, or --body-file with --title")
        title = args.title or ""
        try:
            with open(args.body_file, encoding="utf-8", errors="replace") as f:
                body = f.read(MAX_BODY + 1)
        except OSError as exc:
            sys.exit(f"error: cannot read body file: {exc}")

    if len(body) > MAX_BODY:
        print(f"warning: body over {MAX_BODY} bytes — truncated for parsing",
              file=sys.stderr)
        body = body[:MAX_BODY]

    t = parse_title(title)
    report = extract_report(body)
    if not t or not report:
        print("NOT a parseable `dev test` issue "
              f"(title marker: {'yes' if t else 'no'}, "
              f"JSON report: {'yes' if report else 'no'})")
        return 1

    auto = report.get("auto_capture") or {}
    steps = report.get("steps") or []
    volt = report.get("voltage") or {}
    dbd = report.get("db_diff") or {}

    print(f"#{args.number if args.number is not None else '?'}  "
          f"{t['chip']}  —  {t['verdict'].upper()}")
    print(f"  schema      {report.get('schema_version')}   "
          f"generated {report.get('generated')}")

    # Two-clause `is None or == ""`, never `or`-coalescing: an `or` also
    # fires on "", which would hide an empty-string transport fault.
    host_version = auto.get("host_version")
    host_version_cell = (
        NOT_REPORTED if host_version is None or host_version == ""
        else host_version
    )
    hw_revision = auto.get("hw_revision")
    hw_revision_cell = (
        NOT_REPORTED if hw_revision is None or hw_revision == ""
        else hw_revision
    )
    print(f"  host        {host_version_cell}   hw {hw_revision_cell}")

    # `hw_revision` above is deliberately not part of this identity: it is a
    # coarse silkscreen bucket that cannot tell a Rev 2.2 from a Rev 2.0 or a
    # modified Rev 0, so it is never treated as attribution evidence.
    fw_board_identity = auto.get("fw_board_identity")
    identity_absent = fw_board_identity is None or fw_board_identity == ""
    firmware_cell = (
        f"{NOT_REPORTED} -- {NOT_ATTRIBUTABLE}" if identity_absent
        else fw_board_identity
    )
    print(f"  firmware    {firmware_cell}")

    print(f"  protocol    {auto.get('protocol')}   chip {auto.get('chip')}")
    cid_e, cid_a = auto.get("chip_id_expected"), auto.get("chip_id_actual")
    if cid_e is not None or cid_a is not None:
        exp = f"0x{cid_e:X}" if isinstance(cid_e, int) else str(cid_e)
        act = f"0x{cid_a:X}" if isinstance(cid_a, int) else str(cid_a)
        print(f"  chip id     expected {exp}  actual {act}")
    print(f"  fingerprint {fingerprint(report, body)}")

    print(f"\n  {'step':<12} {'verdict':<10} {'error':<28} reason")
    failing, soft = [], []
    for s in steps:
        if not isinstance(s, dict):
            continue
        op = str(s.get("op", "?"))
        v = str(s.get("verdict", "?"))
        reason = str(s.get("reason") or "")[:90]
        err = firmware_messages.resolve_error(
            s.get("error_code"), s.get("error_name")
        )
        print(f"  {op:<12} {v:<10} {err:<28} {reason}")
        if v.upper() in BAD:
            failing.append(op)
        elif v.upper() in SOFT:
            soft.append(op)

    if volt:
        print(f"\n  voltage     vpp {volt.get('vpp_before_mv')} -> "
              f"{volt.get('vpp_after_mv')} mV   "
              f"vpe {volt.get('vpe_before_mv')} -> {volt.get('vpe_after_mv')} mV")
    if dbd:
        print(f"  db_diff     status={dbd.get('current_support_status')}  "
              f"ladder={dbd.get('ladder_state')}")

    print()
    if failing:
        print(f"  ROUTE: FAIL — datasheet cross-check needed. Failing: "
              f"{', '.join(failing)}")
    elif soft:
        print(f"  ROUTE: MARGINAL — datasheet cross-check needed. Marginal: "
              f"{', '.join(soft)}")
    else:
        print("  ROUTE: PASS — every applicable step OK/NA/SKIPPED. "
              "Close the issue and log the chip.")
    print("  NA means the step does not apply to this family — never report it "
          "as a failure.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--repo", default=REPO, help=f"default {REPO}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list [dev test] issues with verdicts")
    p.add_argument("--state", default="open", choices=["open", "closed", "all"])
    p.add_argument("--limit", type=int, default=200)
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser(
        "fold", help="group open issues by EPROM and fold each group into one")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--db", default=DEFAULT_DB,
                   help="chip database, read as data for alias-aware grouping")
    p.add_argument("--canonical", type=int,
                   help="force this issue number as the canonical one")
    p.add_argument("--apply", action="store_true",
                   help="actually comment and close (default is a dry run)")
    p.set_defaults(fn=cmd_fold)

    p = sub.add_parser(
        "labels", help="create this skill's label taxonomy (idempotent)")
    p.set_defaults(fn=cmd_labels)

    p = sub.add_parser("show", help="parse one issue and route it")
    p.add_argument("number", nargs="?", type=int)
    p.add_argument("--title", help="issue title (with --body-file)")
    p.add_argument("--body-file", help="issue body on disk (offline mode)")
    p.set_defaults(fn=cmd_show)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
