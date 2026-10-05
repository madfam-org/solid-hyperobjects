# A/B Front Idler

A printed **front idler** for a CoreXY gantry whose two belts run **stacked on two levels**, a
2.4-class "flying gantry". It is generated with **CadQuery** (B-Rep).
- **Mounting:** it sits flush on the front end of a gantry Y extrusion, a 2020 "C" extrusion
  carrying the MGN9 rail. M5 screws hold it to T-nuts in that extrusion's top and inner side
  slots.
- **The belt:** it turns one belt through 180° on a stack of **two F695 flanged bearings**
  (shim, F695, F695, shim) on an **M5x40** axle.
- **The pocket** is open to the back, where both runs of the belt leave.
- **Hands:** the left idler carries the B belt on the low level; the right one, mirrored, carries
  the A belt on the high level.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and configurator:
[Yantra4D](https://app.yantra4d.com).

> **Original design.** The functional brief comes from a Voron 2.4-class gantry. It is cited by
> page and section only, from the *Voron 2.4r2 build guide*, version 2023-07-04
> (VoronDesign/Voron-2 @ `a192410`, GPL-3.0):
> - pp. 65 and 69: the A and B idlers carry an F695 stack (M5 shim, F695, F695, M5 shim) on
>   an M5x40 SHCS;
> - pp. 91–93: the idlers sit flush with the front ends of the C extrusions, on M5 screws into
>   T-nuts;
> - p. 88: the MGN9 rail starts 25 mm from that end;
> - pp. 126–127: each belt makes a U-turn round the front idler.
>
> No Voron geometry, STL or CAD was copied, traced or derived. It is licensed CERN-OHL-W-2.0.
> It has no tension arm: the belt is tensioned at the X carriage, where the guide pulls both
> belt ends tight (p. 141).

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Front Idler** | `front_idler` | The single idler. `mirrored` builds the right (A) idler. |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Idler | `stack_y` | 16 mm | The stack's axle, measured from the extrusion's front end. At 16 its pilot clears the side screw; at 18 the flange stays ahead of the rail. |
| Hand | `mirrored` | off | Builds the right (A) idler: x is reflected and the stack moves to the high belt level. |

## Belt geometry

The model frame:
- **Origin:** on the C extrusion's top face, on its centreline, at its front end face.
- **+x:** to the gantry's right.
- **+y:** to the back, along the extrusion.
- **+z:** up.

**The stack sits 17.480 inboard of the rail centre.** That is where the gantry's two runs of
this belt put it:
- **The run toward the XY joint**, at 24.994. That is 32 − 7.006: the `xy-joint`'s stack sits 32
  inboard, and the belt's back runs on it.
- **The run toward the A/B drive**, at 9.966.

The belt's **teeth** run on this stack, so its centre lies one F695 running radius plus the
belt's **teeth-side offset** from each run: 13 / 2 + 1.014 = 7.514.
- The 1.014 is T + U. T = 0.76 comes from Pfeifer's 2MR/PGGT2 row; U = 0.254 from SDP/SI
  Table 4.
- Catalog `gt2-belt-6mm` records both values.
- The effective diameter is therefore 15.03 (ASM-1 §9).

**The belt mid-plane** is z 22 for the left (B) idler and z 31 for the right (A). The same levels
appear in `xy-joint` and `ab-drive`. The stack's mid-plane is where the plain faces meet, 5 from
either end: a 1 mm shim plus a 4 mm F695 (DIN 988, NSK F695ZZ).

## Sources and conventions

**Cited facts**
- **F695ZZ:** 5 × 13 × 4, flange 15 × 1 (NSK).
- **M5x40 SHCS, l 40 (ISO 4762).** With the head on the roof (z_belt + 10), the tip ends at
  z_belt − 30, in a Ø4.2 pilot. That is −8 for the left idler, in the block beside the extrusion,
  and +1 for the right. Ø4.2 is the hole MISUMI taps M5.
- **MISUMI HFS5-2020:** the 20 profile, 6 mm slots with 2 mm lips, and the side slot's centre 10
  below the top face. The tongues are 2 mm deep.
- **Guide p. 88:** the rail starts 25 from the end, so the body stops at y 24.
- **ISO 7380-1 M5 heads:** dk 9.5, counterbores Ø10.5. The head seats sit 10.5 from the clamped
  faces, so an M5x16 BHCS (guide p. 91) passes 5.5 into its T-nut, as in `corner-idler-bracket`.

**Conventions (not sourced)**
- **Slot stations:** both T-nuts sit 10 from the front end, `extrusion-2020`'s default
  `slot_station_mm`.
- **Walls:**
  - the outboard and inboard walls clear the belt's back and teeth by ≥ 1.5;
  - the front wall clears the U-turn by 1.5;
  - the roof is 5 thick.
- **Clearances:** Ø5.5 holes; tongues 5.8 wide.

## Interfaces

Every frame reads `s = 1 − 2·mirrored` and `zf = 22 + 9·mirrored`.

| Interface | Type | Polarity / key / symmetry | Where |
| :--- | :--- | :--- | :--- |
| `front_idler_top_mount` | `bolt_pattern` | male, `m5-screw-joint`, 0 | (0, 10, 0), normal −z. It mates `tnut-2020-m5.thread` in the C's top slot. |
| `front_idler_top_mount_head` | `socket` | female, `m5-clearance-hole`, 0 | (0, 10, 10.5), normal +z. It takes an M5x16 BHCS. |
| `front_idler_top_key` | `profile` | male, `tslot-2020-6mm`, 2 | (0, 10, 0). It mates the C's top-face `slot_*_a` at `slot_station_mm` 10. |
| `front_idler_side_mount` | `bolt_pattern` | male, `m5-screw-joint`, 0 | (s·10, 10, −10), normal −s·x. It mates the inner side slot's T-nut. |
| `front_idler_side_mount_head` | `socket` | female, `m5-clearance-hole`, 0 | (s·20.5, 10, −10), normal +s·x. |
| `front_idler_side_key` | `profile` | male, `tslot-2020-6mm`, 2 | (s·10, 10, −10). It mates the C's inner-face `slot_*_a`. |
| `front_idler_stack_bolt` | `socket` | female, `m5-clearance-hole`, 0 | (s·17.48, `stack_y`, zf + 10). It mates `shcs-m5x40.head_seat` with `journal_offset_mm` 5 (the roof). |
| `front_idler_stack_roof`, `_floor` | `surface` | neutral, `m5-axle-stack-face`, 0 | zf ± 5. The stack's outer shims bear here. |

**Gate results.** The render-time frame gate checks all nine interfaces at the defaults and at
every preset: 36 of 36 pass. The cartridge uses only size keys already in the pinned keystone.

**Not modelled:**
- the belt;
- a tension arm (tension comes from the belt ends at the X carriage).

## Presets

- **Left (B) Idler, 350 Gantry:** the defaults.
- **Right (A) Idler, 350 Gantry:** mirrored, on the high level.
- **Left (B) Idler, Stack Set Back:** `stack_y` 18.

## Hyperobject Profile

- **Domain:** industrial.
- **Material awareness:** `tolerance_by_material`.
- **Societal benefit:** an open, printable front idler for stacked-belt CoreXY gantries. It uses
  off-the-shelf M5 screws, T-nuts and F695 bearings, and its belt runs are derived from cited belt
  and bearing data.
- **License:** CERN-OHL-W-2.0.

## Engine notes

- **Engine:** CadQuery (`main.py`), one body.
- **Sandbox-safe:** it reads `PARAM(lambda: name, default)`, dispatches on `target_part`, and
  assigns the solid to `result`.

## Resumen (es)

Polea loca frontal impresa para un pórtico CoreXY con dos bandas apiladas (tipo 2.4):
- **Montaje:** se asienta al ras en el extremo frontal de un perfil Y del pórtico, sujeta con
  tornillos M5 a tuercas en T.
- **Banda:** la gira 180° en una pila de dos rodamientos F695 sobre un eje M5x40.
- **Manos:** la izquierda lleva la banda B en el nivel bajo; la derecha, en espejo, la banda A
  en el nivel alto.

Es un diseño original. La guía de armado de la Voron 2.4r2 (GPL-3.0) se cita solo por página
(pp. 65, 69, 88, 91–93, 126–127, 141); no se copia su geometría. Licencia CERN-OHL-W-2.0.
