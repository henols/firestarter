# Hardware-Revision Switches

List each revision as an explicit `case`. Never use a range test such as `>= REVISION_2_0`.

```cpp
#ifdef HARDWARE_REVISION
    switch (rurp_get_hardware_revision()) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
    case REVISION_2_3:
        mask |= CTRL_VPP_VPE_DROP_ENABLE;
        break;
    default:   // REVISION_0, _1, UNKNOWN (0xFE), any unknown byte
        break; // keep the pre-Rev-2 behaviour
    }
#endif
```

- A range test silently includes a future revision. An explicit list makes each site opt in.
- `default:` is the fail-safe path: pre-Rev-2 behaviour. This covers `REVISION_UNKNOWN` and any unknown byte.
- Every runtime revision read sits inside `#ifdef HARDWARE_REVISION`. A build without it keeps the legacy behaviour.
- VPP checks on `REVISION_0`: send `MSG_WARN_REV0_VPP_UNSUPPORTED`, set `RESPONSE_CODE_WARNING`, return.
- When you add a `REVISION_*` value, find every revision switch and decide at each site. Nothing includes it automatically.
