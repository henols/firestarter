# Gate Polarity

A gate fails closed by default: absent evidence means "not provably safe", never "probably fine".

| Worst case of a wrong guess | Polarity | Example |
|---|---|---|
| Chip damage or data loss | Fail closed | `jp5_gate`, `page_size_gate`, `write_blank_guard` |
| Only an operation becomes unavailable | Fail open allowed | `flash4_erase_gate` |

- A fail-open gate must state why its worst case is only lost availability.
- The module docstring names the polarity, the worst case in each direction, and the operator escape.
- The escape is a documented CLI option (`-b`) or an interactive yes. Never an environment variable: those fail open.
- An invalid recorded value (non-power-of-two page size, out-of-range) refuses exactly like a missing value.
