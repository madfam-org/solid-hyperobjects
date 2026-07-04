# Parametric Gears

Involute spur and herringbone gears (OpenSCAD + CadQuery).

Full parameter, preset, and assembly documentation: [docs/README.md](docs/README.md).

## License & attribution

This project is licensed under the CERN Open Hardware Licence Version 2 — Weakly
Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).

Third-party libraries and design lineage:

- **[MCAD](https://github.com/openscad/MCAD)** — the OpenSCAD MCAD library,
  licensed under the GNU Lesser General Public License v2.1 (LGPL-2.1).
  The original gear implementations in this project were built on MCAD's
  `involute_gears.scad`, and the involute gear parameterization (module,
  teeth, pressure angle) follows that lineage. The project description still
  refers to this MCAD heritage.
- **[BOSL2](https://github.com/BelfrySCAD/BOSL2)** by Revar Desmera and
  contributors — licensed under the BSD 2-Clause License. The current `.scad`
  sources are migrated to BOSL2's `gears.scad` (`spur_gear()`). BOSL2 is
  **not vendored** in this repository; it is resolved at render time from
  `../../libs/BOSL2` on the build environment's library path.

See [NOTICE](NOTICE) for the full third-party attribution list.
