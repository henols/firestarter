# Token census — `.claude/skills/devtest-triage/SKILL.md`

Reserved tokens: `id`, `read`, `blank-check`, `write`, `verify`, `erase` — the `steps[]`
names an agent parses out of a `dev test` report JSON. Every occurrence of one of these
tokens (or an inflection) outside a code fence must fall into exactly one of three
allowed classes:

- **STEP** — a reference to the dev-test step of that name.
- **QUOTED** — verbatim external text: a datasheet term, a `firestarter info` output
  field, a GitHub issue title, a tool name, a file name, a flag, an identifier.
- **NOUN** — a compound technical noun whose head is not the step.

The forbidden class is **VERB** — the token used as an ordinary English verb. This
table classifies every occurrence in `token-census.txt`, in the same order, one row
per occurrence.

| # | Line | Token | Class | Reason |
|---|------|-------|-------|--------|
| 1 | 114 | erase | NOUN | Compound noun "UV-EPROM erase" naming the erase category for that family, not a verb |
| 2 | 174 | blank-check | STEP | Backticked reference to the `blank-check` step's verdict in the §3a trap illustration |
| 3 | 174 | blank-check | STEP | Backticked reference to the `blank-check` step's verdict (the `BAD` example) |
| 4 | 174 | blank-check | STEP | Backticked reference to the `blank-check` step's verdict (the `NA` example) |
| 5 | 300 | Read | QUOTED | "the Read tool" — the proper name of the Read tool used to view PDF pages |
| 6 | 319 | writes | NOUN | Compound noun "erratic writes" naming the write operations affected by out-of-range VCC, not a verb |
| 7 | 320 | Erase | NOUN | Checklist row label naming the erase-capability check (the datasheet-vs-database cross-check row), not an instruction to erase |
| 8 | 320 | erased | QUOTED | Verbatim `firestarter info` field name, backticked as `` `Can be erased:` `` |
| 9 | 320 | erase | STEP | Backticked reference to the `erase` step ("`erase` reported NA/BAD wrongly") |
| 10 | 321 | ID | QUOTED | Datasheet section name "Chip ID" (device-identification / signature-byte section) |
| 11 | 321 | ID | QUOTED | Verbatim `firestarter info` field name, backticked as `` `Chip ID:` `` |
| 12 | 321 | id | STEP | Backticked reference to the `id` step |
| 13 | 322 | write | NOUN | Compound noun "page-write" naming the programming-waveform style, not a verb |
| 14 | 322 | write | NOUN | Compound noun "write path" naming the programming code path, not a verb |
| 15 | 323 | write | NOUN | Compound noun "page-write buffer size", not a verb |
| 16 | 323 | writes | NOUN | Compound noun "page writes" naming the operation that goes partial/corrupt, not a verb |
| 17 | 324 | Write | NOUN | Compound noun "Write protection", the checklist row label, not an instruction to write |
| 18 | 324 | writes | NOUN | Compound noun "refuses writes" naming the blocked operation, not a verb |
| 19 | 325 | write | NOUN | Compound noun "write cycle" naming the program-pulse timing window, not a verb |
| 20 | 406 | blank-check | STEP | Backticked reference to the `blank-check` step's verdict in the worked example |
| 21 | 407 | write | STEP | Backticked reference to the `write` step's verdict in the worked example |
| 22 | 408 | Write | QUOTED | Verbatim GitHub issue title: "AT28Cxxx Write Protection Enable/Disable missing" |
| 23 | 414 | write | NOUN | Compound noun "write protection" (whether it is represented in the DB entry), not a verb |
| 24 | 434 | Read | QUOTED | "the Read tool" — the proper name of the Read tool, in the troubleshooting table |

No occurrence classifies as VERB. Every ordinary-verb usage found during planning (line 3
`verify`, line 14 "reads and writes", line 149 "read as data", line 244 "person reading",
line 280 `verify`, line 288 `delete`, the §5b heading "Read it", line 293 "read the page",
line 333 "the rig reads a rail", line 345 "write the body", line 413 "read the field",
line 424 "write the table", line 425 "the script reads it back", line 442 "read the
reason") was rewritten out of the prose in Task 2, using the locked substitution table
from the plan (`inspect`, `save`, `check`, or a full recast) or removed by a passive
recast (lines 149, 244) that does not use any of the six reserved tokens at all.
