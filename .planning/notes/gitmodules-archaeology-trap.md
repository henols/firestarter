# The `.gitmodules` archaeology trap

**Date:** 2026-09-14
**Raised during:** Phase 193 (GATE-03). This note promotes `.planning/notes/999.9-repo-rename-impact-analysis.md`'s § "The `.gitmodules` archaeology trap" from a reasoned description into an executed, dedicated note.
**Status:** The trap cannot be solved. It is only documented and worked around. Both workarounds below were executed at the published `v1.35` tag on 2026-09-14. Their transcripts are committed under `${phase_dir}/evidence/`.
**Method:** Direct execution in disposable clones (`mktemp -d`), on 2026-09-14. Every figure below is reproducible from the command noted beside it, and from the cited transcript.

## The trap

`.gitmodules` records a submodule URL per commit. Fixing the URL on `beta` and `main` today does not change what any past commit records. Checking out an old tag resurrects the old URL from that commit. So does bisecting firmware history, or reading any pre-rename commit. This project does a great deal of archaeology, so the trap will be met. The concrete ref a reader will actually hit is the published `v1.35` tag (`6e84030b…`, 2026-09-02). Its `.gitmodules` still declares `url = git@github.com:henols/firestarter.git` for the firmware submodule. It stays that way permanently, because tags do not move.

**The trap is armed.** It stopped being hypothetical on 2026-09-14, when `henols/firestarter` was claimed for the meta repository and the redirect to `henols/firestarter_fw` was destroyed. `gh api repos/henols/firestarter` now returns `id: 1232995399` (this repository); `henols/firestarter_fw` is `id: 810276812`. A plain `git submodule update --init` at `v1.35` with no override now registers the old URL, clones **this repository** into its own `firestarter/` directory, fails to find the firmware sha, and exits **128** — leaving a half-initialised wrong repository behind. Executed and recorded in `evidence/gitmodules-trap-armed-2026-09-15.txt`. The workarounds below are no longer precautionary; they are required.

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

## Recovery — a clone that already hit the trap

Workarounds A and B both assume the override is set **before** the first
`git submodule update`. Once an update has run without it, the child clone exists with
the wrong origin and setting the override afterwards does nothing: the next update
reuses the existing clone and fails identically. Measured, both attempts exit 128
(`evidence/gitmodules-trap-armed-2026-09-15.txt`, READING 2).

This is the journey a reader actually takes — try it, fail, look up the workaround,
apply it, fail again — so the way out is written here rather than left to be derived.

```
git submodule deinit -f firestarter
rm -rf .git/modules/firestarter
git config submodule.firestarter.url git@github.com:henols/firestarter_fw.git
git submodule update --init firestarter
```

Two ordering constraints, both load-bearing:

- `deinit` **unregisters** the submodule and discards `submodule.<name>.url`, so the
  override must be set **after** it, never before.
- Removing `.git/modules/<name>` is required. `deinit` clears the working directory but
  leaves the cached module, and the next update reuses its wrong origin.

Verified end to end: rc 0, `firestarter/` origin `git@github.com:henols/firestarter_fw.git`,
firmware checked out at `4f73c80` (READING 4).

Substitute the submodule's name at the ref you are on. It is `firestarter` at every
pre-rename ref, and `firestarter_fw` from v1.38 onward.

## The sync hazard

Running `git submodule sync` while HEAD is at a pre-rename ref **silently destroys** the workaround set up by Workaround A or Workaround B. This is not a corner case. `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Ordered procedure", Phase A step 2, names it as routine hygiene. That step tells an operator to run `git submodule sync --recursive` after repointing `.gitmodules`. An operator who has learned that step will undo the GATE-03 workaround. No warning appears. No error appears. It happens the moment `sync` runs at a pre-rename ref.

Captured reproduction, `evidence/193-gate-03-submodule-sync-hazard.txt` READING 1 and READING 2:

```
$ git config --get submodule.firestarter.url
git@github.com:henols/firestarter_fw.git
$ git -C firestarter remote get-url origin
git@github.com:henols/firestarter_fw.git

$ git submodule sync firestarter
Synchronizing submodule url for 'firestarter'

