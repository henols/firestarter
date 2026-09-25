# Standards for the CLAUDE.md Trim and PY32 Twin Retirement

The following standards apply to this work. The trimmed CLAUDE.md files point to them and do not repeat them.

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

---

## protocol/duplicated-constants

Some wire values exist on both sides. Change both sides in one change pair.

| Host (`firestarter_app/firestarter/`) | Firmware (`firestarter_fw/`) |
|---|---|
| `constants.py` `COMMAND_*` | `include/firestarter.h` `CMD_*` |
| `constants.py` `FLAG_*` | `include/firestarter.h` `FLAG_*` |
| `constants.py` `CTRL_*` | `include/rurp_pinout.h` `CTRL_*` |
| `constants.py` `JSON_KEY_*` | `src/json_parser.c` key strings |
| `constants.py` `BUFFER_SIZE`, `CMD_FRAME_MAX` | `firestarter.h` `DATA_BUFFER_SIZE`, `CMD_FRAME_MAX` |

- Edit both files and commit both on the same milestone branch.
- A change to one side only is incomplete, even if all tests pass.

---

## protocol/retired-ordinals

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

---

## protocol/message-catalog

Message IDs have one source: `tools/catalog/messages.toml` in the meta repo. Generate the artifacts only there.

```bash
# edit tools/catalog/messages.toml, then:
tools/catalog/sync_to_subrepos.sh   # writes firestarter_fw/include/messages.h
                                    #    and firestarter_app/firestarter/messages.py
```

- Never hand-edit `messages.h` or `messages.py`. The next sync overwrites them without warning.
- Never regenerate in a sub-repo. The sub-repos hold generated artifacts only.
- Commit in all three repos on the same milestone branch: catalog (meta), `messages.h` (fw), `messages.py` (app).
- A new ID needs host rendering in the same change (format string, render hints, decoder handling).
- Never reorder entries.
- The ERROR band `0xA0–0xBF` is full. New ERROR IDs start at `0xC0`. Severity comes from the `severity` field, never from the ID range.
- Params: at most 24 wire bytes. `wire_format = "text"` entries have `params = []`.
