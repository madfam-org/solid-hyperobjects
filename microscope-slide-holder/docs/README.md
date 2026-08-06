# Microscope Slide Holder

A parametric microscope-slide retention system — a **dual-kernel** hyperobject
that renders on **CadQuery (B-Rep)** by default and keeps its original **OpenSCAD**
modes. All classes share one Central Design Geometry (CDG): the **standard slide
pocket** — a 25.4 × 76.2 mm (1" × 3") slide, ~1 mm thick, per **ISO 8037-1** / the
US "3×1" convention — plus a per-side printable clearance so the printed slot
actually accepts a real slide.

*Sistema paramétrico de retención de portaobjetos de microscopio — un hiperobjeto
de **doble núcleo** que renderiza en **CadQuery (B-Rep)** por defecto y conserva
sus modos **OpenSCAD** originales. Todas las clases comparten una Geometría de
Diseño Central: el **bolsillo estándar de laminilla** de 25.4 × 76.2 mm según
ISO 8037-1, más una holgura imprimible por lado.*

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

> ⚠️ **Not a certified clinical device.** These are open hardware lab-organizer
> blanks for histology/cytology/archival workflows. They are not diagnostic
> instruments; validation for any clinical or laboratory-accredited use is the
> user's responsibility.

**Version**: 3.1.0 · **Slug**: `microscope-slide-holder`

## Modes

The default kernel is **CadQuery (B-Rep)**; every legacy OpenSCAD mode carries an
explicit `engine: openscad`. The CadQuery re-author uses distinct mode ids
(`slide_box`, `slide_tray`, `staining_rack_cq`) so they do not collide with the
OpenSCAD mode ids in the dual-engine manifest.

| Mode id | Label (en) | Engine | File |
| :--- | :--- | :--- | :--- |
| `slide_box` | Storage Box | CadQuery B-Rep | `main.py` |
| `slide_tray` | Horizontal Tray | CadQuery B-Rep | `main.py` |
| `staining_rack_cq` | Staining Rack | CadQuery B-Rep | `main.py` |
| `box` | Storage Box (OpenSCAD) | OpenSCAD | `box.scad` |
| `tray` | Horizontal Tray (OpenSCAD) | OpenSCAD | `tray.scad` |
| `staining_rack` | Staining Rack (OpenSCAD) | OpenSCAD | `staining_rack.scad` |
| `cabinet_drawer` | Cabinet Drawer (OpenSCAD) | OpenSCAD | `cabinet_drawer.scad` |

**CadQuery modes** — `slide_box`, `slide_tray`, `staining_rack_cq`:

- **Storage Box** (`slide_box`, parts `slide_box` + `slide_box_lid`) — covered box
  holding N slides on edge in a comb of parallel slots, with a matching skirt lid
  (optional inner snap lip).
- **Horizontal Tray** (`slide_tray`) — flat tray with a `columns × rows` grid of
  slide-shaped pockets; optional finger notch cut through each pocket for removal.
- **Staining Rack** (`staining_rack_cq`) — open skeletonised frame that holds
  slides on edge for dipping in reagent; open crossbar bottom (fluid circulation)
  or a drainage-sloped solid floor, optional carrying handle.

**OpenSCAD modes** — `box` (parts `box_base` + `box_lid`), `tray` (`tray`),
`staining_rack` (`rack`), and `cabinet_drawer` (parts `drawer` + `shell`): the
original four retention classes. The **Cabinet Drawer** class exists **only** on
the OpenSCAD engine — it was not re-authored in CadQuery.

Each CadQuery mode dispatches on the `target_part` global injected by the
platform, and the manifest's `parts[]` ids equal those dispatch keys.

## Parameters

### CadQuery parameters (main modes)

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Slide | `slide_standard` | US 3"×1" (1) | ISO / US / Petrographic / Supa Mega / Custom. |
| Slide | `custom_slide_length` / `_width` / `_thickness` | 76.2 / 25.4 / 1.0 mm | Used only when Standard = Custom. |
| Architecture | `num_slots` | 20 | Slide capacity (box + rack). |
| Structure | `wall` | 2.0 mm | Outer wall / floor thickness. |
| Tolerance | `tolerance_xy` / `tolerance_z` | 0.4 / 0.2 mm | In-plane and thickness clearance for FDM fit. |
| Box | `density` | Working (1) | Rib width between slots → slot pitch. |
| Box | `lid_snap` | on | Inner retention lip on the lid. |
| Tray | `tray_columns` / `tray_rows` | 5 / 2 | Pocket grid. |
| Tray | `finger_notch` | on | Removal notch per pocket. |
| Rack | `handle` | on | Carrying handle. |
| Rack | `open_bottom` | on | Crossbars vs. solid drainage floor. |
| Rack | `drainage_angle` | 5° | Floor runoff slope (solid floor only). |

