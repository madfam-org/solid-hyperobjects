# Book-Fold Phone

The book-fold phone as a parametric **archetype**: two rigid half-frames on a
fold axis running along the long edge, one continuous display folded inward
across both of them, a cover display on the outside of one half, a teardrop
crease relief, and one continuous fold angle from closed to open. Dual-engine —
a CadQuery (B-Rep) reference and a node-graph twin that build the same three
parts.

Named devices ride as **presets**, and every millimetre in a preset is a
published dimension with a provenance line or a declared archetype default.
Read [`../NOTICE`](../NOTICE) before you use one: this is a fit envelope, not a
likeness, and it reproduces no trade dress of any kind.

## Frame — read this first

Manufacturers in this family label the LONG axis "width" (Apple's iPhone Duo
page reads "Open: Width: 6.48 inches (164.6 mm); Height: 4.64 inches (117.8 mm)"
— the 117.8 mm figure is the SHORT edge by Apple's labels and the axis the hinge
runs along), and Telesia's registry records their labels literally. The mapping
is:

| Model | Registry field | What it is |
|---|---|---|
| `hinge_axis_length` | `dimensions_mm.closed.height` | X — the long axis. **The fold axis is the X axis through the origin.** It equals `dimensions_mm.open.height` on every device in this family that publishes both, which is what makes this mapping a checked fact rather than a reading of a label. |
| `cover_half_width` | `dimensions_mm.closed.width` | Y — the folding axis, for the half that carries the cover display. It runs from the fold at `y = 0` to its opening edge. |
| `camera_half_width` | `open.width − closed.width` | Y — the other half, which is **narrower**. That difference is why a book fold closes, and both ends of the subtraction are the manufacturer's. |
| `half_thickness` | `dimensions_mm.open.depth` | Z — the open body IS one half. |
| the hinge gap | `closed.depth − 2 × open.depth` | Z — the space the folded panel's teardrop occupies. |

`fold_angle` 0 is closed; 180 is open.

**The fold axis sits in the MIDDLE of the gap.** That single choice is what makes
the closed depth `2 × half_thickness + gap` and the open depth exactly
`half_thickness`: a 180° turn about that axis lands the camera half in the cover
half's own z band, so the gap closes itself as the device opens — which is what a
teardrop hinge does, and what the published pair of depths describes.

## Modes and parts

| Mode | Engine | Parts | What it is |
|---|---|---|---|
| `device` | CadQuery | cover_half, camera_half, hinge | All three in world coordinates at the current fold angle. A preview, not a print target. |
| `cover_half` | CadQuery | cover_half | The half with the cover display, the side buttons and the end-face openings. |
| `camera_half` | CadQuery | camera_half | The half with the camera island, already turned by `fold_angle`. |
| `hinge` | CadQuery | hinge | The leaf that turns inside the crease relief. |
| `graph_device` | graph | cover_half, camera_half, hinge | The same three parts from `bookfold.graph.json`. Server-only, pro/premium, like every graph cartridge. |

Expected body count: 1 for each part, at every fold angle.

## Composition — a device is a hyperobject of hyperobjects

A display, a hinge, a lens window, a button, a port and a card tray are each a
hyperobject in their own right that feeds into this one — Telesia's
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
| `frame_half` | `framehalf_` | `device_envelope`, `cradle_seat` | — |
| `foldable_display` | `foldabledisplay_` | `crease_region` | `fold_axis` |
| `display_panel` | `displaypanel_` | `display_recess` | — |
| `hinge_foldable` | `hingefold_` | `fold_axis` | `crease_region` |
| `lens_window` | `lenswindow_` | `lens_aperture` | — |
| `system_button_cluster` | `systembuttons_` | `button_seat` | — |
| `port_receptacle` | `port_` | `port_cutout` | — |
| `card_slot` | `cardslot_` | `card_slot` | — |
| `speaker_grille` | `speaker_` | — (a vented face is not a mating feature) | — |

