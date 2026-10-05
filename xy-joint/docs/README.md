# XY Joint

A printed **XY joint** for a CoreXY gantry whose two belts run **stacked on two levels**, a
2.4-class "flying gantry". It is generated with **CadQuery** (B-Rep) and does three jobs:

- it rides an **MGN9H block** on the gantry's Y rail;
- it carries the end of the **2020 X beam**, which hangs under it on two M5 T-nuts;
- it turns both belts through 90°. One belt turns on a **GT2 20-tooth toothed idler**, the other on a
  stack of **two F695 flanged bearings**.

Each turning part sits on an M5x40 axle. The axles hang from a bridge above both belt levels.
There are left- and right-hand versions. The right hand also swaps the belt levels.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and configurator:
[Yantra4D](https://app.yantra4d.com).

> **Original design.** The functional brief comes from a Voron 2.4-class gantry. It is cited by
> page and section only, from the *Voron 2.4r2 build guide*, version 2023-07-04
> (VoronDesign/Voron-2 @ `a192410`, GPL-3.0):
> - pp. 97 and 99: an F695 stack (M5 shim, F695, F695, M5 shim) on an M5x40 SHCS, in each XY joint;
> - pp. 98 and 100: a GT2 20-tooth idler on an M5x40 SHCS screwed into plastic;
> - p. 88: the Y axis runs on MGN9 rails;
> - p. 104: the X beam is fixed to the joints with M5 button-head screws;
> - p. 125: the two belts are stacked and the CoreXY crossing is omitted;
> - p. 131: the A/B belts are 6 mm wide.
>
> No Voron geometry, STL or CAD was copied, traced or derived. The joint's shape comes from the
> cited facts below. It is licensed CERN-OHL-W-2.0.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **XY Joint** | `xy_joint` | The single joint. `mirrored` builds the right hand. |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Idler | `idler_width` | 9 mm | The toothed idler's width, flange to flange. 9 is the cited listing's GT2 20T 6 mm-belt idler (catalog `gt2-idler-20t-6mm`). The maximum is 10: a wider low idler would reach the high belt level. |
| Hand | `mirrored` | off | Builds the right joint: x is reflected, and the stack and the idler swap belt levels. |

## How the belts run (and why the right hand swaps levels)

The two belts never cross. Each runs on its own level, and the joint turns each one through
90° from the X run (along the beam) to the Y run (along the rail).

On one joint, one belt makes a **convex** corner of its loop: the corner turns toward the inside
of the loop, so the belt's teeth face the axle. That belt goes round the **toothed idler**. The
other belt makes a **reflex** corner, so its smooth back faces the axle. That belt goes round the
**F695 stack**.

On the other joint the roles are exchanged, which is why the mirrored joint swaps levels.

The joint's model frame:
- **Origin:** the centre of the MGN9H block's top face.
- **+x:** to the gantry's right.
- **+y:** to the back.
- **+z:** up.
- **The belt line:** both X runs lie on y = 0, the line above the block's centre.

| | Left joint (default) | Right joint (`mirrored`) |
| :--- | :--- | :--- |
| F695 stack, at (±32, −7.006) | low level, z 12 (22 above the C extrusion) | high level, z 21 (31) |
| Toothed idler, at (±37, +6.366) | high level, z 21 | low level, z 12 |

**Cited derivations**
- **Idler y = +6.366.** The GT2 20T pitch radius: SDP/SI Technical Section, Table 33, gives pd
  12.73 mm for 20 grooves. The idler's pitch circle is tangent to the belt line.
- **Stack y = −7.006.** The F695's Ø13 outer ring (NSK F695ZZ) plus the belt's **back-side
  offset**, 0.506 mm. The offset is B − T − U:
  - B = 1.52 (belt height) and T = 0.76 (tooth depth), both from Pfeifer's 2MR/PGGT2 row;
  - U = 0.254 (pitch line to tooth bottom), from SDP/SI Table 4.

  The belt's back runs on the stack. Catalog `gt2-belt-6mm` records these values.
- **Stack height 10.** A 1 mm DIN 988 shim, two 4 mm F695 and another shim. The stack's belt
  mid-plane is where the plain faces meet, 5 from either end.
- **The block top is 10 above the C extrusion.** That is the MGN9 assembly height H (HIWIN MG
  series).

**Conventions** (not sourced): the belt levels 12 and 21 above the block top, chosen as follows.
- The low stack sits 1 mm above the 6 mm floor.
- The high belt runs 1 mm clear of the low stack's top.
- The bridge underside is the high stack's top, z 26.

Elsewhere in the gantry (lane P6-GANTRY's report), the low level is the **B** belt and the high
level the **A** belt.

## Sources and conventions

**Cited facts**
- **MGN9H:** W 20, L 39.9, H 10, M3 on B 15 × C 16 (HIWIN MG series). The plate's four M3
  holes follow this pattern.
- **M5x40 SHCS (ISO 4762), l 40.** With the head on the bridge top (z 31), the tip ends at
  z −9, inside the block's Ø4.2 pilot. The guide's joint idlers are screwed into plastic
  (pp. 98, 100). Ø4.2 is the hole MISUMI taps M5 (p2_0681).
- **MISUMI HFS5:** a 6 mm slot opening and 2 mm lips. The beam tongue is 2 mm deep.
- **MISUMI HNTAP5-5 T-nuts** are 15 long. The two beam nuts sit 22.5 apart.
- **ISO 7380-1 M5 button head:** dk 9.5. The beam-screw counterbores are Ø10.5. Their floor sits
  4.5 above the beam face, so an M5x10 passes 5.5 into the nut, as in `corner-idler-bracket`.

**Conventions (not sourced)**
- **The X beam's end sits 12.5 inboard of the rail centre.** With the 430 mm D extrusion (the
  coordinator's cited 350 lengths), that puts the C extrusion centres 227.5 from the gantry's
  centre.
- **Beam screw stations:**
  - A is 10 from the beam's end, the beam's slot station;
  - B is 22.5 further along.
- **Axle stations:** the stack is 32 inboard of the rail centre, the idler 37. The extra 5 mm
  keeps the A/B drive pulley 5.8 mm clear of the other belt, and the idler's Ø18 flange 0.27 mm
  clear of the stack's shims.
- **Clamp columns** are Ø8 and bear on the shim's or idler's inner face. Holes are Ø5.5 and
  Ø3.4. The M3 counterbores are Ø6.5 × 3.5.
- **Pillars** stand off every belt line:
  - outboard ones span x −8 … 6, outside the outer run at x ≈ ±10;
  - inboard ones span x 51 … 59, at |y| ≥ 5.

## Interfaces

Every frame reads `s = 1 − 2·mirrored`. The stack's level is `zs = 12 + 9·mirrored` and the
idler's is `zi = 21 − 9·mirrored`.

| Interface | Type | Polarity / key / symmetry | Where |
| :--- | :--- | :--- | :--- |
| `xy_joint_carriage` | `bolt_pattern` | male, `mgn9-carriage`, 2 | At the origin, normal −z, x_axis along the rail (+y). It mates `mgn9h-carriage.top`. |
| `xy_joint_beam_a`, `_b` | `bolt_pattern` | male, `m5-screw-joint`, 0 | On the block's underside (z −10) at x = s·22.5 and s·45. Each mates a `tnut-2020-m5.thread` in the X beam's top slot. |
| `xy_joint_beam_a_head`, `_b_head` | `socket` | female, `m5-clearance-hole`, 0 | The counterbore floors at z −5.5. They take an M5x10 BHCS. That screw is not catalogued yet; the key is shared with `bhcs-m5x30.head_seat`. |
| `xy_joint_beam_key` | `profile` | male, `tslot-2020-6mm`, 2 | (s·22.5, 0, −10). It mates the X beam's `slot_{face}_{a\|b}` at its default `slot_station_mm` of 10. |
| `xy_joint_stack_bolt` | `socket` | female, `m5-clearance-hole`, 0 | The bridge top, (s·32, −7.006, 31). It mates `shcs-m5x40.head_seat`. The `journal` is 14 for the low stack (left) and 5 for the high one (right). |
| `xy_joint_stack_roof`, `_floor` | `surface` | neutral, `m5-axle-stack-face`, 0 | `zs ± 5`. The stack's outer shims bear here. |
| `xy_joint_idler_bolt` | `socket` | female, `m5-clearance-hole`, 0 | (s·37, 6.366, 31). It mates `shcs-m5x40.head_seat`. The `journal` is 5.5 for the high idler (left) and 14.5 for the low one (right), at width 9. |
| `xy_joint_idler_roof`, `_floor` | `surface` | neutral, `m5-axle-stack-face`, 0 | `zi ± idler_width / 2`. They mate the idler's `face_a` and `face_b`. |

**Gate results.** The render-time frame gate checks all twelve interfaces at the defaults and at
every preset, mirrored ones included: 60 of 60 pass.

**Closure.** The keystone test `tests/test_catalog_gantry.py` (hyperobjects-spec PR #47) closes
this chain: C extrusion → MGN9 rail at its 25 mm setback (guide p. 88) → MGN9H → this joint →
M5x40 → shim → F695 → F695 → shim between the floor and roof faces, and M5x40 → idler. That
places the stack and the idler on their belt levels.

**Not modelled:**
- the belt;
- the endstop and its wiring channel;
- the X carriage.

## Presets

- **Left Joint, 350 Gantry.** The defaults, stated explicitly.
- **Right Joint, 350 Gantry.** The mirrored hand. The render check notes that this preset renders
  "identical to the defaults". That note is expected: the check compares volume only. A
  reflection keeps volume, and the swapped columns happen to total the same length. The
  bounding box moves from x −10…61 to x −61…10.
- **Left / Right Joint, 10 mm-Wide Idler.** For a Gates-style idler 10 mm wide, flange to flange.

## Hyperobject Profile

- **Domain:** industrial.
- **Material awareness:** `tolerance_by_material`.
- **Societal benefit:** an open, printable XY joint for stacked-belt CoreXY gantries. It uses only
  off-the-shelf M5 screws, T-nuts, F695 bearings and a standard GT2 idler. Its belt geometry is
  derived from cited belt and bearing data.
- **License:** CERN-OHL-W-2.0.

## Engine notes

- **Engine:** CadQuery (`main.py`), one body.
- **Sandbox-safe:** it reads `PARAM(lambda: name, default)`, dispatches on `target_part`, and
  assigns the solid to `result`.
- **Keystone needed:** a keystone with the gantry catalog (`mgn9-carriage`, hyperobjects-spec
  PR #47). Until `SPEC_PIN` moves past it, `y4d-spec check` reports that size key as unknown.

## Resumen (es)

Unión XY impresa para un pórtico CoreXY con dos bandas apiladas (tipo 2.4):
- **Montaje:** corre sobre un bloque MGN9H y sostiene el extremo de la viga X de perfil 2020 con
  dos tuercas en T M5.
- **Bandas:** gira una banda en una polea dentada GT2 de 20 dientes y la otra en una pila de
  dos rodamientos F695, cada una sobre un eje M5x40 que cuelga de un puente.
- **Manos:** la versión derecha es el espejo e intercambia los niveles de banda.

Es un diseño original. La guía de armado de la Voron 2.4r2 (GPL-3.0) se cita solo por página
(pp. 88, 97–100, 104, 125, 131); no se copia su geometría. Licencia CERN-OHL-W-2.0.
