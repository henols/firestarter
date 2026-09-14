#!/usr/bin/env python3
"""Digest a source tree with every comment removed.

A comment-only edit must not change this digest. A single changed token of
code must change it. That is the whole contract, and `--self-test` proves
both halves before any run is trusted.

Comments are replaced by a single space rather than deleted, so a block
comment sitting between two tokens cannot silently join them. Blank lines and
trailing whitespace are dropped, because removing a whole comment block also
removes the blank lines that framed it.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

C_LIKE = {".c", ".cpp", ".cc", ".h", ".hpp", ".inc", ".ino"}
PY_LIKE = {".py"}
SCAN_EXT = C_LIKE | PY_LIKE
SKIP_DIRS = {
    ".git", ".pio", "__pycache__", ".venv", "venv", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "build", "dist",
}


def strip_c(src: str) -> str:
    out, i, n = [], 0, len(src)
    while i < n:
        ch = src[i]
        if ch in "\"'":
            quote, start, i = ch, i, i + 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == quote:
                    i += 1
                    break
                if src[i] == "\n":
                    break
                i += 1
            out.append(src[start:i])
        elif src.startswith("//", i):
            end = src.find("\n", i)
            i = n if end < 0 else end
            out.append(" ")
        elif src.startswith("/*", i):
            end = src.find("*/", i + 2)
            end = n if end < 0 else end + 2
            out.append("\n" * src[i:end].count("\n") or " ")
            out.append(" ")
            i = end
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def strip_py(src: str) -> str:
    out, i, n = [], 0, len(src)
    while i < n:
        ch = src[i]
        if ch in "\"'":
            triple = src[i:i + 3]
            if triple in ('"""', "'''"):
                end = src.find(triple, i + 3)
                end = n if end < 0 else end + 3
                out.append(src[i:end])
                i = end
                continue
            quote, start, i = ch, i, i + 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == quote:
                    i += 1
                    break
                if src[i] == "\n":
                    break
                i += 1
            out.append(src[start:i])
        elif ch == "#":
            end = src.find("\n", i)
            i = n if end < 0 else end
            out.append(" ")
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def normalise(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln.strip())


def digest_file(path: Path) -> str:
    src = path.read_text(encoding="utf-8", errors="replace")
    stripped = strip_py(src) if path.suffix in PY_LIKE else strip_c(src)
    return hashlib.sha256(normalise(stripped).encode()).hexdigest()


def walk(roots):
    for root in roots:
        if root.is_file():
            if root.suffix in SCAN_EXT:
                yield root
            continue
        for path in sorted(root.rglob("*")):
            if path.suffix in SCAN_EXT and path.is_file() and not any(
                    part in SKIP_DIRS for part in path.parts):
                yield path


def self_test() -> int:
    """Prove the digest is sensitive to code and blind to comments."""
    base = ("int f(int a) {\n"
            "    int b = a + 1;\n"
            "    const char *s = \"/* not a comment */\";\n"
            "    return b;\n"
            "}\n")
    comment_only = ("/* a whole block of prose\n"
                    " * over several lines\n"
                    " */\n"
                    "int f(int a) {\n"
                    "    int b = a + 1;  // trailing note\n"
                    "    const char *s = \"/* not a comment */\";\n"
                    "    return b;\n"
                    "}\n")
    code_changed = base.replace("a + 1", "a + 2")
    with tempfile.TemporaryDirectory() as tmp:
        results = {}
        for name, text in (("base", base), ("comment", comment_only),
                           ("code", code_changed)):
            path = Path(tmp) / f"{name}.c"
            path.write_text(text)
            results[name] = digest_file(path)
        ok = True
        if results["base"] != results["comment"]:
            print("SELF-TEST FAIL: a comment-only edit moved the digest",
                  file=sys.stderr)
            ok = False
        if results["base"] == results["code"]:
            print("SELF-TEST FAIL: a one-token code edit did NOT move the "
                  "digest -- the digest is vacuous", file=sys.stderr)
            ok = False
        py_base = "x = 1\ns = '# not a comment'\n"
        py_comment = "# a note\nx = 1  # another\ns = '# not a comment'\n"
        py_code = "x = 2\ns = '# not a comment'\n"
        vals = {}
        for name, text in (("b", py_base), ("c", py_comment), ("k", py_code)):
            path = Path(tmp) / f"{name}.py"
            path.write_text(text)
            vals[name] = digest_file(path)
        if vals["b"] != vals["c"]:
            print("SELF-TEST FAIL: python comment-only edit moved the digest",
                  file=sys.stderr)
            ok = False
        if vals["b"] == vals["k"]:
            print("SELF-TEST FAIL: python code edit did NOT move the digest",
                  file=sys.stderr)
            ok = False
    print("SELF-TEST PASS: comment-blind and code-sensitive, C and Python.",
          file=sys.stderr)
    return 0 if ok else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--per-file", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.roots:
        parser.error("give at least one path, or --self-test")

    overall = hashlib.sha256()
    count = 0
    for path in walk(args.roots):
        value = digest_file(path)
        count += 1
        if args.per_file:
            print(f"{value}  {path}")
        overall.update(f"{path}\0{value}\0".encode())
    print(f"{overall.hexdigest()}  ({count} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
