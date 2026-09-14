# The clamshell dual-screen handheld archetype

Why this cartridge exists, how far up the resolution ladder it reaches, and what
the graph twin still cannot say.

Companions: Telesia's [`docs/DEVICE_GEOMETRY.md`](https://github.com/madfam-org/telesia/blob/main/docs/DEVICE_GEOMETRY.md)
(the plan, §3 archetypes, §4 the ladder, §5 provenance) and ADR
[0015](https://github.com/madfam-org/telesia/blob/main/docs/adr/0015-device-geometry-via-yantra4d-hyperobjects.md).

## 1. The archetype

Two rigid decks, joined by a knuckle hinge that runs along the long edge. The
upper deck carries the primary display; the lower deck carries the secondary
display, the controls and the ports. One continuous `fold_angle` turns the upper
deck about the hinge: 0 closed, 180 flat.

Three decisions make the geometry behave, and each is load-bearing:

**The hinge axis is the X axis through the origin.** Not an offset line, not a
translated frame — the origin itself. The graph engine's `rotate` node turns
about the origin and nothing else, so anchoring the model there is what lets the
fold be one node with no compensating translate. The CadQuery reference uses the
same anchor for the same reason: the two engines must agree operation for
operation, not merely in the end.

**The decks end at the hinge axis, and the barrel is a half-cylinder.** Both
decks span `y ∈ [0, deck_depth]`; the barrel is a cylinder on the axis with
everything at `y < 0` cut away. Two consequences follow, and they are why this
shape rather than a full barrel inset from the rear face:

  * the closed envelope is exactly `deck_length × deck_depth ×
    (upper + lower thickness)` — the published figure, with nothing protruding;
  * at 180° the rotated upper deck lands at `y ∈ [−deck_depth, 0]` and the two
    decks share only the plane `y = 0`. Measured interference between the decks
    is **0 mm³ at every fold angle tested (0, 45, 90, 135, 180) for every
    preset**. A full barrel inset by its own radius would have put a
    `2 × radius`-wide band of both decks in the same space when flat.

**The seam plane is z = 0.** Closed, the two display faces meet there; flat, both
face up. A hinge axis anywhere else would not map the seam plane to itself, and
the upper display would end up facing down when the device is open.

The one visible consequence to know about: because the barrel is centred on the
seam plane, half of it stands proud when the device is flat. That is real — a
clamshell's hinge bump is above the open surface — and it is why an open
bounding box is taller than the thicker deck by the barrel radius.

## 2. Where it sits on the resolution ladder

The plan's ladder, and what this cartridge reaches:

| Rung | Carried here |
|---|---|
| **L0 envelope** | ✅ closed height × width × depth, corner radius, hinge position and clearance, a continuous `fold_angle`. |
| **L1 displays and bezels** | ✅ per-screen active area from the registry, recess depth, screen position. ⚠️ Bezel *offsets* are archetype: no manufacturer in this family publishes how a display sits within its deck, so the presets centre it. |
| **L2 features** | ✅ D-pad, face buttons, analogue sticks, shoulder triggers, start/select, USB-C, 3.5 mm jack, cartridge slot, speaker grille — sizes and positions archetype, counts and port presence from the registry. |
| **L3 kinematics and materials** | ❌ Not modelled. See §4. |

Open dimensions are **not** asserted against the registry for this family,
because no manufacturer in it publishes an open envelope: 0 of the 16 registry
entries carry `dimensions_mm.open`. The model produces one and the verification
table reports it as a model output, never as a device claim.

## 3. What the graph twin cannot express, by yantra4d lane

The twin (`clamshell.graph.json`) reaches the same bounding boxes and the same
volumes as the CadQuery reference at the defaults — the two are diffed part by
part in the PR's verification table. These are the places where the two files
could not be made the same thing, each with the lane that would close it.

### G-EXPR — expressions in a socket

**Every derived dimension is a frozen constant.** 30-odd of this cartridge's 82
parameters exist only because the graph format has no arithmetic: `deck_center_y`
is `deck_depth / 2`, `lower_deck_center_z` is `−lower_deck_thickness / 2`,
`hinge_relief_radius` is `hinge_barrel_radius + 0.4`, `hinge_knuckle_pitch` is
`(hinge run − knuckle length) / (count − 1)`, `face_button_spacing_deg` is
`360 / face_button_count`, and every `*_center_*` value places a solid the engine
cannot compute for itself. They are honest parameters with defaults and comments
rather than hidden constants, and Telesia's `scripts/device-presets.py` emits
them together from one registry entry so they cannot drift — but a user who
drags `deck_depth` in the Studio today gets a model whose decks no longer sit on
their own centre line. That is the cost the lane's own documentation names, and
this cartridge is a large, concrete instance of it.

**Conditional presence.** `usb_c_present`, `headphone_present` and
`cartridge_slot_present` are real, sourced facts — the registry knows that
Nintendo lists a 3.5 mm jack and no USB-C on a DS, and that the Pocket DS has no
jack. The CadQuery reference honours them. The graph has no branching, so the
twin always cuts all three. A ternary in a socket (the lane's proposed
`{"expr": "..."}` form, evaluated at transpile time) would express it as a
depth or a size that goes to zero, or a position that moves the tool clear.

**A count of zero.** Pattern counts are clamped to `1..200` in the generated
script — deliberately, so a slider cannot detonate a boolean loop in the render
worker. But a count of zero is a *sourced fact* for two devices here: Nintendo's
own control list for the DS and DS Lite contains no analogue stick, and AYANEO's
for the Flip DS / Flip 1S DS / Pocket DS contains no start/select. The reference
renders those devices with no stick and no menu row; the twin renders one of
each. The clamp is right; what is missing is a way to say "none", which the same
ternary would give.

### G-NODES-1 — free-form profiles

* The **D-pad** is two crossed boxes. A real directional pad is a cross with
  rounded re-entrant corners, which is a profile, not a boolean of primitives.
* The **hinge relief** is a plain cylinder. A real clamshell hinge uses a
  teardrop or water-drop relief whose section is not circular — the L3 shape that
  makes the fold interference-free at a much smaller barrel.
* **Chamfered display bezels** and any non-rectangular screen aperture (a rounded
  display corner, which every device in this family actually has) need a profile
  too. Both engines cut a plain rectangle today.

### G-NODES-2 — a bounded revolve

* A **domed stick seat** and a **capped hinge knuckle** are revolves. The seats
  here are flat-bottomed cylinders.

### G-CLUSTERS — sub-graph reuse

This is the lane the cartridge's own structure is waiting on — together with
Telesia's gate **H8**, which is what will rule the mechanism (a shared import
path in the commons for the CadQuery references, sub-graph references for the
twins).

