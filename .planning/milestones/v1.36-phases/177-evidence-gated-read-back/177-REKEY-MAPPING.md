# Phase 177 Filed-Corpus Re-Key Mapping

**GATE-06.** `count_agreeing` reads the `dedup_fingerprint` value embedded in a filed
`henols/firestarter_prom` issue body and never re-hashes it. PRUNE-03's evidence-gated
read-back (D-4/D-6: a passing write/verify step's fingerprint classifies `match` instead of
`indeterminate`) moves the fingerprint that WOULD be recomputed for 18 of the 26 rows
committed in `firestarter_app/tests/fixtures/devtest_issue_corpus.json`, applying the
PRUNE-01+PRUNE-03 rule to each row's own recorded step vector (`op in {"write", "write-partial",
"verify"}` AND `verdict == "OK"` steps move to fingerprint classification `match`). This is
**permanent for the historical corpus** -- no migration of an already-filed GitHub issue is
possible, and none is performed by this plan. No GitHub issue is edited, closed or commented
on.

`tests/fixtures/devtest_issue_corpus.json` itself is **unchanged** by this re-key -- its
`filed_hash` column remains the historical, as-filed value forever, and `recomputed_hash`
(when present) likewise reflects what reproduced at filing time. This mapping is a NEW,
separate artifact recording what the SAME recorded step vector re-keys to under PRUNE-03's
rule, not an edit to the corpus fixture.

**gh#39 and gh#40 share `filed_hash` `334c3fa198bf` before this re-key and move TOGETHER to
`16aac69da5bc` after it** -- the dedup group survives intact, merely re-keyed. No dedup group
present in the 26-row corpus splits or merges as a side effect of this re-key.

Measured count: **18 of 26** filed rows re-key, matching `177-RESEARCH.md`'s projected count and
issue list exactly (`corpus_projection_agreement` in
`evidence/177-01-red-capture.txt`).

| Issue | Chip | Before `dedup_fingerprint` | After `dedup_fingerprint` |
|---|---|---|---|
| 22 | w27c512 | `0eec03f6821b` | `ae8bcb4888b1` |
| 24 | w27e257 | `3870f9b5f6ca` | `9b8db06b2796` |
| 25 | sst39sf020 | `ed1b5dc79022` | `e4c3506816b8` |
| 26 | w27c020 | `f8cb30c62aac` | `2aab7ffddd1c` |
| 27 | w27c020 | `ea556a61c3db` | `6f5ccf0f736d` |
| 29 | m27c512 | `7c6997788e25` | `80085c799534` |
| 31 | m27c1001 | `d8771536cb43` | `b69de8bde40a` |
| 39 | at28c256 | `334c3fa198bf` | `16aac69da5bc` |
| 40 | at28c256 | `334c3fa198bf` | `16aac69da5bc` |
| 42 | w27c512 | `8236361b75a5` | `b2eedefb3435` |
| 45 | W27E040 | `957307f7b750` | `5e2a14063327` |
| 46 | W27E512 | `2f4fb4f62ff3` | `4d2bfa33e50c` |
| 47 | sst27sf512 | `f9dbc31dcd27` | `1f812aae49ca` |
| 48 | W29c040 | `969aa43f48c3` | `c1691f167f40` |
| 49 | fm1608 | `0e86f636df87` | `e497a347c9ec` |
| 50 | sst39sf040 | `52af74c52f2c` | `436592268b72` |
| 51 | W27E020 | `e62e68e1c93a` | `2bb103e07469` |
| 52 | W29c020 | `e09213a69a71` | `d26e7e7435b2` |

**gh#47's row above is a statement about the historical FILED corpus row for issue gh#47 --
applying PRUNE-03's rule to its recorded step vector.** It is independent of whether the
REGISTERED shape builder `gh47-sst27sf512-pass` (`firestarter_app/tests/fixtures/report_shapes.py`)
moves. Per D-177-6, that builder's hand-specified `step_specs` are deliberately NOT edited by
this phase -- it stays inside D-177-3's stated re-pointing scope (the two
`sst27sf512-six-step*` builders only) -- so `FROZEN_HASHES['gh47-sst27sf512-pass']` stays
`f9dbc31dcd27`, unmoved, and gets no ledger row. The `1f812aae49ca` projection named in
`177-RESEARCH.md` and in this ledger's earlier prose for that BUILDER is falsified (see
`MILESTONES.md`'s corrections table); this table's gh#47 row is unaffected by that
falsification, since it measures the filed corpus row, not the registered builder.

The 8 unmoved filed rows (issues not listed above) keep their filed `dedup_fingerprint`
unchanged: their recorded step vectors carry no `write`/`write-partial`/`verify` step with
verdict `OK` and classification `indeterminate`, so the PRUNE-01+PRUNE-03 rule has nothing to
move for them.
