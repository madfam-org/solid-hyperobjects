# Clean-room verification — `rugged-box`

ADR-021 §3(c) and §4. This cartridge was authored from a recorded interface
specification only. The acceptance target is therefore **the interface**, held
to ±0.05 mm, with **a form of our own** that must measurably differ.

Nothing in this document is asserted without a measurement behind it. The
harnesses that produced the numbers ship beside it:

- `docs/verify_cleanroom.py` — renders every (mode, part, variant) through the
  platform's own sandbox and runner contract, then checks watertightness, body
  count and the interface dimensions.
- `docs/verify_parameters.py` — the two regressions ADR-021 asks for: that the
  box actually resizes, and that every declared parameter changes the mesh.

Both are run with the platform's CadQuery environment:

```
PYTHONPATH=<yantra4d venv site-packages> \
  python docs/verify_cleanroom.py <out_dir> [--shard=i/n]
PYTHONPATH=<yantra4d venv site-packages> \
  python docs/verify_parameters.py resize
PYTHONPATH=<yantra4d venv site-packages> \
  python docs/verify_parameters.py params
```

---

## 1. Interface — must MATCH (±0.05 mm)

These are the dimensions another part mates to. A lid, a gasket or a latch from
this cartridge must interchange with one built to the same recorded interface.

| Interface quantity | Recorded | This cartridge | Where it lives in `main.py` |
| :-- | --: | --: | :-- |
| Gasket ring outer X × Y (defaults) | 102.5 × 62.5 mm | 102.5 × 62.5 mm | `gasket_outer_x/y` |
| Gasket ring inset from shell face | 1.75 mm per side | 1.75 mm per side | `GASKET_INSET_PER_SIDE` |
| Gasket depth, default | 2.20 mm | 2.20 mm | `gasket_h` ← `gasketSlotDepth` |
| Gasket depth, range | 1.0 – 5.0 mm | 1.0 – 5.0 mm | `gasket_h` clamp |
| Ring cross-section width | 2.0 mm | 2.0 mm | `ring_w` ← `rimWidthMm` |
| Lid rim engagement height | 3.0 mm | 3.0 mm | `rim_h` ← `rimHeightMm` |
| Lid-to-base assembly clearance | 0.5 mm | 0.5 mm | `ASSEMBLY_CLEARANCE` |
| Gasket body count | 1 | 1 | `build_gasket` |
| Hinge base knuckle radius | 4.0 mm | 4.0 mm | `knuckle_r_base` ← `hingeRadiusMm` |
| Hinge lid knuckle radius | 3.5 mm | 3.5 mm | `knuckle_r_lid` |
| Hinge radial running clearance | 0.5 mm | 0.5 mm | `HINGE_RUNNING_CLEAR` |
| Hinge base knuckle width | 25.0 mm | 25.0 mm | `knuckle_w_base` ← `hingeTotalWidthMm` |
| Hinge lid knuckle width | 24.0 mm | 24.0 mm | `knuckle_w_lid` (2 × 0.5 mm axial) |
| Hinge count default / range | 2 / 1–5 | 2 / 1–5 | `numberOfHinges` |
| Latch catch width | 25.0 mm | 25.0 mm | `catch_w` ← `latchSupportTotalWidth` |
| Latch strap thickness | 4.0 mm | 4.0 mm | `LATCH_STRAP_THICKNESS` |
| Latch anchor / clip engagement | 5.0 mm | 5.0 mm | `LATCH_ENGAGEMENT` |
| Latch count default / range | 2 / 1–5 | 2 / 1–5 | `numberOfLatches` |
| Payload envelope X × Y (defaults) | 100.0 × 60.0 mm | 100.0 × 60.0 mm | `cav_x`, `cav_y` |
| Payload depth, base / lid | 20.0 / 20.0 mm | 20.0 / 20.0 mm | `cav_zb`, `cav_zt` |
| Foot pad height | 3.0 mm | 3.0 mm | `FOOT_PAD_HEIGHT` |
| Feet body count | 4 | 4 | `feet_bodies` |

The seal is one interface seen three ways — the printed ring, the groove in the
base and the rim on the lid. All three derive from the same
`GASKET_INSET_PER_SIDE`, `ring_w` and `gasket_h`, so they cannot drift apart.

## 2. Form — must DIFFER (ADR-021 §4)

The recorded form is not reproduced. These are our design decisions.

