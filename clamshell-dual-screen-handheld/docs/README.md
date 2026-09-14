# Clamshell Dual-Screen Handheld

The clamshell dual-screen handheld as a parametric **archetype**: two rigid decks
on a knuckle hinge along the long edge, a display recess in each, the controls
and the ports on the lower deck, and one continuous fold angle from closed to
flat. Dual-engine — a CadQuery (B-Rep) reference and a node-graph twin that
build the same three parts.

Named devices ride as **presets**, and every millimetre in a preset is a
published dimension with a provenance line or a declared archetype default.
Read [`../NOTICE`](../NOTICE) before you use one: this is a fit envelope, not a
likeness, and it reproduces no trade dress of any kind.

## Frame — read this first

Manufacturers in this family label the LONG axis "width" (Nintendo's spec line
is 縦74mm×横134mm×厚さ21mm, where 横 "width" is the 134 mm long edge), and
Telesia's registry records their labels literally. The mapping is:

| Model | Registry field | What it is |
|---|---|---|
| `deck_length` | `dimensions_mm.closed.height` | X — the long axis. **The hinge axis is the X axis through the origin.** |
| `deck_depth` | `dimensions_mm.closed.width` | Y — the folding axis. Both decks run from the hinge at `y = 0` to the front face at `y = deck_depth`. |
| `upper_deck_thickness` + `lower_deck_thickness` | `dimensions_mm.closed.depth` | Z. The seam plane, where the decks meet when closed, is `z = 0`. |

`fold_angle` 0 is closed; 180 is flat. The barrel is a **half** cylinder on the
hinge axis, so the closed envelope is exactly the published figure and the two
decks never overlap through the fold.

## Modes and parts

| Mode | Engine | Parts | What it is |
|---|---|---|---|
| `device` | CadQuery | lower_deck, upper_deck, hinge | All three in world coordinates at the current fold angle. A preview, not a print target. |
| `upper_deck` | CadQuery | upper_deck | The display deck alone. |
| `lower_deck` | CadQuery | lower_deck | The control deck alone. |
| `hinge` | CadQuery | hinge | The knuckle run. `hinge_knuckle_count` separate bodies. |
| `graph_device` | graph | lower_deck, upper_deck, hinge | The same three parts from `clamshell.graph.json`. Server-only, pro/premium, like every graph cartridge. |

Expected body counts: 1 for each deck, `hinge_knuckle_count` for the hinge.

## Composition — a device is a hyperobject of hyperobjects

