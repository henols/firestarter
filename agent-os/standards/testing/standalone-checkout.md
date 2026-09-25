# Tests Run From a Standalone Checkout

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
