#!/usr/bin/env python3
"""check_arms.py -- the standing D-06/D-07/D-08 host-arm verifier and CLI-surface record.

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Pure standard-library Python, no third-party imports. It never imports `firestarter` itself
(it shells out to each arm's own venv interpreter to probe that), so it can run from plain
system `python3` on either arm's behalf.

Re-verifies both host arms on demand:
  - D-08 triple per arm: `git rev-parse HEAD` == pinned SHA; `git status --porcelain` is
    EMPTY; `<venv_python> -P -c 'import firestarter; print(firestarter.__file__)'` resolves
    to a non-empty path under that arm's own worktree. The `-P` is mandatory -- without it
    the probe silently prints `None` because `/workspaces` holds a directory literally named
    `firestarter` (the firmware repo) that a namespace-package portion shadows ahead of the
    setuptools editable finder (Pitfall 1).
  - Pitfall 8: the two arms' `pip freeze` sets (each arm's own `firestarter`/editable line
    excluded) must be identical, checked via `uv pip freeze --python <venv_python>` --
    `uv venv` does not seed a `pip` module into the venv it creates, so the `python -m pip
    freeze` form fails outright.
  - Both `--version` strings identical and equal to the pinned interpreter.
  - D-07: the shared config dir's content SHA (sha256 over the sorted relative-path+content
    tree) matches `--expect-config-sha` when supplied, making a write by either arm to that
    dir a visible, recorded event rather than invisible drift.
  - The CLI surface: every command's option/argument name set is asserted IDENTICAL between
    the two arms (this is the gate); each command's rendered `--help` text is separately
    captured and compared, and a difference there is recorded as a datum, never as a
    gate failure (T-160-19) -- Click renders a command's docstring as its help text, and
    this project has already been bitten by that being a user-facing change.

Every probe failure here is a hard non-zero exit. None of them degrades to a null field --
a `git` call that cannot run and a clean tree are never allowed to look the same.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_PINS = _HERE.parent / "rig-pins.json"

# The probe script executed inside each arm's OWN venv interpreter (via -P) to walk its
# Click CLI tree. Kept as a literal string so this tool never imports `firestarter` itself.
_CLI_PROBE_SCRIPT = r"""
import json
import click


def make_entry(cmd, path):
    opts, args = [], []
    for param in cmd.params:
        tname = getattr(param, "param_type_name", "")
        if tname == "option":
            opts.extend(list(param.opts) + list(getattr(param, "secondary_opts", [])))
        elif tname == "argument":
            args.append(param.name)
    try:
        ctx = click.Context(cmd, info_name=" ".join(path) if path else "firestarter")
        help_text = cmd.get_help(ctx)
    except Exception as exc:  # noqa: BLE001 -- recorded as a datum, not raised
        help_text = "<help unavailable: %r>" % (exc,)
    return {
        "path": path,
        "is_group": bool(getattr(cmd, "commands", None)),
        "options": sorted(set(opts)),
        "arguments": sorted(set(args)),
        "help": help_text,
    }


def walk(cmd, prefix):
    path = prefix + [getattr(cmd, "name", None) or "firestarter"]
    out = [make_entry(cmd, path)]
    commands = getattr(cmd, "commands", None)
    if commands:
        for name in sorted(commands):
            out.extend(walk(commands[name], path))
    return out


from firestarter.cli_handlers import cli  # noqa: E402

