# Parametric Prosthetic Socket

A printable, fully customizable **lower-limb prosthetic socket blank** — a
**dual-kernel** hyperobject that renders on **CadQuery (B-Rep)** by default and
keeps its original **OpenSCAD** modes. The socket is the tapered elliptical cup
that interfaces a residual limb with the prosthetic pylon; the limb is
**parameterized** (proximal/distal diameter, length, wall thickness) and the
distal end carries the open **e-NABLE / Open Source Leg 4-bolt pyramid adapter** so
any compatible foot or knee bolts on.

*Un blank de socket protésico de miembro inferior imprimible y personalizable — un
hiperobjeto de **doble núcleo** que renderiza en **CadQuery (B-Rep)** por defecto y
conserva sus modos **OpenSCAD** originales. Una copa elíptica cónica parametrizada
por los diámetros proximal/distal, la longitud y el grosor de pared, con un
adaptador piramidal distal de 4 pernos e-NABLE / Open Source Leg.*

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

> ⚠️ **Not a certified clinical device.** This is a fabrication *blank*. A
> prosthetic socket must be measured, fitted and approved by a qualified clinician
> (prosthetist) before it is worn or load-bearing. Print a **check socket** first
> and confirm fit under professional supervision.

**Version**: 2.1.0 · **Slug**: `prosthetic-socket`

## Modes

The default kernel is **CadQuery (B-Rep)**; both legacy OpenSCAD modes carry an
explicit `engine: openscad`.

| Mode id | Label (en) | Engine | File |
| :--- | :--- | :--- | :--- |
| `transtibial` | Transtibial (Below-Knee) | CadQuery B-Rep | `main.py` |
| `transfemoral` | Transfemoral (Above-Knee) | CadQuery B-Rep | `main.py` |
| `check_socket` | Check Socket (Test Fit) | CadQuery B-Rep | `main.py` |
| `transtibial_socket` | Transtibial Socket (OpenSCAD) | OpenSCAD | `socket.scad` |
| `transfemoral_socket` | Transfemoral Socket (OpenSCAD) | OpenSCAD | `socket.scad` |

**CadQuery modes** — `transtibial`, `transfemoral`, `check_socket`:

- **Transtibial (Below-Knee)** (`transtibial`) — shorter, more elliptical cup for
  a below-knee residuum.
- **Transfemoral (Above-Knee)** (`transfemoral`) — longer, rounder, fuller-brim
  cup for an above-knee residuum.
- **Check Socket (Test Fit)** (`check_socket`) — thin-wall, always-ventilated
  trial socket for iterative fitting.

**OpenSCAD modes** — `transtibial_socket`, `transfemoral_socket`: the original
Voronoi-patterned `socket_shell` from `socket.scad`, selected by the legacy
`amputation_level` control.

Each CadQuery mode dispatches on `target_part` (the part id injected per-mode), so
the three modes render as three distinct geometries.

## Parameters

### CadQuery parameters (main modes)

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Limb Measurements | `proximal_dia` | 95 mm | Top opening — limb diameter at the brim. |
| Limb Measurements | `distal_dia` | 62 mm | Bottom diameter (must be < proximal). |
| Limb Measurements | `socket_len` | 180 mm | Cup length along the limb axis. |
| Structure | `wall` | 4.0 mm | Shell wall thickness (check socket auto-thins to ≤ 3.5). |
| Structure | `floor` | 6.0 mm | Closed distal-floor thickness under the adapter seat. |
| Cup Shape | `ovality` | 1.18 | 1.0 = round; higher flattens antero-posteriorly. |
| Cup Shape | `brim_flare` | 1.12 | Outward flare of the top rim (1.0 = straight). |
| Distal Adapter | `adapter_plate_dia` | 58 mm | Solid seat diameter carrying the bolt pattern. |
| Distal Adapter | `bolt_circle_dia` | 40 mm | Pitch circle of the 4-bolt pyramid adapter. |
| Distal Adapter | `bolt_dia` | 5.5 mm | Bolt through-hole (5.5 = M5 clearance). |
| Distal Adapter | `pyramid` | on | Add the male 4-sided pyramid boss. |
| Breathability | `ventilation` | off | Ring pattern of wall holes (forced on for check socket). |
| Breathability | `vent_density` | 8 | Holes per ventilation ring. |

