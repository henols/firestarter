<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter/main/images/branding/firestarter_logo_horizontal.png" alt="Firestarter EPROM Programmer" width="400"></p>

# Releasing Firestarter

This runbook tells the maintainer how to make a release. It is written for the operator, and for a
person who must make a release when the operator is not available.

`firestarter_app` and `firestarter_fw` release independently. Each has its own version numbers,
its own schedule and its own release workflow. No release in one repository needs a release in
the other.

---

## 1. What publishes

Each sub-repository has one working branch, `main`. All work goes to `main` through pull requests.
A sub-repository can also have a maintenance branch `release/X.Y` for patches to an older line `X.Y`.
Refer to section 2.4.

| Event | What occurs |
|---|---|
| A merge or a push to `main` or `release/X.Y` | CI only. Nothing publishes. |
| A push of a tag `X.Y.ZbN` or `X.Y.ZrcN` | A pre-release. The app: a GitHub pre-release and a PyPI pre-release. The firmware: a GitHub pre-release with dev tools in each `.hex`, and the `py32f071` image. |
| A push of a tag `X.Y.Z` | A stable release, marked "Latest" only when it is the highest stable version. The app: also a PyPI release. The firmware: `.hex` files without dev tools. |
| A push or a tag in the meta repository | Nothing. |

**The tag is the version.** No file in a sub-repository holds the version, and no bot commits a
version change.

- App: `setuptools-scm` reads the tag when it builds the package.
- Firmware: `version_from_git.py` reads the tag when PlatformIO builds the image. The workflow also
  writes the tag into `include/version.h` for the CMake build of `py32f071`.

Between two tags, a build gets a development version, for example `3.2.0b2.dev5`. This is a PEP 440
pre-release, so a development build behaves as a beta build.

The release workflow (`.github/workflows/release.yml`) refuses a tag in these cases:

- The tag does not have the shape `X.Y.Z`, `X.Y.ZbN` or `X.Y.ZrcN`.
- The tag points at a commit that is not on `main` and not on `release/X.Y` of its own line. (Only the
  firmware accepts `release/X.Y` at this time.)

**A PyPI version can never be used again.** A failed app release that reached PyPI needs a new
version number. A test release is acceptable: use a spare `bN` number.

---

## 2. Make a release

The release script is in the meta repository. Run it from the meta checkout, with both
sub-repositories checked out, and with `gh` logged in. In Claude Code, the `release` skill runs
it.

```bash
S=.claude/skills/release/scripts
python3 $S/release.py <app|fw> <pre|regular|minor|major>          # dry run: checks + PLAN
python3 $S/release.py <app|fw> <type> --yes --expect <VERSION>    # publish
```

| Type | From a beta `3.2.7b3` | From a stable `3.2.6` |
|---|---|---|
| `pre` | `3.2.7b4` | `3.2.7b1` |
| `regular` (stable) | `3.2.7` | refused: a stable release needs a beta of the same commit |
| `minor` | `3.3.0b1` | `3.3.0b1` |
| `major` | `4.0.0b1` | `4.0.0b1` |

1. Merge the pull requests for the release to `main`.
2. Run the dry run. The script computes the version from the tags on origin. It checks that the
   tag is free and sorts above every release tag, that CI on the commit is green, and that the
   version is not below the binary-frame floor. For a stable release, it also checks section 2.1.
3. Read the `PLAN`. To publish, run the `publish:` line that it prints. The script pushes the tag
   on `origin/main`, follows the release run, and checks the GitHub release and PyPI. After a
   stable release, it opens a meta pull request that records the CHANGELOG entry and moves the
   gitlink.

Without the meta checkout, you can push the tag yourself. `release.yml` still checks the tag:

```bash
git fetch origin
git tag -a 3.2.0b1 -m 3.2.0b1 origin/main
git push origin 3.2.0b1
```

### 2.1 Before a stable release

