# Standards for the info Jumper Table

The following standards apply to this work.

---

## host/refusal-text

Keep refusal text in module-level format constants. Tests import the constant; they do not copy the text.

```python
_REFUSAL_FORMAT = (
    "Refusing write to {chip_name}: not blank at 0x{address:06X}, v: 0x{value:02X}."
)
raise SomeRefusalError(_REFUSAL_FORMAT.format(chip_name=chip_name.upper(), ...))
```

- Put the chip name in upper case, near the start: `W27C512: ...` or `Refusing write to W27C512: ...`.
- Say what can go wrong, and how the operator can continue (`-b`, cut JP5 and answer yes).
- For jumpers and pins, quote the board silkscreen exactly (`"Cut for ROMs with A19 on P1"`), so the operator can check it on the board.
- Write in ASD-STE100: short sentences, one instruction per sentence, no hedging.

---

## host/gate-polarity

A gate fails closed by default: absent evidence means "not provably safe", never "probably fine".

| Worst case of a wrong guess | Polarity | Example |
|---|---|---|
| Chip damage or data loss | Fail closed | `jp5_gate`, `page_size_gate`, `write_blank_guard` |
| Only an operation becomes unavailable | Fail open allowed | `flash4_erase_gate` |

- A fail-open gate must state why its worst case is only lost availability.
- The module docstring names the polarity, the worst case in each direction, and the operator escape.
- The escape is a documented CLI option (`-b`) or an interactive yes. Never an environment variable: those fail open.
- An invalid recorded value (non-power-of-two page size, out-of-range) refuses exactly like a missing value.

---

## host/echo-vs-logger

> **Deviation for this spec (D-D):** the `info` view prints all its lines through `logger.info`, which goes to stdout at default verbosity. The new jumper and INFO lines also use `logger.info`, so that one view does not mix two output APIs. A migration of the whole `info` view to `click.echo` is a separate backlog item.

`logger.*` is for diagnostics that show only with `-v`. A fact the operator needs uses `click.echo`, so it shows at default verbosity.

```python
# operator must see this without -v
click.echo(f"{eprom.upper()}: pulse override {pulse_us} us (database: {db_pulse} us)")

# diagnostic detail
logger.debug("resolved bus config: %s", bus_config)
```

- Use `click.echo` for: refusals that exit without an exception, verdict lines, and notices that change what the operation does.
- Use `logger` for: trace detail, timings, raw frames.

---

## testing/non-vacuity

Every new check (gate, guard, refusal) ships with committed tests that feed it violating input and assert that it refuses.

```python
def test_is_affected_true_at_bit_19(): ...                   # refuses
def test_is_affected_false_at_bit_18(): ...                  # boundary: passes
def test_require_acknowledged_no_bus_key_raises_fail_closed(): ...  # absent evidence
```

- Test both sides of each threshold.
- For a fail-closed check, test `None` / empty / missing input.
- The violation is in the input data (synthetic pin map, bad page size). Never mutate source to plant it.
- A test written before the fix must fail on its own assertion. If it fails on setup or lookup, the test is broken, not the code. Read the failure message.
- Assertions on shipped data use exact counts (`== 746`), never floors (`>=`). A change updates the number on purpose.

---

## testing/no-source-introspection

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

---

## testing/standalone-checkout

CI checks out each repo alone (`work/<repo>/<repo>`). The devcontainer's sibling layout (`/workspaces/firestarter_fw` next to `firestarter_app`) hides cross-repo dependencies.

```python
_APP_ROOT = Path(__file__).resolve().parent.parent   # never cwd, never an env var
_DB_FILE = _APP_ROOT / "firestarter" / "data" / "chip_database.json"
```

- A test reads only files inside its own repo. Never a sibling repo, the meta repo or `.planning/`.
- Resolve paths from `Path(__file__)`.
- To check "inside repo X", use `Path.is_relative_to()`, never a name substring.
- Never write a test that skips when a sibling is absent. In CI it never runs.

Before you trust a new test, run it in a fresh clone of that repo only. The clone sees committed files only.

```bash
git clone /workspaces/firestarter_app "$SCRATCH/app" && cd "$SCRATCH/app"
export UV_CACHE_DIR="$SCRATCH/uv-cache"          # default cache is not writable
uv venv --python 3.11 .venv                      # CI runs 3.11; devcontainer has 3.12
VIRTUAL_ENV=.venv uv pip install -e '.[test]' && .venv/bin/pytest tests/
```

Use a new venv. The devcontainer's editable install still points at `/workspaces`.
