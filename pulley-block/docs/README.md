# Pulley Block

A parametric enclosed housing for a cable or rope sheave, generated with
**CadQuery** (B-Rep). Two cheeks cover the sides of the sheave and a rim guard
follows its edge at a fixed gap, open only at the mouth where the cable enters
and leaves. It is the turning point of a hoist, a tackle, a cable-driven machine
or a clothes airer.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the gap decides

Where a cable runs onto a sheave is an in-running nip: it draws in whatever
touches it. The block cannot close the mouth, because the cable has to pass, but
it closes everything else. The rule the manifest enforces is on the gap that is
left around the rim:

```
rim_gap < 9.5 mm
```

A gap that does not change beside a moving part is safe for fingers only while a
fingertip cannot enter it, and 9.5 mm (3/8 in) is the limit equipment-safety
rules commonly set for that case. It is an error here, not a warning. Whether it
is the right limit for a given machine is decided by the standard that governs
that machine, not by this cartridge.

The mouth is derived, not chosen. It opens a chord as wide as the sheave plus
half the rim gap on each side, which is what two parallel legs of cable leaving
the sheave need (a wrap of 180° or more). With the default 90 mm sheave and 4 mm
gap the mouth spans 147° and the guard covers the other 213°.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Hanging Block** | `block` | A rounded lug above the guard with a pivot bore parallel to the axle, so the block swings in a yoke or a shackle. |
| **Fixed Block** | `block_fixed` | The same guard under a mounting plate with one bolt hole at each end, for a beam, a wall or a bench. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `sheave_d` | 30–200 mm | Outside (rim) diameter of the sheave the block houses |
| `sheave_w` | 8–40 mm | Width of the sheave along its axle |
| `axle_d` | 4–20 mm | Bore through both cheeks for the sheave axle |
| `rim_gap` | 1–12 mm | Fixed gap between the sheave rim and the guard (must stay under 9.5 mm) |
| `side_gap` | 0.5–3 mm | Clearance between each face of the sheave and its cheek |
| `wall` | 2.5–8 mm | Thickness of the cheeks and of the rim guard |
| `pivot_d`, `lug_rise` | 4–16 mm, 6–40 mm | Pivot bore, and its height above the outside of the guard (hanging mode) |
| `mount_bolt_d`, `plate_t` | 3.5–10.5 mm, 3–12 mm | Bolt clearance hole and plate thickness (fixed mode) |

The block is `sheave_w + 2 × side_gap + 2 × wall` wide: that is the opening a
yoke needs between its ears.

## Constraints

- The rim gap stays under 9.5 mm (error), and a gap under 1.5 mm is flagged
  because a sheave that runs slightly out of true can rub the guard (warning).
- The axle leaves at least 6 mm of sheave around it.
- The pivot bore clears the guard by at least 2 mm.
- The bolt hole is at most half the width of the block, so the plate keeps a
  wall on both sides of it.

## Making it

The body is a prism along the axle, so it prints lying on one cheek; the pocket
then bridges across the sheave diameter and needs supports, or the block can be
split at mid-width and bolted through the axle. Machined from plate it is two
cheeks and a spacer. The sheave is not part of this cartridge: any wheel whose
rim diameter and width match the pocket fits.

This cartridge is a geometry family, not a rated component. The whole pull on
the cable goes through the axle, the cheeks and the lug or the plate, at up to
twice the cable tension for a 180° wrap. The safe working load depends on the
material, the process and the fasteners, and has to be established by whoever
builds and uses it.

## Interfaces

- **Sheave pocket and axle** (`sheave_pocket`): `sheave_d`, `sheave_w`, `rim_gap`, `side_gap`, `axle_d`.
- **Hanging pivot** (`hang_pivot`): `pivot_d`, `lug_rise`, `wall`.
- **Mounting plate bolts** (`mount_plate`): `mount_bolt_d`, `plate_t`.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
