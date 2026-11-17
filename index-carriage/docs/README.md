# Index Carriage

A parametric sleeve that slides on a rectangular column and locks at a height
with an index pin, generated with **CadQuery** (B-Rep). The pin passes through a
guide boss on the sleeve into one of a row of holes in the column. Below the
boss, a yoke of two ears hangs a block, a hook or an arm from a pivot pin. It is
the moving part of a height-adjustable stand, rack, jig or cable machine.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the sleeve height decides

A sleeve on a column is held square only by its own length. A load hung in front
of it tips it until the top edge bears on one face of the column and the bottom
edge on the opposite face. With `slide_clr` of clearance on each side, the sleeve
can tilt by about

```
tilt ≈ 2 × slide_clr ÷ sleeve_h        (radians)
```

and the two edge forces that resist a load `F` hung at a distance `a` in front
of the column are each about `F × a ÷ sleeve_h`. A longer sleeve tilts less,
presses less on the column and slides more freely under load. The manifest warns
when the sleeve is shorter than the column is deep.

The index pin carries the load along the column in shear. The boss keeps the pin
square to the column, so a longer boss guides the pin better and gives a spring
plunger more thread to hold, if one is fitted in place of a plain pin.

## Part

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Carriage with Yoke** | `carriage` | The sleeve, its pin boss and its two-ear yoke, as one body. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `column_w`, `column_d` | 20–120 mm | Outside width and depth of the column; the index holes are in the face `column_w` wide |
| `slide_clr` | 0.2–2 mm | Gap between the column and the sleeve on each side |
| `sleeve_wall` | 3–12 mm | Wall thickness of the sleeve |
| `sleeve_h` | 30–200 mm | Length of the sleeve along the column |
| `pin_d` | 4–16 mm | Index pin diameter; the bore is 0.4 mm larger |
| `boss_l` | 8–40 mm | How far the guide boss stands out from the sleeve |
| `ear_h`, `ear_t` | 20–100 mm, 4–12 mm | Height of each ear where it meets the sleeve, and its thickness |
| `yoke_gap` | 8–80 mm | Clear width between the two ears |
| `ear_reach` | 10–80 mm | Distance from the sleeve face to the centre of the pivot bore |
| `pivot_d` | 4–16 mm | Bore through both ears for the pivot pin |

The pin axis is `3 + (pin_d + 12) ÷ 2` mm below the top of the sleeve, centred
on the column width. The boss wall and the wall of the eye around the pivot bore
are both 6 mm.

## Constraints

- The sleeve is tall enough to stack the pin boss above the yoke
  (`sleeve_h ≥ ear_h + pin_d + 22`).
- Neither the pin boss nor the yoke is wider than the sleeve.
- The ears are at least as tall as the eye around the pivot bore, and the pivot
  stands far enough out for that eye to clear the sleeve face.
- Warnings: a clearance under 0.3 mm per side can bind a printed sleeve, and a
  sleeve shorter than the column is deep tilts and binds under an offset load.

## Making it

The column axis is vertical, so the sleeve prints upright with no supports
inside it; the boss and the ears overhang and want supports, or the part can be
printed lying on its back face. Welded from plate and tube it is a sleeve, a
turned boss and two profiled ears. Every added feature is let into the sleeve
wall by half its thickness, so the model has a real overlap at each join.

This cartridge is a geometry family, not a rated component. The hung load goes
through the pivot, the ears, the sleeve and one index pin in shear. The safe
working load depends on the material, the process, the pin and the column, and
has to be established by whoever builds and uses it.

## Interfaces

- **Column section and sliding fit** (`column_sleeve`): `column_w`, `column_d`, `slide_clr`.
- **Index pin bore** (`index_pin`): `pin_d`, `boss_l`.
- **Yoke pivot** (`yoke_pivot`): `yoke_gap`, `pivot_d`, `ear_reach`.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
