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

The plates are square on the bolt circle with `plate_margin` of material
outside the holes. The bolts are spaced evenly and turned half a step, so no
bolt sits at the very bottom where the base is.

The shaft axis stands `axis_h` above the mounting face. It has to be high
enough for two things, and the manifest checks both: the lowest face bolt must
clear the base, and the drum must turn above it.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Cradle** | `cradle` | A U: base, motor plate and an outboard plate with a bore for the bearing that carries the far end of the shaft. For a drum under a real pull. |
| **Overhung Cradle** | `cradle_overhung` | An L: base and motor plate. The drum hangs on the motor's own bearings, so it suits a short drum and a light pull. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `pilot_d` | 10–150 mm | Bore for the motor's pilot and shaft |
| `bolt_circle`, `bolt_d`, `bolt_count` | 25–200 mm, 3.4–12.5 mm, 3–8 | The motor's face bolts |
| `drum_d`, `drum_w` | 30–400 mm, 10–300 mm | Largest rotating diameter and overall width of the drum |
| `end_gap` | 2–40 mm | Space between each face of the drum and the plate beside it |
| `axis_h` | 20–300 mm | Height of the shaft axis above the mounting face |
| `plate_t`, `plate_margin` | 4–20 mm, 5–40 mm | Thickness of base and plates, and material outside the bolt holes |
| `mount_bolt_d` | 3.4–12.5 mm | Holes through the base |
| `bearing_d` | 8–120 mm | Bore in the outboard plate (Cradle only; 22 seats a 608) |

## Constraints

- The pilot bore leaves 2 mm of plate before the bolt holes, and neighbouring
  bolt holes keep 2 mm between them.
- The axis is high enough for the face bolts and for the drum.
- The outboard bore leaves 4 mm of plate on each side.
- The base between the plates is long enough for its mounting holes.
- A gap under 3 mm beside the drum is flagged.

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
  underside of the base; an M5 screw joint when `mount_bolt_d` is 5.5.
- **Drum space** (`drum_space`): `drum_d`, `drum_w`, `end_gap`, `axis_h`.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
