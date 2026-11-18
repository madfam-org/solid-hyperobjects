# Indexed Column

A parametric open rectangular tube with a row of index holes along one face,
generated with **CadQuery** (B-Rep). It is the fixed half of a pin-and-hole
height adjustment: a sleeve slides on the tube and a pin through the sleeve
drops into one of the holes. It is the post of a height-adjustable stand, rack,
jig or cable machine.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the hole row decides

The row is the adjustment. Hole `i` (counting from 1 at the lower end) is at

```
height(i) = first_hole + (i − 1) × hole_pitch
```

so `hole_pitch` is the height step, `hole_count` is the number of positions and
the travel from the lowest position to the highest is
`(hole_count − 1) × hole_pitch`. A finer pitch gives a finer adjustment and
leaves less wall between holes; the manifest refuses a pitch under one and a half
hole diameters.

Every hole takes material out of the face that carries it. Where the column
bends, the holed face is the weakened one, which is why the row usually goes on
a face that is not the most heavily loaded, and why the manifest warns when a
hole is wider than half the face.

The same parameters are a drilling plan. Read `first_hole`, `hole_pitch` and
`hole_count` off the manifest and they are the layout to mark on a length of
tube stock.

## Part

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Indexed Column** | `column` | The tube with its row of holes, one body. Lower end on Z = 0, holes in the front face. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `column_w`, `column_d` | 20–120 mm | Outside width and depth of the tube; the holes are in the face `column_w` wide |
| `wall` | 1.5–10 mm | Wall thickness |
| `length` | 100–2400 mm | Length of the column |
| `hole_d` | 4–17 mm | Hole diameter: the pin diameter plus its clearance |
| `hole_pitch` | 10–200 mm | Distance between the centres of neighbouring holes |
| `first_hole` | 5–1000 mm | Height of the centre of the lowest hole above the lower end |
| `hole_count` | 1–60 | Number of holes |
| `through` | on/off | Drill each hole through the back wall too, for a pin that passes right through |

## Constraints

- The row ends at least one hole diameter before the upper end, and starts at
  least one hole diameter above the lower end.
- Neighbouring holes keep at least half a diameter of wall between them.
- The hole fits between the two side walls.
- The tube stays open: at least 4 mm of bore in both directions.
- Warning: a hole wider than half the face removes most of the wall there.

## Making it

A column of working length is longer than a desktop printer's bed. The usual way
to make one is to drill a length of rectangular tube to this layout. For
printing, the `rect_40x60_printable` preset is a 240 mm section that prints
upright with no supports inside the tube; each hole prints as a small round
overhang in a vertical wall.

This cartridge is a geometry family, not a rated component. A column carries its
load in bending and in compression, and each pin position loads the edge of one
hole. The safe working load depends on the material, the wall, the length, how
the ends are held and the pin, and has to be established by whoever builds and
uses it.

## Interfaces

- **Column section** (`column_section`): `column_w`, `column_d`, `wall`.
- **Index hole row** (`index_holes`): `hole_d`, `hole_pitch`, `first_hole`, `hole_count`, `through`.

## Mating frames (assemblies)

Three interfaces carry a SEM-1 frame, so the column can be placed in an
assembly: stood in a socket, capped, and ridden by a sleeve.

- **`end_a`** and **`end_b`**: the two end faces of the tube. Origins `(0, 0, 0)`
  and `(0, 0, length)`, on the axis; normals `-z` and `+z`, out of each end;
  `x_axis` `+x`. Symmetry 2: the row of holes is on one face, so the section is
  the same again only after a half turn. Polarity male.
- **`column_section`**: the face a sleeve bears on, opposite the holes. Origin
  `(0, -column_d/2, first_hole)`, at the height of the first hole; normal `-y`,
  out of the rear face; `x_axis` `+z`, along the column. Symmetry 1. Polarity
  male. It declares `travel` along its `x` axis from 0 to
  `(hole_count - 1) * hole_pitch`: the span of the hole row.

All three share one size key, `{param: column_w, map: {"80": square-tube-80mm}}`.
The frames are verified against the rendered part at the defaults and every
preset (`y4d-spec check --render`).

Limits:

- **One section size.** The key resolves only at `column_w` = 80 mm. At any other
  width the interfaces have no size key, so a mate that needs one fails and names
  the slider value.
- **The key reads the width.** A size key follows one parameter, so a column
  80 mm wide and another depth would still resolve to the square's key. Keep
  `column_d` equal to `column_w` when you rely on it.
- **The holes are not a mating frame.** A sleeve slides continuously on
  `column_section`; that it locks only at a hole is not something a frame states.
  `index_holes` stays a descriptive interface.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