A screen, a hinge, a button, a D-pad, a stick, a port and a cartridge slot are
each a hyperobject in their own right that feeds into this one — Telesia's
[`DEVICE_GEOMETRY.md`](https://github.com/madfam-org/telesia/blob/main/docs/DEVICE_GEOMETRY.md)
§3.1 and ADR 0015 §1, with gate **H8** still to rule how a component cartridge
will feed an assembly cartridge. Until it does, a component lives inside the
assembly that needs it, already carrying the id it will export. `main.py` is
factored that way: each is its own function taking its **own parameter dict**,
reading no manifest global, so any of them can be lifted into its own cartridge
without a rewrite. The assembly functions are the only code that maps this
manifest's parameters onto those dicts. The same table is in `project.json` under
`composition` for machines.

| Component (`main.py`) | Graph node prefix | CDG exposed | CDG consumed |
|---|---|---|---|
| `deck_shell` | `deckshell_` | `device_envelope`, `cradle_seat` | — |
| `display_panel` | `display_` | `display_recess` | — |
| `hinge_barrel` | `hingebarrel_` | `revolute_axis`, `mounting_surface` (the ids [`hinge-hyperobject`](../../hinge-hyperobject) declares) | — |
| `hinge_relief` | `hingerelief_` | — | `revolute_axis` |
| `d_pad` | `dpad_` | `dpad_seat` | — |
| `face_button` | `facebtn_` | `button_seat` (ring) | — |
| `button_row` | `buttonrow_` | `button_seat` (row — start/select) | — |
| `analog_stick` | `stick_` | `stick_seat` | — |
| `shoulder_trigger` | `trigger_` | `trigger_seat` | — |
| `port_receptacle` | `port_` | `port_cutout` | — |
| `cartridge_slot` | `slot_` | `cartridge_slot` | — |
| `speaker_grille` | `speaker_` | — (a vented face is not a mating feature) | — |

The twin can only **imitate** that boundary: its node ids carry the component
slug as a prefix and nothing more, because sub-graph reuse — yantra4d lane
**G-CLUSTERS** — is what would let it *reference* a component cartridge instead
of duplicating its nodes. (`component:<slug>` cannot be the literal prefix: the
transpiler's node-id grammar is `^[A-Za-z][A-Za-z0-9_]*$`, so a colon fails
validation before the graph renders.)

## Hyperobject Profile

- **Domain:** consumer-electronics
- **CDG interfaces:**
  - **Device Envelope** (`profile`, internal) — the closed outline,
    `deck_length × deck_depth × (upper + lower thickness)` with `corner_radius`
    corners. What a stand or a mount takes as its device.
  - **Hinge Axis** (`hinge`, internal) — the X axis through the origin, in the
    seam plane at the rear face. `hinge_barrel_radius` against a
    `hinge_relief_radius` pocket in both decks; the difference is the running
    clearance. `compatible_with` [`hinge-hyperobject`](../../hinge-hyperobject)
    and [`rugged-box`](../../rugged-box), the commons' other knuckle hinges.
  - **Primary / Secondary Display Window** (`screen`, internal) — a rectangular
    aperture of the display's published active area, sunk `screen_recess_depth`
    into its deck's inner face.
  - **USB-C Port Opening** (`port`, internal) — a rectangular opening in the
    front face, sized to clear a USB-C receptacle. Present only where the
    registry lists the port.
  - **Cradle Seat** (`surface`, internal) — the lower deck's outer face and its
    rounded footprint, the surface a dock or cradle registers against.
- **Material awareness:** `tolerance_by_material` — the barrel-versus-relief
  clearance is the knob a material profile moves. Nothing else here is
  material-aware, and the registry's `materials` block is null for every device
  in this family.
- **Societal benefit:** a dimensioned, parametric model of the dual-screen
  handhelds people actually own lets anyone fabricate a cradle, a dock, a travel
  shell or a repair fixture that fits — for hardware whose manufacturer publishes
  an outline and nothing else, and for hardware whose manufacturer is gone.
- **Licence:** CERN-OHL-W-2.0

## Presets — where every number comes from

Presets are **generated**, never typed: Telesia's `scripts/device-presets.py`
reads `data/registry/device-geometry.json` (snapshot 2026-09-13, 84 devices, 944
source entries, all tier `primary`) and emits the `presets` block together with
`_generated_from`, which records the registry's SHA-256. A preset sets **only**
the parameters the registry sources for that device; everything else stays at the
archetype default, and the last column says which.

Every preset reaches rung **L2** of the plan's resolution ladder (envelope,
displays, features). Two reach L2 with their display windows at archetype size,
because Nintendo publishes no pixel count for them and the registry therefore has
no active area — see the note below the table.

| Preset | Closed H × W × D (mm) | Registry source (tier `primary`) | Rung | Groups that fell back to the archetype |
|---|---|---|---|---|
| `ayaneo-flip-ds` | 180 × 102 × 29.8 | ayaneo.com/product/AYANEO-FLIP-DS.html | L2 | stick count, shoulder-button count |
| `ayaneo-flip-1s-ds` | 180 × 102 × 29.3 | ayaneo.com/product/AYANEO-Flip-1S-DS | L2 | stick count, shoulder-button count |
| `ayaneo-pocket-ds` | 179.8 × 101.8 × 25 | ayaneo.com/product/AYANEO-Pocket-DS.html | L2 | stick count, shoulder-button count |
| `nintendo-ds` | 148.7 × 84.7 × 28.9 | nintendo.co.jp/ds/spec/index.html | L2 | — |
| `nintendo-ds-lite` | 133 × 73.9 × 21.5 | nintendo.co.jp/corporate/release/2008/081002.html | L2 | — |
| `nintendo-dsi` | 137 × 74.9 × 18.9 | nintendo.co.jp/ds/series/dsi/spec/index.html | L2 † | both display active areas, all four control counts |
| `nintendo-dsi-xl` | 161 × 91.4 × 21.2 | nintendo.co.jp/ds/dsiLL/spec.html | L2 † | both display active areas, all four control counts |
| `nintendo-3ds` | 134 × 74 × 21 | nintendo.co.jp/hardware/3dsseries/3ds/index.html | L2 | — |
| `nintendo-3ds-xl` | 156 × 93 × 22 | nintendo.co.jp/hardware/3dsseries/3dsll/index.html | L2 | — |
| `new-nintendo-3ds` | 142 × 80.6 × 21.6 | nintendo.co.jp/hardware/3dsseries/new3ds/index.html | L2 | — |
| `new-nintendo-3ds-xl` | 160 × 93.5 × 21.5 | nintendo.co.jp/hardware/3dsseries/specs/index.html | L2 | — |
| `nintendo-2ds` ‡ | 144 × 127 × 20.3 | nintendo.co.jp/hardware/3dsseries/2ds/index.html | L2 | — |
| `new-nintendo-2ds-xl` | 159.36 × 86.36 × 20.8 | nintendo.co.jp/hardware/new2dsll/spec.html | L2 | — |

