# Keep Case

An original one-piece media-case shell with a continuous kinematic spine and a
separate retention insert. It supports disc hub, cartridge pocket, card slots
and mixed retention. Closed case and pocket sizes are archetype choices unless
a named catalog record supplies them. See [NOTICE](../NOTICE).

## Frame and modes

X is closed case width, Y height, Z thickness; the base underside is Z=0.
Catalog `states.closed` width/height/depth maps directly to X/Y/Z. The left
spine consumes part of the width. Opening moves the lid onto the left side.

| Mode | Parts | Meaning |
|---|---|---|
| case | shell, insert | assembled preview, two separate bodies |
| shell | shell | connected base, spine and lid at `open_angle` |
| insert | insert | carrier with disc hub, pocket rims or card slots |
| flat_shell | flat_shell | connected shell fully open, independent of `open_angle` |
| envelope | envelope | one closed W×H×T hull, independent of opening pose |

`family.py` is authored; `main.py` is generated with
`python3 tools/inline_parts.py --write keep-case`. It inlines `media_cases` and
`case_flexure` shared components. Interfaces expose closed envelope, media seat,
booklet seat and sleeve seat. The media itself is a separate `plug-in-media` or
`disc-media` asset in a scene; no artwork is included here.

## What the motion actually computes

The spine starts as a semicircular skin between the two rigid panels. Its
centerline length is fixed at π times half the closed internal thickness. When
the case opens, the remaining bend angle decreases and its radius increases.
The arc endpoint places the rigid lid. At 180°, the skin becomes exactly flat
and the panels are separated by that spine length. Small tails overlap the
panels so the shell remains one connected body at every pose.

This is an explicit kinematic construction for an explanatory animation. It
preserves the spine skin's volume, not a claim about real plastic strain,
flexural stiffness, fatigue, bend radius or molding practice. No physical hinge
profile is copied from a commercial package. Closed/open projections show this
model's construction, not a historical case's exact movement.

## Archetypes and provenance

| Archetype | W × H × T (mm) | Retention |
|---|---|---|
| disc (default) | 150 × 210 × 16 | original rosette hub |
| double disc | 150 × 210 × 22 | two-sided removable carrier |
| cartridge | 150 × 175 × 18 | 75 × 85 × 8 mm pocket |
| cards | 115 × 150 × 14 | two 40 × 30 × 3 mm pockets |
| mixed | 165 × 230 × 20 | disc hub and original media pocket |

These are original sizes, not named products. Disc diameter and nominal centre
hole are read from `optical-disc-cd-120mm` at the frozen keystone pin; its digest
is recorded in archetype presets. Hub diameter is nominal hole minus 0.5 mm,
an original clearance rule. Wall 1.2 mm, hinge skin 0.5 mm, running clearance
0.4 mm and corner radius 2 mm are archetype values. Sleeve edge recesses are
0.2 mm deep; they describe film seating and contain no film or artwork mesh.

The generator reads sourced closed envelope, capacity and retention. Unknown
groups are named as fallbacks. Missing envelopes or unsupported capacity above
two produce no named preset. The frozen catalog currently contains no keep-case
records, so the family has no named historical-case presets. The media pocket
geometry remains explicitly archetypal until a source supplies it.

## Limits

The flat shells exceed common print beds in several archetypes. Physical
retention, media/clip collision clearance, booklet capacity, sleeve fit, material
behavior, manufacturing process and commercial compatibility are unverified.
The insert's double-disc flip is a pose control, not a physical pivot design.
