# No Source Introspection

A test exercises production code with data. It never reads source text and asserts on its contents, whether by regex, substring or `ast`. This applies in all repos.

| Allowed | Forbidden |
|---|---|
| Call production functions; assert on results | Read `.py` `.c` `.h` `.cpp` `.md` `.yml` `.toml` and assert on the text |
| Read shipped data (`firestarter/data/*.json`, `pinouts.json`) | `ast` walks of production modules |
| Native Unity tests that run firmware code | Tests that parse another repo's source |

Why: source scanners fail open. A rename makes them skip or match zero times, and nothing goes red.

- If a hazard cannot be observed by a test, make it true by construction: codegen from one source (like `tools/catalog/`), a single shared definition, `static_assert` / `#error`.
- Host/firmware parity comes from codegen, not from a parity test.
- The source contracts in `firestarter_fw/tests/` are legacy, pending removal. Add none, do not extend them, and remove one when you touch it.
