# Winch Cradle

The frame of a direct-drive winch, generated with **CadQuery** (B-Rep): a
base, a plate the motor bolts onto by its face, and room for a drum on the
shaft. It is the body of a small hoist, a cable-driven actuator, a spooler, a
reel winder or a test rig.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the motor face decides

Motors that mount by a flange differ in size and agree in kind: a round
**pilot** that centres the motor, and bolts on a **circle** round it. This
cartridge takes those four numbers from the motor's data sheet instead of a
frame-size name, so one family fits a servo, a gearmotor or a stepper.

| The data sheet says | Enter |
| :--- | :--- |
| Pilot (register, spigot) diameter | `pilot_d`, a little larger so the pilot enters |
| Bolt circle diameter | `bolt_circle` |
| A square bolt pattern of side *s* | `bolt_circle` = 1.414 × *s*, `bolt_count` = 4 |
| Bolt size | `bolt_d`, the clearance hole for it |

The bolts are spaced evenly and turned half a step, so no bolt sits at the
very bottom where the base is. The plates are square, and the base is as wide
as they are. Their side is

| `compact_plate` | Plate side |
| :--- | :--- |
| off (default) | `bolt_circle` + `bolt_d` + 2 × `plate_margin`: square on the whole circle |
| on | *k* × `bolt_circle` + `bolt_d` + 2 × `plate_margin`: square on the bolts where they are |

Turned half a step, four bolts reach only 0.707 of the circle's radius
sideways and upward, and eight reach 0.924, so *k* is 0.707 for 4 bolts and
0.924 for 8. Every other count has a bolt at the very top or on the
horizontal, *k* is 1 and the plate does not change. A compact plate is never
narrower than `pilot_d` + 2 × `plate_margin`. For a 145 mm circle of four
9 mm holes with a 10 mm margin the side is 174 mm, or 131.5 mm compact.

The shaft axis stands `axis_h` above the mounting face. It has to be high
enough for four things, and the manifest checks each: the lowest face bolts,
the pilot bore and the outboard bore must each keep 2 mm of plate above the
base, and the drum must turn 3 mm above it. The lowest bolts are not a full
radius below the axis but the radius times this factor:

| Face bolts | 3 | 4 | 5 | 6 | 7 | 8 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Lowest bolt below the axis, × radius | 0.500 | 0.707 | 0.809 | 0.866 | 0.901 | 0.924 |

So the lowest axis is the largest of `plate_t` + 2 + `bolt_d` / 2 + factor ×
`bolt_circle` / 2, `plate_t` + 2 + `pilot_d` / 2, `plate_t` + 2 +
`bearing_d` / 2 and `plate_t` + 3 + `drum_d` / 2. For a 110 mm pilot and four
9 mm holes on 145 mm in a 10 mm plate that is 67.8 mm, set by the bolts.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Cradle** | `cradle` | A U: base, motor plate and an outboard plate with a bore for the bearing that carries the far end of the shaft. For a drum under a real pull. |
| **Overhung Cradle** | `cradle_overhung` | An L: base and motor plate. The drum hangs on the motor's own bearings, so it suits a short drum and a light pull. |

With `hood_seats` on, either cradle also carries four tapped holes through its
base, in two rows along the shaft and centred under the drum: the seat of a
fixed guard that stands on the base over the drum. It is off by default.

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `pilot_d` | 10–150 mm | Bore for the motor's pilot and shaft |
| `bolt_circle`, `bolt_d`, `bolt_count` | 25–200 mm, 3.4–12.5 mm, 3–8 | The motor's face bolts |
| `drum_d`, `drum_w` | 30–400 mm, 10–300 mm | Largest rotating diameter and overall width of the drum |
| `end_gap` | 2–40 mm | Space between each face of the drum and the plate beside it |
| `axis_h` | 20–300 mm | Height of the shaft axis above the mounting face |
| `plate_t`, `plate_margin` | 4–20 mm, 5–40 mm | Thickness of base and plates, and material outside the bolt holes |
| `compact_plate` | on / off | Size the plates on the bolts where they are instead of on the whole circle (smaller with 4 or 8 bolts) |
| `mount_bolt_d` | 3.4–12.5 mm | Holes through the base: the clearance hole of the bolt (5.5 for M5, 6.5 for M6, 8.5 for M8, 10.5 for M10) |
| `bearing_d` | 8–120 mm | Bore in the outboard plate (Cradle only; 22 seats a 608) |
| `hood_seats`, `hood_seat_px`, `hood_seat_py`, `hood_hole_d` | on / off, 0–340 mm, 20–480 mm, 2.5–6.8 mm | Tapped holes through the base for the feet of a hood over the drum: the pitch of the two holes of each row along the shaft (0 gives one hole per row), the spacing of the two rows, and the hole diameter (the tap drill: 4.2 for M5, 5 for M6, 6.8 for M8) |

