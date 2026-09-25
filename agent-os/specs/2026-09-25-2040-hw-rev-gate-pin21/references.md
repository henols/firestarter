# References for the Shield-Revision Gate

## Similar Implementations

### Existing shield-revision check
- **Location:** `firestarter_app/firestarter/serial_comm.py` `_validate_hardware_revision` and
  `setup_command`.
- **Relevance:** this is the policy that moves into `hw_revision_gate.py`, and the place after the
  ack where it is called.
- **Key patterns:** an allowlist, not `>=`. The comment explains why a check after the ack is safe:
  VPP waits for the next host ack.

### JP5 gate
- **Location:** `firestarter_app/firestarter/jp5_gate.py`.
- **Relevance:** the shape of a pure gate module: `is_*`, `require_*`, and refusal constants.

### Jumper table
- **Location:** `firestarter_app/firestarter/jumper_table.py` (`VPP_UNREACHABLE_TEXT`,
  `JP4_SILKSCREEN_RULE`).
- **Relevance:** the operator wording for "only Rev 2.2 or later can put VPP on pin 21".

### Revision silkscreen map
- **Location:** `firestarter_app/firestarter/codec.py` `_REVISION_SILKSCREEN`, and
  `constants.py` `REVISION_*`.
- **Relevance:** revision byte ↔ silkscreen text, for the refusal text and for `config --rev`.

### Tests
- **Location:** `firestarter_app/tests/test_hw_revision_gate.py`.
- **Relevance:** the existing policy, ack-decode and `_probe_port` tests, which are rewritten.

### Firmware config parse
- **Location:** `firestarter_fw/src/json_parser.c` (`get_rev`, `json_parse_config`), and
  `firestarter_fw/src/firestarter.cpp` (the `CMD_CONFIG` arm of `parse_json`).
- **Relevance:** where the `rev` range check goes.
