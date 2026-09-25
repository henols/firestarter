# Confirmation Prompts

A damage-capable operation on an affected part asks the operator first. A refusal is the default.

```python
_print(hazard_text(chip_name, operation, bit), console=console)
if not isatty_fn():
    _print(f"{chip_name.upper()}: refusing to {operation} -- not an interactive session ...")
    return False
return bool(confirm_fn("Cut JP5 before continuing? ...", default=False))
```

- Print the full hazard text first, then ask.
- Always `default=False`. Never a default-yes.
- Off-TTY: refuse before the prompt is reached.
- Unaffected part or non-damage operation: return `True` and print nothing.
