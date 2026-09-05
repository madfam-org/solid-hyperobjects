# Gridfinity Extended

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

Upstream attribution:

- **[gridfinity_extended_openscad](https://github.com/ostat/gridfinity_extended_openscad)**
  by ostat — included as the `gridfinity_extended` git submodule (via the
  [madfam-org fork](https://github.com/madfam-org/gridfinity_extended_openscad)).
  Licensed under the **GNU General Public License v3.0 (GPL-3.0)**. The
  submodule is fetched at build time; its source is not copied into this
  repository.
- **[Gridfinity](https://gridfinity.xyz/)** by Zack Freedman
  ([Voidstar Lab](https://www.voidstarlab.com/)) — the modular storage system
  standard this project implements, released as free and open source under the
  **MIT License**.
- **[gridfinity_openscad](https://github.com/vector76/gridfinity_openscad)**
  by vector76 (© 2022 Jamie) — **MIT License**; the OpenSCAD implementation
  that gridfinity_extended_openscad is based on.

See [NOTICE](NOTICE) for the full third-party attribution list.