Three of those — `display_panel`, `port_receptacle` and the `button_seat`
interface — already exist in
[`clamshell-dual-screen-handheld`](../../clamshell-dual-screen-handheld) under
the same ids. That duplication is the concrete thing gate H8 and yantra4d's
**G-CLUSTERS** lane would remove; it is written down here rather than hidden so
the second cartridge is evidence for the lane rather than just more surface.

The twin can only **imitate** the component boundary: its node ids carry the
component slug as a prefix and nothing more. (`component:<slug>` cannot be the
literal prefix: the transpiler's node-id grammar is `^[A-Za-z][A-Za-z0-9_]*$`, so
a colon fails validation before the graph renders.)

## Hyperobject Profile

- **Domain:** consumer-electronics
- **CDG interfaces:**
  - **Device Envelope** (`profile`, internal) — the closed outline,
    `hinge_axis_length × cover_half_width × (2 × half_thickness + gap)`; the open
    one is `hinge_axis_length × (cover_half_width + camera_half_width) ×
    half_thickness`. What a stand or a mount takes as its device.
  - **Fold Axis** (`hinge`, internal) — the X axis through the origin, in the
    middle of the gap. `compatible_with`
    [`hinge-hyperobject`](../../hinge-hyperobject) and
    [`rugged-box`](../../rugged-box).
  - **Crease Region** (`surface`, internal) — the strip of the folding panel that
    bends, and what the relief is sized to give room to.
  - **Display Recess** (`screen`, internal) — the cover display's window, sunk
    `display_recess_depth` into the cover half's outer face.
  - **Lens Aperture** (`pocket`, internal) — the recessed camera island and its
    apertures.
  - **Button Seat** (`pocket`, internal) — a pocket in the opening edge for a
    power or volume key.
  - **USB-C Port Opening** (`port`, internal) — present only where the registry
    lists the port.
  - **Card Tray Slot** (`socket`, internal) — present only where the registry
    lists a `sim` port.
  - **Cradle Seat** (`surface`, internal) — the cover half's outer face and
    footprint.
- **Material awareness:** `tolerance_by_material` — the relief-versus-leaf
  clearance is the knob a material profile moves. Nothing else here is
  material-aware; the registry's `materials` block is populated for most devices
  in this family (titanium, aluminium, glass) but names finishes, not figures.
- **Societal benefit:** a dimensioned, parametric model of the book-fold phones
  people actually own lets anyone fabricate a cradle, a dock, a travel shell, a
  screen-protector jig or a repair fixture that fits.
- **Licence:** CERN-OHL-W-2.0

## Presets — where every number comes from

Presets are **generated**, never typed: Telesia's `scripts/device-presets.py`
reads `data/registry/device-geometry.json` (snapshot 2026-09-13) and emits the
`presets` block together with `_generated_from`, which records the registry's
SHA-256. A preset sets **only** the parameters the registry sources for that
device; everything else stays at the archetype default, and the last column says
which. Every source in this family is tier `primary` — the manufacturer's own
specification page or press release.

Every preset reaches rung **L2** of the plan's resolution ladder (envelope,
displays, features).

