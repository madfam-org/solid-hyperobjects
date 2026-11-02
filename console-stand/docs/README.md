# Console Stand

An original support family with circular/elliptical base, vertical clip and
cradle constructions. Named presets carry a **sourced stand body envelope**;
all support shape and mating details remain explicit archetype rules. Read
[NOTICE](../NOTICE).

## Source mapping and frame

X is width, Y depth, Z height above the bottom at Z=0. Catalog
`dimensions_mm.states.body` width/depth/height maps directly to X/Y/Z. The
`envelope` is a single body hull at these dimensions. It is independent of
support cutouts and does not prove a console seats correctly.

| Named preset | Sourced W × D × H (mm) |
|---|---|
| Nintendo Switch charging stand (free-stop) | 47.9 × 28.1 × 44.7 |
| Wii console stand RVL-017 | 55.4 × 225.6 × 42 |
| PS5 vertical stand CFI-ZVS1 | 155 × 155 × 11 |

The keystone records source URLs, dates, quotes and whether projections are
excluded. The generator retains their family digest and names every unknown
construction group as a fallback. A name never asserts a replica shell or a
published seat shape.

## Modes and composition

| Mode | Part | Purpose |
|---|---|---|
| stand | stand | connected original support |
| envelope | envelope | one closed W×D×H body hull |

`family.py` is authored; regenerate `main.py` with
`python3 tools/inline_parts.py --write console-stand`. New `console_stands`
components reuse `console_supports` box/disc primitives. Interfaces expose the
support envelope, console/stand seat and device cradle. They describe design
intent; physical mating, load and stability remain unverified.

Census: existing `device-stand` models a phone/tablet incline. This family groups
the console-stand catalog and adds disc-base and vertical console-clip
constructions with their own seat interfaces; it does not copy that wedge.

## Archetype rules

A shallow body (height below 20% of the smaller footprint axis) selects disc
base; otherwise a deeper-than-wide body selects vertical clip; the rest select
cradle. That is our rule from envelope ratios, not a sourced manufacturer shape.

The default cradle is 110×70×65 mm; original clip 80×180×40 mm; original disc
base 160×160×14 mm. These sizes assert no product. Wall 2 mm, base 20% of height
(or 65% for the disc base), and corner radius 4% of the smaller footprint axis
are our rules. Seats use 65% of width (45% on a disc base); their depth is 75%
for cradle, 85% for clip and 45% for disc base. The 4 mm mounting hole and cable
path min(12 mm,15% width) are original details, not measured fit features.

The cradle-angle animation changes the back-support construction from 60° to
80°. It is an explanatory shape change, not a modeled physical adjustment joint.
The other construction types do not use this angle. Generic stand cutouts do
not certify a fastener, cable, electrical connector or physical device fit.

## Awaiting a source

Seat profiles, mounting fasteners, clearances, console contact surfaces, wall
thickness, actual adjustment mechanisms, materials, retention and tipping/load
limits remain unverified. No packaged game/console exterior dimensions are used
as support inside dimensions.