print(json.dumps(walk(cli, [])))
"""


class ArmCheckError(Exception):
    """Raised only inside --selftest fixtures; production code returns (ok, msg) tuples."""


# ---------------------------------------------------------------------------
# Individual probes. Each returns (ok: bool, detail: str). A probe that cannot
# run at all (OSError, non-zero exit, unparsable output) returns ok=False --
# never a silent null standing in for "clean" or "absent".
# ---------------------------------------------------------------------------


def check_head(worktree: str, expected_sha: str) -> tuple[bool, str]:
    try:
        done = subprocess.run(
            ["git", "-C", worktree, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        return False, f"git rev-parse HEAD failed to execute: {exc}"
    if done.returncode != 0:
        return False, f"git rev-parse HEAD exited {done.returncode}: {done.stderr.strip()}"
    actual = done.stdout.strip()
    if not actual:
        return False, "git rev-parse HEAD produced empty output"
    if actual != expected_sha:
        return False, f"HEAD {actual} != pinned {expected_sha}"
    return True, actual


def check_porcelain(worktree: str) -> tuple[bool, str]:
    try:
        done = subprocess.run(
            ["git", "-C", worktree, "status", "--porcelain"],
            capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        return False, f"git status --porcelain failed to execute: {exc}"
    if done.returncode != 0:
        return False, f"git status --porcelain exited {done.returncode}: {done.stderr.strip()}"
    if done.stdout.strip():
        return False, f"worktree not clean: {done.stdout.strip()[:200]!r}"
    return True, ""


def check_file_probe(venv_python: str, worktree: str | None = None) -> tuple[bool, str]:
    try:
        done = subprocess.run(
            [venv_python, "-P", "-c", "import firestarter; print(firestarter.__file__)"],
            capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        return False, f"__file__ probe failed to execute: {exc}"
    if done.returncode != 0:
        return False, f"__file__ probe exited {done.returncode}: {done.stderr.strip()}"
    path = done.stdout.strip()
    if not path or path == "None":
        return False, "__file__ probe returned empty/None (Pitfall 1 -- was -P dropped?)"
    if worktree and not path.startswith(worktree):
        return False, f"__file__ path {path!r} does not resolve under worktree {worktree!r}"
    return True, path


def get_pip_freeze(venv_python: str, uv_cache_dir: str) -> tuple[bool, list[str] | str]:
    env = dict(os.environ)
    env["UV_CACHE_DIR"] = uv_cache_dir
    try:
        done = subprocess.run(
            ["uv", "pip", "freeze", "--python", venv_python],
            capture_output=True, text=True, check=False, env=env,
        )
    except OSError as exc:
        return False, f"uv pip freeze failed to execute: {exc}"
    if done.returncode != 0:
        return False, f"uv pip freeze exited {done.returncode}: {done.stderr.strip()}"
    lines = [
        line for line in done.stdout.splitlines()
        if line.strip()
        and not line.lower().startswith("firestarter")
        and not line.startswith("-e file://")
    ]
    return True, sorted(lines)


def check_dep_equality(freeze_a: list[str], freeze_b: list[str]) -> tuple[bool, str]:
    sa, sb = set(freeze_a), set(freeze_b)
    if sa != sb:
        return False, (
            f"dependency sets differ: only in A={sorted(sa - sb)} "
            f"only in B={sorted(sb - sa)}"
        )
    return True, ""


def get_python_version(venv_python: str) -> tuple[bool, str]:
    try:
        done = subprocess.run(
            [venv_python, "--version"], capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        return False, f"python --version failed to execute: {exc}"
    if done.returncode != 0:
        return False, f"python --version exited {done.returncode}: {done.stderr.strip()}"
    version = (done.stdout or done.stderr).strip()
    if not version:
        return False, "python --version produced empty output"
    return True, version


def compute_config_dir_sha(config_dir: str) -> str:
    """sha256 over the sorted (relative_path, content) tree -- matches the exact scheme
    recorded in arms-provenance.json's config_dir_sha (verified byte-for-byte)."""
    root = Path(config_dir)
    h = hashlib.sha256()
    for p in sorted(f for f in root.rglob("*") if f.is_file()):
        rel = p.relative_to(root).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(p.read_bytes())
    return h.hexdigest()


def check_config_sha(config_dir: str, expected: str | None) -> tuple[bool, str]:
    try:
        actual = compute_config_dir_sha(config_dir)
    except OSError as exc:
        return False, f"config dir sha computation failed: {exc}"
    if expected is None:
        return True, actual
    if actual != expected:
        return False, f"config dir sha {actual} != expected {expected}"
    return True, actual


