# Spiral Planter

Generative spiral planter with parametric drainage (OpenSCAD + CadQuery).

Full parameter, preset, and assembly documentation: [docs/README.md](docs/README.md).

## License & attribution

This project is licensed under the CERN Open Hardware Licence Version 2 — Weakly
Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).

The OpenSCAD model depends on the following third-party library:

- **[dotSCAD](https://github.com/JustinSDK/dotSCAD)** by Justin Lin (@JustinSDK) —
  licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0).
  `spiral_planter.scad` uses dotSCAD's `archimedean_spiral.scad` and
  `archimedean_spiral_extrude.scad` (via `use <dotSCAD/src/...>`) for the
  spiral wall path generation. dotSCAD is **not vendored** in this repository;
  it is resolved at render time from the OpenSCAD library path (`OPENSCADPATH`).

See [NOTICE](NOTICE) for the full third-party attribution list.
