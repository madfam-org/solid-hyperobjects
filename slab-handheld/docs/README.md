# Slab Handheld

An original parametric flat-face handheld with a display recess, control seats,
media cavity and proxy, battery or service door, optional rear grips, attachment
grooves and a moving kickstand. Named presets carry catalog facts; the styling,
mechanical layout and surface profiles remain archetypal. See [NOTICE](../NOTICE).

## Frame and source axes

| Model | Source | Meaning |
|---|---|---|
| X | body width | across the face, centered at X=0 |
| Z | larger of published height/depth | height above the bottom at Z=0 |
| Y | smaller of published height/depth | thickness, front at Y=0 and rear toward +Y |

Makers disagree about whether height or depth names thickness. The smaller-axis
mapping is an explicit family rule and preserves every source's original labels
in the catalog. A Switch-type `with_controllers` envelope is never substituted
for an unresolved tablet body. The fit envelope is the body only, including
rear grips but excluding media insertion, kickstand displacement and protrusions.

## Modes and composition

| Mode | Parts | Purpose |
|---|---|---|
| device | front_shell, rear_body, battery_door | assembled preview |
| envelope | envelope | one body, the uncut fit hull |
| front_shell | front_shell | hollow front print part |
| rear_body | rear_body | rear shell with kickstand and optional separate media proxy |
| battery_door | battery_door | battery or service cover |

| Module | Components | Interfaces |
|---|---|---|
| displays | display recess | display window |
| controls | D-pad, face-button ring, stick and system seats | dpad_seat, button_seat, stick_seat |
| handheld_body | slab, crown, rear grips, shell split | device_envelope, cradle_seat |
| handheld_body | media cavity and separate fit proxy | media_slot, consumes media_envelope |
| handheld_body | cell bay, door and rear recesses | battery_bay, rear button seats |
| handheld_body | rail grooves, ports, kickstand | rail, port_cutout, revolute_axis |

`family.py` is authored; `main.py` is generated with
`python3 tools/inline_parts.py --write slab-handheld`. The shared components take
their own parameter dictionaries and are inlined at build. Ports and attachment
grooves are generic keep-outs, not proprietary connector profiles. The media
proxy is a separate solid so the assembly shows a real clearance gap.

## Presets and rules

The generator `tools/presets/slab_handheld.py` reads the keystone at `SPEC_PIN`.
Unresolved body envelopes produce no preset. Missing controls, features or
active display areas are explicitly named in `archetype_fallbacks`. No dimensions
are measured from photographs.

| Archetype | W × H × D (mm) | Features |
|---|---|---|
| portrait cart rear | 90 × 155 × 32 | four AA cells, rear cartridge |
| landscape | 170 × 90 × 26 | top slot, two sticks and kickstand |
| gripped PC | 290 × 120 × 45 | rear grips/buttons, no media |
| hybrid rail | 180 × 105 × 14 | tablet face and attachment grooves |
| hybrid magnetic | 200 × 115 × 16 | tablet face and shallow magnetic seats |
| faceplate | 100 × 160 × 30 | two AAA cells and faceplate cavity proxy |
| landscape UMD | 180 × 90 × 28 | generic rear disc-shell bay |

These are original sizes, not named products. A faceplate is represented by the
rear-open cavity archetype; no historical shell reproduction is claimed.
The rounded face radius is 8% of the shorter face axis, rear crown 8% of depth
(capped at 2 mm), wall 2 mm, fit clearance 0.4 mm and face recess 1.2 mm. Rear
grips take 18% of width and 75% of height. A default display uses 65%/32% of a
portrait face and 52%/65% of a landscape face. Sourced display areas override
those rules. All control sizes and positions follow the ratios in the generator.

AA/AAA bays use maximum diameter and length from `cell-aa`/`cell-aaa`; the bay
adds clearance for the declared number of cells. A built-in cell gets a service
cover rather than an asserted battery geometry. The barrel of the kickstand
joins the rear shell; rotation is an explanatory pose, not a compliant printed
hinge design. All insertion and kickstand animation frames are verified as
geometric solids; physical retention, contacts and electronics remain untested.

## Awaiting a source

Tablet-only envelopes, precise port/control positions, battery arrangements,
wall thickness, connectors, rails and manufacturer shell profiles remain
unresolved facts or explicit archetype rules. No claim of mechanical mating,
fastener design, comfort, electrical function or fabrication certification is
made by these models.
