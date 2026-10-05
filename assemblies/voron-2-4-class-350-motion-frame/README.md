# Voron 2.4-class 350 motion system (`voron-2-4-class-350-motion-frame`)

Assembly A of the Digital Twins programme (ASM-1 §7, §9): a **producer** (a fabrication
machine model) that is **posable**. It is the full motion system of a Voron 2.4-class 350
CoreXY printer (owner decision D1), checked by the keystone's `y4d-spec assembly check` at
home, at every joint limit and over the pose sweep, with `--collision`.
Document licence: CERN-OHL-W-2.0.

235 components, 292 mates, 10 belt paths, 23 poses
(home, the six limits of the three driven joints, 16 Halton samples).

> **Original design, cited facts.** Facts come from the *Voron 2.4r2 build guide*
> ([`Manual/Assembly_Manual_2.4r2.pdf`](https://github.com/VoronDesign/Voron-2/blob/a192410e27ea345644ae5c4b29b4c9c40cbe1a73/Manual/Assembly_Manual_2.4r2.pdf),
> version 2023-07-04, GPL-3.0), cited by page only, and from Voron's public Klipper reference
> configuration for the 2.4 (`firmware/klipper_configurations/Octopus/Voron2_Octopus_Config.cfg`
> at VoronDesign/Voron-2 `a192410`, cited path:line). No Voron text, figure, STL or CAD is in
> this repository; every printed part is an original commons cartridge.

## What it is

| Group | Components | Parts |
| :--- | ---: | :--- |
| Frame cube | 12 | `extrusion-2020` ×12 |
| Z drives | 52 | **`z-drive-housing`** ×4, `bearing-625` ×12, `bhcs-m5x10` ×8, `gt2-pulley-16t-5mm` ×4, `gt2-pulley-20t-9mm` ×4, `gt2-pulley-80t-5mm` ×4, `nema-17-48mm` ×4, `shaft-5mm` ×4, `tnut-2020-m5` ×8 |
| Bed | 35 | **`bed-extrusion-mount`** ×4, `bed-plate-350` ×1, `bhcs-m5x10` ×12, `extrusion-2020` ×2, `tnut-2020-m3` ×4, `tnut-2020-m5` ×12 |
| Top corners (Z idlers) | 28 | **`corner-idler-bracket`** ×4, `bhcs-m5x30` ×12, `gt2-idler-20t-9mm` ×4, `tnut-2020-m5` ×8 |
| Z rails and blocks | 8 | `mgn9-rail` ×4, `mgn9h-carriage` ×4 |
| Z joints and Z belt clamps | 20 | **`z-belt-clamp`** ×4, **`z-joint`** ×4, `bhcs-m5x10` ×8, `tnut-2020-m5` ×4 |
| Gantry (C, D, E, Y rails, XY joints, front idlers, A/B drives) | 76 | **`ab-drive`** ×2, **`ab-front-idler`** ×2, **`xy-joint`** ×2, `bearing-f695` ×12, `bhcs-m5x10` ×8, `bhcs-m5x16` ×12, `extrusion-2020` ×4, `gt2-idler-20t-6mm` ×6, `gt2-pulley-20t-5mm` ×2, `mgn9-rail` ×2, `mgn9h-carriage` ×2, `nema-17-48mm` ×2, `shim-5x10` ×12, `tnut-2020-m5` ×8 |
| X axis and toolhead | 4 | **`toolhead-proxy`** ×1, **`x-carriage`** ×1, `mgn12-rail` ×1, `mgn12h-carriage` ×1 |

- **Frame cube** (guide p. 13 counts, kit listings for the 350 cut lengths): four 530 uprights
  and eight 470 horizontals, all blind-jointed. Upright axes at x, y ∈ {0, 490}; the outer
  frame is 510 × 510 × 530. The front and back bottom horizontals carry `slot_station_mm` 170
  for the bed mounts (255 − 65 − 20, guide p. 20); every other station is a mate `offset`
  (ASM-1 §9 v1.4).
- **Top corners ×4:** `corner-idler-bracket` (mirrored on the front-right and back-left), a GT2
  20T 9 mm idler on an M5x30 BHCS, two T-nuts and two M5x30 (guide pp. 48–50).
- **Z rails ×4:** MGN9, 400 (sourcing sheet: MGN9H ×6 at 400 for the 350), centred on each
  upright's inner x face, the rails facing each other across the frame (guide pp. 25, 27), their
  lower ends 3 above the bottom horizontals ("~3 mm", guide p. 25): z 23 … 423.
- **Z drives ×4** (`z-drive-housing`, guide pp. 32–47): 625 bearings, a 5 mm shaft, the 20T
  9 mm Z pulley and the 80T reduction pulley, a NEMA 17 with a 16T pulley (80 / 16 = 5:1,
  guide p. 38).
- **Bed** (fixed; the gantry flies): two 470 bed extrusions 130 apart (p. 20) on four
  `bed-extrusion-mount`s, and `bed-plate-350` on four M3 T-nuts (pp. 53–60).
- **Z joints ×4** (`z-joint`): each bolts to a Z block, holds a C end by a pad in its bottom
  slot, and carries a `z-belt-clamp` so the clamped Z strand runs vertical.
- **Gantry** (P6-GANTRY round 2): C ×2 (450), D (430), E (340); MGN9 Y rails (400, 25 from the
  C ends, p. 88); `xy-joint` ×2 with D riding over the C's (pp. 104–106); `ab-front-idler` ×2;
  `ab-drive` ×2 with their NEMA 17s and GT2 20T pulleys. C centres at x 41 / 449.
- **X axis and toolhead** (P6-XCAR): MGN12, 400, on D's front face (p. 101), the MGN12H, the
  `x-carriage` carrying both A/B belt ends, and the `toolhead-proxy` (D3: an original stand-in
  body with a `nozzle_tip` frame; the Stealthburner is not modelled).

**Out (D1):** electronics, wiring, panels, the endstop and cable-chain mounts.

## A's printed cartridges

Phase 8's graph twins follow this list.

| Cartridge | In A |
| :--- | ---: |
| `ab-drive` | 2 |
| `ab-front-idler` | 2 |
| `bed-extrusion-mount` | 4 |
| `corner-idler-bracket` | 4 |
| `toolhead-proxy` | 1 |
| `x-carriage` | 1 |
| `xy-joint` | 2 |
| `z-belt-clamp` | 4 |
| `z-drive-housing` | 4 |
| `z-joint` | 4 |

## Joints (ASM-1 §9)

| Joint | Type | Role | Mate | Limits | Home / follows |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `z0_shaft_turn` | revolute z | follower | `z0_shaft_in_a` | continuous | -9.00169·gantry_z |
| `z0_motor_turn` | revolute z | follower | `z0_motor_pulley_on_motor` | continuous | -5·z0_shaft_turn |
| `z1_shaft_turn` | revolute z | follower | `z1_shaft_in_a` | continuous | 9.00169·gantry_z |
| `z1_motor_turn` | revolute z | follower | `z1_motor_pulley_on_motor` | continuous | -5·z1_shaft_turn |
| `z2_shaft_turn` | revolute z | follower | `z2_shaft_in_a` | continuous | 9.00169·gantry_z |
| `z2_motor_turn` | revolute z | follower | `z2_motor_pulley_on_motor` | continuous | -5·z2_shaft_turn |
| `z3_shaft_turn` | revolute z | follower | `z3_shaft_in_a` | continuous | -9.00169·gantry_z |
| `z3_motor_turn` | revolute z | follower | `z3_motor_pulley_on_motor` | continuous | -5·z3_shaft_turn |
| `gantry_z` | prismatic x | driven | `z0_block_on_rail` | [-168.975, 146.025] | home 0 |
| `z1_block_follow` | prismatic x | follower | `z1_block_on_rail` | [-180.05, 180.05] | 1·gantry_z |
| `z2_block_follow` | prismatic x | follower | `z2_block_on_rail` | [-180.05, 180.05] | 1·gantry_z |
| `z3_block_follow` | prismatic x | follower | `z3_block_on_rail` | [-180.05, 180.05] | 1·gantry_z |
| `gantry_y` | prismatic x | driven | `y_block_l_on_rail` | [-174, 176] | home 0 |
| `motor_l_turn` | revolute z | follower | `pulley_l_on_shaft` | continuous | 9.00169·x_carriage + 9.00169·gantry_y |
| `gantry_y_right` | prismatic x | follower | `y_block_r_on_rail` | [-174, 176] | 1·gantry_y |
| `motor_r_turn` | revolute z | follower | `pulley_r_on_shaft` | continuous | 9.00169·x_carriage + -9.00169·gantry_y |
| `x_carriage` | prismatic x | driven | `x_block_on_rail` | [-175, 175] | home 0 |

Eight **passive** revolute joints (`z*_shaft_in_b`, `_in_c`) let each Z shaft close its second
and third bearings while it turns. Idlers and F695 stacks carry no joint: they are rotationally
symmetric and close no cycle.

- **`x_carriage`, `gantry_y`, `gantry_z`** are the three driven joints. Their limits are exactly
  the machine's soft range through the bindings below, so every position Klipper can report
  poses (`pose()` never clamps).
- **D2.** One logical Z: the three other Z blocks follow `gantry_z` one to one; quad gantry
  levelling tilt is later fidelity.
- **CoreXY motors.** 360 / (π · 12.73) = 9.00169° per mm on the GT2 20T pitch circle (PD 12.73,
  Gates 20-2MR, catalog `gt2-pulley-20t-5mm`). The left motor turns as x + y and the right one
  as x − y (CoreXY a = x + y, b = x − y). The signs were measured on A's own belt paths by finite
  differences: moving x or y by 1 mm changes the belt length between the carriage and each
  pulley by ±1 mm, and the pulley turns that way.
- **Z drives.** Each output shaft turns z / (π · 12.73) turns (the 20T Z pulley, catalog
  `gt2-pulley-20t-9mm`), signed by hand so the clamped strand's side of the pulley rises with the
  gantry: − on the front-left and back-right, + on the other two. Each motor pulley turns 5 times
  as far (80 / 16) in the same sense about the world axis; its frame is flipped (it sits on
  `bore_b`), hence the scale −5.

## Machine bindings (`machine`, ASM-1 §9.2)

`kinematics: corexy` (Octopus cfg :34). joint = scale · axis + offset:

| Axis | Joint | Scale | Offset | Source |
| :--- | :--- | ---: | ---: | :--- |
| x | `x_carriage` | 1 | −175 | Klipper X 0 … 350: cfg :56 `position_min 0`, :68–69 `position_endstop` / `position_max 350`. CONVENTION: X 175 at the X rail's mid-length, which centres X over the plate (nozzle x 70 … 420; plate 67.5 … 422.5). |
| y | `gantry_y` | 1 | −174 | Klipper Y 0 … 350: cfg :95, :107–108. CONVENTION: Y 0 puts the nozzle over the plate's front edge, y 28 (p. 60: 38 behind the frame's front face at y −10). The nozzle is 43.0 ahead of the Y blocks' centre (P6-XCAR's reach, a convention), so Y 350 puts it at y 378, inside the plate (rear edge 383). The blocks then run −174 … 176, inside their collision-free −176.75 … 177.25 (P6-GANTRY). |
| z | `gantry_z` | 1 | −163.975 | Klipper Z: cfg :155 `position_min −5`, :152 `position_max 310`, :142 `position_endstop −0.5`. CONVENTION: Z 0 puts `nozzle_tip` on the plate's top face: the tip is at z 203.0 at `gantry_z` 0, the plate's top at 29.5 + 9.525 = 39.025 (`bed-plate-350`: spacer 9.5, thickness 9.525). |