- [ ] The release entry in the meta [`CHANGELOG.md`](CHANGELOG.md) is written.
- [ ] The wiki pages [Install](https://github.com/henols/firestarter/wiki/Install) and
      [Known Issues](https://github.com/henols/firestarter/wiki/Known-Issues) agree with the
      release.
- [ ] A pre-release of the same commit is green and was tested.

### 2.2 After a release

- App: in a clean virtual environment, run `pip install firestarter==<version>` (add `--pre` for a
  pre-release). Then run `firestarter --version`.
- Firmware: on a real board, run `firestarter fw -i -b <board>`, then `firestarter fw`. The two
  versions agree.

### 2.3 If a release fails

- The run failed before the release was created: delete the tag, fix the cause on `main`, and tag
  again. To delete the tag, run `git push origin :refs/tags/<version>` and `git tag -d <version>`.
- The app reached GitHub but not PyPI: run the `Publish to PyPI.org` workflow by hand, with the
  tag as input.
- The app reached PyPI: do not use the version again. Fix the cause and release the next number.

### 2.4 A patch to an older line

Use a maintenance branch when `main` has a change that must not go into the patch, for example a
wire-protocol change for the next `X.Y`.

1. Cut `release/X.Y` from the last commit of the line on `main`, before the next line merges into
   `main`. When `main` has already moved on, cut it from the last stable tag of the line instead:
   `git branch release/3.2 3.2.1`, then `git push origin release/3.2`.
2. Branch from `release/X.Y` and open pull requests to `release/X.Y`.
3. Write the CHANGELOG entry under a `## [Unreleased X.Y]` heading, directly below
   `## [Unreleased]`. Then run the release script with `--line X.Y` and the type `pre` or
   `regular`: `python3 $S/release.py <app|fw> <pre|regular> --line X.Y`. It tags
   `origin/release/X.Y`, and the version continues the tags of the line. The release follows the
   steps of section 2. The meta pull request records the CHANGELOG entry and leaves the gitlink on
   `main`. The `release.yml` of `release/X.Y` must accept a tag on that branch; the script checks
   it.
4. Merge `release/X.Y` forward into `main` through a pull request, so that `main` keeps every fix.

A patch to an older line does not become "Latest" when a higher stable version exists. A stable
CLI X.Y.z does not read `/releases/latest`. It installs the highest stable firmware X.Y.y, so a
patch to an older firmware line still reaches the CLIs on that line.

Open lines: `release/3.2` in `firestarter_fw` and `firestarter_app`, cut on 2026-10-29 from `main`
(fw `c70ce14`, app `470db9f`). `main` becomes the 3.3 line (the binary command frame and the
firmware offload) when the `perf/fw-offload` pull requests merge. Write 3.2.x fixes to
`release/3.2` and merge them forward into `main`.

---

## 3. Version numbers

PEP 440 sets the order: `3.1.0b8` < `3.1.0` < `3.1.1b1` < `3.1.1`.

- A pre-release of the next version starts after the last stable release. After `3.1.0`, the next
  pre-release is `3.1.1b1` or `3.2.0b1`, never `3.1.0b9`. `pip` and `firestarter fw` sort a
  `3.1.0b9` below `3.1.0`, so they never offer it. The release script never gives such a version.
- A firmware change that breaks the wire protocol increases `X.Y`. A 3.1 or later CLI refuses
  firmware whose `X.Y` is higher than its own. This check is the only coupling between the two
  repositories. It operates at run time, not at release time.

---

## 4. Users of an older CLI

A 2.0.x CLI asks for the newest stable firmware at
`https://api.github.com/repos/henols/firestarter_fw/releases/latest`. It offers that firmware even
when it is a newer major version. After a 2.0.x CLI installs 3.x firmware, it cannot connect to
the board. No chip is damaged. The user must upgrade the CLI.

The protection for older CLIs is the documentation:

- The wiki page [Install](https://github.com/henols/firestarter/wiki/Install) and the
  [`CHANGELOG.md`](CHANGELOG.md) say "upgrade the CLI first".
- The first line of the firmware release notes says the same.

---

## 5. The meta repository

The meta repository publishes nothing. To mark a milestone:

1. Open a pull request that moves the gitlinks to the commits that you want to record. Merge it.
2. Push a bare tag only, for example `git tag v1.44 && git push origin v1.44`.

**Never publish a GitHub Release from the meta repository.** A tag such as `v1.42` parses as the
PEP 440 version `1.42`. `Version("3.1.1") >= Version("1.42")` is true. A CLI that reads firmware
releases from the meta repository would then report "firmware up to date" for all time.