| Preset | Closed H × W × D (mm) | Open H × W × D (mm) | Gap (mm) | Registry source (tier `primary`) | Groups that fell back to the archetype |
|---|---|---|---|---|---|
| `xiaomi-mix-fold-3` | 161.2 × 73.5 × 10.96 | 161.2 × 143.28 × 5.26 | 0.44 | mi.com/xiaomi-mix-fold-3/specs | display windows (inner + cover) |
| `xiaomi-mix-fold-4` | 159.37 × 73.1 × 9.47 | 159.37 × 143.3 × 4.59 | 0.29 | mi.com/prod/xiaomi-mix-fold-4/specs | display windows (inner + cover) |
| `vivo-x-fold-3-pro` | 159.96 × 72.55 × 11.2 | 159.96 × 142.4 × 5.2 | 0.8 | vivo.com/en/products/param/x-fold3-pro | display windows (inner + cover) |
| `vivo-x-fold-5` | 159.68 × 72.6 × 9.2 | 159.68 × 142.29 × 4.3 | 0.6 | vivo.com/en/products/param/x-fold5 | display windows (inner + cover) |
| `oppo-find-n3` ‡ | 153.4 × 73.3 × 11.7 | — × — × 5.9 | 0.05 | oppo.com/en/smartphones/series-find-n/find-n3/specs/ | half thickness (see ‡); camera-half width (no published open width); display windows |
| `oppo-find-n5` | 160.87 × 74.42 × 8.93 | 160.87 × 146.58 × 4.21 | 0.51 | oppo.com/en/smartphones/series-find-n/find-n5/specs/ | display windows (inner + cover) |
| `honor-magic-v2` | 156.7 × 74.0 × 10.1 | 156.7 × 145.4 × 4.8 | 0.5 | honor.com/global/phones/honor-magic-v2/spec/ | display windows (inner + cover) |
| `honor-magic-v3` | 156.6 × 74.0 × 9.3 | 156.6 × 145.3 × 4.4 | 0.5 | honor.com/global/phones/honor-magic-v3/spec/ | display windows (inner + cover) |
| `honor-magic-v5` | 156.8 × 74.3 × 9.0 | 156.8 × 145.9 × 4.2 | 0.6 | honor.com/global/phones/honor-magic-v5/spec/ | display windows (inner + cover) |
| `huawei-mate-x3` | 156.9 × 72.4 × 11.08 | 156.9 × 141.5 × 5.3 | 0.48 | consumer.huawei.com/om/phones/mate-x3/specs/ | display windows (inner + cover) |
| `huawei-mate-x5` | 156.9 × 72.4 × 11.08 | 156.9 × 141.5 × 5.3 | 0.48 | web.archive.org/…/consumer.huawei.com/cn/phones/mate-x5/specs/ | display windows (inner + cover) |
| `huawei-mate-x6` | 156.6 × 73.78 × 9.9 | 156.6 × 144.04 × 4.6 | 0.7 | consumer.huawei.com/en/phones/mate-x6/specs/ | display windows (inner + cover) |
| `oneplus-open` | 153.4 × 73.3 × 11.9 | 153.4 × 143.1 × 5.9 | 0.1 | oneplus.com/us/open/specs | display windows (inner + cover) |
| `google-pixel-fold` | 139.7 × 79.5 × 12.1 | 139.7 × 158.7 × 5.8 | 0.5 | web.archive.org/…/store.google.com/gb/product/pixel_fold_specs | display windows (inner + cover) |
| `google-pixel-10-pro-fold` | 155.2 × 76.3 × 10.8 | 155.2 × 150.4 × 5.2 | 0.4 | store.google.com/gb/product/pixel_10_pro_fold_specs | display windows (inner + cover) |
| `samsung-galaxy-fold` | 160.9 × 62.8 × 17.1 | 160.9 × 117.9 × 7.6 | 1.9 | news.samsung.com/global/samsung-unfolds-the-future-with-a-whole-new-mobile-category… | display windows (inner + cover) |
| `samsung-galaxy-z-fold2` | 159.2 × 68.0 × 16.8 | 159.2 × 128.2 × 6.9 | 3.0 | news.samsung.com/global/introducing-the-galaxy-z-fold2… | display windows (inner + cover) |
| `samsung-galaxy-z-fold3` | 158.2 × 67.1 × 16.0 | 158.2 × 128.1 × 6.4 | 3.2 | news.samsung.com/global/the-next-chapter-in-mobile-innovation… | display windows; sim card slot |
| `samsung-galaxy-z-fold4` | 155.1 × 67.1 × 15.8 | 155.1 × 130.1 × 6.3 | 3.2 | news.samsung.com/global/introducing-samsung-galaxy-z-flip4-and-galaxy-z-fold4… | display windows; sim card slot |
| `samsung-galaxy-z-fold5` | 154.9 × 67.1 × 13.4 | 154.9 × 129.9 × 6.1 | 1.2 | news.samsung.com/global/samsung-galaxy-z-flip5-and-galaxy-z-fold5… | display windows; sim card slot |
| `samsung-galaxy-z-fold6` | 153.5 × 68.1 × 12.1 | 153.5 × 132.6 × 5.6 | 0.9 | news.samsung.com/global/samsung-galaxy-z-fold-6-and-z-flip-6… | display windows; sim card slot |
| `samsung-galaxy-z-fold7` | 158.4 × 72.8 × 8.9 | 158.4 × 143.2 × 4.2 | 0.5 | news.samsung.com/global/samsung-galaxy-z-fold7-raising-the-bar-for-smartphones | display windows; sim card slot |
| `samsung-galaxy-z-fold8` | 123.9 × 81.9 × 9.7 | 123.9 × 161.4 × 4.5 | 0.7 | news.samsung.com/global/samsung-galaxy-z-fold8-ultra-fold8-and-flip8… | display windows (inner + cover) |
| `samsung-galaxy-z-fold8-ultra` | 158.4 × 72.8 × 8.9 | 158.4 × 143.2 × 4.1 | 0.7 | news.samsung.com/global/samsung-galaxy-z-fold8-ultra-fold8-and-flip8… | display windows; sim card slot |
| `google-pixel-9-pro-fold` | 155.2 × 77.1 × 10.5 | 155.2 × 150.2 × 5.1 | 0.3 | store.google.com/gb/product/pixel_9_pro_fold_specs | display windows (inner + cover) |
| `google-pixel-11-pro-fold` | 155.2 × 76 × 10.1 | 155.2 × 150.4 × 5.0 | 0.1 | store.google.com/gb/product/pixel_11_pro_fold_specs | display windows (inner + cover) |
| `apple-iphone-duo` † | 117.8 × 84.1 × 11.3 | 117.8 × 164.6 × 5.2 | 0.9 | apple.com/iphone-duo/specs/ | **none** |