pravara forwards raw axis values; the viewer maps them through these bindings (D4).

**Z below 0.** `gantry_z`'s lower limit is Klipper's `position_min −5`, so the proxy's nozzle
passes 5 mm into the plate at that one pose. That is declared (below) rather than hidden by a
narrower limit: physically the bed stops the nozzle; the twin must still pose every position
Klipper reports (owner-programme decision, option (a), 2026-10-05).

## Belt paths (ASM-1 §9.3)

| Path | Belt | Kind | At home (mm) | Min over the sweep | Max | Spread |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `z0_reduction_loop` | `gt2-belt-loop-188mm` | closed | 188.0062 | 188.0062 | 188.0062 | 0.0000 |
| `z1_reduction_loop` | `gt2-belt-loop-188mm` | closed | 188.0062 | 188.0062 | 188.0062 | 0.0000 |
| `z2_reduction_loop` | `gt2-belt-loop-188mm` | closed | 188.0062 | 188.0062 | 188.0062 | 0.0000 |
| `z3_reduction_loop` | `gt2-belt-loop-188mm` | closed | 188.0062 | 188.0062 | 188.0062 | 0.0000 |
| `z0_z_belt` | `gt2-belt-9mm` | open | 1048.8525 | 1048.8525 | 1048.8525 | 0.0000 |
| `z1_z_belt` | `gt2-belt-9mm` | open | 1048.8525 | 1048.8525 | 1048.8525 | 0.0000 |
| `z2_z_belt` | `gt2-belt-9mm` | open | 1048.8525 | 1048.8525 | 1048.8525 | 0.0000 |
| `z3_z_belt` | `gt2-belt-9mm` | open | 1048.8525 | 1048.8525 | 1048.8525 | 0.0000 |
| `belt_b` | `gt2-belt-6mm` | open | 1682.2879 | 1682.2879 | 1682.2879 | 0.0000 |
| `belt_a` | `gt2-belt-6mm` | open | 1682.2882 | 1682.2882 | 1682.2882 | 0.0000 |

