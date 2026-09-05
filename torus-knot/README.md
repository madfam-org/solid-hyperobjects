# Torus Knot Sculpture

Generative torus knot sculptures (OpenSCAD + CadQuery). The (p, q) torus-knot
path is computed inline in `torus_knot.scad` from the standard parametric
equations and swept into a solid with BOSL2.

Full parameter, preset, and assembly documentation: [docs/README.md](docs/README.md).

## License & attribution

This project is licensed under the CERN Open Hardware Licence Version 2 — Weakly
Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).

Third-party libraries and lineage:

- **[BOSL2](https://github.com/BelfrySCAD/BOSL2)** by Revar Desmera and
  contributors — licensed under the BSD 2-Clause License. `torus_knot.scad`
  uses BOSL2 (`std.scad`, `skin.scad`) to sweep the knot path into a solid.
  BOSL2 is **not vendored** in this repository; it is resolved at render time
  from `../../libs/BOSL2` on the build environment's library path.
- **[dotSCAD](https://github.com/JustinSDK/dotSCAD)** by Justin Lin
  (@JustinSDK) — LGPL-3.0. Earlier versions of this project generated the
  torus-knot path with dotSCAD. That dependency was removed by inlining the
  standard parametric torus-knot curve directly in `torus_knot.scad`; no
  dotSCAD code is used or distributed by the current version. dotSCAD is
  credited here for the project's design lineage.

See [NOTICE](NOTICE) for the full third-party attribution list.
