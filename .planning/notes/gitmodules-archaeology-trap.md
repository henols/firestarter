# The `.gitmodules` archaeology trap

**Date:** 2026-09-14
**Raised during:** Phase 193 (GATE-03). This note promotes `.planning/notes/999.9-repo-rename-impact-analysis.md`'s § "The `.gitmodules` archaeology trap" from a reasoned description into an executed, dedicated note.
**Status:** The trap cannot be solved. It is only documented and worked around. Both workarounds below were executed at the published `v1.35` tag on 2026-09-14. Their transcripts are committed under `${phase_dir}/evidence/`.
**Method:** Direct execution in disposable clones (`mktemp -d`), on 2026-09-14. Every figure below is reproducible from the command noted beside it, and from the cited transcript.

## The trap

`.gitmodules` records a submodule URL per commit. Fixing the URL on `beta` and `main` today does not change what any past commit records. Checking out an old tag resurrects the old URL from that commit. So does bisecting firmware history, or reading any pre-rename commit. This project does a great deal of archaeology, so the trap will be met. The concrete ref a reader will actually hit is the published `v1.35` tag (`6e84030b…`, 2026-09-02). Its `.gitmodules` still declares `url = git@github.com:henols/firestarter.git` for the firmware submodule. It stays that way permanently, because tags do not move.

**The trap does not bite today.** The old firmware slug `henols/firestarter` still redirects to `henols/firestarter_fw`. `gh api repos/henols/firestarter` and `gh api repos/henols/firestarter_fw` both return the same `id: 810276812`. A plain `git submodule update --init` at `v1.35`, with no override set at all, succeeds today. It fetches through the redirect (`evidence/193-gate-03-fresh-clone.txt`, READING 2). The workarounds below exist for the state that arrives once the freed slug `henols/firestarter` is claimed for the meta repository. That state has not arrived.

## Workaround A — an existing clone

Use this when a clone already exists in the maintained, post-rename state most clones of this repository carry. It then travels back to a pre-rename ref — a checkout, a bisect.

1. Set the override, if it is not already set: `git config submodule.firestarter.url git@github.com:henols/firestarter_fw.git`. Consequence: `.git/config` now carries an explicit `submodule.firestarter.url`. That value stays fixed no matter what `.gitmodules` says at any given commit.
2. Check out the pre-rename ref: `git checkout v1.35` (or any commit before `RENAME-02`). Consequence: the working tree's `.gitmodules` now reads the OLD slug — `git@github.com:henols/firestarter.git`. A checkout does not touch `.git/config`. Only `.gitmodules` moved.
3. `git submodule update --init firestarter`. Consequence: the fetch follows `.git/config`, not the checked-out ref's `.gitmodules`.

The mechanism: **where `.gitmodules` and `.git/config` disagree, `.git/config` wins.** Step 2 is what forces that disagreement, and it is the entire workaround. **Where the two agree, nothing observable distinguishes them, and the override is invisible.** A reader who sees `submodule.firestarter.url` and `.gitmodules`'s `url =` line naming the same repository cannot tell which one is in force. Agreement alone does not answer that question. `evidence/193-gate-03-existing-clone.txt` READING 1 captures exactly that invisible-agreement state — both name `firestarter_fw`. READING 2 then forces the divergence by checking out `v1.35`. `.gitmodules` reverts to the old slug. The override does not move. The subsequent `submodule update` follows the override. READING 2 is the reading that proves the override was doing anything at all.

Cite: `evidence/193-gate-03-existing-clone.txt` — READING 1 for the agreement state, READING 2 for the forced divergence and its resolution.

## Workaround B — a fresh clone at a pre-rename ref

Use this when no clone exists yet and the destination is a pre-rename ref from the start.

1. `git clone --no-recurse-submodules https://github.com/henols/firestarter_prom.git <dir>`. Consequence: submodule paths exist as empty placeholder directories. Nothing is fetched into them yet.
2. `git checkout v1.35`. Consequence: `.gitmodules` in the working tree now names the old slug. No submodule has been touched yet, so there is nothing to check against.
3. `git config submodule.firestarter.url git@github.com:henols/firestarter_fw.git`. Consequence: `.git/config` now carries the override. Neither `submodule init` nor `submodule update` has run yet.
4. `git submodule update --init --depth 1 firestarter`. Consequence: the child is cloned from `firestarter_fw`, not from what `.gitmodules` names at this ref.

**The order is load-bearing.** `git submodule init` preserves an existing `submodule.<name>.url` in `.git/config` rather than re-copying it from `.gitmodules`. So the override must be set (step 3) before `submodule update --init` runs (step 4). Setting it afterward would already have cloned from the wrong URL. There is no "fix it after" once the fetch has happened. `evidence/193-gate-03-fresh-clone.txt` READING 1 proves the non-clobbering half directly. `git submodule init firestarter` runs between the override and the update, and the override survives it unchanged.

The ref to demonstrate against is the published `v1.35` tag, not a commit on a milestone branch. The commit that actually landed the URL repoint, `5aba9dbc…`, has a parent (`9ccf0414…`) whose `.gitmodules` still names the old slug. That parent commit lives only on the unpushed milestone branch `gsd/v1.38-repository-rename-activated-2026-09-13` (GSD pushes at ship time, never ad hoc). `git cat-file -t` on it fails in a fresh clone of `origin`. It is unreachable there. A procedure written against an unreachable commit cannot be followed by the person who needs it. `v1.35` is published, immutable, and reachable by anyone with network access to GitHub. It is the very ref `.planning/notes/999.9-repo-rename-impact-analysis.md` § "The `.gitmodules` archaeology trap" names when it describes checking out an old tag.

Cite: `evidence/193-gate-03-fresh-clone.txt` — READING 1.

## A one-shot variant, supplementary

For a single archaeology checkout, a non-persisting idiom exists that skips `.git/config` entirely:

```
git -c submodule.firestarter.url=git@github.com:henols/firestarter_fw.git \
    submodule update --init --depth 1 firestarter
```

Verified clean, in a fresh clone at `v1.35` with no prior override. It checks out the child from `firestarter_fw`. It leaves `git config --get submodule.firestarter.url` unset afterward — the override lives only in that one command's environment. This is a **convenience** for a single checkout, offered **beside** Workaround A and Workaround B, not a replacement for either. Those two are the workarounds `.planning/notes/999.9-repo-rename-impact-analysis.md` prescribes and the ones this phase actually executed and banked as transcripts.