No `path-length` warning: the CoreXY belts and the Z belts are constant-length by
construction, and the sweep confirms it.

- **A and B** (`gt2-belt-6mm`, guide p. 131): from one `x-carriage` anchor round the XY joints,
  the drives and the front idlers back to the other anchor, stacked on two levels (p. 125).
- **Z ×4** (`gt2-belt-9mm`, p. 111), open, teeth inside the loop (p. 118): clamp (lower jaw) →
  Z pulley → top idler → clamp (upper jaw). The anchored strand is the outer one and runs
  vertical; the inner strand runs free past the C. The guide's 1200 minimum cut (p. 111) leaves
  about 150 mm for the folded tails.
- **Reduction loops ×4** (`gt2-belt-loop-188mm`, p. 34), closed: 188.006 against the catalog's
  188 at the housing's 40.8 centre distance.

## Collision (`--collision`, ASM-1 §3.7)

Checked at home, the six limits and the 16 samples: no undeclared overlap. The
149 declared overlaps are all **designed** ones, each measured, with `max_mm3` at the measured value
plus 5–10 % (P6-JOINT's convention):

- keys, tongues and screw shanks in 2020 slots (the catalog's 2020 envelope is the solid
  profile: no cited slot depth);
- shafts and axles in bores (an envelope has no bore), and M5 screws cutting their thread in
  printed Ø4.2 pilots;
- the toolhead proxy into the bed plate at `gantry_z`'s lower limit only (Klipper's −5
  overtravel, above).

**Collision-unchecked** (no envelope, named by the check, never silently passed): every
`tnut-2020-m5` and `tnut-2020-m3` (no cited body height), and the `gt2-pulley-20t-9mm` and
`gt2-pulley-16t-5mm` (no cited flange diameter).

**Budget.** The whole check, `--collision` at the default 16 samples, takes about 33 s on
the lane's macOS laptop (wall clock, local); it fits every-PR CI.

<details><summary>Declared overlaps</summary>

