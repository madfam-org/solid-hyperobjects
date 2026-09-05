# Fastener Generator

Parametric ISO metric hardware — bolts, nuts and washers sized to mate real M-series fasteners. Major diameter equals the nominal (M5 = 5 mm), pitch is the real coarse-series value, and head/nut across-flats follow the ISO wrench envelope. Threads default to a fast cosmetic profile with an opt-in real helical thread.

A **dual-engine** hyperobject: exact new **CadQuery** B-Rep modes alongside the original **OpenSCAD** modes. Un hiperobjeto de doble kernel: modos nuevos en CadQuery B-Rep junto a los modos originales de OpenSCAD.

Part of the **Yantra4D Hyperobjects Commons** · Official visualizer: [Yantra4D](https://app.yantra4d.com)

## Modes

| Mode | Label | Engine | File |
| :--- | :--- | :--- | :--- |
| `bolt_cq` | Bolt | CadQuery B-Rep | `main.py` |
| `nut_cq` | Nut | CadQuery B-Rep | `main.py` |
| `washer` | Washer | CadQuery B-Rep | `main.py` |
| `bolt` | Bolt (OpenSCAD) | OpenSCAD | `bolt.scad` |
| `nut` | Nut (OpenSCAD) | OpenSCAD | `nut.scad` |

The CadQuery modes render watertight and export STEP. The legacy OpenSCAD modes carry an explicit per-mode `engine: openscad` override (the platform resolves the render engine per mode).

## Parameters

The CadQuery modes expose the core parametric controls (see `project.json` → `parameters`). The OpenSCAD-extended modes add their own legacy parameters, grouped in the manifest and visible only in those modes.

## Hyperobject Profile

- **Domain:** industrial
- **CDG interfaces:**
- **ISO Metric Thread** (`thread`, ISO 261 / ISO 965)
- **Bolt Head Wrench Interface** (`profile`, ISO 4014 / ISO 4762 / ISO 7380)
- **Nut Wrench Interface** (`profile`, ISO 4032 / ISO 4033)
- **Societal benefit:** On-demand fabrication of standard ISO metric fasteners — enables prototyping and repair without hardware-store dependency, and lets a bolt, nut and washer be printed to mate real hardware.
- **License:** CERN-OHL-W-2.0

## Engines

Default engine is **CadQuery**; the original OpenSCAD modes are preserved with a per-mode `engine: openscad` override. All CadQuery modes are verified watertight through the render sandbox and render distinctly.
