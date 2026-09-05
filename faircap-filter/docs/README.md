# Faircap Water Filter

An open-source, **print-at-home water filter** that screws onto a standard **PET
bottle neck (PCO-1881)** — a **dual-kernel** hyperobject that renders on
**CadQuery (B-Rep)** by default and keeps its original **OpenSCAD** mode. Screw
the cap onto a bottle of raw water, invert, and drink filtered water from the
nozzle. Clean water from plastic waste, no proprietary cartridges, no commercial
dependency.

*Filtro de agua de código abierto e imprimible en casa que se enrosca en el cuello
de una botella PET estándar (PCO-1881) — un hiperobjeto de **doble núcleo** que
renderiza en **CadQuery (B-Rep)** por defecto y conserva su modo **OpenSCAD**
original. Enrosca la tapa en una botella con agua cruda, inviértela y bebe agua
filtrada por la boquilla. Agua limpia a partir de residuos plásticos, sin
dependencia comercial.*

This is the **output side of the [bottle-thread](../bottle-thread) ecosystem**:
bottle-thread caps/couplers/spouts re-use a bottle as a vessel; Faircap turns the
same neck thread into a filter. Part of the **Yantra4D Hyperobjects Commons**.
Official visualizer and configurator: [Yantra4D](https://app.yantra4d.com).

> ⚠️ **Not a certified clinical/medical device.** This is an open hardware
> fabrication project for making a working filter housing. Filter-media selection,
> water-quality validation and safe drinking-water assurance are the user's
> responsibility; the printed part alone does not guarantee potable output.

**Version**: 2.1.0 · **Slug**: `faircap-filter`

## Modes

The default kernel is **CadQuery (B-Rep)**; the legacy `Standard` mode carries an
explicit `engine: openscad` and renders on OpenSCAD.

| Mode id | Label (en) | Engine | File |
| :--- | :--- | :--- | :--- |
| `cap` | Bottle Cap Filter | CadQuery B-Rep | `main.py` |
| `housing` | Cartridge Housing | CadQuery B-Rep | `main.py` |
| `membrane_holder` | Membrane / Disc Holder | CadQuery B-Rep | `main.py` |
| `Standard` | Standard Filter (OpenSCAD) | OpenSCAD | `faircap.scad` |

**CadQuery modes** — `cap`, `housing`, `membrane_holder`:

- **Bottle Cap Filter** (`cap`) — screws directly onto the bottle: female
  PCO-1881 thread, a drink nozzle you sip from, and an internal seat ledge that
  retains the filter medium. Water path: bottle → threaded bore → past the filter
  seat → nozzle.
- **Cartridge Housing** (`housing`) — a stand-alone filter chamber sized by
  diameter/length: female thread at the inlet, a hollow medium chamber, perforated
  retaining grilles top and bottom, and a reduced outlet boss on top.
- **Membrane / Disc Holder** (`membrane_holder`) — a shallow perforated cup that
  carries a hollow-fiber or ceramic element and drops into the housing (or cap)
  bore; a rim lip lands on the seat ledge so it self-locates.

**OpenSCAD mode** — `Standard`: the original single `filter_housing` filter from
`faircap.scad` (OpenSCAD/BOSL2), driven by the legacy parameter set.

## Interfaces (CDG)

The functional screw interface is a **real single-start helical thread** matched
to the PCO-1881 finish so the printed part actually mates a soda/water bottle:

| Property | Value |
| :--- | :---: |
| Standard | **PCO-1881** |
| Thread major Ø | 27.4 mm |
| Pitch | 2.7 mm |
| Engagement | ~1.5 turns |

The female thread bore is the male major diameter **plus `clearance` per side**,
so printed parts screw on despite tolerances. Because this is the same finish the
`bottle-thread` cartridge threads to, a Faircap and a bottle-thread cap are
interchangeable on the neck (`compatible_with: [bottle-thread]`).

## Parameters

### CadQuery parameters (main modes)

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Filtration | `filter_type` | charcoal | `charcoal` / `membrane` / `ceramic`. Sets grille spacing and disc-holder standoff. |
| Dimensions | `housing_od` | 40 mm | Housing outer diameter (housing / holder). |
| Dimensions | `housing_length` | 80 mm | Housing length — more length holds more medium. |
| Thread Fit & Walls | `clearance` | 0.4 mm | Per-side thread gap for a printable fit (0.3–0.5 typical). |
| Thread Fit & Walls | `wall` | 2.6 mm | Radial wall around thread and chamber. |
| Thread Fit & Walls | `seat_lip` | 2.4 mm | Width of the cap's internal retaining ledge. |
| Drink Nozzle | `nozzle_bore` | 6 mm | Nozzle bore (cap) / outlet spigot bore (housing). |
| Drink Nozzle | `nozzle_len` | 16 mm | Nozzle rise above the cap. |

### OpenSCAD-extended parameters

The legacy `Standard` (OpenSCAD) mode adds its own **Dimensions**-group
parameters — `housing_od_mm` and `housing_length_mm` — driving the single
`filter_housing` solid. Only `Standard` exposes these legacy rows; `filter_type`
is shared.

## Presets

- **Charcoal Cartridge (Standard)** — 40 × 80 mm housing for granular charcoal (`housing`).
- **Ceramic Cartridge (Long)** — 44 × 120 mm housing for a ceramic element (`housing`).
- **Hollow-Fiber Bottle Cap** — sip-cap sized for a hollow-fiber membrane (`cap`).
- **Ceramic Disc Holder** — the disc-holder insert with a central standoff post (`membrane_holder`).
- Legacy OpenSCAD presets — **Charcoal Filter (Standard)**, **Ceramic Filter
  (Long)** — target the `Standard` mode.

## Hyperobject Profile

- **Domain:** household
- **CDG interfaces:**
  - **PET Bottle Neck Thread** (`thread`, *PCO 1881*) — the functional screw
    interface, defined by `clearance` and `wall`. Declared
    `compatible_with: [bottle-thread]`: a Faircap cap and a bottle-thread cap
    mate the same bottle neck.
  - **Filter Medium Housing** (`socket`, internal) — the chamber + retaining
    ledges that seat the filter medium, defined by `filter_type`, `housing_od`,
    `housing_length`, `seat_lip`. The `membrane_holder` element is sized to drop
    into this socket.
- **Material awareness:** the printed-thread fit is exposed as `clearance` so the
  screw fit can be tuned per material/printer; `tolerance_by_material` is declared.
- **Societal benefit:** a discarded PET bottle plus a printed cap becomes a
  working water filter — safe drinking water from questionable sources with no
  supply chain and no commercial dependency. Water sovereignty and plastic
  upcycling in one object.
- **License:** CERN-OHL-W-2.0

## Engines

- **Default engine: CadQuery (B-Rep).** `cap`, `housing`, and `membrane_holder`
  render on CadQuery; every shipped preset and default renders **watertight** and
  exports **STEP** (alongside STL / 3MF / GLB / GLTF / OBJ).
- **Legacy engine: OpenSCAD.** The `Standard` mode carries an explicit per-mode
  `engine: openscad` and renders `faircap.scad` (OpenSCAD/BOSL2) through the
  OpenSCAD kernel.
- The CadQuery script is **self-contained** (sandbox-safe): parameters are read via
  a `PARAM(lambda: name, default)` guard because the render sandbox does not expose
  `globals()` / `eval`. The final solid is assigned to `result`.
- **Threads are real, not cosmetic.** A trapezoidal profile is swept along a
  genuine helical path (`makeHelix`) for the neck's short ~1.5 turns. The rib's
  **root radius is pushed slightly into the surrounding wall material** so the
  boolean union is a clean volumetric merge rather than a fragile tangent kiss —
  which is what keeps the mesh **watertight**. A rib whose root sits exactly on
  the bore surface tessellates into cracks; the overlap fixes that.
- The retaining grilles and seat rings are single bounded boolean operations
  (bounded hole counts), keeping renders fast (~3–10 s) and watertight across all
  shipped presets and the full parameter ranges.
- The `housing` mode is the heaviest (its helical inlet thread lives inside a
  full chamber, ~40k faces); `cap` and `membrane_holder` are lighter.
