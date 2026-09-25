# Pre-Serial Gates

Each host safety policy is its own module (`*_gate.py`, `*_guard.py`). It is a pure predicate over the resolved wire dict and the operation name.

```python
DAMAGE_CAPABLE_OPERATIONS = frozenset({"write", "erase"})

def is_affected(bus_config: dict | None) -> bool: ...

def require_acknowledged(chip_name, bus_config, operation, acknowledged) -> None:
    if operation not in DAMAGE_CAPABLE_OPERATIONS:
        return
    if not bus_config or not bus_config.get("bus"):
        raise Pin1HazardRefusedError(...)   # absent evidence = refuse
    ...
```

- No I/O, no environment reads, no serial access.
- `require_*()` raises a typed exception on refusal and returns `None` on pass. `is_*()` / `requires_*()` return a bool.
- Call it from `eprom_operations.py`, not only `cli_handlers.py`. `dev test`, `chip_test` and library callers must reach it too.
- It refuses before the port opens and before the wire dict reaches the transport.
- Never inline the policy in `eprom_operations.py` or `cli_handlers.py`.
- Import protocol IDs (`FLASH4_PROTOCOL_ID`, `SDP_PROTOCOL_ID`). Never retype the literal.
- Ship a test that plants a violation and proves the gate refuses it.