$ git config --get submodule.firestarter.url
git@github.com:henols/firestarter.git
$ git -C firestarter remote get-url origin
git@github.com:henols/firestarter.git
```

The discriminating lines are the two `git config --get` and `git -C firestarter remote get-url origin` pairs, read before and after `sync`. Both read `firestarter_fw` before. Both read the old `firestarter` slug after. The `Synchronizing submodule url for 'firestarter'` line proves nothing by itself. It is `sync`'s routine, silent-success message, not a warning. It names no URL.

`sync` re-reads `.gitmodules` **at the current HEAD**. At a pre-rename ref, that HEAD's `.gitmodules` still names the old slug, so `sync` overwrites the override with it. It clobbers **two places, not one**: `.git/config`'s `submodule.firestarter.url` override, and the child's own `origin` remote (`git -C firestarter remote get-url origin`). A repair that touches only the `.git/config` override would look complete. It would not be. The child would still fetch from the old slug on its next `git -C firestarter fetch`.

The repair for this hazard is two literal commands, run in this order:

```
git config submodule.firestarter.url git@github.com:henols/firestarter_fw.git
git -C firestarter remote set-url origin git@github.com:henols/firestarter_fw.git
```

`evidence/193-gate-03-submodule-sync-hazard.txt` READING 3 runs both and reads both values back to `firestarter_fw`. The same transcript then re-runs `sync` at the same HEAD as a durability check. Both values are immediately re-clobbered again. **This is a repair, not a fix.** It undoes one run of `sync`. Any further `sync` at the same pre-rename ref undoes it again. The durable answer is not to run `git submodule sync` while HEAD sits at a pre-rename ref at all.

## Banked evidence — the executed transcripts

Each transcript carries its own capture dates and the literal commands that produced it. Re-run them rather than trust this note's prose.

- `evidence/193-gate-03-fresh-clone.txt` — Workaround B, executed at `v1.35` in a clean, no-override clone. READING 1 proves the workaround. The override survives `submodule init`, and the child is cloned from `firestarter_fw` despite the ref's own `.gitmodules` naming the old slug. READING 2 proved the trap did not bite *on 2026-09-14*, through the then-live redirect. It is correct as history and is no longer a statement about today — the redirect was destroyed on 2026-09-14. See `evidence/gitmodules-trap-armed-2026-09-15.txt` for the executed post-claim behaviour.
- `evidence/193-gate-03-existing-clone.txt` — Workaround A, executed by taking a maintained, post-rename clone back to `v1.35`. READING 1 captures the invisible agreement state. READING 2 forces the divergence by checking out `v1.35`, and shows the override outliving the checkout and being honoured by the subsequent update.
- `evidence/193-gate-03-submodule-sync-hazard.txt` — the hazard reproduced and repaired. READING 1 is the pre-`sync` baseline, both values on `firestarter_fw`. READING 2 is the clobber, both values reverted to the old slug. READING 3 is the two-command repair, plus the durability check proving a second `sync` re-clobbers both.

- `evidence/gitmodules-trap-armed-2026-09-15.txt` — the trap executed **after** the slug
  claim, on 2026-09-15. READING 1 is the failure itself (exit 128, this repository cloned
  into its own `firestarter/`). READING 2 shows the override failing to recover an
  already-failed clone. READING 3 confirms the clean-slate order still works. READING 4 is
  the recovery. This transcript is an observation, not a projection.

## Honest limits

**(a) The trap is armed, and this limit is retired.** It read "does not bite today" until 2026-09-14, when the freed slug was claimed for the meta repository. That state has arrived. A plain `git submodule update --init` at a pre-rename ref now fails with exit 128 (`evidence/gitmodules-trap-armed-2026-09-15.txt`, READING 1).

**(b) The post-claim failure shape is now an observation, and the projection was right.** `.planning/notes/999.9-repo-rename-impact-analysis.md` § "The `.gitmodules` archaeology trap" reasoned that after the claim, `git submodule update --init` would resolve the old URL to the **meta** repository itself, and that the parent would then clone into its own `firestarter/` child directory. Executed on 2026-09-15: that is exactly what happens. It was untestable while the redirect was live — testing it required performing the destructive claim, which the operator directed on 2026-09-14 (`.planning/seeds/SEED-claim-firestarter-slug.md`). So it was tested, and this limit is discharged rather than standing. Two things the projection did not predict are recorded in `evidence/gitmodules-trap-armed-2026-09-15.txt`: the failure leaves a half-initialised **wrong** repository in `firestarter/` rather than an empty directory, and the override does **not** recover a clone that has already failed — that needs `deinit` plus removal of `.git/modules/<name>` first.

**(c) History cannot be repaired.** Fixing `.gitmodules` on `beta` and `main` does not change what any past commit records. The trap is a property of history, not of the current tip. Rewriting history across a repository with published tags and two submodules is not on the table. The trap is documented and worked around here, not solved. `.planning/notes/999.9-repo-rename-impact-analysis.md` reaches the same verdict, and this note does not revise it.