### OpenSCAD-extended parameters

The legacy OpenSCAD modes (`box`, `tray`, `staining_rack`, `cabinet_drawer`) add
their own parameters by group on top of the shared `slide_standard` / slide
envelope, including:

- **Structure / Features / Quality** — `wall_thickness`, `label_area`, `fn` ($fn).
- **Box — Architecture** — `rib_profile`, `rib_width`, `lid_latch` (snap /
  magnetic / none), `stackable`, `numbering_start`.
- **Tray — Features** — `anti_capillary`.
- **Cabinet — Features** — `rail_profile` (T-slot / L-rail), `backstop`,
  `drawers_per_shell`.

Only the OpenSCAD modes expose these legacy rows.

## Presets

- **Standard 20-Place Box** — US slides, working density, snap lid (`slide_box`).
- **100-Place Archival Box** — ISO slides at archival density (`slide_box`).
- **Drying Tray (5×2)** — 10 pockets, finger notches (`slide_tray`).
- **20-Slide Staining Rack** — open bottom, 5° drainage, handle (`staining_rack_cq`).
- Legacy OpenSCAD presets — **Standard 25-Place Box**, **100-Place Archival Box**,
  **Petrographic Box (20)**, **Drying Tray (5×2)**, **20-Slide Staining Rack**,
  **Compact 5-Slide Box**, **Supa Mega Tray (2×2)**, **Cabinet Unit (5 drawers)** —
  target the OpenSCAD modes.

## Hyperobject Profile

- **Domain:** medical
- **CDG interfaces:**
  - **Microscope Slide Slot** (`pocket`, *ISO 8037-1 (25.4×76.2mm)*) — the shared
    slide envelope. Driven by `slide_standard` (or the `custom_slide_*` trio) plus
    `tolerance_xy` / `tolerance_z` and `num_slots`. Every mode's retaining
    geometry derives its slot/pocket from this one interface, so a slide that
    fits one fits all.
  - **Retention Pitch System** (`rail`, internal) — `density`, `num_slots`; the
    rib width between slots sets the box slot pitch.
  - **Press-Fit Lid Seam** (`snap`, internal) — `lid_snap`, `wall`, `num_slots`;
    the lid skirt is sized from the same envelope as the box so it always caps
    its base.
- **Material awareness:** clearance is exposed (`tolerance_xy`, `tolerance_z`) so
  the fit can be tuned per material/printer; `tolerance_by_material` is declared.
- **Societal benefit:** lets laboratories and pathology departments fabricate
  precision slide retention for histology, cytology, and archival workflows,
  independent of commercial supply chains.
- **License:** CERN-OHL-W-2.0

## Engines

- **Default engine: CadQuery (B-Rep).** `slide_box`, `slide_tray`, and
  `staining_rack_cq` render on CadQuery; every shipped preset and default renders
  **watertight** and exports **STEP** (alongside STL / 3MF / GLB / GLTF / OBJ).
- **Legacy engine: OpenSCAD.** `box`, `tray`, `staining_rack`, and `cabinet_drawer`
  each carry an explicit per-mode `engine: openscad` and render their respective
  `.scad` files through the OpenSCAD kernel. The **Cabinet Drawer** class is
  available only here.
- The CadQuery script is **self-contained** (sandbox-safe): parameters are read via
  a `PARAM(lambda: name, default)` guard because the render sandbox exposes neither
  `globals()` nor `eval` / `getattr`; the final solid is assigned to `result`.
- Repeated features (slot combs, pocket grids, rib rails) are built as a single
  `pushPoints` / `eachpoint` compound so each becomes one boolean, keeping every
  variant (including the 100-slot box and 10×5 tray) watertight and fast.
