# Jewel Case

An original rigid media-case family with a base, removable disc tray and hinged
lid. It provides single, slim, double and thick-box archetypes. No manufacturer
case dimensions are claimed by these archetypes. Read [NOTICE](../NOTICE).

## Frame and modes

X is closed case width, Y is height, Z is thickness; the base underside is Z=0.
A published `dimensions_mm.states.closed` maps width/height/depth to X/Y/Z.
The hinge runs along Y near the left edge. `lid_angle=0` is closed and 180°
places the lid open on the left. `tray_angle` flips the separate double tray.

| Mode | Parts | Purpose |
|---|---|---|
| case | base, tray, lid | assembled preview, three separate solids |
| envelope | envelope | one closed bounding hull, independent of opening pose |
| base | base | open pan and integrated hinge pins |
| tray | tray | removable disc tray, hub and optional reverse hub |
| lid | lid | lid shell, hinge eyes and booklet ledges |

An interface records design intent, not a proof of collision-free operation or
physical retention. Exported meshes are geometry proxies, not manufacturing
specifications for a commercial jewel case.

## Composition

`commons-lib/hardware/media_cases.py` supplies rounded boxes and open pans,
hinge pins/eyes, an original slotted rosette or button hub, removable tray,
booklet ledges and opening transforms. The case consumes a disc envelope and
exposes its closed envelope, media seat, booklet seat and hinge axis. A separate
`disc-media` asset supplies the actual medium to an unboxing scene; artwork
belongs outside the commons.

`family.py` is authored. Generate `main.py` with
`python3 tools/inline_parts.py --write jewel-case`; never edit the generated file.
Each shared component takes its own parameter dictionary. Open cavities cut
past their faces; hub roots and hinge supports overlap their parent solids.

## Presets and provenance

| Archetype | Closed W × H × T (mm) | Tray |
|---|---|---|
| single (default) | 150 × 140 × 14 | single hub |
| slim | 150 × 140 × 10 | single hub |
| double | 150 × 140 × 20 | flip tray with two hub faces |
| fatbox | 160 × 150 × 32 | flip tray with two hub faces |

These case sizes and all construction details are ours. Disc diameter and
nominal hole are read from keystone `optical-disc-cd-120mm`, with its digest
recorded in each archetype preset. The hub diameter is that nominal hole minus
0.5 mm, an archetype clearance rather than a standard retention profile.
Wall 1.2 mm, running clearance 0.4 mm, corner radius 2 mm, and an eight-petal
rosette are original choices. The thinner tray floor and slits produce visible
thin-wall notes in the verifier; no material flexibility is simulated.

`tools/presets/jewel_case.py` reads only sourced closed envelopes and capacity.
An unresolved envelope produces no named preset. A sourced case too small for
the current CD tray is reported rather than squeezed. The frozen catalog
currently contains no jewel-case objects, so there are no named case presets.
No historical SKU should be inferred from a generic archetype.

## Awaiting a source

Named case dimensions, material, wall/flexure thicknesses, hinge profiles,
retention force, multi-disc leaf counts above two, booklet capacity and sleeve
layouts remain unresolved. Closed/open views explain the model's motion; they
do not certify clearance, durability, printability or compatibility.