| a | b | max mm³ | Why |
| :--- | :--- | ---: | :--- |
| `bed_plate` | `toolhead` | 190 | Klipper's probe overtravel: position_min −5 (VoronDesign/Voron-2 @ a192410, firmware/klipper_configurations/Octopus/Voron2_Octopus_Config.cfg:155) lets Z go 5 mm below the bed's surface, and gantry_z's limits cover the machine's whole soft range so every position Klipper reports poses (D4). Physically the bed stops the nozzle; the twin's proxy nozzle passes 5 mm into the plate at gantry_z's lower limit only. Measured 176.7 mm3 (owner-programme option (a), 2026-10-05). |
| `bed_rail_l` | `bed_rail_l_back_mount` | 142 | bed_rail_l_back_mount (bed-extrusion-mount) keys its tongue into bed_rail_l's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 132.3 mm3. |
| `bed_rail_l` | `bed_rail_l_back_mount_screw_bed` | 116 | the bhcs-m5x10 shank runs into bed_rail_l's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bed_rail_l` | `bed_rail_l_front_mount` | 142 | bed_rail_l_front_mount (bed-extrusion-mount) keys its tongue into bed_rail_l's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 132.3 mm3. |
| `bed_rail_l` | `bed_rail_l_front_mount_screw_bed` | 116 | the bhcs-m5x10 shank runs into bed_rail_l's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bed_rail_r` | `bed_rail_r_back_mount` | 142 | bed_rail_r_back_mount (bed-extrusion-mount) keys its tongue into bed_rail_r's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 132.3 mm3. |
| `bed_rail_r` | `bed_rail_r_back_mount_screw_bed` | 116 | the bhcs-m5x10 shank runs into bed_rail_r's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bed_rail_r` | `bed_rail_r_front_mount` | 142 | bed_rail_r_front_mount (bed-extrusion-mount) keys its tongue into bed_rail_r's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 132.3 mm3. |
| `bed_rail_r` | `bed_rail_r_front_mount_screw_bed` | 116 | the bhcs-m5x10 shank runs into bed_rail_r's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_back` | `bed_rail_l_back_mount` | 402 | bed_rail_l_back_mount (bed-extrusion-mount) keys its tongue into bx_back's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 374.8 mm3. |
| `bx_back` | `bed_rail_l_back_mount_screw_frame_a` | 116 | the bhcs-m5x10 shank runs into bx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_back` | `bed_rail_l_back_mount_screw_frame_b` | 116 | the bhcs-m5x10 shank runs into bx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_back` | `bed_rail_r_back_mount` | 402 | bed_rail_r_back_mount (bed-extrusion-mount) keys its tongue into bx_back's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 374.8 mm3. |
| `bx_back` | `bed_rail_r_back_mount_screw_frame_a` | 116 | the bhcs-m5x10 shank runs into bx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_back` | `bed_rail_r_back_mount_screw_frame_b` | 116 | the bhcs-m5x10 shank runs into bx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_back` | `z2_housing` | 470 | z2_housing (z-drive-housing) keys its tongue into bx_back's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 438.6 mm3. |
| `bx_back` | `z2_screw_a` | 116 | the bhcs-m5x10 shank runs into bx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_back` | `z2_screw_b` | 116 | the bhcs-m5x10 shank runs into bx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_back` | `z3_housing` | 470 | z3_housing (z-drive-housing) keys its tongue into bx_back's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 438.6 mm3. |
| `bx_back` | `z3_screw_a` | 116 | the bhcs-m5x10 shank runs into bx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_back` | `z3_screw_b` | 116 | the bhcs-m5x10 shank runs into bx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_front` | `bed_rail_l_front_mount` | 402 | bed_rail_l_front_mount (bed-extrusion-mount) keys its tongue into bx_front's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 374.8 mm3. |
| `bx_front` | `bed_rail_l_front_mount_screw_frame_a` | 116 | the bhcs-m5x10 shank runs into bx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_front` | `bed_rail_l_front_mount_screw_frame_b` | 116 | the bhcs-m5x10 shank runs into bx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_front` | `bed_rail_r_front_mount` | 402 | bed_rail_r_front_mount (bed-extrusion-mount) keys its tongue into bx_front's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 374.8 mm3. |
| `bx_front` | `bed_rail_r_front_mount_screw_frame_a` | 116 | the bhcs-m5x10 shank runs into bx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_front` | `bed_rail_r_front_mount_screw_frame_b` | 116 | the bhcs-m5x10 shank runs into bx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_front` | `z0_housing` | 470 | z0_housing (z-drive-housing) keys its tongue into bx_front's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 438.6 mm3. |
| `bx_front` | `z0_screw_a` | 116 | the bhcs-m5x10 shank runs into bx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_front` | `z0_screw_b` | 116 | the bhcs-m5x10 shank runs into bx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_front` | `z1_housing` | 470 | z1_housing (z-drive-housing) keys its tongue into bx_front's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 438.6 mm3. |
| `bx_front` | `z1_screw_a` | 116 | the bhcs-m5x10 shank runs into bx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `bx_front` | `z1_screw_b` | 116 | the bhcs-m5x10 shank runs into bx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `by_left` | `z0_housing` | 348 | z0_housing (z-drive-housing) keys its tongue into by_left's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 324.8 mm3. |
| `by_left` | `z2_housing` | 348 | z2_housing (z-drive-housing) keys its tongue into by_left's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 324.8 mm3. |
| `by_right` | `z1_housing` | 348 | z1_housing (z-drive-housing) keys its tongue into by_right's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 324.8 mm3. |
| `by_right` | `z3_housing` | 348 | z3_housing (z-drive-housing) keys its tongue into by_right's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 324.8 mm3. |
| `c_left` | `drive_l` | 234.83 | the printed part's 2 mm tongue in the extrusion's 6 mm slot (the extrusion's envelope is solid); measured 213.48 mm³, allowance +10 % (P6-JOINT's convention) |
| `c_left` | `drive_l_c_screw` | 118.79 | an M5 screw's shank in the extrusion's slot, into its T-nut (the extrusion's envelope is solid); measured 107.99 mm³, allowance +10 % (P6-JOINT's convention) |
| `c_left` | `front_idler_l` | 228.45 | the printed part's 2 mm tongue in the extrusion's 6 mm slot (the extrusion's envelope is solid); measured 207.68 mm³, allowance +10 % (P6-JOINT's convention) |
| `c_left` | `front_idler_l_c_screw` | 118.79 | an M5 screw's shank in the extrusion's slot, into its T-nut (the extrusion's envelope is solid); measured 107.99 mm³, allowance +10 % (P6-JOINT's convention) |
| `c_right` | `drive_r` | 234.83 | the printed part's 2 mm tongue in the extrusion's 6 mm slot (the extrusion's envelope is solid); measured 213.48 mm³, allowance +10 % (P6-JOINT's convention) |
| `c_right` | `drive_r_c_screw` | 118.79 | an M5 screw's shank in the extrusion's slot, into its T-nut (the extrusion's envelope is solid); measured 107.99 mm³, allowance +10 % (P6-JOINT's convention) |
| `c_right` | `front_idler_r` | 228.45 | the printed part's 2 mm tongue in the extrusion's 6 mm slot (the extrusion's envelope is solid); measured 207.68 mm³, allowance +10 % (P6-JOINT's convention) |
| `c_right` | `front_idler_r_c_screw` | 118.79 | an M5 screw's shank in the extrusion's slot, into its T-nut (the extrusion's envelope is solid); measured 107.99 mm³, allowance +10 % (P6-JOINT's convention) |
| `dk_l_screw` | `dk_l` | 194.38 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 176.71 mm³, allowance +10 % (P6-JOINT's convention) |
| `dk_r_screw` | `dk_r` | 194.38 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 176.71 mm³, allowance +10 % (P6-JOINT's convention) |
| `dq_l_screw` | `dq_l_f695_1` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `dq_l_screw` | `dq_l_f695_2` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `dq_l_screw` | `dq_l_shim_1` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `dq_l_screw` | `dq_l_shim_2` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `dq_r_screw` | `dq_r_f695_1` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `dq_r_screw` | `dq_r_f695_2` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `dq_r_screw` | `dq_r_shim_1` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `dq_r_screw` | `dq_r_shim_2` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `drive_l` | `dk_l_screw` | 25.43 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 23.12 mm³, allowance +10 % (P6-JOINT's convention) |
| `drive_l` | `dq_l_screw` | 17.19 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 15.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `drive_l` | `ds_l_screw` | 19.07 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 17.34 mm³, allowance +10 % (P6-JOINT's convention) |
| `drive_r` | `dk_r_screw` | 25.43 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 23.12 mm³, allowance +10 % (P6-JOINT's convention) |
| `drive_r` | `dq_r_screw` | 16.93 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 15.39 mm³, allowance +10 % (P6-JOINT's convention) |
| `drive_r` | `ds_r_screw` | 19.07 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 17.34 mm³, allowance +10 % (P6-JOINT's convention) |
| `ds_l_screw` | `ds_l_f695_1` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `ds_l_screw` | `ds_l_f695_2` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `ds_l_screw` | `ds_l_shim_1` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `ds_l_screw` | `ds_l_shim_2` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `ds_r_screw` | `ds_r_f695_1` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `ds_r_screw` | `ds_r_f695_2` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `ds_r_screw` | `ds_r_shim_1` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `ds_r_screw` | `ds_r_shim_2` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `fi_l_screw` | `fi_l` | 194.38 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 176.71 mm³, allowance +10 % (P6-JOINT's convention) |
| `fi_r_screw` | `fi_r` | 194.38 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 176.71 mm³, allowance +10 % (P6-JOINT's convention) |
| `front_idler_l` | `fi_l_screw` | 25.43 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 23.12 mm³, allowance +10 % (P6-JOINT's convention) |
| `front_idler_r` | `fi_r_screw` | 25.43 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 23.12 mm³, allowance +10 % (P6-JOINT's convention) |
| `ji_l_screw` | `ji_l` | 194.38 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 176.71 mm³, allowance +10 % (P6-JOINT's convention) |
| `ji_r_screw` | `ji_r` | 194.38 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 176.71 mm³, allowance +10 % (P6-JOINT's convention) |
| `joint_l` | `ji_l_screw` | 25.43 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 23.12 mm³, allowance +10 % (P6-JOINT's convention) |
| `joint_l` | `js_l_screw` | 19.07 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 17.34 mm³, allowance +10 % (P6-JOINT's convention) |
| `joint_r` | `ji_r_screw` | 25.43 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 23.12 mm³, allowance +10 % (P6-JOINT's convention) |
| `joint_r` | `js_r_screw` | 19.07 | the M5x16 axle's shank in its Ø4.2 pilot in the printed host (the thread it cuts); measured 17.34 mm³, allowance +10 % (P6-JOINT's convention) |
| `js_l_screw` | `js_l_f695_1` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `js_l_screw` | `js_l_f695_2` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `js_l_screw` | `js_l_shim_1` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `js_l_screw` | `js_l_shim_2` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `js_r_screw` | `js_r_f695_1` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `js_r_screw` | `js_r_f695_2` | 86.39 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 78.54 mm³, allowance +10 % (P6-JOINT's convention) |
| `js_r_screw` | `js_r_shim_1` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `js_r_screw` | `js_r_shim_2` | 21.59 | the M5x16 axle's shank in the bore of the part it carries (envelopes are solid); measured 19.63 mm³, allowance +10 % (P6-JOINT's convention) |
| `motor_l` | `pulley_l` | 345.58 | the motor's Ø5 shaft in the pulley's bore; measured 314.16 mm³, allowance +10 % (P6-JOINT's convention) |
| `motor_r` | `pulley_r` | 345.58 | the motor's Ø5 shaft in the pulley's bore; measured 314.16 mm³, allowance +10 % (P6-JOINT's convention) |
| `rear_beam` | `drive_l` | 164.65 | the printed part's 2 mm tongue in the extrusion's 6 mm slot (the extrusion's envelope is solid); measured 149.68 mm³, allowance +10 % (P6-JOINT's convention) |
| `rear_beam` | `drive_l_e_screw` | 118.79 | an M5 screw's shank in the extrusion's slot, into its T-nut (the extrusion's envelope is solid); measured 107.99 mm³, allowance +10 % (P6-JOINT's convention) |
| `rear_beam` | `drive_r` | 164.65 | the printed part's 2 mm tongue in the extrusion's 6 mm slot (the extrusion's envelope is solid); measured 149.68 mm³, allowance +10 % (P6-JOINT's convention) |
| `rear_beam` | `drive_r_e_screw` | 118.79 | an M5 screw's shank in the extrusion's slot, into its T-nut (the extrusion's envelope is solid); measured 107.99 mm³, allowance +10 % (P6-JOINT's convention) |
| `tx_back` | `z2_idler_screw_a` | 116 | the bhcs-m5x30 shank runs into tx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `tx_back` | `z2_idler_screw_b` | 116 | the bhcs-m5x30 shank runs into tx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `tx_back` | `z3_idler_screw_a` | 116 | the bhcs-m5x30 shank runs into tx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `tx_back` | `z3_idler_screw_b` | 116 | the bhcs-m5x30 shank runs into tx_back's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `tx_front` | `z0_idler_screw_a` | 116 | the bhcs-m5x30 shank runs into tx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `tx_front` | `z0_idler_screw_b` | 116 | the bhcs-m5x30 shank runs into tx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `tx_front` | `z1_idler_screw_a` | 116 | the bhcs-m5x30 shank runs into tx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `tx_front` | `z1_idler_screw_b` | 116 | the bhcs-m5x30 shank runs into tx_front's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `ty_left` | `z0_idler_bracket` | 323 | z0_idler_bracket (corner-idler-bracket) keys its tongue into ty_left's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 301.6 mm3. |
| `ty_left` | `z2_idler_bracket` | 323 | z2_idler_bracket (corner-idler-bracket) keys its tongue into ty_left's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 301.6 mm3. |
| `ty_right` | `z1_idler_bracket` | 323 | z1_idler_bracket (corner-idler-bracket) keys its tongue into ty_right's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 301.6 mm3. |
| `ty_right` | `z3_idler_bracket` | 323 | z3_idler_bracket (corner-idler-bracket) keys its tongue into ty_right's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 301.6 mm3. |
| `u0` | `z0_idler_bracket` | 205 | z0_idler_bracket (corner-idler-bracket) keys its tongue into u0's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 191.4 mm3. |
| `u1` | `z1_idler_bracket` | 205 | z1_idler_bracket (corner-idler-bracket) keys its tongue into u1's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 191.4 mm3. |
| `u2` | `z2_idler_bracket` | 205 | z2_idler_bracket (corner-idler-bracket) keys its tongue into u2's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 191.4 mm3. |
| `u3` | `z3_idler_bracket` | 205 | z3_idler_bracket (corner-idler-bracket) keys its tongue into u3's slot; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 191.4 mm3. |
| `x_beam` | `joint_l` | 172.26 | the printed part's 2 mm tongue in the extrusion's 6 mm slot (the extrusion's envelope is solid); measured 156.6 mm³, allowance +10 % (P6-JOINT's convention) |
| `x_beam` | `joint_l_d_screw` | 118.79 | an M5 screw's shank in the extrusion's slot, into its T-nut (the extrusion's envelope is solid); measured 107.99 mm³, allowance +10 % (P6-JOINT's convention) |
| `x_beam` | `joint_r` | 172.26 | the printed part's 2 mm tongue in the extrusion's 6 mm slot (the extrusion's envelope is solid); measured 156.6 mm³, allowance +10 % (P6-JOINT's convention) |
| `x_beam` | `joint_r_d_screw` | 118.79 | an M5 screw's shank in the extrusion's slot, into its T-nut (the extrusion's envelope is solid); measured 107.99 mm³, allowance +10 % (P6-JOINT's convention) |
| `z0_bearing_a` | `z0_shaft` | 106 | a 5 mm shaft runs through the bore of z0_bearing_a; an envelope has no bore. Measured 98.2 mm3. |
| `z0_bearing_b` | `z0_shaft` | 106 | a 5 mm shaft runs through the bore of z0_bearing_b; an envelope has no bore. Measured 98.2 mm3. |
| `z0_bearing_c` | `z0_shaft` | 106 | a 5 mm shaft runs through the bore of z0_bearing_c; an envelope has no bore. Measured 98.2 mm3. |
| `z0_idler_axle` | `z0_idler` | 295 | the M5 axle runs through the bore of z0_idler; an envelope has no bore. Measured 274.9 mm3. |
| `z0_idler_bracket` | `z0_idler_axle` | 62 | the M5 screw cuts its thread in the printed pilot of z0_idler_bracket (Ø4.2, as P4-AUTH-E measured for the corner idler). Measured 57.8 mm3. |
| `z0_pad_screw` | `c_left` | 116 | the bhcs-m5x10 shank runs into c_left's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `z0_shaft` | `z0_big_pulley` | 379 | a 5 mm shaft runs through the bore of z0_big_pulley; an envelope has no bore. Measured 353.4 mm3. |
| `z0_z_joint` | `c_left` | 253.97 | the z-joint's 6 mm tongue in the C's bottom slot (P6-ASM's pad; the C's envelope is the solid 20 × 20 square); measured 230.88 mm³, allowance +10 % (P6-JOINT's convention) |
| `z0_z_joint` | `z0_clamp_screw` | 19 | the M5 screw cuts its thread in the printed pilot of z0_z_joint (Ø4.2, as P4-AUTH-E measured for the corner idler). Measured 17.3 mm3. |
| `z1_bearing_a` | `z1_shaft` | 106 | a 5 mm shaft runs through the bore of z1_bearing_a; an envelope has no bore. Measured 98.2 mm3. |
| `z1_bearing_b` | `z1_shaft` | 106 | a 5 mm shaft runs through the bore of z1_bearing_b; an envelope has no bore. Measured 98.2 mm3. |
| `z1_bearing_c` | `z1_shaft` | 106 | a 5 mm shaft runs through the bore of z1_bearing_c; an envelope has no bore. Measured 98.2 mm3. |
| `z1_idler_axle` | `z1_idler` | 295 | the M5 axle runs through the bore of z1_idler; an envelope has no bore. Measured 274.9 mm3. |
| `z1_idler_bracket` | `z1_idler_axle` | 62 | the M5 screw cuts its thread in the printed pilot of z1_idler_bracket (Ø4.2, as P4-AUTH-E measured for the corner idler). Measured 57.8 mm3. |
| `z1_pad_screw` | `c_right` | 116 | the bhcs-m5x10 shank runs into c_right's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `z1_shaft` | `z1_big_pulley` | 379 | a 5 mm shaft runs through the bore of z1_big_pulley; an envelope has no bore. Measured 353.4 mm3. |
| `z1_z_joint` | `c_right` | 253.97 | the z-joint's 6 mm tongue in the C's bottom slot (P6-ASM's pad; the C's envelope is the solid 20 × 20 square); measured 230.88 mm³, allowance +10 % (P6-JOINT's convention) |
| `z1_z_joint` | `z1_clamp_screw` | 19 | the M5 screw cuts its thread in the printed pilot of z1_z_joint (Ø4.2, as P4-AUTH-E measured for the corner idler). Measured 17.3 mm3. |
| `z2_bearing_a` | `z2_shaft` | 106 | a 5 mm shaft runs through the bore of z2_bearing_a; an envelope has no bore. Measured 98.2 mm3. |
| `z2_bearing_b` | `z2_shaft` | 106 | a 5 mm shaft runs through the bore of z2_bearing_b; an envelope has no bore. Measured 98.2 mm3. |
| `z2_bearing_c` | `z2_shaft` | 106 | a 5 mm shaft runs through the bore of z2_bearing_c; an envelope has no bore. Measured 98.2 mm3. |
| `z2_idler_axle` | `z2_idler` | 295 | the M5 axle runs through the bore of z2_idler; an envelope has no bore. Measured 274.9 mm3. |
| `z2_idler_bracket` | `z2_idler_axle` | 62 | the M5 screw cuts its thread in the printed pilot of z2_idler_bracket (Ø4.2, as P4-AUTH-E measured for the corner idler). Measured 57.8 mm3. |
| `z2_pad_screw` | `c_left` | 116 | the bhcs-m5x10 shank runs into c_left's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `z2_shaft` | `z2_big_pulley` | 379 | a 5 mm shaft runs through the bore of z2_big_pulley; an envelope has no bore. Measured 353.4 mm3. |
| `z2_z_joint` | `c_left` | 253.97 | the z-joint's 6 mm tongue in the C's bottom slot (P6-ASM's pad; the C's envelope is the solid 20 × 20 square); measured 230.88 mm³, allowance +10 % (P6-JOINT's convention) |
| `z2_z_joint` | `z2_clamp_screw` | 19 | the M5 screw cuts its thread in the printed pilot of z2_z_joint (Ø4.2, as P4-AUTH-E measured for the corner idler). Measured 17.3 mm3. |
| `z3_bearing_a` | `z3_shaft` | 106 | a 5 mm shaft runs through the bore of z3_bearing_a; an envelope has no bore. Measured 98.2 mm3. |
| `z3_bearing_b` | `z3_shaft` | 106 | a 5 mm shaft runs through the bore of z3_bearing_b; an envelope has no bore. Measured 98.2 mm3. |
| `z3_bearing_c` | `z3_shaft` | 106 | a 5 mm shaft runs through the bore of z3_bearing_c; an envelope has no bore. Measured 98.2 mm3. |
| `z3_idler_axle` | `z3_idler` | 295 | the M5 axle runs through the bore of z3_idler; an envelope has no bore. Measured 274.9 mm3. |
| `z3_idler_bracket` | `z3_idler_axle` | 62 | the M5 screw cuts its thread in the printed pilot of z3_idler_bracket (Ø4.2, as P4-AUTH-E measured for the corner idler). Measured 57.8 mm3. |
| `z3_pad_screw` | `c_right` | 116 | the bhcs-m5x10 shank runs into c_right's slot to its T-nut; the 2020 envelope is the solid profile (no cited slot depth), so the slot is not hollowed. Measured 108.0 mm3. |
| `z3_shaft` | `z3_big_pulley` | 379 | a 5 mm shaft runs through the bore of z3_big_pulley; an envelope has no bore. Measured 353.4 mm3. |
| `z3_z_joint` | `c_right` | 253.97 | the z-joint's 6 mm tongue in the C's bottom slot (P6-ASM's pad; the C's envelope is the solid 20 × 20 square); measured 230.88 mm³, allowance +10 % (P6-JOINT's convention) |
| `z3_z_joint` | `z3_clamp_screw` | 19 | the M5 screw cuts its thread in the printed pilot of z3_z_joint (Ø4.2, as P4-AUTH-E measured for the corner idler). Measured 17.3 mm3. |

</details>

## Conventions (labelled; not sourced facts)

- Home: every driven joint at 0 (mid-travel); the sweep: 16 Halton samples, seed 1 (ASM-1 §9.4).
- The X, Y and Z offsets above; the nozzle's 43.0 reach and the tip's height (P6-XCAR).
- The Z blocks' centres sit 10 below the C's centre line (the z-joint pad's top is the C's
  bottom face).
- The bed plate's holes 150 either side of its centre (no listing publishes the pattern).
- The belt levels and element stations of the gantry cartridges (their READMEs).

## History

- **Phase 4's A** (solid `ce632af`, #147; digest `a60c6e34…` on keystone `5b4913c`): a 29-component
  static subset. One braced frame corner and one blind-jointed top corner with the Z idler, an
  MGN12 rail and block carrying the Stealthburner as an external reference, one NEMA 17 on a
  `nema-bracket`, an endstop and a drag-chain anchor, and a 608 idler on an 8 mm axle in a
  `roller-bracket`.
- **The owner's idler decisions (2026-10-04).** (a) The 608 idler chain stood as a documented
  layout convention (#143); (b) the build guide was checked and no cited Voron idler maps onto a
  608 on an 8 mm axle: the 2.4 uses F695, 625 and GT2 idlers on M5 hardware (pp. 8, 48–50, 65,
  69, 83, 91–100) (#144).
- **Superseded in Phase 6** by this composition (D1). The 608 chain, `nema-bracket`,
  `roller-bracket`, `tslot-corner` and the `tslot-2020` brace leave A (no 2.4 counterpart; the
  cube is blind-jointed), and so do the endstop and cable-chain mounts (D1: electronics out).

## Check it

```bash
pip install "hyperobjects-spec[geometry] @ git+https://github.com/madfam-org/hyperobjects-spec@<SPEC_PIN>"
parts=$(python -c 'import hyperobjects_standard_parts as h, pathlib; print(pathlib.Path(h.__file__).parent / "parts")')
y4d-spec assembly check assemblies/voron-2-4-class-350-motion-frame/assembly.json \
    --commons . --standard-parts "$parts" --collision
y4d-spec assembly poses assemblies/voron-2-4-class-350-motion-frame/assembly.json \
    --commons . --standard-parts "$parts"        # the golden pose file (ASM-1 §9.5)
```

`SPEC_PIN` is in [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml). CI runs the check,
with `--collision`, on every PR (the `assemblies` job).

---

## Español

Ensamble A del programa de gemelos digitales: el **sistema de movimiento completo** de una
impresora CoreXY clase Voron 2.4 350 (decisión D1), **posable** (ASM-1 §9). Lo verifica
`y4d-spec assembly check` en la posición inicial, en cada límite y en el barrido, con
`--collision`. Licencia del documento: CERN-OHL-W-2.0.

- **Contenido:** el cubo del marco 350 con uniones ciegas; cuatro esquinas superiores con su
  polea Z; cuatro rieles Z MGN9 (pp. 25, 27); cuatro accionamientos Z con reducción 5:1; la cama
  fija con su placa; el pórtico volante (C, D, E, rieles Y, uniones XY, poleas delanteras y
  accionamientos A/B) colgado de cuatro uniones Z originales; el riel X MGN12, el carro X y un
  sustituto original del cabezal (D3).
- **Articulaciones:** `x_carriage`, `gantry_y` (el carro Y derecho la sigue) y `gantry_z` (los
  otros tres carros Z la siguen, D2) son las motrices; los motores A/B giran como x + y y
  x − y, y cada flecha y motor Z como seguidores.
- **Enlaces de máquina:** `corexy`, con X, Y y Z de Klipper (configuración de referencia
  Octopus de Voron, citada por línea) mapeados a las articulaciones; Z 0 pone la punta de la
  boquilla sobre la cara superior de la placa, Y 0 sobre su borde delantero.
- **Bandas:** A y B, cuatro bandas Z y cuatro lazos de reducción; longitud constante en todo el
  barrido, sin advertencias.
- **Colisiones:** solo interferencias de diseño, medidas y declaradas, incluida la boquilla 5 mm
  dentro de la placa en el límite inferior de Z (sobrerrecorrido de Klipper, −5).
- **Historia:** sustituye al A estático de la fase 4 (29 componentes, `ce632af`), con sus
  decisiones de la polea 608 (a)+(b) registradas arriba.

Ninguna geometría Voron se copia; la guía de armado (GPL-3.0) se cita solo por página.
