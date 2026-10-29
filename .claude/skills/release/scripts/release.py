#!/usr/bin/env python3
"""Release firestarter_app or firestarter_fw: compute the next tag, check, push, watch, verify.

    release.py <app|fw> <pre|regular|minor|major>                 # dry run: checks + PLAN
    release.py <app|fw> <type> --yes --expect <VERSION>           # publish
    release.py --selftest                                         # offline tests

The tag is the version (RELEASING.md section 1). A pushed tag PUBLISHES, and a PyPI
version can never be reused, so the dry run is the default and --yes needs --expect
to name the exact version the operator confirmed.

The meta repository is never tagged or released here (CLAUDE.md, Release Hazards).
Stdlib only: the skill owns its logic and does not call the sub-repos' tools/release.sh.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
META_GH = "henols/firestarter"

REPOS = {
    "app": {
        "sub": "firestarter_app",
        "gh": "henols/firestarter_app",
        "label": "CLI",            # CHANGELOG bullet prefix: - **CLI:**
        "suffix": "CLI",           # CHANGELOG heading: ## [V] - date (CLI)
        "pypi": "firestarter",
        "assets": [r"\.whl$", r"\.tar\.gz$"],
    },
    "fw": {
        "sub": "firestarter_fw",
        "gh": "henols/firestarter_fw",
        "label": "Firmware",
        "suffix": "firmware",
        "pypi": None,
        "assets": [r"^firestarter_leonardo\.hex$", r"^firestarter_uno\.hex$",
                   r"^firestarter_uno328pb\.hex$", r"^firestarter_py32f071\.hex$"],
    },
}
TYPES = ("pre", "regular", "minor", "major")

TAG_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:(b|rc)(\d+))?$")
PHASE = {"b": 0, "rc": 1, None: 2}


# --- versions -----------------------------------------------------------------

def parse(tag):
    m = TAG_RE.match(tag)
    if not m:
        return None
    x, y, z, pre, n = m.groups()
    return int(x), int(y), int(z), pre, int(n) if n else 0


def sort_key(tag):
    # PEP 440 order for this grammar: 3.1.0b8 < 3.1.0rc1 < 3.1.0 < 3.1.1b1.
    x, y, z, pre, n = parse(tag)
    return x, y, z, PHASE[pre], n


def fmt(x, y, z, pre=None, n=0):
    return f"{x}.{y}.{z}{pre}{n}" if pre else f"{x}.{y}.{z}"


def next_version(latest, kind):
    """The next tag after `latest` for one of TYPES. See SKILL.md for the table."""
    x, y, z, pre, n = parse(latest)
    if kind == "pre":
        return fmt(x, y, z, pre, n + 1) if pre else fmt(x, y, z + 1, "b", 1)
    if kind == "regular":
        return fmt(x, y, z) if pre else fmt(x, y, z + 1)
    if kind == "minor":
        return fmt(x, y + 1, 0, "b", 1)
    if kind == "major":
        return fmt(x + 1, 0, 0, "b", 1)
    raise ValueError(kind)


# --- CHANGELOG ----------------------------------------------------------------

def _unreleased_span(lines):
    start = next((i for i, l in enumerate(lines) if l.strip() == "## [Unreleased]"), None)
    if start is None:
        return None, None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def _parse_unreleased(body):
    """Split the [Unreleased] body into prose lines and (subsection, bullet-lines) items."""
    prose, items, sub, cur = [], [], None, None
    for line in body:
        if line.startswith("### "):
            sub, cur = line[4:].strip(), None
        elif line.startswith("- "):
            cur = [line]
            items.append((sub, cur))
        elif line.strip() and line[0] in " \t" and cur is not None:
            cur.append(line)
        elif line.strip():
            cur = None
            prose.append(line)
        else:
            cur = None
    return prose, items


def _emit(items):
    out, order = [], []
    for sub, _ in items:
        if sub not in order:
            order.append(sub)
    for sub in order:
        if sub:
            out += [f"### {sub}", ""]
        for s, bullet in items:
            if s == sub:
                out += bullet
        out.append("")
    return out


def changelog_items(text, label):
    """Bullets for `label` under [Unreleased]."""
    lines = text.splitlines()
    start, end = _unreleased_span(lines)
    if start is None:
        return []
    _, items = _parse_unreleased(lines[start + 1:end])
    return [b for s, b in items if b[0].startswith(f"- **{label}:**")]


def changelog_heading(text, version):
    """The `## [version]` heading line, or None."""
    return next((l for l in text.splitlines() if l.startswith(f"## [{version}]")), None)


def _merge_into(section, moved, date, suffix, version):
    """Add `moved` to an existing section that the other sub-repo released with the same number.

    Precedent: `## [3.2.2] - 2026-10-25 (CLI), 2026-10-27 (firmware)`, one section, a note
    line, and the bullets of both parts under shared ### subsections.
    """
    out = [f"{section[0]}, {date} ({suffix})"]
    body = section[1:]
    note = f"The CLI {version} and the firmware {version} are two different releases with the same number."
    first_sub = next((i for i, l in enumerate(body) if l.startswith("### ")), len(body))
    if not any(l.strip() and not l.startswith("### ") for l in body[:first_sub]):
        body = ["", note] + body
    for sub in dict.fromkeys(s for s, _ in moved):
        bullets = [l for s, b in moved if s == sub for l in b]
        head = next((i for i, l in enumerate(body) if l.strip() == f"### {sub}"), None)
        if head is None:
            while body and not body[-1].strip():
                body.pop()
            body += ["", f"### {sub}", "", *bullets, ""]
            continue
        end = next((i for i in range(head + 1, len(body)) if body[i].startswith("### ")), len(body))
        while end > head + 1 and not body[end - 1].strip():
            end -= 1
        body[end:end] = bullets
    while body and not body[-1].strip():
        body.pop()
    return out + body + [""]


def changelog_release(text, label, version, date, suffix):
    """Move the `label` bullets out of [Unreleased] into the `## [version]` section.

    A new section goes directly under [Unreleased]. When the other sub-repo already has a
    section with this number, the bullets merge into it.
    """
    lines = text.splitlines()
    start, end = _unreleased_span(lines)
    prose, items = _parse_unreleased(lines[start + 1:end])
    moved = [(s, b) for s, b in items if b[0].startswith(f"- **{label}:**")]
    kept = [(s, b) for s, b in items if not b[0].startswith(f"- **{label}:**")]
    keep_block = ([*prose, ""] if prose else []) + _emit(kept)
    rest = lines[end:]
    h = next((i for i, l in enumerate(rest) if l.startswith(f"## [{version}]")), None)
    if h is None:
        new = (lines[:start + 1] + [""] + keep_block
               + [f"## [{version}] - {date} ({suffix})", ""] + _emit(moved) + rest)
    else:
        e = next((i for i in range(h + 1, len(rest)) if rest[i].startswith("## ")), len(rest))
        merged = _merge_into(rest[h:e], moved, date, suffix, version)
        new = lines[:start + 1] + [""] + keep_block + rest[:h] + merged + rest[e:]
    return "\n".join(new) + ("\n" if text.endswith("\n") else ""), len(moved)


# --- shell --------------------------------------------------------------------

def run(cmd, cwd=None, check=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if check and p.returncode != 0:
        raise SystemExit(f"error: {' '.join(cmd)}\n{p.stderr.strip() or p.stdout.strip()}")
    return p.stdout.strip()


def gh_json(args):
    return json.loads(run(["gh", *args]) or "null")


def meta_root():
    root = Path(run(["git", "-C", str(SCRIPT_DIR), "rev-parse", "--show-toplevel"]))
    for r in REPOS.values():
        if not (root / r["sub"] / ".git").exists():
            raise SystemExit(f"error: {root / r['sub']} is not checked out "
                             "(run from the main meta checkout, not a worktree)")
    return root


def remote_tags(path):
    """{tag: commit sha} for every release-shaped tag on origin (peeled)."""
    tags = {}
    for line in run(["git", "-C", str(path), "ls-remote", "--tags", "origin"]).splitlines():
        sha, ref = line.split("\t")
        name = ref.removeprefix("refs/tags/")
        peeled = name.endswith("^{}")
        name = name.removesuffix("^{}")
        if parse(name) and (peeled or name not in tags):
            tags[name] = sha
    return tags


# --- checks -------------------------------------------------------------------

class Report:
    def __init__(self):
        self.fails = 0

    def __call__(self, level, msg):
        if level == "FAIL":
            self.fails += 1
        print(f"  {level:<4} {msg}")


def plan(name, kind, root):
    r = REPOS[name]
    path = root / r["sub"]
    run(["git", "-C", str(path), "fetch", "--quiet", "origin", "main"])
    sha = run(["git", "-C", str(path), "rev-parse", "origin/main"])
    subject = run(["git", "-C", str(path), "log", "-1", "--format=%h %s", sha])
    tags = remote_tags(path)
    latest = max(tags, key=sort_key)
    version = next_version(latest, kind)
    stable = parse(version)[3] is None
    say = Report()

    print(f"{r['sub']}: latest tag {latest} -> {version} ({'stable' if stable else 'pre-release'})")
    print(f"  target origin/main {subject}")
    since = run(["git", "-C", str(path), "log", "--first-parent", "--format=%h %s",
                 f"{tags[latest]}..{sha}"]).splitlines()
    print(f"  changes since {latest}: {len(since)} commit(s) on main")
    for line in since[:10]:
        print(f"    {line}")
    if len(since) > 10:
        print(f"    … {len(since) - 10} more")

    if not since and not stable:
        say("WARN", f"main has nothing new since {latest}; {version} would publish the same code")
    if version in tags:
        say("FAIL", f"tag {version} already exists on origin")
    elif run(["git", "-C", str(path), "tag", "--list", version]):
        say("FAIL", f"a local tag {version} exists that origin does not have; "
                    f"remove it: git -C {path} tag -d {version}")
    else:
        say("ok", f"tag {version} is free")
    if all(sort_key(version) > sort_key(t) for t in tags):
        say("ok", f"{version} sorts above every release tag")
    else:
        say("FAIL", f"{version} does not sort above {latest}")

    runs = gh_json(["run", "list", "-R", r["gh"], "--commit", sha, "--limit", "50",
                    "--json", "workflowName,headBranch,status,conclusion"]) or []
    ci = [x for x in runs if x["headBranch"] == "main"]
    bad = [x for x in ci if x["status"] != "completed"
           or x["conclusion"] not in ("success", "skipped", "neutral")]
    if not ci:
        say("WARN", "no CI run on main for this commit (build.yml skips doc-only commits)")
    elif bad:
        say("FAIL", "CI not green: " + ", ".join(
            f"{x['workflowName']} {x['conclusion'] or x['status']}" for x in bad))
    else:
        say("ok", "CI green: " + ", ".join(sorted({x["workflowName"] for x in ci})))

    if stable:
        pres = [t for t, s in tags.items() if s == sha and parse(t)[3]]
        if pres:
            say("ok", f"pre-release {max(pres, key=sort_key)} is on the same commit")
        else:
            say("FAIL", "no pre-release tag on this commit; release it as 'pre' and "
                        "test it first (RELEASING.md 2.1)")
        run(["git", "-C", str(root), "fetch", "--quiet", "origin", "main"])
        log = run(["git", "-C", str(root), "show", "origin/main:CHANGELOG.md"])
        n = len(changelog_items(log, r["label"]))
        heading = changelog_heading(log, version)
        if heading and f"({r['suffix']})" in heading:
            say("FAIL", f"CHANGELOG already records {r['label']} {version}: {heading}")
        elif n:
            say("ok", f"CHANGELOG [Unreleased] has {n} {r['label']} item(s) on meta main")
            if heading:
                say("ok", f"the items merge into the shared heading: {heading}")
        else:
            say("FAIL", f"CHANGELOG [Unreleased] on meta main has no '- **{r['label']}:**' "
                        "items; write the entry and merge it first (RELEASING.md 2.1)")
        say("ok", "after the release: a meta PR records the CHANGELOG and moves the gitlink")
    else:
        say("ok", "pre-release: no meta follow-up")

    if kind in ("minor", "major"):
        other = REPOS["fw" if name == "app" else "app"]
        o = max(remote_tags(root / other["sub"]), key=sort_key)
        x, y = parse(version)[:2]
        if parse(o)[:2] != (x, y):
            say("WARN", f"{other['sub']} is on {o}; CLI and firmware must share X.Y "
                        f"({x}.{y}) before the line goes stable")

    return version, sha, stable, say.fails


# --- publish ------------------------------------------------------------------

def watch(r, version):
    run_id = None
    for _ in range(12):
        runs = gh_json(["run", "list", "-R", r["gh"], "--workflow", "release.yml",
                        "--limit", "10", "--json", "databaseId,headBranch"]) or []
        run_id = next((x["databaseId"] for x in runs if x["headBranch"] == version), None)
        if run_id:
            break
        time.sleep(5)
    if not run_id:
        print(f"  WARN release run not found; follow it: gh run list -R {r['gh']} --workflow release.yml")
        return None
    print(f"  release run https://github.com/{r['gh']}/actions/runs/{run_id}")
    last = None
    deadline = time.time() + 45 * 60
    while time.time() < deadline:
        v = gh_json(["run", "view", str(run_id), "-R", r["gh"], "--json", "status,conclusion"])
        state = v["conclusion"] or v["status"]
        if state != last:
            print(f"  {time.strftime('%H:%M:%S')} {state}", flush=True)
            last = state
        if v["status"] == "completed":
            return v["conclusion"] == "success"
        time.sleep(20)
    print("  WARN gave up watching after 45 min; the run continues")
    return None


def verify(r, version, stable):
    ok = True
    rel = None
    for _ in range(6):
        p = subprocess.run(["gh", "release", "view", version, "-R", r["gh"],
                            "--json", "isPrerelease,isDraft,assets,url"],
                           capture_output=True, text=True, check=False)
        if p.returncode == 0:
            rel = json.loads(p.stdout)
            break
        time.sleep(10)
    if not rel:
        print(f"  FAIL no GitHub release {version}")
        return False
    names = [a["name"] for a in rel["assets"]]
    if rel["isPrerelease"] == stable or rel["isDraft"]:
        print(f"  FAIL release flags: prerelease={rel['isPrerelease']} draft={rel['isDraft']}")
        ok = False
    missing = [p for p in r["assets"] if not any(re.search(p, n) for n in names)]
    if missing:
        print(f"  FAIL assets missing: {missing} (have {names})")
        ok = False
    else:
        print(f"  ok   GitHub release {rel['url']} ({len(names)} assets)")
    if r["pypi"]:
        url = f"https://pypi.org/pypi/{r['pypi']}/{version}/json"
        for _ in range(12):
            try:
                urllib.request.urlopen(url, timeout=20).close()
                print(f"  ok   PyPI {r['pypi']}=={version}")
                break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(15)
        else:
            print(f"  FAIL PyPI has no {r['pypi']}=={version} after 3 min")
            ok = False
    return ok


def meta_followup(name, version, sha, root):
    r = REPOS[name]
    branch = f"docs/release-{name}-{version}"
    if run(["git", "-C", str(root), "ls-remote", "--heads", "origin", branch]):
        raise SystemExit(f"error: branch {branch} already exists on origin")
    run(["git", "-C", str(root), "fetch", "--quiet", "origin", "main"])
    wt = Path(tempfile.mkdtemp(prefix="release-meta-"))
    run(["git", "-C", str(root), "worktree", "add", "--quiet", "-B", branch, str(wt), "origin/main"])
    try:
        log_path = wt / "CHANGELOG.md"
        date = datetime.date.today().isoformat()
        text, n = changelog_release(log_path.read_text(), r["label"], version, date, r["suffix"])
        log_path.write_text(text)
        run(["git", "-C", str(wt), "update-index", "--cacheinfo", f"160000,{sha},{r['sub']}"])
        run(["git", "-C", str(wt), "add", "CHANGELOG.md"])
        what = "CLI" if name == "app" else "firmware"
        title = f"docs(changelog): record {what} {version}, and point the {r['sub']} gitlink at it"
        run(["git", "-C", str(wt), "commit", "--quiet", "-m", title])
        run(["git", "-C", str(wt), "push", "--quiet", "-u", "origin", branch])
        body = (f"The {what} {version} is released: https://github.com/{r['gh']}/releases/tag/{version}\n\n"
                f"- `CHANGELOG.md`: the {n} `{r['label']}` item(s) move from `[Unreleased]` to `[{version}]`.\n"
                f"- `{r['sub']}`: the gitlink moves to `{sha[:7]}`, the commit of tag `{version}`.\n\n"
                "This PR publishes nothing. Never publish a GitHub Release from this repository.")
        url = run(["gh", "pr", "create", "-R", META_GH, "--base", "main", "--head", branch,
                   "--title", title, "--body", body], cwd=wt)
        print(f"  ok   meta PR {url}")
    finally:
        run(["git", "-C", str(root), "worktree", "remove", "--force", str(wt)], check=False)
        run(["git", "-C", str(root), "branch", "-D", branch], check=False)


def publish(name, version, sha, stable, root, no_meta):
    r = REPOS[name]
    path = root / r["sub"]
    run(["git", "-C", str(path), "tag", "-a", version, "-m", version, sha])
    run(["git", "-C", str(path), "push", "--quiet", "origin", f"refs/tags/{version}"])
    print(f"  ok   pushed tag {version} -> {sha[:7]}  (PUBLISHED: from here on {version} is spent)")

    result = watch(r, version)
    if result is False:
        print("\nThe release run failed. Recovery (RELEASING.md 2.3):")
        if r["pypi"]:
            print(f"  - If PyPI has {version}: do not use {version} again; fix main and release the next number.")
            print("  - If GitHub has the release but PyPI does not: run 'Publish to PyPI.org' by hand with the tag.")
        print(f"  - If the run failed before the release was created: "
              f"git -C {path} push origin :refs/tags/{version} && git -C {path} tag -d {version}; "
              "fix main, then release again.")
        return 1
    if not verify(r, version, stable):
        return 1
    if stable and not no_meta:
        meta_followup(name, version, sha, root)
    print(f"\nDONE {r['sub']} {version}")
    return 0


# --- self-test ----------------------------------------------------------------

def selftest():
    cases = [
        ("3.2.7b3", "pre", "3.2.7b4"), ("3.2.6", "pre", "3.2.7b1"), ("3.3.0rc1", "pre", "3.3.0rc2"),
        ("3.2.7b3", "regular", "3.2.7"), ("3.2.6", "regular", "3.2.7"), ("3.3.0rc2", "regular", "3.3.0"),
        ("3.2.7b3", "minor", "3.3.0b1"), ("3.2.6", "minor", "3.3.0b1"),
        ("3.2.7b3", "major", "4.0.0b1"), ("3.9.9", "major", "4.0.0b1"),
    ]
    for latest, kind, want in cases:
        got = next_version(latest, kind)
        assert got == want, (latest, kind, got, want)
        assert sort_key(got) > sort_key(latest), (latest, got)
    order = ["3.1.0b8", "3.1.0rc1", "3.1.0", "3.1.1b1", "3.1.10", "3.10.0b1"]
    assert sorted(["3.1.10", "3.1.0", "3.10.0b1", "3.1.0rc1", "3.1.1b1", "3.1.0b8"], key=sort_key) == order
    assert parse("v1.42") is None and parse("archive/x") is None

    log = (
        "# Changelog\n\nintro\n\n## [Unreleased]\n\n### Added\n\n"
        "- **CLI:** new thing,\n  continued.\n- **Firmware:** fw thing.\n\n"
        "### Fixed\n\n- **CLI:** a fix.\n\n## [3.2.6] - 2026-10-27 (CLI)\n\n### Added\n\n- **CLI:** old.\n"
    )
    assert len(changelog_items(log, "CLI")) == 2 and len(changelog_items(log, "Firmware")) == 1
    out, n = changelog_release(log, "CLI", "3.2.7", "2026-10-29", "CLI")
    want = (
        "# Changelog\n\nintro\n\n## [Unreleased]\n\n### Added\n\n- **Firmware:** fw thing.\n\n"
        "## [3.2.7] - 2026-10-29 (CLI)\n\n### Added\n\n- **CLI:** new thing,\n  continued.\n\n"
        "### Fixed\n\n- **CLI:** a fix.\n\n## [3.2.6] - 2026-10-27 (CLI)\n\n### Added\n\n- **CLI:** old.\n"
    )
    assert n == 2 and out == want, out
    out, n = changelog_release(out, "Firmware", "3.2.3", "2026-10-29", "firmware")
    assert n == 1 and "## [Unreleased]\n\n## [3.2.3] - 2026-10-29 (firmware)\n\n### Added\n\n- **Firmware:** fw thing.\n\n## [3.2.7]" in out, out

    # Same number already released by the other sub-repo: merge, as 3.2.2 did.
    log = (
        "## [Unreleased]\n\n### Fixed\n\n- **Firmware:** fw fix.\n\n### Added\n\n- **Firmware:** fw add.\n\n"
        "## [3.2.3] - 2026-10-25 (CLI)\n\n### Fixed\n\n- **CLI:** cli fix.\n\n## [3.2.2] - x\n"
    )
    assert changelog_heading(log, "3.2.3") == "## [3.2.3] - 2026-10-25 (CLI)"
    out, n = changelog_release(log, "Firmware", "3.2.3", "2026-10-29", "firmware")
    want = (
        "## [Unreleased]\n\n## [3.2.3] - 2026-10-25 (CLI), 2026-10-29 (firmware)\n\n"
        "The CLI 3.2.3 and the firmware 3.2.3 are two different releases with the same number.\n\n"
        "### Fixed\n\n- **CLI:** cli fix.\n- **Firmware:** fw fix.\n\n"
        "### Added\n\n- **Firmware:** fw add.\n\n## [3.2.2] - x\n"
    )
    assert n == 2 and out == want, out
    print(f"selftest ok ({len(cases)} version cases, changelog rewrite)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", choices=REPOS)
    ap.add_argument("type", nargs="?", choices=TYPES)
    ap.add_argument("--yes", action="store_true", help="push the tag and publish")
    ap.add_argument("--expect", metavar="VERSION", help="with --yes: the version the operator confirmed")
    ap.add_argument("--no-meta", action="store_true", help="skip the meta CHANGELOG/gitlink PR")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.repo and a.type):
        ap.error("repo and type are required")
    if a.yes and not a.expect:
        ap.error("--yes needs --expect <VERSION> from the dry run")

    root = meta_root()
    version, sha, stable, fails = plan(a.repo, a.type, root)
    if fails:
        print(f"\nREFUSED {a.repo} {version}: {fails} check(s) failed. Nothing pushed.")
        return 1
    if not a.yes:
        kind = "stable" if stable else "pre-release"
        print(f"\nPLAN {a.repo} {version} ({kind}) on origin/main {sha[:7]}")
        print(f"  publish: python3 {Path(__file__).resolve()} {a.repo} {a.type} --yes --expect {version}")
        return 0
    if a.expect != version:
        print(f"\nREFUSED: the next version is now {version}, not the confirmed {a.expect}. Nothing pushed.")
        return 1
    return publish(a.repo, version, sha, stable, root, a.no_meta)


if __name__ == "__main__":
    sys.exit(main())