† **The DSi and DSi XL display windows are the archetype's size, not Nintendo's.**
Nintendo publishes the panel diagonal and type for both but **no pixel count
anywhere** — not the JP spec pages, not the 2008 comparison table, not Nintendo
UK, not the archived Nintendo of America comparison — so the registry has no
active area and this cartridge will not derive one. Carrying the DS's figures
across would have been exactly the forbidden inference. Their envelopes are
fully sourced; their screens are not.

‡ **The Nintendo 2DS does not fold.** In Nintendo's own launch wording it is "a
new distinctive fixed slate form design", and its registry entry has every
`hinge.*` field null. Its preset pins `fold_angle` to 0 and carries the envelope
only; the archetype's fold is not a claim about this device. The registry's own
compilation report proposes moving it to a `slate-dual-screen-handheld` family.

### Which components each preset exercises

Counts marked **R** come from the manufacturer's own quoted control list in the
registry; **A** is an archetype fallback because the registry does not resolve
it. A count of **0** marked R is a sourced *absence* — the manufacturer's list is
complete and does not contain that control.

| Preset | sticks | face buttons | shoulder | start/select | USB-C | 3.5 mm | cartridge slot |
|---|---|---|---|---|---|---|---|
| `ayaneo-flip-ds` | 2 A | 4 R | 2 A | **0 R** | yes R | yes R | archetype |
| `ayaneo-flip-1s-ds` | 2 A | 4 R | 2 A | **0 R** | yes R | yes R | archetype |
| `ayaneo-pocket-ds` | 2 A | 4 R | 2 A | **0 R** | yes R | **no R** | archetype |
| `nintendo-ds` | **0 R** | 4 R | 2 R | 2 R | no R | yes R | archetype |
| `nintendo-ds-lite` | **0 R** | 4 R | 2 R | 2 R | no R | yes R | archetype |
| `nintendo-dsi` | 2 A | 4 A | 2 A | 2 A | no R | yes R | archetype |
| `nintendo-dsi-xl` | 2 A | 4 A | 2 A | 2 A | no R | yes R | archetype |
| `nintendo-3ds` | 1 R | 4 R | 2 R | 2 R | no R | yes R | archetype |
| `nintendo-3ds-xl` | 1 R | 4 R | 2 R | 2 R | no R | yes R | archetype |
| `new-nintendo-3ds` | 2 R | 4 R | 4 R | 2 R | no R | yes R | archetype |
| `new-nintendo-3ds-xl` | 2 R | 4 R | 4 R | 2 R | no R | yes R | archetype |
| `nintendo-2ds` | 1 R | 4 R | 2 R | 2 R | no R | yes R | archetype |
| `new-nintendo-2ds-xl` | 2 R | 4 R | 4 R | 2 R | no R | yes R | archetype |

The **cartridge slot is archetype at every preset**: the registry's `ports[]`
vocabulary has no game-card kind (its compilation report records Nintendo's card
slot as omitted for want of a matching enum), so nothing sources it either way.
The D-pad is present on every preset, and the speaker grille is archetype
throughout — the registry does not describe grilles.

### Awaiting a source — no preset