† **The iPhone Duo is the only preset in this family with no fallback at all.**
Apple publishes a pixel count *and a ppi* for both displays, so the registry can
derive an active area — 110.93 × 157.72 mm inner, 77.19 × 112.31 mm cover, both
marked `derived` with the formula — and every other value it needs is on the same
page. No other manufacturer in this family publishes a ppi, so the registry
leaves their active areas `null` and this cartridge will not derive one.

‡ **OPPO's two published depths cannot both hold.** 11.7 mm closed against
2 × 5.9 mm open is −0.1 mm of gap. The closed envelope is what this cartridge
asserts against, so the half thickness comes from it instead (5.825 mm) and the
model's open depth lands 0.075 mm from OPPO's figure — reported in the
verification table, not hidden. OPPO also publishes no open width or height for
this model.

### Three fold states, also generated

`fold-state-closed` (0°), `fold-state-half-open` (90°) and `fold-state-open`
(180°) are presets too, emitted by the same generator, so no degree in this
cartridge is typed by hand either. They set `fold_angle` and nothing else, which
means `cover_half` and `hinge` render identically across all three — those two
parts do not move with the fold, by construction. `y4d-spec --render` reports
that as a note, and it is the expected one.

### Which components each preset exercises

**R** = the registry's port list carries the entry. **no R** = the
manufacturer's own port list is sourced and does NOT contain it — a sourced
*absence*, which is a zero, not an unknown. **A** = the registry does not resolve
it and the archetype's default applies.