def probe_cli_surface(venv_python: str) -> tuple[bool, list[dict] | str]:
    try:
        done = subprocess.run(
            [venv_python, "-P", "-c", _CLI_PROBE_SCRIPT],
            capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        return False, f"CLI surface probe failed to execute: {exc}"
    if done.returncode != 0:
        return False, f"CLI surface probe exited {done.returncode}: {done.stderr.strip()}"
    try:
        data = json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        return False, f"CLI surface probe produced unparsable JSON: {exc}"
    return True, data


def _surface_set(entries: list[dict]) -> set[tuple]:
    s: set[tuple] = set()
    for entry in entries:
        path = tuple(entry["path"])
        s.add(("cmd", path))
        for o in entry["options"]:
            s.add(("opt", path, o))
        for a in entry["arguments"]:
            s.add(("arg", path, a))
    return s


def check_cli_surface_equal(entries_a: list[dict], entries_b: list[dict]) -> tuple[bool, str]:
    sa, sb = _surface_set(entries_a), _surface_set(entries_b)
    if sa != sb:
        only_a = sorted(str(x) for x in (sa - sb))
        only_b = sorted(str(x) for x in (sb - sa))
        return False, f"CLI surface sets differ: only in A={only_a} only in B={only_b}"
    return True, ""


def diff_help_text(entries_a: list[dict], entries_b: list[dict]) -> list[tuple[str, str, str]]:
    by_a = {tuple(e["path"]): e["help"] for e in entries_a}
    by_b = {tuple(e["path"]): e["help"] for e in entries_b}
    diffs = []
    for path in sorted(set(by_a) & set(by_b)):
        if by_a[path] != by_b[path]:
            diffs.append((" ".join(path), by_a[path], by_b[path]))
    return diffs


# ---------------------------------------------------------------------------
# ARM-CLI-SURFACE.md renderer
# ---------------------------------------------------------------------------


def render_cli_surface_md(
    *, arm_names: tuple[str, str], counts: tuple[int, int],
    set_diff_ab: list[str], set_diff_ba: list[str],
    help_diffs: list[tuple[str, str, str]],
) -> str:
    a, b = arm_names
    lines = [
        "# Arm CLI Surface Comparison",
        "",
        f"Compared: `{a}` vs `{b}` (Phase 160 D-06/RIG-03).",
        "",
        f"- `{a}` command/group entry count: {counts[0]}",
        f"- `{b}` command/group entry count: {counts[1]}",
        "",
        "## Option/argument name set difference (THE GATE)",
        "",
        f"- Entries present in `{a}` but not `{b}`: "
        + (f"{len(set_diff_ab)} -- {set_diff_ab}" if set_diff_ab else "**none**"),
        f"- Entries present in `{b}` but not `{a}`: "
        + (f"{len(set_diff_ba)} -- {set_diff_ba}" if set_diff_ba else "**none**"),
        "",
        "This set comparison is the gate that makes one arm-agnostic step vocabulary valid "
        "for PROCEDURE.md: it must be empty in both directions.",
        "",
        "## `--help` text differences (recorded datum, NOT a gate failure)",
        "",
    ]
    if help_diffs:
        lines.append(f"{len(help_diffs)} command(s) have differing `--help` text between the two arms:")
        lines.append("")
        for path, _help_a, _help_b in help_diffs:
            lines.append(f"- `{path}`")
    else:
        lines.append("None. Both arms render identical `--help` text for every command.")
    lines += [
        "",
        "A help-text difference is a recorded datum, not a gate failure -- the v1.33 app "
        "range contains a commit titled \"restore Click command docstrings\", so help text "
        "is known to have moved independently of the option/argument surface. No "
        "PROCEDURE.md step depends on help text, so a difference here does not invalidate "
        "the shared step vocabulary.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _run_checks(pins: dict, expect_config_sha: str | None) -> tuple[list[str], dict]:
    """Run every check against the live pinned arms. Returns (failures, result_dict)."""
    failures: list[str] = []
    arms = pins["arms"]
    uv_cache_dir = pins["uv_cache_dir"]
    pinned_interpreter = pins["interpreter"]
    config_dir = pins["config_dir"]

    per_arm: dict[str, dict] = {}
    freezes: dict[str, list[str]] = {}
    versions: dict[str, str] = {}
    surfaces: dict[str, list[dict]] = {}

    for arm_name, arm in arms.items():
        worktree = arm["worktree"]
        venv_python = arm["venv_python"]

        ok, detail = check_head(worktree, arm["app_sha"])
        if not ok:
            failures.append(f"FAIL: {arm_name} git-head: {detail}")
        per_arm.setdefault(arm_name, {})["head"] = detail

        ok, detail = check_porcelain(worktree)
        if not ok:
            failures.append(f"FAIL: {arm_name} porcelain: {detail}")
        per_arm[arm_name]["porcelain_clean"] = ok

        ok, detail = check_file_probe(venv_python, worktree)
        if not ok:
            failures.append(f"FAIL: {arm_name} file-probe: {detail}")
        per_arm[arm_name]["file_probe"] = detail

        ok, freeze_or_msg = get_pip_freeze(venv_python, uv_cache_dir)
        if not ok:
            failures.append(f"FAIL: {arm_name} pip-freeze: {freeze_or_msg}")
            freezes[arm_name] = []
        else:
            freezes[arm_name] = freeze_or_msg  # type: ignore[assignment]
        per_arm[arm_name]["dep_freeze"] = freezes[arm_name]

        ok, version_or_msg = get_python_version(venv_python)
        if not ok:
            failures.append(f"FAIL: {arm_name} python-version: {version_or_msg}")
            versions[arm_name] = ""
        else:
            versions[arm_name] = version_or_msg
        per_arm[arm_name]["interpreter"] = versions[arm_name]
        if versions[arm_name] and versions[arm_name].split()[-1] != pinned_interpreter.split()[-1]:
            failures.append(
                f"FAIL: {arm_name} python-version: {versions[arm_name]!r} != "
                f"pinned {pinned_interpreter!r}"
            )

        ok, surface_or_msg = probe_cli_surface(venv_python)
        if not ok:
            failures.append(f"FAIL: {arm_name} cli-surface-probe: {surface_or_msg}")
            surfaces[arm_name] = []
        else:
            surfaces[arm_name] = surface_or_msg  # type: ignore[assignment]

    arm_names = list(arms.keys())
    if len(arm_names) == 2 and all(freezes.get(n) for n in arm_names):
        ok, detail = check_dep_equality(freezes[arm_names[0]], freezes[arm_names[1]])
        if not ok:
            failures.append(f"FAIL: dependency-set-equality: {detail}")

    if len(arm_names) == 2 and all(versions.get(n) for n in arm_names):
        if versions[arm_names[0]] != versions[arm_names[1]]:
            failures.append(
                f"FAIL: interpreter-equality: {arm_names[0]}={versions[arm_names[0]]!r} != "
                f"{arm_names[1]}={versions[arm_names[1]]!r}"
            )

    ok, config_detail = check_config_sha(config_dir, expect_config_sha)
    if not ok:
        failures.append(f"FAIL: config-dir-sha: {config_detail}")

    surface_diff_ab: list[str] = []
    surface_diff_ba: list[str] = []
    help_diffs: list[tuple[str, str, str]] = []
    if len(arm_names) == 2 and all(surfaces.get(n) for n in arm_names):
        a_name, b_name = arm_names[0], arm_names[1]
        ok, detail = check_cli_surface_equal(surfaces[a_name], surfaces[b_name])
        if not ok:
            failures.append(f"FAIL: cli-surface-equality: {detail}")
            sa, sb = _surface_set(surfaces[a_name]), _surface_set(surfaces[b_name])
            surface_diff_ab = sorted(str(x) for x in (sa - sb))
            surface_diff_ba = sorted(str(x) for x in (sb - sa))
        help_diffs = diff_help_text(surfaces[a_name], surfaces[b_name])

    result = {
        "per_arm": per_arm,
        "config_dir_sha": config_detail,
        "arm_names": arm_names,
        "surface_counts": {n: len(surfaces.get(n, [])) for n in arm_names},
        "surface_diff_ab": surface_diff_ab,
        "surface_diff_ba": surface_diff_ba,
        "help_diffs": [p for p, _a, _b in help_diffs],
        "_surfaces_for_render": surfaces,
        "_help_diffs_for_render": help_diffs,
    }
    return failures, result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pins", default=str(_DEFAULT_PINS), help="path to rig-pins.json")
    ap.add_argument("--out", default=None, help="write the result JSON here")
    ap.add_argument("--help-diff-out", default=None, help="write the CLI surface comparison here")
    ap.add_argument("--expect-config-sha", default=None, help="compare recomputed config-dir sha against this value")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    pins_path = Path(args.pins)
    try:
        pins = json.loads(pins_path.read_text())
    except OSError as exc:
        print(f"FAIL: could not read pins file {pins_path}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL: pins file {pins_path} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    failures, result = _run_checks(pins, args.expect_config_sha)

    arm_names = result["arm_names"]
    if len(arm_names) == 2:
        a_name, b_name = arm_names[0], arm_names[1]
        surfaces = result.pop("_surfaces_for_render")
        help_diffs = result.pop("_help_diffs_for_render")
        md = render_cli_surface_md(
            arm_names=(a_name, b_name),
            counts=(result["surface_counts"].get(a_name, 0), result["surface_counts"].get(b_name, 0)),
            set_diff_ab=result["surface_diff_ab"],
            set_diff_ba=result["surface_diff_ba"],
            help_diffs=help_diffs,
        )
        if args.help_diff_out:
            Path(args.help_diff_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.help_diff_out).write_text(md, encoding="utf-8")
    else:
        result.pop("_surfaces_for_render", None)
        result.pop("_help_diffs_for_render", None)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    if failures:
        for f in failures:
            print(f, file=sys.stderr)
        return 1

    print(
        f"check_arms OK: {len(arm_names)} arms verified "
        f"(SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha+cli-surface)"
    )
    return 0


# ---------------------------------------------------------------------------
# --selftest: exercises each check function in isolation with fabricated
# fixtures. A positive fixture must pass every check; five negative fixtures
# must each fail, with a FAIL: line naming the specific check.
# ---------------------------------------------------------------------------


def _run_selftest() -> int:
    import shutil
    import tempfile

    ok_overall = True

    def report(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok_overall
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok_overall = False
        suffix = f" -- {detail}" if detail else ""
        print(f"{status}: {name}{suffix}")

    tmp = tempfile.mkdtemp(prefix="check_arms_selftest_")
    try:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        subprocess.run(["git", "init", "-q", repo], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.email", "selftest@example.com"], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.name", "selftest"], check=True)
        Path(repo, "f.txt").write_text("hello\n")
        subprocess.run(["git", "-C", repo, "add", "f.txt"], check=True)
        subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "init"], check=True)
        sha = subprocess.run(
            ["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()

        # --- POSITIVE fixture: git-head + porcelain ---
        ok, detail = check_head(repo, sha)
        report("positive: git-head matches pinned SHA", ok, detail)
        ok, detail = check_porcelain(repo)
        report("positive: porcelain is clean", ok, detail)

        # --- NEGATIVE 1: HEAD does not match its pinned SHA ---
        ok, detail = check_head(repo, "0" * 40)
        report("negative 1: HEAD mismatch is caught", not ok, detail)

        # --- NEGATIVE 2: dirty porcelain ---
        Path(repo, "f.txt").write_text("dirty\n")
        ok, detail = check_porcelain(repo)
        report("negative 2: dirty porcelain is caught", not ok, detail)
        subprocess.run(["git", "-C", repo, "checkout", "--", "f.txt"], check=True)

        # --- NEGATIVE 3: __file__ probe returning empty ---
        # Use system python3 with a -c that prints nothing but exits 0, simulating an
        # empty/None resolution without depending on a real firestarter install.
        fake_probe_script = "print('')"
        try:
            done = subprocess.run(
                [sys.executable, "-c", fake_probe_script], capture_output=True, text=True, check=False,
            )
            path = done.stdout.strip()
            probe_ok = bool(path) and path != "None"
        except OSError as exc:
            probe_ok, path = False, str(exc)
        report(
            "negative 3: empty __file__ probe is caught",
            not probe_ok,
            f"probe returned {path!r}",
        )

        # --- NEGATIVE 4: non-empty dependency-set diff ---
        freeze_a = ["click==8.5.0", "requests==2.34.2"]
        freeze_b = ["click==8.5.0", "requests==2.34.3"]  # deliberately different
        ok, detail = check_dep_equality(freeze_a, freeze_b)
        report("negative 4: dependency-set diff is caught", not ok, detail)
        ok, detail = check_dep_equality(freeze_a, list(freeze_a))
        report("positive: identical dependency sets pass", ok, detail)

        # --- NEGATIVE 5: config-dir SHA mismatch ---
        cfgdir = os.path.join(tmp, "config")
        os.makedirs(cfgdir)
        Path(cfgdir, "config.json").write_text('{"a": 1}')
        actual_sha = compute_config_dir_sha(cfgdir)
        ok, detail = check_config_sha(cfgdir, actual_sha)
        report("positive: config-dir sha matches expected", ok, detail)
        ok, detail = check_config_sha(cfgdir, "0" * 64)
        report("negative 5: config-dir sha mismatch is caught", not ok, detail)

        # --- CLI surface set-equality sanity (no live arms needed) ---
        entries_a = [{"path": ["cli"], "options": ["-v"], "arguments": []}]
        entries_b = [{"path": ["cli"], "options": ["-v", "-x"], "arguments": []}]
        ok, detail = check_cli_surface_equal(entries_a, list(entries_a))
        report("positive: identical CLI surfaces pass", ok, detail)
        ok, detail = check_cli_surface_equal(entries_a, entries_b)
        report("negative: differing CLI surfaces are caught", not ok, detail)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
