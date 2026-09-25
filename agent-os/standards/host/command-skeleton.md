# Click Command Skeleton

```python
@cli.command(name="read")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.option("-a", "--address", default=None, help="Read start address in dec/hex")
@click.pass_obj
@map_typed_errors                      # innermost
def read(app: AppContext, eprom: str, address: str | None) -> None:
    """Reads an EPROM into a file."""
    ok = app.eprom_operator.read_eprom(...)
    sys.exit(0 if ok else 1)
```

- Decorator order: `@cli.command` → arguments/options → `@click.pass_obj` → `@map_typed_errors`.
- Handlers take `app: AppContext`. Never build managers inside a handler. Tests pass `obj=AppContext(...)` to `CliRunner.invoke`.
- Check invalid option combinations first and raise `click.UsageError` (e.g. `--full` without `--verify`), before `resolve_chip`.
- Plain commands end with `sys.exit(0 if ok else 1)`.
- Verdict commands (`verify`, `write --verify`, `blank -b`): `0` = proven good, `1` = proven bad, `2` = could not decide (read failed, refused before compare).