A screen, a hinge, a button, a D-pad, a stick, a port and a cartridge slot are
each a hyperobject that feeds into this one, and `main.py` is factored that way: each is its own
function taking its own parameter dict, reading no manifest global, so it can be
lifted into its own cartridge without a rewrite. The twin can only *imitate* that
boundary — its node ids carry the component slug as a prefix
(`hingebarrel_`, `display_`, `facebtn_`, `stick_`, `slot_` …) and nothing more.
With sub-graph reuse the twin would **reference** `hinge-hyperobject` — whose
`revolute_axis` and `mounting_surface` interfaces this cartridge's `hinge_barrel`
already names — instead of duplicating seven nodes that say the same thing.

A note for whoever implements the lane, and a correction to the plan:
`component:<slug>` **cannot** be the literal prefix Telesia's §3.1 asks for. The
transpiler's node-id grammar is `^[A-Za-z][A-Za-z0-9_]*$`, so a colon fails
validation before a graph ever renders. This cartridge therefore uses the slug
plus an underscore. If cluster namespacing wants a separator, it has to arrive
with a grammar change.

### G-SPEC — a render bar for graphs

`y4d-spec`'s `mode_sources()` recognises `.py`, `.cq` and `.scad`, so this
cartridge's `graph_device` mode gets no watertight check, no body-count check, no
cross-kernel parity and no nightly row. The `verification` block in
`project.json` therefore covers the four CadQuery modes; the twin is checked by
the render probe in the graph guide, run by hand and pasted into the PR. That is
one more cartridge's worth of unverified surface until the lane lands.

## 4. L3, and what it needs that is not a lane

* **Hinge kinematics.** The barrel here is a cylinder with a running clearance,
  and that is enough for the envelope and the fold. A real free-stop hinge, a
  cam, a detent or a water-drop fold is geometry no published source describes
  for any device in this family, so modelling one would be invention, not
  resolution. It needs a measurement, not a node type.
* **Materials.** The registry's `materials` block (frame / back / cover glass) is
  null for every device in this family. `tolerance_by_material` is declared
  because the barrel-versus-relief clearance is the knob a material profile would
  move; nothing else here is material-aware.
* **Mass.** The registry publishes `mass_g` for 12 of the 13 presets. The
  cartridge does not model internal volume, so it cannot reproduce a mass and
  does not try.

## 5. Two traps worth writing down

**The axis names lie.** Manufacturers in this family label the LONG axis
"width" — Nintendo's spec line reads 縦74mm×横134mm×厚さ21mm, where 横 ("width")
is the 134 mm long edge — and the registry records their labels literally. The
mapping every consumer of this cartridge needs is therefore
`registry closed.height → deck_length (X, the hinge axis)`,
`registry closed.width → deck_depth (Y, the folding axis)`. Apple's iPhone Duo
page has the same inversion, which is why Telesia's compilation report carries an
explicit axis warning.

**One device in the family does not fold.** The Nintendo 2DS is, in Nintendo's
own launch wording, "a new distinctive fixed slate form design". The registry
files it under this family at the requester's instruction, with every `hinge.*`
field null, and its own report proposes moving it to a
`slate-dual-screen-handheld` family. Its preset here pins `fold_angle` to 0 and
carries the envelope only; the archetype's fold is not a claim about that device.
