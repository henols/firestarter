# Click Docstrings Are --help

A command docstring and every `help=` string are user documentation. Click prints them as `--help`.

- No internal references: no phase or plan IDs, requirement tags (`WRITE-01`), `file:line`, or maintainer notes.
- Put implementation reasoning in a `#` comment in the function body, not in the docstring.
- Write in ASD-STE100 (same as refusal text).
- Do not add tests that pin `--help` text.
