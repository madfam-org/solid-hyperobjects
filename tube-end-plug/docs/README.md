# Tube End Plug

A plug for the open end of a square or rectangular tube, generated with
**CadQuery** (B-Rep): a flange that covers the end and an insert that enters
the tube. Plain, it closes the tube; with a bolt seat, it makes the end of the
tube a place to bolt something on.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the tube decides

The plug is drawn from the tube, not the other way round. Measure three
things on the tube in hand, because nominal sizes hide real differences:

- **The outside** (`tube_w` × `tube_d`). The flange is exactly this size, so
  it sits flush with the tube's faces.
- **The wall** (`tube_wall`). The insert is the outside less two walls less
  the fit. Welded tube has a seam bead inside one wall; measure across it.
- **The inside corners.** Formed tube is round inside its corners. The insert
  has its corners cut by `corner_c` so it does not ride on them; raise it if
  the plug stops short of seating.

`fit` is the clearance per side. Zero gives a press fit in a soft material;
0.2 to 0.4 mm slides in and wants glue or the bolt.

## The bolt seat

With `bolt_seat` on, the insert is solid. A clearance hole runs along the
axis, and a hexagonal pocket in the inner end holds a nut so it cannot turn.
Put the nut in, push the plug into the tube, and a bolt from outside draws
whatever it carries (a crossbar, a levelling foot, a caster plate) down onto
the flange. The pull goes through the insert into the nut; the tube only
locates the plug sideways, so pin or glue the plug if the joint is pulled
outward.

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `tube_w`, `tube_d` | 15–120 mm | Outside section of the tube |
| `tube_wall` | 1–10 mm | Wall thickness of the tube |
| `fit` | 0–1.5 mm | Clearance per side between insert and tube |
| `corner_c` | 0–10 mm | Chamfer on the insert's corners |
| `flange_t`, `insert_l` | 1.5–12 mm, 6–80 mm | Flange thickness, and how far the insert enters |
| `skirt_wall` | 1.5–8 mm | Wall of the hollow insert (plain plug) |
| `bolt_seat` | on / off | Solid insert with a bolt hole and a nut pocket |
| `bolt_d`, `nut_af`, `nut_h` | 3.4–12.5 mm, 5.5–19 mm, 2–12 mm | Bolt hole, nut width across flats, and pocket depth |

## Constraints

- The insert is at least 6 mm across, and the corner relief fits it.
- With the bolt seat on: the nut fits inside the insert with 2 mm of wall, the
  insert keeps 3 mm of solid above the pocket, and the nut is wider than the
  bolt hole.
- A fit over 0.6 mm and a very short insert are flagged.

## Making it

Print it flange down: the plain plug needs no support, and the nut pocket of
the bolt seat ends up on top, open. A flexible material makes a plain cap
that presses in and stays; a rigid one makes a bolt seat. Machined, it is a
block with a shoulder.

This cartridge is a geometry family, not a structural fitting. A joint made
through a bolt seat is only as strong as the insert around the nut, and a
printed insert in tension is weak across its layers. Whoever builds and uses
it has to establish what the joint carries.

## Interfaces

- **Tube end seat** (`tube_end`): the underside of the flange, which sits on
  the cut end of the tube. It carries the size key `square-tube-80mm` when
  `tube_w` is 80; the key reads the width only, so a rectangular tube has no
  key yet.
- **Outer face** (`outer_face`): the top of the flange, where a bolted part
  seats.
- **Captive nut seat** (`nut_seat`): `bolt_d`, `nut_af`, `nut_h`.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
