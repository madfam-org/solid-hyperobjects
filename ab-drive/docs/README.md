# A/B Drive

A printed **A/B drive unit** for a CoreXY gantry whose two belts run **stacked on two levels**, a
2.4-class "flying gantry". It is generated with **CadQuery** (B-Rep).

It joins the rear end of a gantry Y extrusion (the 2020 "C" extrusion) to the rear gantry beam
(the "E" extrusion), using M5 screws into T-nuts. It hangs a **NEMA 17** under a motor plate,
behind the extrusion's end. It carries three belt elements:

- **The pulley.** The motor's **GT2 20T pulley** drives this unit's belt.
- **The backside stack.** An F695 stack that the belt's back runs on. It wraps the belt **125°**
  round the pulley.
- **The pass-through stack.** An F695 stack that the *other* belt's teeth run on. It turns that
  belt from the gantry side onto the rear beam, on the other level.

There are left (B) and right (A) versions.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and configurator:
[Yantra4D](https://app.yantra4d.com).

> **Original design.** The functional brief comes from a Voron 2.4-class gantry. It is cited by
> page and section only, from the *Voron 2.4r2 build guide*, version 2023-07-04
> (VoronDesign/Voron-2 @ `a192410`, GPL-3.0):
> - pp. 73–80: the A and B drives carry a NEMA 17 with a GT2 20-tooth pulley, and F695 stacks on
>   M5x30 BHCS threaded into plastic;
> - pp. 85–87: the rear E extrusion, and the drives fixed to it with M5 T-nuts and M5x10 BHCS;
> - p. 95: the drives sit flush on the rear ends of the C extrusions;
> - pp. 125–127: the stacked CoreXY belt path.
>
> No Voron geometry, STL or CAD was copied, traced or derived. It is licensed CERN-OHL-W-2.0.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **A/B Drive** | `ab_drive` | The single unit. `mirrored` builds the right (A) drive. |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Hand | `mirrored` | off | Builds the right (A) drive. x is reflected. The pulley and the backside stack move to the high belt level, and the pass-through stack to the low one. |

## Belt geometry and the wrap rule

The model frame:
- **Origin:** on the C extrusion's top face, on its centreline, at its **rear** end face.
- **+x:** to the gantry's right.
- **+y:** to the back.
- **+z:** up.

Below, "inboard" is the distance toward the gantry's centre.

| Element | Inboard x | y | Level (left / right) | Belt contact |
| :--- | :--- | :--- | :--- | :--- |
| Pulley P (motor shaft) | 16.332 | 22.000 | 22 / 31 | teeth, pitch radius 6.366 |
| Backside stack Q | 31.375 | 27.792 | 22 / 31 | back, effective radius 7.006 |
| Pass-through stack S | 38.148 | 13.272 | 31 / 22 | teeth, effective radius 7.514 |

- **The outer run,** to the front idler, leaves P at inboard 9.966. That is the run `ab-front-idler`
  and `xy-joint` make: 32 − 7.006 − 2 × 7.514.
- **The other belt's run** from the XY joint comes up at 30.634 = 37 − 6.366. S turns it onto the
  rear run.
- **The rear runs** of both belts lie on y = 20.786, one above the other.
- **The design wrap on the pulley is 125°.** The P–Q span is 9 long and leaves P at 55°. The 9 keeps
  the pulley's Ø16 flange (Adafruit 1251) and the F695's Ø15 flange 0.6 apart.
  - **The rule:** SDP/SI's Technical Section §13.3 (p. T-35) asks for at least 6 teeth in mesh and
    60° of wrap on a loaded pulley.
  - **What that means here:** a 20-tooth pulley turns 18° per tooth, so it needs **≥ 108°**.
  - **Measured:** lane P6-GANTRY's layout check computes 125.0° (6.9 teeth) on both drives, at
    every gantry position.
- **Effective radii:**
  - teeth on a smooth F695: 13 / 2 + 1.014;
  - back on it: 13 / 2 + 0.506.

  The offsets come from catalog `gt2-belt-6mm`: B 1.52 and T 0.76 from Pfeifer 2MR/PGGT2, U 0.254
  from SDP/SI Table 4. The pulley's pitch diameter is 12.73 (SDP/SI Table 33).

**The motor and the pulley.**
- **The motor face sits at z 10 in both hands.** The plate's underside carries the 4 × M3 on 31
  and a Ø24 pass for the Ø22 pilot.
- **The pulley's belt mid-plane is 8 from its face A.** That is a **convention**, shared with the
  keystone's `gt2-pulley-20t-5mm` `belt_engagement` (mid-length of the 16 mm body); no cited source
  places the toothed section.
- **The resulting shaft seats (`nema-17-48mm.shaft_seat_mm`):**
  - **4** for the left (B) drive, which puts the belt at 22;
  - **13** for the right (A) drive, which puts the belt at 31. That pulley sits 11 mm on the
    24 mm shaft.
- If a later keystone cites a different belt plane, P6-ASM changes only those two seats.

## Sources and conventions

**Cited facts**
- **NEMA 17** (keystone `nema-17-48mm`, from LDO and Nanotec): face 42.3, 4 × M3 on 31 (thread
  4.5 deep), pilot Ø22 × 2, shaft 24. The motor body clears the C and E extrusions: it starts at
  y 0.85, behind their end faces.
- **ISO 7380-1 M5x30 BHCS** (guide pp. 73, 77): l 30. With heads on the bridge top (z 42), the
  tips end at z 12. That is 2 above the motor face, in a Ø4.2 pilot in the plate.
- **ISO 7380-1 M5x10 BHCS** (guide pp. 86–87): the head seats sit 4.5 above the C and E top faces,
  so 5.5 of the screw passes into the T-nut.
- **MISUMI HFS5-2020:** the 20 profile, 6 mm slots with 2 mm lips, and Ø4.2 for M5. The tongues
  are 2 mm deep.
- **The 350 gantry** (the coordinator's cited lengths): E 340 between C centres at ±227.5, so E's
  end is 57.5 inboard of the rail centre.

**Conventions (not sourced)**
- **Levels:** belts at 22 and 31; the plate top at 17 (the low stacks' floor); the bridge from
  36 to 42.
- **Pulley position:** the axis 22 behind the C end.
- **Wrap geometry:** 125° of wrap and a 9 mm P–Q span.
- **Stations:** the C and E screws sit at the slot stations 10 from each extrusion's end.
- **Pillars** stand off every belt line and clear of the screw and motor counterbores.

## Interfaces

Every frame reads `s = 1 − 2·mirrored`. This unit's level is `zp = 22 + 9·mirrored`; the other
belt's level is `zo = 31 − 9·mirrored`.

| Interface | Type | Polarity / key / symmetry | Where |
| :--- | :--- | :--- | :--- |
| `ab_drive_motor_face` | `bolt_pattern` | male, `nema-17-face`, 4 | (s·16.332, 22, 10), normal −z. It mates `nema-17-48mm.face`. |
| `ab_drive_c_mount` | `bolt_pattern` | male, `m5-screw-joint`, 0 | (0, −10, 0). It mates the C top slot's `tnut-2020-m5.thread`. |
| `ab_drive_c_mount_head` | `socket` | female, `m5-clearance-hole`, 0 | (0, −10, 4.5). |
| `ab_drive_c_key` | `profile` | male, `tslot-2020-6mm`, 2 | (0, −10, 0). It mates the C's top-face `slot_*_b` at `slot_station_mm` 10. |
| `ab_drive_e_mount`, `_head`, `ab_drive_e_key` | as the C ones | as the C ones | at (s·67.5, −10, 0 / 4.5). The rear beam's slot station is 10 from its end. |
| `ab_drive_backside_bolt` | `socket` | female, `m5-clearance-hole`, 0 | (s·31.375, 27.792, 42). It takes `bhcs-m5x30.head_seat`, with `journal_offset_mm` 15 (low) or 6 (high). |
| `ab_drive_backside_roof`, `_floor` | `surface` | neutral, `m5-axle-stack-face`, 0 | zp ± 5. |
| `ab_drive_pass_bolt` | `socket` | female, `m5-clearance-hole`, 0 | (s·38.148, 13.272, 42). The journal is 6 (high, left) or 15 (low, right). |
| `ab_drive_pass_roof`, `_floor` | `surface` | neutral, `m5-axle-stack-face`, 0 | zo ± 5. |

**Gate results.** The render-time frame gate checks all thirteen interfaces at the defaults and
at both presets: 39 of 39 pass. The cartridge uses only size keys already in the pinned keystone.

**Not modelled:**
- the belt;
- the motor's wiring;
- squaring adjustment (guide p. 122).

## Presets

- **Left (B) Drive, 350 Gantry:** the defaults.
- **Right (A) Drive, 350 Gantry:** mirrored, with the levels swapped. The render check notes that this preset renders
  "identical to the defaults". That note is expected: the check compares volume only, and a
  reflection with swapped column lengths keeps the volume. The bounding box moves from
  x −10…77.5 to x −77.5…10.

## Hyperobject Profile

- **Domain:** industrial.
- **Material awareness:** `tolerance_by_material`.
- **Societal benefit:** an open, printable A/B drive for stacked-belt CoreXY gantries. It uses a
  standard NEMA 17, a GT2 pulley, F695 bearings and M5 hardware, and its pulley wrap follows a
  cited teeth-in-mesh rule.
- **License:** CERN-OHL-W-2.0.

## Engine notes

- **Engine:** CadQuery (`main.py`), one body.
- **Sandbox-safe:** it reads `PARAM(lambda: name, default)`, dispatches on `target_part`, and
  assigns the solid to `result`.

## Resumen (es)

Unidad de tracción A/B impresa para un pórtico CoreXY con dos bandas apiladas (tipo 2.4):
- **Montaje:** une el extremo trasero de un perfil Y del pórtico con la viga trasera mediante
  tuercas en T M5, y cuelga un NEMA 17 bajo una placa.
- **Polea:** su banda abraza la polea GT2 de 20 dientes 125°, gracias a una pila F695 por el dorso.
  La regla citada (SDP/SI §13.3) pide al menos 6 dientes engranados, es decir ≥ 108°.
- **Otra banda:** una pila F695 de paso la gira en el otro nivel.

Es un diseño original. La guía de armado de la Voron 2.4r2 (GPL-3.0) se cita solo por página
(pp. 73–80, 85–87, 95, 125–127); no se copia su geometría. Licencia CERN-OHL-W-2.0.
