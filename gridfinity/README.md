# Gridfinity

An advanced, fully parametric implementation of Zack Freedman's [Gridfinity](https://gridfinity.xyz/) storage system.

## Features

-   **Parametric Dimensions**: Customize width, depth, and height in standard 42mm units.
-   **Stackable**: Bases fit perfectly into other Gridfinity bins.
-   **Magnet Support**: Optional holes for 6x2mm magnets.
-   **Label Window**: Integrated lip for labeling your bins.
-   **Dividers**: Add internal walls to compartmentalize a single bin.

## Modes

1.  **Standard Bin**: The classic open utility bin.
2.  **Baseplate**: The mounting grid for your drawers or workbenches.
3.  **Lid**: A simple cover for standard bins.

## Parameters

| Name | Type | Description |
| :--- | :--- | :--- |
| `gridx` | Integer | Width in 42mm units (default: 1) |
| `gridy` | Integer | Depth in 42mm units (default: 1) |
| `gridz` | Integer | Height in 7mm units (default: 3) |
| `stackable` | Boolean | Add lip for stacking (default: true) |
| `magnet_holes` | Boolean | Add holes for 6x2mm magnets (default: false) |
| `div_x` | Integer | Internal dividers along X axis (default: 0) |
| `div_y` | Integer | Internal dividers along Y axis (default: 0) |

## Export

This project supports exporting compliant STL files ready for slicing.

## License & attribution

This repository is licensed under the CERN Open Hardware Licence Version 2 —
Weakly Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).


> **2026-09-04 (ADR-021, internal-devops):** the three OpenSCAD modes (`cup`,
> `baseplate_scad`, `lid`) that descended from GPL-3.0 code were removed from the
> commons together with that git submodule and the helper scripts and exports
> derived from them — and have since been **re-created clean-room** and returned,
> with their 27 parameters and 7 presets, from the published Gridfinity standard
> and a recorded measurement baseline, without access to the removed
> implementation or to any upstream one. See [NOTICE](NOTICE) for the provenance
> statement, [docs/CLEANROOM-VERIFICATION.md](docs/CLEANROOM-VERIFICATION.md) for
> the measurements, and [docs/README.md](docs/README.md) for the current
> parameter surface (the table above predates the manifest and is kept only for
> historical context). The CadQuery modes (`bin`, `baseplate`) implement the same
> published standard and are unchanged.

Upstream attribution:

- **[Gridfinity](https://gridfinity.xyz/)** by Zack Freedman
  ([Voidstar Lab](https://www.voidstarlab.com/)) — the modular storage system
  standard this project implements, released as free and open source under the
  **MIT License**.

See [NOTICE](NOTICE) for the full third-party attribution list.