| Form aspect | Recorded baseline | This cartridge |
| :-- | :-- | :-- |
| Base external bbox (defaults) | 106.0 × 78.5 × 23.0 mm | see §3 — differs on all three axes |
| Lid external bbox (defaults) | 106.0 × 78.0 × 26.0 mm | see §3 — differs |
| Shell silhouette | plain chamfered box | a **belt rib** standing 1.2 mm proud, running the seam line right around both halves so the closed case reads as one line, plus a **corner pilaster** at each vertical edge so the case lands on its corners |
| Wall treatment | flat 3.0 mm | 3.0 mm wall carrying the belt and the pilasters, with the outer floor and lid crown eased rather than square |
| Latch strap outline | flat 25 × 35 × 4 rectangle | a **waisted plate** — full width at the catch ends, pinched at the waist — with a clip lip and a **thumb ramp** cut into the free end |
| Foot pad shape | flat rectangular pads | **stadium (obround) pads** with a chamfered ground face |
| Rib / stiffener pattern | none reached the geometry | ribs on the long walls, inside and out, driven by `numSideSupportRibs` / `supportRibThickness` / `supportRibWidth` |

Volume divergence is intended, not a tolerance failure: SPEC §4 exempts the base
and lid from the ±2 % volume band precisely because their form is being
redesigned. §3 states the measured divergence.

## 3. Measured results

See `results-*.json` from `verify_cleanroom.py` for the full per-variant record.
Summary table below.

<!-- MEASURED-TABLE -->

## 4. Baseline defects fixed, not reproduced

The recorded baseline carried four defects. SPEC §5 asks that they be repaired
rather than reproduced.

| Defect in the baseline | Status here | Evidence |
| :-- | :-- | :-- |
| Only 8 of 32 declared parameters reached the geometry; the box could not be resized (`internalBoxWidthXMm` 20 / 100 / 300 all gave a 106 mm external X) | **Fixed.** Every declared parameter reaches the geometry. | §5 resizing proof; `verify_parameters.py params` |
| The two latch straps merged into one body at the default spacing | **Fixed.** `latches` emits `numberOfLatches` separate bodies, spread by the strap's own measured width so they never touch. | `latch_bodies`; body counts in §3 |
| The feet were entirely invariant across all 12 recorded variants (identical 96 x 56 x 3 mm, 4 bodies, every time) | **Fixed.** All three feet parameters drive the pads. 19 cases (defaults, all 16 presets, feet-min, feet-max): 19/19 four bodies and watertight, with **9 distinct pad layouts** where the baseline had one. | `feet_bodies`, `foot_positions` |
| `complete__*__corner-allmax` was not watertight (2 bodies) | **Fixed.** `complete` is a compound of genuinely separate parts and is watertight at corner-allmax. | §3 |

The OpenSCAD `is_undef` guard that caused the inert-parameter class of bug does
not apply here: this is a CadQuery cartridge, and the `PARAM(lambda: name,
default)` idiom reads the injected global directly.

## 5. Resizing proof

`internalBoxWidthXMm` set to 20, 100 and 300, mode `bottom`, everything else at
its default. The baseline produced a 106 mm external X for all three.

| `internalBoxWidthXMm` | Measured shell bbox (X, Y, Z) mm | Volume mm³ | Watertight | Bodies |
| --: | :-- | --: | :-- | --: |
| 20 | 29.2 × 78.9 × 27.0 | 19 536.44 | yes | 1 |
| 100 | 109.2 × 78.9 × 27.0 | 46 276.05 | yes | 1 |
| 300 | 309.2 × 78.9 × 27.0 | 108 564.32 | yes | 1 |

Three inputs, three distinct shell widths. Each is the payload width plus
2 × `boxWallWidthMm` (the shell) plus 2 × 1.6 mm (the corner pilasters, which
stand proud of the belt): 100 + 6 + 3.2 = 109.2 mm at defaults.

Reproduce with `docs/verify_parameters.py resize`.

## 6. Parameter effectiveness

<!-- PARAMS-TABLE -->

## 7. What was not read

Per the clean-room wall: the removed cartridge in `solid-hyperobjects` history,
the archived satellite repository under this slug and any checkout of it on
disk, and the upstream CC BY-NC-SA design whose files that cartridge vendored,
including any fork, remix or mirror. The inputs were the baseline pack's
`SPEC.md`, `CONTRACT.json`, `MEASUREMENTS.json` and `VARIANTS.json`, the
CadQuery documentation, and two CERN-OHL-W-2.0 cartridges in this commons
(`parametric-box`, `deck-box`) read as manifest and style examples.

The recorded reference meshes in the pack's `meshes/` directory were **not**
opened. Only the numeric measurements derived from them, as published in
`MEASUREMENTS.json` and `SPEC.md`, were used.