### OpenSCAD-extended parameters

The legacy OpenSCAD modes (`transtibial_socket`, `transfemoral_socket`) add their
own parameters by group — a **Limb Type** group (`amputation_level`), a
**Measurements** group (`circumference_top`, `circumference_bottom`, `length`), a
**Pattern** group (`voronoi_density`, driving the breathable Voronoi shell), a
**Structure** group (`wall_thickness`), and a **Quality** group (`fn`, $fn). Only
the OpenSCAD modes expose these legacy rows.

## Presets

- **Adult Below-Knee** — 100 / 68 mm, 175 mm long (`transtibial`).
- **Adult Above-Knee** — 150 / 110 mm, 300 mm long, flared brim (`transfemoral`).
- **Child Check Socket** — 78 / 52 mm, 130 mm, ventilated (`check_socket`).
- Legacy OpenSCAD presets — **Child Below-Knee (Small)**, **Adult Below-Knee
  (Medium)**, **Adult Above-Knee (Large)** — target the OpenSCAD modes.

## Hyperobject Profile

- **Domain:** medical
- **CDG interfaces:**
  - **Distal Pyramid Adapter** (`bolt_pattern`, *e-NABLE / OSL 4-bolt*) — the
    load-bearing interface to the pylon/foot/knee, defined by `bolt_circle_dia`,
    `bolt_dia`, `adapter_plate_dia`, `pyramid`. Any compatible component that
    honours the same 4-bolt pyramid pattern mounts to this socket.
  - **Limb Socket Contour** (`surface`, internal) — the fitted cup surface,
    defined by `proximal_dia`, `distal_dia`, `socket_len`, `ovality`,
    `brim_flare`. These four field-measurable limb dimensions stand in for a scan.
- **Material awareness:** wall/floor and clearances are exposed so the fit can be
  tuned per material and printer; `shrinkage_compensation` and
  `tolerance_by_material` are declared.
- **Societal benefit:** accessible, custom-fit prosthetic care — a socket sized
  to any limb from four measurable dimensions and printed locally at a fraction of
  clinical cost, with a check-socket workflow for iterative fitting, riding the
  open e-NABLE / Open Source Leg interface for cross-commons interoperability.
- **License:** CERN-OHL-W-2.0

## Engines

- **Default engine: CadQuery (B-Rep).** `transtibial`, `transfemoral`, and
  `check_socket` render on CadQuery; every mode and every extreme parameter
  combination exports as one closed **watertight** manifold solid, with **STEP**
  export (alongside STL / 3MF / OFF / GLB / GLTF / OBJ).
- **Legacy engine: OpenSCAD.** `transtibial_socket` and `transfemoral_socket` each
  carry an explicit per-mode `engine: openscad` and render `socket.scad` (the
  Voronoi-shell edition) through the OpenSCAD kernel.
- **Watertight by construction (CadQuery).** Organic revolved profiles crack at
  the axis, so the socket is **never revolved**. The outer body is a **loft through
  a stack of closed elliptical wires** (distal-small → proximal-large, with an
  optional brim flare); the distal end is closed by a solid adapter plate; the
  cavity is a **second inner loft cut** from the outer solid (a robust hollowing
  that does not rely on `.shell()`). Ventilation and bolt holes are through-cuts,
  grouped into a single `Compound` and cut once (fast and manifold).
- The CadQuery script is **self-contained** (sandbox-safe): parameters are read via
  a `PARAM(lambda: name, default)` guard because the render sandbox does not expose
  `globals()` / `eval`. The final solid is assigned to `result`.
