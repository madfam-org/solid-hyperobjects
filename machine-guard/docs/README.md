# Machine Guard

A parametric fixed guard that bolts over a moving or hot part of a machine,
generated with **CadQuery** (B-Rep). It covers the part, keeps a fixed gap from
it, and leaves only the openings the machine needs: a slot for a cable, vents
for heat, a notch for a shaft.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the openings decide

A guard works by distance: a hand cannot reach the hazard through it. Every
opening is therefore a dimension that matters, and the manifest holds three of
them as errors, not warnings:

```
gap    < 9.5 mm     between a rotating drum and the hood
slot_w < 9.5 mm     the slot a cable or belt leaves through
vent_w < 9.5 mm     each vent slot in a cover
```

9.5 mm (3/8 in) is the limit equipment-safety rules commonly set for a gap a
fingertip must not enter. Whether it is the right limit for a given machine is
decided by the standard that governs that machine, not by this cartridge: an
opening close to a hazard may need to be smaller still.

One opening is not held by a rule: the **end notch** of the box cover. It is
sized to the shaft or cable bundle that passes through it, and that part is
what closes it. A notch the passing part does not fill needs its own closure.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Drum Hood** | `drum_hood` | An arch over a rotating drum, spool, pulley or roller. It follows the rim at `gap`, comes straight down to two bolted feet, and can close one end with a wall. A slot lets the cable or belt out. |
| **Box Cover** | `box_cover` | A five-sided cover over a drive, a coupling, a braking resistor or a terminal row, with vent slots across the top and a notch at the foot of one end wall. |

With `end_wall` on, the hood suits a drum overhung on its shaft: the support
closes one end and the wall closes the other. With it off the hood is a tunnel
and both ends are closed by the supports that carry the drum. Either way the
hood drops over the drum from above and never has to be threaded onto a shaft.

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `drum_d`, `drum_w` | 30–400 mm, 10–300 mm | Largest rotating diameter and overall width under the hood |
| `axis_h` | 20–300 mm | Height of the drum axis above the mounting face |
| `gap` | 1–12 mm | Fixed gap between the rim and the hood (must stay under 9.5 mm) |
| `end_clear` | 1–10 mm | Space between each drum face and the end of the hood |
| `end_wall` | on / off | Close the +X end with a wall |
| `cable_slot`, `slot_w`, `slot_len`, `slot_angle` | on / off, 3–12 mm, 5–300 mm, 0–80° | The cable slot: width (under 9.5 mm), length along the axis, and position round the arch from the top toward +Y |
| `inner_w`, `inner_d`, `inner_h` | 40–1000 mm, 40–600 mm, 20–400 mm | Inside length, depth and height of the box cover |
| `vent_count`, `vent_w` | 0–40, 2–12 mm | Vent slots across the top and their width (under 9.5 mm) |
| `notch`, `notch_w`, `notch_h` | on / off, 4–200 mm | Notch at the foot of the -X end wall |
| `wall` | 1.5–8 mm | Shell thickness |
| `foot_w`, `foot_t`, `bolt_d` | 8–40 mm, 2–10 mm, 2.5–8.5 mm | Feet and their bolt clearance holes |

The feet carry two bolt holes per side, and one more per 200 mm of length.

## Constraints

- The three openings stay under 9.5 mm (errors).
- The axis sits at least 1 mm higher than the drum radius, so the drum clears
  the mounting face.
- The cable slot is no longer than the drum is wide.
- Each foot leaves at least 2 mm of material on both sides of its bolt hole.
- The vent slots keep at least 2 mm of solid top between them.
- The notch leaves at least 4 mm of end wall beside and above it.
- A rim gap under 2 mm is flagged, because a drum that runs slightly out of
  true can rub the hood (warning).

## Making it

Both parts are one profile along the feet, so they print standing on an end
(the tunnel hood) or on the feet with supports under the top, and they fold
from sheet as a single hat section with the ends added. In sheet metal the
vent slots are punched before folding.

This cartridge is a geometry family, not a certified guard. A guard on a real
machine also has to stay in place under a blow, resist the temperature of what
it covers, and be removable only with a tool; the material, the fasteners and
the governing standard decide those, and whoever builds and uses the machine
has to establish them.

## Interfaces

- **Drum envelope and rim gap** (`drum_envelope`): `drum_d`, `drum_w`, `axis_h`, `gap`, `end_clear`.
- **Hood feet** (`hood_feet`): the bolt pattern under the hood. Frame on the
  mounting face under the drum centre, normal toward the base; an M5 screw
  joint when `bolt_d` is 5.5.
- **Covered space** (`cover_space`): `inner_w`, `inner_d`, `inner_h`.
- **Cover feet** (`cover_feet`): the bolt pattern under the box cover, same
  frame and size key.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
