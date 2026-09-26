# GATE-1.6 v2 Axis 4 desk-side `.hex` SHA-256 assertion table
# Generated: 2026-05-26 — Plan 28-03 Task 4

| Env | Pre-revert (`4f205e58`) | Post-prune (`efd203a`) | Δ | Axis 4 verdict |
|-----|------------------------|------------------------|---|----------------|
| uno | `5e7f393a48543b4d2c95f48c37a3751814a3221afebda6866eb4a7d73be28927` (62617 B) | `5e7f393a48543b4d2c95f48c37a3751814a3221afebda6866eb4a7d73be28927` (62617 B) | byte-identical | PASS — uno source untouched |
| leonardo | `2619eea6989870d699a921348be8024b1ee22b0c2ef3f2da53224765d38b1bfb` (68917 B) | `734b9a85fabc4477776f8371968cb109630d7d79c37f467aadaf9e64e3f6a33d` (68884 B) | differs by revert delta | PASS — revert removes 10-line PORTx-clear block from rurp_set_data_input |
| uno328pb | `d9e51b7e54fe26af6a3286ae8a6e483b56892936c4efd15c13dad9ed22e91ee7` (62854 B) | `d9e51b7e54fe26af6a3286ae8a6e483b56892936c4efd15c13dad9ed22e91ee7` (62854 B) | byte-identical | PASS — uno328pb source untouched; matches Plan 27-04 falsifier |

Bonus: Leonardo @ fdb1ed5 SHA = 9bc0ed128fb0729c6952c2a8e922516fc42a47f49426f3d6e641a6536ed6095e
Note: fdb1ed5 ≠ post-prune (9bc0ed12 ≠ 734b9a85) — expected; post-prune still includes
4f205e58's _NOP() settling changes in rurp_read_data_buffer. Only 437339b6 was reverted
by Plan 28-03; 4f205e58 stays on branch (Plan 28-04 conditional scope).
