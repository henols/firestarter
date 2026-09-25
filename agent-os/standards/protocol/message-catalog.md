# Message Catalog

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
