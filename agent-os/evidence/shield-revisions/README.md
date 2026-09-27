# RURP shield revision photographs — originals

Full-resolution originals of the three shield photographs taken by the operator on **2026-09-10**.

Until 2026-09-27 these existed only in the untracked, gitignored `/workspaces/tmp/` directory. The
v1.37 Phase 182 notes recorded twice that they were *"not preserved by any commit"* and asked for
them to be re-exported before that directory was cleared. This directory is that preservation.

| File | Board | Capture | Size | SHA-256 |
|---|---|---|---|---|
| `shield-rev0-modified-jp1-jp2-jp3.jpg` | Modified Rev 0 | 10:27:36 | 12106582 | `93ec5e8e770f3ff0054f66f4696fb7daa5ca191a7834f75e0880507227088e66` |
| `shield-rev2-jp4-jp5.jpg` | Rev 2 | 10:27:48 | 17719412 | `78068dfbf5a13f2f0b7a9b35bb35f26e4d334f5d6badb54ee6f1a02a6191c99d` |
| `shield-rev2.2-jp4-jp5-jp6-jp9.jpg` | Rev 2.2 | 10:27:54 | 15616263 | `d039a0341567ce9a2090edc6c71f3e0f254b358bdfbe942fde94608a8d174ea3` |

All three: OnePlus 13, 2304×4096, EXIF `DateTime` as above.

## Why these matter

- The **Rev 2.2** photograph is the silkscreen ground truth that retired a wrong sentence from
  operator-facing text. The board's JP4 is a 3-pole selector, so the
  "Open for 32 pin ROMs, Closed for 28 pin ROMs" clause cannot describe it and must never be
  reproduced. The correct parenthetical is *"Only for ROMs with VPP on P1."*
- The **Rev 2** photograph records JP5's unconditional silkscreen instruction, verbatim:
  *"JP5: Cut for ROMs with A19 on P1"* — no "cut if VPP is asserted" qualifier.
- The **modified Rev 0** photograph closed a standing evidence gap: that board had never been
  physically photographed before Phase 182.

Re-acquiring any of them means re-acquiring three specific physical boards and re-photographing
them. Treat this directory as evidence, not as build output.

## Relationship to the committed downscales

~250 KB downscales (900×1600) were committed under the v1.37 Phase 182 evidence directory in the
`.planning/` tree. Each was matched back to its original by perceptual signature at a 270–327×
margin over the next candidate, which is how the board names above were assigned — the source notes
never recorded the `IMG*.jpg` → board mapping.

When `.planning/` was retired, those downscales went with it. They remain readable from history at
the tag `archive/planning-tree-final`, and at meta commit `5b9e41ab`:

```bash
git -C /workspaces show '5b9e41ab:.planning/notes/jumper-display-ground-truth.md'
```

The originals here are the durable copy.
