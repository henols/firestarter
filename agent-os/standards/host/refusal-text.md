# Operator-Facing Refusal Text

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
