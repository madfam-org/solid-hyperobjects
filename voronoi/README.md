# Voronoi Generator

Voronoi pattern generator for coasters, vases, and lampshades (OpenSCAD + CadQuery).

Full parameter, preset, and assembly documentation: [docs/README.md](docs/README.md).

## License & attribution

This project is licensed under the CERN Open Hardware Licence Version 2 — Weakly
Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).

The OpenSCAD models depend on the following third-party library:

- **[dotSCAD](https://github.com/JustinSDK/dotSCAD)** by Justin Lin (@JustinSDK) —
  licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0).
  The Voronoi modules `voronoi/vrn2_space.scad` and `voronoi/vrn_sphere.scad`,
  plus `fibonacci_lattice.scad` and `polyline_join.scad`, referenced by the
  `.scad` sources are dotSCAD modules. dotSCAD is **not vendored** in this
  repository; it is resolved at render time from the OpenSCAD library path
  (`OPENSCADPATH`).

See [NOTICE](NOTICE) for the full third-party attribution list.
