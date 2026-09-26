# Flash and RAM Reporting

Every firmware change reports flash and RAM, before and after, for `leonardo` and `uno`.

```bash
pio run -e leonardo                                       # stable image
PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1" pio run -e leonardo   # beta image (larger)
pio run -e uno
```

- Take the numbers from the `RAM:` / `Flash:` lines of the build output.
- Leonardo is the tightest target: 28672 B Caterina ceiling, not 32768.
- Report the beta (`DEV_TOOLS=1`) image too. It ships and it is larger.
- Always report RAM next to flash. A PROGMEM move trades one for the other.
