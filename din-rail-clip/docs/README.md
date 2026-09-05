# Heavy Duty DIN Rail Clip

A snap-on clip for standard top-hat DIN rail (DIN EN 60715) — the spine of industrial control panels. Grips the two rolled rail lips with one fixed hook and one COMPLIANT spring hook, so a printed clip holds through geometry, not permanently strained plastic (avoiding the creep and fatigue that kill rigid printed snaps). Flat mount face with a device bolt pattern; Gridfinity-on-DIN and multi-device strip variants.

A **dual-engine** hyperobject: exact new **CadQuery** B-Rep modes alongside the original **OpenSCAD** modes. Un hiperobjeto de doble kernel: modos nuevos en CadQuery B-Rep junto a los modos originales de OpenSCAD.

Part of the **Yantra4D Hyperobjects Commons** · Official visualizer: [Yantra4D](https://app.yantra4d.com)

## Modes

| Mode | Label | Engine | File |
| :--- | :--- | :--- | :--- |
| `clip` | DIN Clip | CadQuery B-Rep | `main.py` |
| `gridfinity_clip` | Gridfinity DIN Clip | CadQuery B-Rep | `main.py` |
| `clip_wide` | Wide Multi-Device Strip | CadQuery B-Rep | `main.py` |
| `Standard` | Clip Body (OpenSCAD) | OpenSCAD | `din_clip.scad` |

The CadQuery modes render watertight and export STEP. The legacy OpenSCAD modes carry an explicit per-mode `engine: openscad` override (the platform resolves the render engine per mode).

## Parameters

The CadQuery modes expose the core parametric controls (see `project.json` → `parameters`). The OpenSCAD-extended modes add their own legacy parameters, grouped in the manifest and visible only in those modes.

## Hyperobject Profile

- **Domain:** industrial
- **CDG interfaces:**
- **DIN TS35 Rail Profile** (`rail`, DIN EN 60715 TS35)
- **Compliant Spring Hook** (`snap`, internal)
- **Device Bolt Pattern** (`bolt_pattern`, ISO 261 M3/M4/M5)
- **Gridfinity 42 mm Dock** (`socket`, Gridfinity (42 mm module))
- **Societal benefit:** Democratized industrial automation and repair: anyone can mount, adapt, or repair control-panel hardware on the universal DIN rail without proprietary carriers. The compliant spring hook makes a printed clip that survives creep, so repairs last — extending the life of breakers, relays, and controllers instead of scrapping enclosures.
- **License:** CERN-OHL-W-2.0

## Engines

Default engine is **CadQuery**; the original OpenSCAD modes are preserved with a per-mode `engine: openscad` override. All CadQuery modes are verified watertight through the render sandbox and render distinctly.