| Preset | inner display | cover display | crease | USB-C | card tray | camera island | buttons |
|---|---|---|---|---|---|---|---|
| `xiaomi-mix-fold-3` | A | A | — | yes R | **no R** | archetype | archetype |
| `xiaomi-mix-fold-4` | A | A | teardrop R | yes R | yes R | archetype | archetype |
| `vivo-x-fold-3-pro` | A | A | — | yes R | yes R | archetype | archetype |
| `vivo-x-fold-5` | A | A | — | yes R | yes R | archetype | archetype |
| `oppo-find-n3` | A | A | — | yes R | yes R | archetype | archetype |
| `oppo-find-n5` | A | A | — | yes R | yes R | archetype | archetype |
| `honor-magic-v2` | A | A | teardrop R | yes R | yes R | archetype | archetype |
| `honor-magic-v3` | A | A | — | yes R | yes R | archetype | archetype |
| `honor-magic-v5` | A | A | — | yes R | yes R | archetype | archetype |
| `huawei-mate-x3` | A | A | teardrop R | yes R | yes R | archetype | archetype |
| `huawei-mate-x5` | A | A | teardrop R | yes R | yes R | archetype | archetype |
| `huawei-mate-x6` | A | A | teardrop R | yes R | yes R | archetype | archetype |
| `oneplus-open` | A | A | teardrop R | yes R | yes R | archetype | archetype |
| `google-pixel-fold` | A | A | — | yes R | yes R | archetype | archetype |
| `google-pixel-10-pro-fold` | A | A | — | yes R | yes R | archetype | archetype |
| `samsung-galaxy-fold` | A | A | — | yes R | **no R** | archetype | archetype |
| `samsung-galaxy-z-fold2` | A | A | — | yes R | **no R** | archetype | archetype |
| `samsung-galaxy-z-fold3` | A | A | — | yes R | yes A | archetype | archetype |
| `samsung-galaxy-z-fold4` | A | A | — | yes R | yes A | archetype | archetype |
| `samsung-galaxy-z-fold5` | A | A | — | yes R | yes A | archetype | archetype |
| `samsung-galaxy-z-fold6` | A | A | — | yes R | yes A | archetype | archetype |
| `samsung-galaxy-z-fold7` | A | A | teardrop R | yes R | yes A | archetype | archetype |
| `samsung-galaxy-z-fold8` | A | A | — | yes R | **no R** | archetype | archetype |
| `samsung-galaxy-z-fold8-ultra` | A | A | — | yes R | yes A | archetype | archetype |
| `google-pixel-9-pro-fold` | A | A | — | yes R | yes R | archetype | archetype |
| `google-pixel-11-pro-fold` | A | A | — | yes R | yes R | archetype | archetype |
| `apple-iphone-duo` | **R, derived** | **R, derived** | — | yes R | **no R** (eSIM only) | archetype | archetype |

The `crease` column is what the registry knows about the hinge itself: seven
devices' manufacturers say "teardrop" (or "water-drop") in words. **None of them
publishes a figure for it**, so the column changes no geometry — the relief here
is a plain cylinder at an archetype radius. Turning that word into a section is
L3, and it needs a free-form profile (yantra4d lane G-NODES-1).

The camera island, the buttons and the speaker grille are **archetype at every
preset**. The registry records no camera geometry for any device in this family,
and its only control kind here is `fingerprint` (4 of 28 devices), with no
geometry attached.

### Awaiting a source — no preset

| Device | Why |
|---|---|
| Samsung Galaxy Z Fold Special Edition (`samsung-galaxy-z-fold-special-edition`) | The Korean launch release gives a closed thickness (10.6 mm) and a mass, but no closed height or width and no open envelope. Without a closed envelope there is nothing for a preset to be. |

`null = unresolved, never guessed.`

## Archetype derivation rules — these are ours

Where a preset value is not read straight from the registry, it is computed from
one by a rule declared in the generator. They are not manufacturer figures:

| Rule | Value | What it produces |
|---|---|---|
| Half thickness | the published open depth | `half_thickness`. Falls back to `(closed depth − 0.05) / 2` only when the two published depths contradict each other. |
| Hinge gap | `closed depth − 2 × half thickness` | the two halves' centre-Z values. Recorded per preset as `registry.hinge_gap_mm`. |
| Camera-half width | `open width − closed width` | `camera_half_width`. Falls back to the cover half's width when no open width is published. |
| Crease relief radius | `gap/2 + 0.45 × half thickness`, capped at `gap/2 + half thickness − 0.6` | `hinge_cavity_radius`. The cap is the wall left against the outer face. |
| Running clearance | 0.3 mm | `hinge_leaf_radius = hinge_cavity_radius − 0.3` |
| Hinge run | 94 % of the hinge-axis length | `hinge_cavity_span`, `hinge_leaf_span` |
| Display window fallback | the published envelope inset by a 2.5 mm bezel | `inner_display_*`, `cover_display_*` where the registry resolves no active area. On the one device that publishes one, this rule lands within 0.5 mm of the manufacturer's own cover-display figure. |
| Display centring | the inner display is centred on the OPEN envelope | `inner_display_cover_span`, `inner_display_camera_span` — equal bezels, and therefore an unequal split about the fold axis. |
| Corner radius | 6 mm, on the opening edge only | `corner_radius` — **0 of the registry's 84 devices publishes one**. |
| Recesses | 0.8 mm displays, 0.6 mm camera island, 1.8 mm lens apertures | `display_recess_depth`, `lens_island_depth`, `lens_depth` |
| Camera island | `min(0.20 × length, 0.42 × camera-half width)`, 6 mm in from two edges | `lens_island_*`, `lens_*` |
| Port openings | 8.6 × 2.8 mm USB-C, 12.5 × 2.0 mm card tray | the USB-C figure clears a receptacle whose plug is 8.34 × 2.56 mm nominal; the rest is ours. |
| End-face layout | USB-C centred, card tray at 22 % of the width, speaker row inboard of the corner radius | the three are checked against each other and the derivation raises rather than overlapping them. |

## Verification

Run at the archetype defaults and at every one of the 27 device presets, at
`fold_angle` 0 and 180:

* **Closed envelope** — the union of the three parts against the registry's
  closed height × width × depth. Tolerance 0.5 mm; measured delta **0.000 mm on
  every axis of every preset**.
* **Open envelope** — against the registry's open height × width × depth, which
  26 of the 27 devices publish. Measured delta **0.000 mm on every axis of every
  preset except `oppo-find-n3`**, whose open depth is 0.075 mm out because OPPO's
  own two figures contradict each other (see ‡ above); its open height and width
  are unpublished and are reported as model outputs.
* **Solids** — every part a valid B-Rep (`BRepCheck_Analyzer`), a watertight
  mesh, positive volume, and one body.
* **Interference** — the two halves against each other and against the hinge leaf
  at 0, 45, 90, 135 and 180°: **0 mm³ everywhere**.
* **Graph twin** — the same parts through `transpile()` + `cq_runner`, diffed
  against the reference part by part, by bounding box **and by volume**.
* **Audits** — `y4d-spec check book-fold-phone --render -v` against the
  hyperobjects-spec pin: **0 failures, 186 renders, 180 of them presets**.
* Orthographic SVG projections of a representative set of presets, closed and
  open, are committed under [`projections/`](projections).

The full table is in the pull request that introduced this cartridge.

## Printing

`cover_half`, `camera_half` and `hinge` are separate print targets. The halves
lie with their display faces on the plate. Two printability notes from
`y4d-spec --render`, both real and both worth knowing before you press print:

* **The hinge leaf is thin on the thinnest presets.** On devices whose published
  open depth is around 4 mm the leaf's median local thickness is 0.70–0.79 mm,
  below two 0.4 mm perimeters. It is a fit and clearance study at those sizes,
  not an FDM part; increase `hinge_leaf_radius` (and `hinge_cavity_radius` with
  it) for your process.
* **The camera half has overhang.** The crease relief is a cylinder cut into the
  inner face, so 26–41 % of that part's surface is downward-facing slope
  depending on the preset. Reorient or support it.

The 0.3 mm relief-to-leaf figure is a **running clearance for an assembled
hinge**, not a print-in-place gap; a printer that lays 0.3 mm down as a fused
layer will weld it.

## Research

[`research/book-fold-archetype.md`](research/book-fold-archetype.md) — the
archetype's load-bearing geometric decisions, where it sits on Telesia's
resolution ladder, and what the graph twin cannot yet express, lane by lane
(G-EXPR, G-NODES-1, G-NODES-2, G-CLUSTERS, G-SPEC).