## Constraints

- The pilot bore leaves 2 mm of plate before the bolt holes, and neighbouring
  bolt holes keep 2 mm between them.
- The axis is high enough for the lowest face bolts (by bolt count), the pilot
  bore, the outboard bore and the drum.
- The outboard bore leaves 4 mm of plate on each side, compact plate or not.
- The base between the plates is long enough for its mounting holes.
- A gap under 3 mm beside the drum is flagged.
- The hood seat holes stay on the base between the plates, 3 mm clear of each,
  and their rows lie between the two rows of mounting holes with 3 mm of base
  between the holes. Two holes in a row keep 3 mm between them.
- Seat rows closer together than the drum is wide, and a base thinner than the
  seat hole, are flagged.

## A hood over the drum

The seats are made for the `drum_hood` of the **machine-guard** cartridge, an
arch over the drum with a foot on each side. Give the hood the same `drum_d`
and `drum_w` as the cradle and an `axis_h` of the cradle's `axis_h` minus
`plate_t`, because the hood stands on the top of the base. Its foot holes are
then at

| Cradle | From the hood |
| :--- | :--- |
| `hood_seat_px` | `drum_w` + 2 × `end_clear` − 2 × (the larger of `bolt_d` and `foot_w` / 2) |
| `hood_seat_py` | `drum_d` + 2 × `gap` + 2 × `wall` + `foot_w` |
| `hood_hole_d` | the tap drill of the thread the hood's `bolt_d` clears (4.2 under a 5.5 hole) |

For a 100 × 70 mm drum the hood's defaults give 60, 130 and 4.2, which are the
cradle's defaults. A hood under 400 mm long has two holes in each foot, so
every drum this cradle accepts gives a four-hole pattern; a hood too short for
two has one in the middle of each foot, which is a pitch of 0.

Three things the manifest cannot check, because they depend on the hood:

- **The base must be as wide as the hood.** Each foot reaches `foot_w` / 2
  beyond its row of holes, and the base is only as wide as the plates
  (the plate side above). A small motor face under a wide drum gives a base
  narrower than the hood: at this cartridge's defaults the base is 100.5 mm
  wide and the hood for its drum is 146 mm. Widen `plate_margin`, or the seats
  do not fit. A compact plate narrows the base, so under a hood it needs the
  margin back: the hood sets the width, not the motor.
- **The heads of the mounting bolts must clear the feet.** The mounting holes
  are `mount_bolt_d` + 4 in from each edge of the base. Leave the head or the
  washer of that bolt room outside the foot.
- **The hood must fit between the plates.** In the Cradle that means an
  `end_clear` no larger than `end_gap` and the hood's end wall off: the shaft
  runs through to the outboard plate, so the hood is a tunnel between the two
  plates. In the Overhung Cradle the end wall closes the free end of the drum.

## Making it

The cradle is one profile across its width: a U or an L. It is cut from a
length of channel or angle, bent from plate, milled from a block, or printed
on its side. The plate the motor seats on has to be flat and square to the
base; in a printed cradle that face is a side wall and comes out true.

This cartridge is a geometry family, not a rated winch. The pull on the cable
bends the motor plate and loads the motor's bearings (all of it, in the
overhung cradle), and a drum that turns is a hazard in itself: cover it. What
the frame carries depends on the material, the plate thickness and the
fasteners, and has to be established by whoever builds and uses it.

## Interfaces

- **Motor face** (`motor_face`, `overhung_motor_face`): the outside of the
  motor plate, on the shaft axis, facing the motor. No size key is declared:
  the face is given by four parameters and a size key reads one.
- **Outboard bearing bore** (`outboard_bore`): a 608 seat when `bearing_d`
  is 22.
- **Base mounting holes** (`base_mount`, `overhung_base_mount`): the
  underside of the base. The size key follows `mount_bolt_d`:
  `m5-screw-joint` at 5.5, `m6-screw-joint` at 6.5, `m8-screw-joint` at 8.5,
  `m10-screw-joint` at 10.5. Any other diameter declares no key.
- **Hood seats** (`hood_seat`, `overhung_hood_seat`): the top of the base under
  the drum axis, facing up. Polarity female. The size key follows
  `hood_hole_d`: `m5-screw-joint` at 4.2, `m6-screw-joint` at 5,
  `m8-screw-joint` at 6.8. The frame is on the face whether or not the holes
  are drilled; turn `hood_seats` on to drill them. The pitches are parameters,
  not a standard: the seats mate a hood only if its foot holes have the same
  pitches, which the size key does not check.
- **Drum space** (`drum_space`): `drum_d`, `drum_w`, `end_gap`, `axis_h`.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
