<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter/main/images/branding/firestarter_logo_horizontal.png" alt="Firestarter EPROM Programmer" width="400"></p>

# Releasing Firestarter

This runbook tells the maintainer how to make a release. It is written for the operator, and for a
person who must make a release when the operator is not available.

The current stable release is **3.1.0** (CLI and firmware, 2026-09-26). The beta channel continues
from it (`3.1.0bN`).

---

## 1. What publishes

| Event | What occurs |
|---|---|
| A push to `beta` in `firestarter_app` | A GitHub pre-release and a PyPI pre-release. There is no path filter. |
| A push to `beta` in `firestarter_fw` | A GitHub pre-release with one `.hex` file for each board. There is no path filter. |
| A push to `main` whose version has no tag | A stable GitHub release, marked "Latest". For the app, also a PyPI release. |
| A push to `main` whose version already has a tag | Nothing. The workflow writes "Tag already exists" and stops. |
| A push to `main` that changes only ignored paths | Nothing. The workflow does not start. The ignored paths include `**.md`, `images/**`, `.github/**` and `tools/**`. |
| A push or a tag in the meta repository | Nothing. |

**A PyPI version can never be used again.** A documentation-only push to `beta` cuts a new
pre-release and uses a new PyPI version. Decide the scope of a beta push before you make it.

The stable workflows read the version from the source. They do not calculate a version:

- App: `firestarter/__init__.py` (`__version__`), read by `.github/workflows/release.yml`.
- Firmware: `include/version.h` (`#define VERSION`), read by `.github/workflows/build.yml`.

The `Protect main` ruleset is active in all three repositories. It requires a pull request for
each change to `main`. Nobody can push to `main` directly, the owner included.

---

## 2. Stable release runbook

Release the app first, then the firmware, then the meta repository. The app must be on PyPI before
the firmware release becomes "Latest". Then `pip install --upgrade firestarter` gives a CLI that
can operate the new firmware.

### 2.1 Before you start

- [ ] The release entry in the meta [`CHANGELOG.md`](CHANGELOG.md) is written.
- [ ] The wiki pages [Install](https://github.com/henols/firestarter/wiki/Install) and
      [Known Issues](https://github.com/henols/firestarter/wiki/Known-Issues) are correct for the
      release.
- [ ] The newest `beta` pre-release is green in CI, in both sub-repositories.
- [ ] You decided the version number. It has no `b` suffix.

### 2.2 The app

1. Make a branch `release/X.Y.x` from `main`.
2. Merge `origin/beta` into it. This is not a fast-forward, because `main` has commits that `beta`
   does not have. Expect conflicts in `README.md` and `firestarter/__init__.py`.
3. Set `__version__` in `firestarter/__init__.py` to the stable version.
4. Open a pull request to `main`. Make sure that `ci.yml` is green.
5. Merge the pull request with a **merge commit**. Do not squash.
6. `release.yml` makes the tag and the GitHub release, and its `pypi` job publishes to PyPI.
7. Examine the result: `pip download firestarter==X.Y.Z --no-deps` in a clean virtual environment.

A pull request can contain commits that GitHub cannot attribute to an account. Then the ruleset
asks for one approval. Before the merge, examine the state with
`gh pr view <n> --json mergeStateStatus,reviewDecision`.

### 2.3 The firmware

1. Make a branch `release/X.Y.x` from `main`. Merge `origin/beta` into it. Expect conflicts in
   `README.md` and `include/version.h`.
2. Set `VERSION` in `include/version.h` to the stable version.
3. Open a pull request to `main`. The pull-request run of `build.yml` compiles each board and makes
   sure that no stable image contains the `dev` commands. It publishes nothing. This run is the
   only dry run. Wait until it is green.
4. Merge the pull request with a merge commit.
5. `build.yml` builds the `.hex` files, makes the tag and makes the GitHub release, marked
   "Latest". **This is the step that you cannot undo.** Read section 3 first.
6. Examine the result: `gh api repos/henols/firestarter_fw/releases/latest --jq .tag_name`.

### 2.4 The meta repository

1. Open a pull request that moves both gitlinks to the new `main` commits of the sub-repositories.
   Merge it.
2. Push a bare tag only, for example `git tag v1.44 && git push origin v1.44`.

**Never publish a GitHub Release from the meta repository.** A tag such as `v1.42` parses as the
PEP 440 version `1.42`. `Version("3.1.1") >= Version("1.42")` is true. A CLI that reads firmware
releases from the meta repository would then report "firmware up to date" for all time.

### 2.5 After the release

1. In a clean virtual environment, run `pip install firestarter` and `firestarter --version`. The
   version has no `b` suffix.
2. On a real board, run `firestarter fw -i -b <board>`, then `firestarter fw`. The two versions
   agree.

---

## 3. Users of an older CLI

A 2.0.x CLI asks for the newest stable firmware at
`https://api.github.com/repos/henols/firestarter_fw/releases/latest`. It offers that firmware even
when it is a newer major version. After a 2.0.x CLI installs 3.x firmware, it cannot connect to
the board. No chip is damaged. The user must upgrade the CLI.

A 3.1 or later CLI refuses firmware whose first two version numbers are higher than its own.

The protection for older CLIs is the documentation:

- The wiki page [Install](https://github.com/henols/firestarter/wiki/Install) and the
  [`CHANGELOG.md`](CHANGELOG.md) say "upgrade the CLI first".
- The first line of the firmware release notes says the same.

---

## 4. Beta releases

Merge to `beta` in each sub-repository. Each merge publishes (refer to section 1). The firmware
compiles its version into the binary. Thus each beta push must make a new version, or the firmware
reports a wrong version.
