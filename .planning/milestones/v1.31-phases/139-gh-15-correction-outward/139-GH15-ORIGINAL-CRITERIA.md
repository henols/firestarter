## Acceptance criteria

- [ ] `0x07`, `0x08`, and `0x0B` use separate write handlers.
- [ ] No new database algorithm flags are introduced.
- [ ] `EPROM_STD` uses per-byte fixed 1 ms pulse/verify cycles and a final overprogram pulse.
- [ ] `EPROM_QUICK` uses its own fixed short-pulse handler.
- [ ] `EPROM_LEGACY` uses a long fixed programming pulse rather than the current adaptive loop.
- [ ] The current block mismatch/adaptive pulse-growth algorithm is removed from EPROM writing.
- [ ] VPP routing remains protocol-correct and is disabled on all exits.
- [ ] Native tests cover dispatch, pulse behavior, verification, failure, and cleanup.
- [ ] All firmware targets build successfully.
