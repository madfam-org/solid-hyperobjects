# Machine Guard

A parametric fixed guard that bolts over a moving or hot part of a machine,
generated with **CadQuery** (B-Rep). It covers the part, keeps a fixed gap from
it, and leaves only the openings the machine needs: a slot for a cable, vents
for heat, a notch for a shaft.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the openings decide

A guard works by distance: a hand cannot reach the hazard through it. Every
opening is therefore a dimension that matters, and the manifest holds four of
them as errors, not warnings:

```
gap    < 9.5 mm     between a rotating drum and the hood
slot_w < 9.5 mm     the slot a cable or belt leaves through
wall_slot_w < 9.5 mm   the low slot in a side wall, when it is on
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
| **Drum Hood** | `drum_hood` | An arch over a rotating drum, spool, pulley or roller. It follows the rim at `gap`, comes straight down to two bolted feet, and can close one end with a wall. A slot in the arch lets the cable or belt out over the top; an optional slot low in a side wall lets it out from the underside. |
| **Box Cover** | `box_cover` | A five-sided cover over a drive, a coupling, a braking resistor or a terminal row, with vent slots across the top and a notch at the foot of one end wall. |

With `end_wall` on, the hood suits a drum overhung on its shaft: the support
closes one end and the wall closes the other. With it off the hood is a tunnel
and both ends are closed by the supports that carry the drum. Either way the
hood drops over the drum from above and never has to be threaded onto a shaft.

The end wall is solid: it crosses the shaft line and has no hole for a shaft.
A drum carried between two plates or bearings, with its shaft passing through
both ends, cannot take a hood with `end_wall` on. Turn `end_wall` off and let
the two plates close the ends of the tunnel.

## Where the cable leaves

The arch slot (`cable_slot`) sits round the top half, from the top of the arch
(`slot_angle` 0) to 80° toward +Y. It serves a cable that leaves over the drum.

A cable that leaves the underside of the drum, toward a pulley at floor level,
crosses a straight side wall below the axis. The low slot (`wall_slot`, off by
default) is for that: a horizontal slot through one wall, `wall_slot_len` long
and centred on the drum like the arch slot, `wall_slot_w` wide, with its centre
`wall_slot_h` above the mounting face. It is in the +Y wall, or in the -Y wall
with `wall_slot_far` on. Set `wall_slot_h` to the height at which the cable
crosses the wall: for a level cable off the underside, the axis height less
the radius the cable is wound at.

The low slot stays in the straight wall. It keeps 2 mm of wall above the foot,
so a cable that runs lower than `foot_t` + 2 mm + half the slot width cannot
pass: raise the axis (stand the drum and the hood on a higher base) until it
can. It does not reach above the axis, and the arch slot does not reach the
last 10° above it, so a cable that crosses within a few millimetres of the
axis height on the +Y side has no slot in this version. With both slots on the
same side the low one stays 2 mm below the arch one, so the two never join
into a wider opening.

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `drum_d`, `drum_w` | 30–400 mm, 10–300 mm | Largest rotating diameter and overall width under the hood |
| `axis_h` | 20–300 mm | Height of the drum axis above the mounting face |
| `gap` | 1–12 mm | Fixed gap between the rim and the hood (must stay under 9.5 mm) |
| `end_clear` | 1–10 mm | Space between each drum face and the end of the hood |
| `end_wall` | on / off | Close the +X end with a wall |
| `cable_slot`, `slot_w`, `slot_len`, `slot_angle` | on / off, 3–12 mm, 5–300 mm, 0–80° | The cable slot: width (under 9.5 mm), length along the axis, and position round the arch from the top toward +Y |
| `wall_slot`, `wall_slot_far`, `wall_slot_h`, `wall_slot_w`, `wall_slot_len` | on / off (default off), on / off, 5–290 mm, 3–12 mm, 5–300 mm | The low cable slot in a straight side wall: which wall (+Y, or -Y with `wall_slot_far`), height of its centre above the mounting face, width up the wall (under 9.5 mm), length along the axis |
| `inner_w`, `inner_d`, `inner_h` | 40–1000 mm, 40–600 mm, 20–400 mm | Inside length, depth and height of the box cover |
| `vent_count`, `vent_w` | 0–40, 2–12 mm | Vent slots across the top and their width (under 9.5 mm) |
| `notch`, `notch_w`, `notch_h` | on / off, 4–200 mm | Notch at the foot of the -X end wall |
| `wall` | 1.5–8 mm | Shell thickness |
| `foot_w`, `foot_t`, `bolt_d` | 8–40 mm, 2–10 mm, 2.5–8.5 mm | Feet and their bolt clearance holes |

The feet carry two bolt holes per side, and one more per 200 mm of length.

## Constraints

- The openings stay under 9.5 mm: the rim gap, the arch slot, the low slot
  when it is on, the vents (errors).
- The axis sits at least 1 mm higher than the drum radius, so the drum clears
  the mounting face.
- The cable slot is no longer than the drum is wide.
- The low slot, when on: no longer than the drum is wide, so it stays clear of
  the ends of the hood and of the end wall; at least 2 mm of wall between it
  and the foot; no higher than the axis; and at least 2 mm below the arch slot
  when both are on the +Y side.
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
