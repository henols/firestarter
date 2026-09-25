# click.echo vs logger

`logger.*` is for diagnostics that show only with `-v`. A fact the operator needs uses `click.echo`, so it shows at default verbosity.

```python
# operator must see this without -v
click.echo(f"{eprom.upper()}: pulse override {pulse_us} us (database: {db_pulse} us)")

# diagnostic detail
logger.debug("resolved bus config: %s", bus_config)
```

- Use `click.echo` for: refusals that exit without an exception, verdict lines, and notices that change what the operation does.
- Use `logger` for: trace detail, timings, raw frames.
