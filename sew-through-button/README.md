# Sew-through button dimensions

Last Updated: 2026-09-30

This cartridge owns the button solid; Fashion Cabinet owns garment sizing and
the mapping from a garment to its hardware. See the
[commons topology](../README.md#the-four-repo-topology) and
[contribution rules](../CONTRIBUTING.md).

The manifest accepts thickness, hole diameter and dish depth in 0.01 mm steps,
and hole spacing in 0.005 mm steps. These steps preserve fine dimensions from
garment mappings, including the ligne-to-millimetre conversion, without silently
rounding them to the former coarse increments. They describe input resolution,
not manufacturing accuracy. Existing bounds, integer ligne sizes, two/four-hole
choices, geometry constraints and batch limits still apply.

Three presets exercise the additional resolution:

| Preset | Dimensions covered |
| --- | --- |
| `infant_precise` | 1.62 mm thickness, 1.08 mm holes, 3.24 mm spacing and 0.36 mm dish |
| `placket_precise` | 24 L button with 5.08 mm hole spacing |
| `small_precise` | 15 L button with 3.175 mm hole spacing |

The source geometry is unchanged. Validation renders both modes and every
preset with the [shared geometry gate](../README.md#validating-a-cartridge).
Platforms must consume the updated manifest contract before the added input
resolution is available in their handoffs. Values outside the declared grid,
bounds or active mode remain unsupported.

Private rollout evidence belongs in Internal DevOps under the
[repository boundary](../docs/PUBLIC_REPO_BOUNDARY.md).
