# Parametric Pipe Connector

A disaster-relief / scavenged-material **structural connector** for cylindrical
stock — PVC pipe, cut bamboo, wooden dowel — a **dual-kernel** hyperobject that
renders on **CadQuery (B-Rep)** by default and keeps its original **OpenSCAD**
mode. You **measure** the outer diameter of whatever material is locally
available, enter it, pick the connectivity, and print a node whose sockets seat
each pipe to a set depth.

*Un conector estructural para material cilíndrico recuperado — tubo de PVC, bambú
o espiga de madera — un hiperobjeto de **doble núcleo** que renderiza en
**CadQuery (B-Rep)** por defecto y conserva su modo **OpenSCAD** original. Mides el
diámetro exterior del material que tengas, lo introduces, eliges la topología e
imprimes un nodo cuyos enchufes asientan cada tubo a una profundidad definida.*

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

**Version**: 2.1.0 · **Slug**: `parametric-connector`

## Modes

The default kernel is **CadQuery (B-Rep)**; the legacy `Standard` mode carries an
explicit `engine: openscad` and renders on OpenSCAD.

| Mode id | Label (en) | Engine | File |
| :--- | :--- | :--- | :--- |
| `elbow` | Elbow (2-way) | CadQuery B-Rep | `main.py` |
| `tee` | Tee (3-way flat) | CadQuery B-Rep | `main.py` |
| `corner_3way` | Corner (3-way 3D) | CadQuery B-Rep | `main.py` |
| `Standard` | Pipe Connector (OpenSCAD) | OpenSCAD | `connector.scad` |

**CadQuery modes** — `elbow`, `tee`, `corner_3way` (each is one solid; the
platform dispatches on `target_part` == the mode's part id):

- **Elbow (2-way)** (`elbow`) — two arms meeting at `elbow_angle` (90° default).
  Open the angle up for the shallow struts of a geodesic dome or a splayed leg.
- **Tee (3-way flat)** (`tee`) — two collinear arms plus one perpendicular
  branch — the classic in-line fitting.
- **Corner (3-way 3D)** (`corner_3way`) — one arm on each of +X, +Y, +Z — the
  orthogonal vertex of a cube / box frame or shelving.

**OpenSCAD mode** — `Standard`: the original single `connector_body` from
`connector.scad`, whose `connector_type` selector spans a wider legacy topology
set (elbow, tee, cross, 3-way / 4-way corner, 5-way, 6-way hub).

## Parameters

### CadQuery parameters (main modes)

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Measured Material | `pipe_od` | 21.3 mm | **Measured** OD of your local PVC / bamboo / dowel. |
| Socket & Fit | `wall` | 3.0 mm | Socket wall thickness around the pipe. |
| Socket & Fit | `insertion_depth` | 20 mm | How deep each pipe seats into its socket. |
| Socket & Fit | `clearance` | 0.5 mm | Slip-fit gap over the measured OD (raise for rough bamboo). |
| Topology | `elbow_angle` | 90° | Angle between the two arms (Elbow mode only). |
| Load & Fixing | `heavy_load` | off | Thicker walls + 3 internal gusset ribs per socket. |
| Load & Fixing | `pin_holes` | off | Cross through-hole per socket for a fixing pin/screw. |
| Load & Fixing | `pin_dia` | 4.0 mm | Pin / screw shank diameter. |

### OpenSCAD-extended parameters

The legacy `Standard` (OpenSCAD) mode adds its own parameters by group — a
**Pipe Size** group (`pipe_od_mm`), a **Topology** group (`connector_type` select
with elbow/tee/cross/3-way/4-way/5-way/6-way options), a **Structure** group
(`wall_thickness_mm`, `insertion_depth_mm`), and a **Quality** group (`fn`, $fn).
Only `Standard` exposes these legacy rows.

## Presets

- **1/2" PVC Elbow** — `pipe_od` 21.3, 90° right-angle elbow (`elbow`).
- **3/4" PVC Tee** — `pipe_od` 26.7 in-line branch (`tee`).
- **Bamboo Shelter Corner** — `pipe_od` 33.4, heavy-load 3D corner with pin holes
  and a wide clearance for irregular bamboo (`corner_3way`).
- **Geodesic Strut (60°)** — `pipe_od` 25, heavy-load elbow opened to 60° (`elbow`).
- Legacy OpenSCAD presets — **1/2" PVC Elbow**, **3/4" PVC Tee**, **Furniture
  3-Way Corner (1")** — target the `Standard` mode.

## Hyperobject Profile

- **Domain:** household
- **CDG interfaces:**
  - **Pipe/Tube Socket** (`socket`, internal) — the variable geometry of the
    joint. A cylindrical bore of `pipe_od + clearance`, seated `insertion_depth`
    deep in a `wall`-thick socket. Any material measured to the same OD, at the
    same depth, seats identically — the socket is the common denominator across
    PVC, bamboo, and dowel. Topology (elbow / tee / corner) sets how many sockets
    radiate from the hub and at what angles.
  - **Cross Fixing Pin** (`bolt_pattern`, internal) — an optional through-hole
    (`pin_dia`) near each socket mouth that captures the seated pipe with a pin or
    self-tapping screw (`pin_holes`).
- **Material awareness:** `clearance` is exposed so the slip fit can be tuned per
  material and printer — tight for smooth PVC, generous for irregular bamboo;
  `tolerance_by_material` is declared.
- **Societal benefit:** turns scavenged cylindrical stock into rigid structures —
  emergency shelters, geodesic domes, furniture — with no proprietary fittings or
  supply chain. Print the nodes; the community supplies the pipe.
- **License:** CERN-OHL-W-2.0

## Engines

- **Default engine: CadQuery (B-Rep).** `elbow`, `tee`, and `corner_3way` render
  on CadQuery; every shipped preset and mode renders **watertight** and exports
  **STEP** (alongside STL / 3MF / GLB / GLTF / OBJ).
- **Legacy engine: OpenSCAD.** The `Standard` mode carries an explicit per-mode
  `engine: openscad` and renders `connector.scad` through the OpenSCAD kernel,
  preserving the wider legacy topology set.
- The CadQuery script is **self-contained** (sandbox-safe): parameters are read via
  a `PARAM(lambda: name, default)` guard because the render sandbox does not expose
  `globals()` / `eval`. The final solid is assigned to `result`.
- The CadQuery hub is a **chamfered cube** rather than a sphere: a sphere's curved
  surface intersecting the orthogonal socket cylinders leaves razor-thin
  tessellation slivers at the exact-tangency seams (non-watertight STL), whereas
  planar hub faces union and cut cleanly.
