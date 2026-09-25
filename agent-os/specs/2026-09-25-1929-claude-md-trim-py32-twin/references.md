# References for the CLAUDE.md Trim and PY32 Twin Retirement

## Similar Implementations

### Standards index

- **Location:** `agent-os/standards/index.yml`
- **Relevance:** each pointer in a trimmed CLAUDE.md names a file in this index.
- **Key patterns:** one rule per file, with a one-line description in the index. A CLAUDE.md line that
  repeats a standard is replaced with the path of that standard.

### info jumper table spec

- **Location:** `agent-os/specs/2026-09-25-1503-info-jumper-table/`
- **Relevance:** the format model for this spec folder.
- **Key patterns:** Context first, then decisions as `D-x` bullets, then tasks, then verification.

### Retired parent record

- **Location:** meta repo, `1ea94a1e^:.planning/milestones/v1.23-FLASH-PATH-DECISION.md`
- **Relevance:** the parent of `platform/py32f071/FLASH-PATH-AND-PCB.md`. It holds the sections that
  the firmware copy never had: §1 (silicon substrate, §1.6 corrections), §7 (rejected routes),
  §8 (obligations), §9 (open questions).
- **Read it with:** `git -C /workspaces show '1ea94a1e^:.planning/milestones/v1.23-FLASH-PATH-DECISION.md'`
