# Typed Refusals

Each refusal has its own exception class in `exceptions.py`, under the root that matches its domain. `@map_typed_errors` turns it into a `click.ClickException` (exit 1).

| Root | Rendered prefix |
|---|---|
| `SerialError` | `Communication error: ` |
| `EpromOperationError` | `Programmer error: ` |
| `HardwareOperationError` | `Hardware error: ` |
| `ChipNotFoundError`, `FirmwareOperationError` | none |

```python
class PageAlignmentError(EpromOperationError):
    """Raised when ... Fired by page_size_gate.require_page_alignment before any serial byte."""
```

- A new class gets its prefix from its root class. Write the message so it reads correctly after that prefix.
- Existing verbatim arms (`ChipNotImplementedError`, `PageSize*`, `PageAlignmentError`, `NegativeStartAddressError`, `Pin1HazardRefusedError`) are exceptions. Do not add more.
- A subclass arm goes above its parent's arm. The first matching `except` wins.
- Gates raise; they never call `sys.exit`. The only exit path is `map_typed_errors` → `ClickException` (exit 1).
- The docstring says which function raises it and that it fires before any serial byte.