| Device | Why |
|---|---|
| AYN Thor (`ayn-thor`) | AYN publishes no dimensions and no mass on its own site. Telesia gates it on a calibrated measurement of a physical unit (plan gate **H7**). The product page's Shopify JSON carries a shipping weight of the boxed product, not a device mass. |
| Sony Tablet P (`sony-tablet-p`) | sony.com refuses the crawler and sony.net's WAF refuses `curl`; the registry entry has **zero** sources. |
| OneXPlayer ONEXSUGAR Sugar 1 (`onexplayer-onexsugar`) | No closed dimensions from the manufacturer. |

`null = unresolved, never guessed.`

## Archetype derivation rules — these are ours

Where a preset value is not read straight from the registry, it is computed from
one by a rule declared in the generator. They are not manufacturer figures:

| Rule | Value | What it produces |
|---|---|---|
| Deck split | 45 % upper / 55 % lower | `upper_deck_thickness`, `lower_deck_thickness` from the published closed depth. The **sum** is always exactly the published figure. |
| Barrel radius | 0.55 × the thinner deck, capped at (hinge-side bezel − 1 mm) | `hinge_barrel_radius`. The second cap keeps the relief pocket clear of both display windows. |
| Running clearance | 0.4 mm | `hinge_relief_radius = hinge_barrel_radius + 0.4` |
| Hinge run | 50 % of `deck_length`, 3 knuckles, each 14 % of `deck_length` | `hinge_relief_span`, `hinge_knuckle_length`, `hinge_knuckle_pitch`, `hinge_knuckle_start_x`. The run is centred, so the rear face stays solid outboard of it — which is where the shoulder triggers cut. |
| Control margin | 18 mm from the secondary display's edge | `dpad_center_x`, `face_button_center_x`, `stick_first_center_x`, `stick_pitch_x` |
| Stick offset | 18 mm toward the hinge from the cluster row | `stick_center_y` |
| Front row | 8 mm past the display, never closer than 6 mm to the front face | `menu_button_center_y`, `speaker_center_y` |
| Corner radius | 5 mm | `corner_radius` — **0 of the registry's 84 devices publishes one**. |
| Recesses | 0.8 mm displays, 1.2 mm controls | `screen_recess_depth`, `control_recess_depth` |
| Port openings | 9 × 3.2 mm USB-C, 1.75 mm jack radius | the jack radius is half the connector's nominal 3.5 mm, which is the registry's own port kind; the rest is ours. |

Sizes and positions of every control, and the whole cartridge slot and speaker
grille, are archetype outright — the registry records how many buttons a device
has, never how large they are or where they sit.

## Verification

Run at the archetype defaults and at every one of the 13 presets, at
`fold_angle` 0 and 180:

* **Closed envelope** — the union of the three parts against the registry's
  closed height × width × depth. Tolerance 0.5 mm; measured delta **0.000 mm on
  every axis of every preset**.
* **Open envelope** — reported as a model output only. No device in this family
  publishes an open envelope (0 of 16 registry entries), so there is nothing to
  assert against.
* **Solids** — every part a valid B-Rep, a watertight mesh, positive volume,
  and the declared body count.
* **Interference** — the upper deck against the lower deck at 0, 45, 90, 135 and
  180°: **0 mm³ everywhere**.
* **Graph twin** — the same parts through `transpile()` + `cq_runner`, diffed
  against the reference part by part, by bounding box **and by volume**.
* **Audits** — `validate_manifests.py` and `compliance_audit.py --strict` against
  a checkout of this commons.
* Orthographic SVG projections of every preset, closed and open, are committed
  under [`projections/`](projections).

The full table is in the pull request that introduced this cartridge.

## Printing

`upper_deck`, `lower_deck` and `hinge` are separate print targets. The decks lie
with their display faces on the plate. The knuckles print as
`hinge_knuckle_count` separate bodies; they are **not** print-in-place — the
0.4 mm figure is a running clearance for an assembled barrel, not a
print-in-place gap, and a printer that lays 0.4 mm down as a fused layer will
weld it. Increase `hinge_relief_radius` for your process.

## Research

[`research/clamshell-archetype.md`](research/clamshell-archetype.md) — the
archetype's three load-bearing geometric decisions, where it sits on Telesia's
resolution ladder, and what the graph twin cannot yet express, lane by lane
(G-EXPR, G-NODES-1, G-NODES-2, G-CLUSTERS, G-SPEC).
