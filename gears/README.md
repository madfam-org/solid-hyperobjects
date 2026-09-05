# Parametric Gears

Involute spur and herringbone gears (OpenSCAD + CadQuery).

Full parameter, preset, and assembly documentation: [docs/README.md](docs/README.md).

## License & attribution

This project is licensed under the CERN Open Hardware Licence Version 2 — Weakly
Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).

This cartridge is MADFAM's own authoring. The involute gear
parameterization (module, teeth, pressure angle) follows the **ISO 53 /
DIN 867** standard tooth profile, which is a published standard, not a
third-party implementation.

Third-party libraries:

- **[BOSL2](https://github.com/BelfrySCAD/BOSL2)** by Revar Desmera and
  contributors — licensed under the BSD 2-Clause License. The `.scad` sources
  are thin wrappers calling BOSL2's `gears.scad` (`spur_gear()`). BOSL2 is
  **not vendored** in this repository; it is resolved at render time from
  BOSL2 on the build environment's library path.

See [NOTICE](NOTICE) for the full third-party attribution list.
