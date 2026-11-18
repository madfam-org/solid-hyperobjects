# Load Cell Mount

The two parts a bar load cell needs to become a measuring point, generated
with **CadQuery** (B-Rep): a base that holds the fixed end and stops an
overload, and a bracket that brings the load onto the live end.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the mount decides

A bar (bending beam) load cell is a short metal bar with two bolt holes at each
end and a thinned section in the middle. It measures by bending. Three things
about the mount decide whether it reads true:

- **The bar must be free.** Only the fixed end touches the base. The riser
  lifts the bar `riser_h` above the plate, so the middle and the live end hang
  in the air.
- **The bar must not bend too far.** A stop stands under the live end,
  `stop_gap` below the unloaded bar. Set the gap just above the bar's
  deflection at full load (the maker's data sheet gives it): the bar then
  meets the stop before an overload damages it.
- **The load must arrive at the live end, in line.** The bracket bolts onto
  the live pair of holes and carries the load on a cross axle above them.

Everything is sized from the bar's own interface: its width, and for each end
the pitch of its pair of holes and their distance from the end. The two ends
are declared separately because on many bars they differ. The defaults are an
80 mm bar, 12.7 mm wide, with holes 15 mm apart starting 5 mm from each end.
Read the real values from the data sheet of the load cell at hand.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Base** | `base` | A plate with four mounting holes, a riser the fixed end bolts onto from below (the bolt heads sink into the underside), and the overload stop. |
| **Load Bracket** | `load_bracket` | A pad with two bolt holes that sits on the live end, and two ears with an axle bore across them. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `beam_l`, `beam_w` | 40–250 mm, 8–60 mm | Length and width of the bar |
| `hole_pitch`, `end_margin` | 8–60 mm, 3–20 mm | Fixed end: distance between its two holes, and from the end to the first |
| `live_pitch`, `live_margin` | 8–60 mm, 3–20 mm | Live end: the same two distances |
| `fixed_bolt_d`, `live_bolt_d` | 3.4–10.5 mm | Clearance holes for the bolts into the fixed and the live end |
| `riser_h` | 2–30 mm | Height of the bar above the plate |
| `stop_gap` | 0.2–5 mm | Gap between the unloaded bar and the overload stop |
| `base_t`, `base_margin`, `mount_bolt_d` | 4–20 mm, 8–40 mm, 3.4–10.5 mm | Plate thickness, its margin round the bar, and the mounting holes in that margin |
| `pad_t` | 3–12 mm | Thickness of the bracket's pad |
| `yoke_gap`, `ear_t` | 6–80 mm, 3–12 mm | Clear width between the ears, and their thickness |
| `axle_d`, `axle_h` | 3–20 mm, 8–80 mm | Axle bore, and its height above the top of the bar |

## Constraints

- The stop gap is smaller than the riser, or there is no stop.
- The two bolted ends leave at least 10 mm of free bar between them.
- Each pair of holes keeps 2 mm between its holes and stays inside the bar.
- The plate margin leaves 2 mm of material on each side of a mounting hole.
- The yoke is wide enough for the bolt heads, and the axle passes above them.
- A riser under 3 mm is flagged: dirt under the bar can carry part of the load.

## Making it

Both parts print flat without supports, or are milled from bar stock. The
fixed-end bolts carry the whole load as a moment, so the base wants a stiff
material and a flat seat: a printed base suits a few kilograms, a machined one
the rest. Use the bolts and the torque the load cell's data sheet names.

This cartridge is a geometry family, not a calibrated instrument. The reading
depends on the load cell, its amplifier and a calibration against known
weights after assembly, and the stop gap has to be checked with a feeler gauge
on the real parts.

## Interfaces

- **Fixed-end seat** (`fixed_seat`): the top of the riser. An M5 screw joint
  when `fixed_bolt_d` is 5.5.
- **Base mounting holes** (`base_mount`): the underside of the plate.
- **Live-end seat** (`live_seat`): the underside of the bracket's pad.
- **Load axle bore** (`load_axle`): the bore through the ears; an 8 mm ground
  shaft when `axle_d` is 8.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
