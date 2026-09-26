# Retired Ordinals

Never reuse a retired wire ordinal. Shipped hosts still send them, so a new meaning would make an old host drive a different operation.

| Kind | Retired |
|---|---|
| Command | `4` (blank check), `6` (verify) |
| Flag | `0x08` (skip blank check) |

When you retire one, leave a tombstone comment at the old slot on both sides (`constants.py` and `firestarter.h`):

```python
# Ordinal 6 -- the verify command -- retired in 3.1.0. This ordinal must
# NEVER be reused for any new command, flag or reserved meaning.
```

- Keep the slot empty. Do not delete the tombstone.
- Give a new command or flag the next unused value.
