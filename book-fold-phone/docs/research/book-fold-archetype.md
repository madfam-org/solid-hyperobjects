# The book-fold phone archetype

Why this cartridge exists, how far up the resolution ladder it reaches, and what
the graph twin still cannot say.

Companions: Telesia's [`docs/DEVICE_GEOMETRY.md`](https://github.com/madfam-org/telesia/blob/main/docs/DEVICE_GEOMETRY.md)
(the plan, §3 archetypes, §4 the ladder, §5 provenance) and ADR
[0015](https://github.com/madfam-org/telesia/blob/main/docs/adr/0015-device-geometry-via-yantra4d-hyperobjects.md).
This is the SECOND device-family cartridge; the first is
[`clamshell-dual-screen-handheld`](../../../clamshell-dual-screen-handheld)
(solid-hyperobjects#83), and several decisions below are explicitly different
from its, for reasons the data forced.

## 1. The archetype

Two rigid half-frames that meet at a fold axis running along the long edge. One
continuous display is folded inward across both of them; a second display sits on
the outside of one half, and the camera island on the outside of the other. One
continuous `fold_angle` turns the camera half about the fold axis: 0 closed, 180
open.

Four decisions make the geometry behave, and each is load-bearing:

**The fold axis is the X axis through the origin.** Not an offset line, not a
translated frame — the origin itself. The graph engine's `rotate` node turns
about the origin and nothing else, so anchoring the model there is what lets the
fold be one node with no compensating translate. The CadQuery reference uses the
same anchor for the same reason: the two engines must agree operation for
operation, not merely in the end. (The clamshell cartridge made the same choice
for the same reason; it is the one piece of this geometry that is inherited.)

**The fold axis sits in the MIDDLE of the gap, and that is what makes the gap
disappear.** The cover half occupies `z ∈ [−(gap/2 + t), −gap/2]` and the camera
half `[+gap/2, +(gap/2 + t)]`. A 180° turn about the axis maps the camera half
into the cover half's own z band, so the model is `2t + gap` deep closed and `t`
deep open — which is exactly the pair of depths every manufacturer in this family
publishes. Nothing about the gap is asserted separately; it falls out of the two
published numbers and is proved by the two bounding boxes.

**The half thickness is the published open depth, and the gap is the remainder.**
This is where the family differs most from the clamshell. There, one closed
thickness had to be split between two decks by an archetype rule (45/55) that was
ours and had to be declared as ours. Here the manufacturer publishes both a
closed and an open depth, and `gap = closed − 2 × open` is arithmetic on two of
their own figures. The numbers it produces are a recognisable history of the
hardware: 1.9 mm on the 2019 Galaxy Fold, 3.0–3.2 mm on the Z Fold2/3/4, 1.2 mm
on the Z Fold5, and 0.1–0.9 mm on everything from 2024 onward. The "gapless fold"
is not a marketing claim in this model; it is a subtraction.

**The two halves are different widths, and that is why a book fold closes.**
`camera_half_width = open.width − closed.width`. On the Galaxy Fold that is
55.1 mm against a 62.8 mm cover half — a 7.7 mm difference, the lip that lets the
narrower half nest inside the wider one. On the iPhone Duo it is 80.5 against
84.1. The closed width is therefore set by the cover half alone, which is what
makes the closed bounding box match the published figure exactly.

Two consequences follow and are worth stating because they are checkable:

  * **The closed and open envelopes are BOTH exact.** 26 of 27 presets reproduce
    six published figures each — closed H×W×D and open H×W×D — to 0.000 mm. The
    clamshell cartridge could assert only the closed envelope, because no device
    in that family publishes an open one.
  * **The two halves cannot interfere at any fold angle.** Both live at radius
    ≥ gap/2 from the fold axis and in opposite half-spaces of it, so for
    θ ∈ (0°, 90°] every point of the camera half has `z > 0` while the cover half
    has `z ≤ −gap/2`, and for θ ∈ (90°, 180°] every point has `y < 0` while the
    cover half has `y ≥ 0`. Measured interference is **0 mm³ at 0, 45, 90, 135 and
    180° for every preset**, and the argument says it could not be otherwise.

**The hinge is a relief plus a leaf, and both stay inside the envelope.** The
crease relief is a cylinder ON the fold axis, so it is invariant under the fold —
cutting it before the rotate and after it give the same solid, which is what lets
the twin cut it early and still agree with the reference. The leaf is that same
cylinder less a 0.3 mm running clearance, with everything at `y < 0` removed (or
the closed width would exceed the published figure) and then intersected with the
cover half's own z band (or it would stand proud of the open face). What survives
is inside the published envelope at every angle. This is the one place the book
fold is *tighter* than the clamshell: there, half the hinge barrel deliberately
stands proud when the device is flat, and the cartridge documents it because
nothing published contradicts it. Here an open depth IS published, so the hinge
had to be made to fit inside it.

## 2. Where it sits on the resolution ladder

| Rung | Carried here |
|---|---|
| **L0 envelope** | ✅ closed AND open height × width × depth, corner radius, the fold axis' position, the hinge gap, a continuous `fold_angle`, and three generated fold states. |
| **L1 displays and bezels** | ⚠️ The inner and cover windows are modelled with recess depth and position, and on the iPhone Duo their active areas are the registry's own derived figures with the `derived` flag carried into the preset. On the other 26 the registry has **no active area at all** and the window is the published envelope inset by an archetype bezel, named per preset. Bezel *offsets* are archetype everywhere: no manufacturer publishes how a display sits within its frame. |
| **L2 features** | ✅ camera island and lens apertures, side buttons, USB-C, a SIM tray, a speaker grille — sizes and positions archetype, port presence from the registry. |
| **L3 kinematics and materials** | ❌ Not modelled. See §4. |

**The L1 gap is a REGISTRY gap, not a cartridge one, and it is the single most
valuable thing this cartridge found.** 27 of the 28 registry entries in this
family carry a display diagonal and a pixel resolution but a `null`
`active_area_mm`, because the registry derives an active area only from a
manufacturer-published **ppi**, and Apple is the only manufacturer here that
publishes one. Deriving from diagonal and aspect instead is arithmetic the plan's
§5 explicitly sanctions ("screen active areas derived from diagonal, aspect and
resolution are marked `derived` with the formula") — but it is the registry's job,
not a cartridge's, because the registry is the only place a dimension may be
typed. Until it is done, this family's L1 rung is one device deep. The fix is one
registry pass, and it would upgrade 26 presets at once.

## 3. What the graph twin cannot express, by yantra4d lane

The twin (`bookfold.graph.json`) reaches the same bounding boxes and the same
volumes as the CadQuery reference — the two are diffed part by part, at both fold
states, in the PR's verification table. These are the places where the two files
could not be made the same thing, each with the lane that would close it.

### G-EXPR — expressions in a socket

**The hinge gap — the dimension that defines this family — cannot be a control at
all.** This is a sharper instance than anything the clamshell turned up. The gap
is `closed.depth − 2 × open.depth`; the only things in the model that carry it are
`cover_half_center_z` and `camera_half_center_z`, each of which is
`∓(gap/2 + half_thickness/2)`. With no arithmetic in a socket, those are frozen
constants, and a constant cannot be driven by the quantity it was computed from.
So a user who drags `half_thickness` in the Studio today gets a model whose gap
silently changes with it, and there is no gap slider to correct. The cartridge
answers by recording the gap per preset under `registry.hinge_gap_mm` — a number
in the manifest that no parameter can reach — and by saying so in the parameter's
own tooltip. A `{"expr": "..."}` input evaluated at transpile time is what would
turn it back into a control.

The same shape applies to some 20 more of this cartridge's 70 parameters:
`cover_half_center_y` is `cover_half_width / 2`, `hinge_leaf_radius` is
`hinge_cavity_radius − 0.3`, `hinge_leaf_span` is `hinge_cavity_span − 0.6`,
`inner_display_cover_center_y` is half its own span, and every `*_center_*` value
places a solid the engine cannot compute for itself. They are honest parameters
with defaults and tooltips rather than hidden constants, and Telesia's
`scripts/device-presets.py` emits them together from one registry entry so they
cannot drift — but the drift is prevented outside the format, not inside it.

**Conditional presence.** `usb_c_present` and `card_slot_present` are real,
sourced facts: the registry knows that five devices in this family are eSIM-only
and that the iPhone Duo says so outright. The CadQuery reference honours them.
The graph has no branching, so the twin always cuts both openings. A ternary in a
socket would express it as a size that goes to zero or a position that moves the
tool clear.

**A count of zero.** Pattern counts are clamped to `1..200` in the generated
script — deliberately, so a slider cannot detonate a boolean loop in the render
worker. `button_count`, `lens_count` and `speaker_hole_count` are all archetype
here, so no *sourced* zero is lost in this family today; the clamp is still a
thing the twin cannot say, and the clamshell cartridge has two devices where it
costs a real fact.

### G-NODES-1 — free-form profiles

* **The crease relief is a plain cylinder.** Seven devices' manufacturers
  describe their hinge as "teardrop" or "water-drop" in words, and the registry
  records that word — `hinge.crease: "teardrop"` — for all seven. A teardrop
  section is not a circle, and nothing in either engine can draw one. That word
  is currently the highest-resolution hinge fact the registry holds and the
  cartridge cannot use it. It is the clearest single case in this collaboration
  of a SOURCED fact blocked on a node type.
* **The spine is square in plan.** Only the opening edge is filleted, because a
  fillet on the fold edge would notch the crease where the inner display crosses
  it. A real spine is rounded in SECTION — a profile swept along the fold — which
  is the same lane.
* **Rounded display corners.** Every device in this family has them; both engines
  cut a plain rectangle, and on presets whose display nearly fills the face the
  body's own corner fillet clips the recess, which is visually right by accident
  rather than by model.
* **The camera island** is a rectangular pocket. Real islands are rounded
  rectangles or circles with their own fillets.

### G-NODES-2 — a bounded revolve

* A **domed lens seat**, a **chamfered port mouth** and a **capped hinge leaf**
  are revolves. Everything here is a flat-bottomed prism or cylinder.

### G-CLUSTERS — sub-graph reuse

This is the lane the cartridge's own structure is waiting on — together with
Telesia's gate **H8**, which is what will rule the mechanism (a shared import
path in the commons for the CadQuery references, sub-graph references for the
twins).

With two device cartridges in the commons the duplication is now measurable
rather than hypothetical. `display_panel` (exposing `display_recess`),
`port_receptacle` (exposing `port_cutout`) and the `button_seat` interface exist
in **both** this cartridge and `clamshell-dual-screen-handheld`, written twice in
Python and twice again as graph nodes. They are the same parts: a rectangular
recess for a rigid panel, a rectangular opening for a connector, a pocket for a
key. Five more family cartridges are planned, and each will copy them again.

`main.py` is factored so that the copy is mechanical: each component is its own
function taking its own parameter dict, reading no manifest global, so it can be
lifted into its own cartridge without a rewrite. The twin can only *imitate* that
boundary — its node ids carry the component slug as a prefix
(`framehalf_`, `foldabledisplay_`, `hingefold_`, `lenswindow_`, `cardslot_` …)
and nothing more.

The note the clamshell cartridge left for whoever implements the lane stands, and
this cartridge is a second witness to it: `component:<slug>` **cannot** be the
literal prefix Telesia's §3.1 asks for, because the transpiler's node-id grammar
is `^[A-Za-z][A-Za-z0-9_]*$` and a colon fails validation before a graph ever
renders. If cluster namespacing wants a separator, it has to arrive with a
grammar change.

### G-SPEC — a render bar for graphs

`y4d-spec`'s `mode_sources()` recognises `.py`, `.cq` and `.scad`, so this
cartridge's `graph_device` mode gets no watertight check, no body-count check, no
cross-kernel parity and no nightly row — and the 186 renders this cartridge's
`--render` run reports are all CadQuery ones. The `verification` block in
`project.json` therefore covers the four CadQuery modes; the twin is checked by
the render probe in the graph guide, run by hand at both fold states and pasted
into the PR. That is a second cartridge's worth of unverified surface until the
lane lands, and it is now the larger half of the device-geometry programme's
output.

## 4. L3, and what it needs that is not a lane

* **Hinge kinematics.** The relief here is a cylinder with a running clearance,
  and that is enough for the envelope and the fold. A real free-stop teardrop
  hinge is a multi-link mechanism; 17 of the 28 registry entries record
  `free_stop: true` and **none** records an angle, a cam profile or a detent.
  Modelling one would be invention, not resolution. It needs a measurement, not a
  node type.
* **Materials.** The registry's `materials` block IS populated for most devices
  in this family — titanium and aluminium frames, glass and ceramic backs — which
  is more than the clamshell family had. But they are finish names, not figures:
  nothing there changes a dimension. `tolerance_by_material` is declared because
  the relief-versus-leaf clearance is the knob a material profile would move.
* **Mass.** The registry publishes `mass_g` for all 28 devices, including the one
  with no preset. The cartridge does not model internal volume, so it cannot
  reproduce a mass and does not try.
* **Depth at the hinge.** `dimensions_mm.depth_at_hinge` is `null` on all 28.
  Several of these devices are visibly wedge-shaped when closed; the model is a
  constant-thickness pair of slabs, because that is what is published.

## 5. Three traps worth writing down

**The axis names lie, and Apple says so in its own table.** Manufacturers in this
family label the LONG axis "width": Apple's iPhone Duo page reads "Open: Width:
6.48 inches (164.6 mm); Height: 4.64 inches (117.8 mm)", so by Apple's own labels
the 117.8 mm figure is the *height* and is the SHORT edge of the open device —
and it is the axis the hinge runs along. The registry records the labels
literally, and this cartridge maps `closed.height → hinge_axis_length (X)`. The
check that makes this safe rather than a guess: `open.height == closed.height` on
**every** device in this family that publishes both. The axis common to the two
states is the axis the fold runs along, by definition.

**A published pair can contradict itself.** OPPO's Find N3 page gives 11.7 mm
closed and 5.9 mm open; twice 5.9 is 11.8. There is no reading of those two
numbers under which a body of two equal halves has a non-negative gap. The
generator does not average them and does not drop the device: the closed envelope
is the one the cartridge asserts against, the half thickness is derived from it,
the preset names that as a fallback, and the resulting 0.075 mm disagreement with
OPPO's open depth is printed in the verification table. `null = unresolved, never
guessed` has a sibling: *contradictory is not silently reconciled.*

**A "derived" flag with a null value is not a derivation.** Every display in this
family carries `active_area_mm.derived: true`. On 27 of 28 devices the width and
height under that flag are `null` — the flag records how the value *would* be
obtained, not that it *was*. A generator that read the flag instead of the values
would have invented 54 active areas. The rule that saved it is the same one the
clamshell cartridge used: read the value, and if it is null, fall back and say so.
