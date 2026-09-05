# Faircap Water Filter

Open-source parametric water filter housing that screws onto standard PET
bottles (PCO-1881 neck thread), implemented in OpenSCAD (BOSL2) and CadQuery.

Full parameter, preset, and assembly documentation: [docs/README.md](docs/README.md).

## License & attribution

This project is licensed under the CERN Open Hardware Licence Version 2 — Weakly
Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).

Upstream attribution:

- **[Faircap](https://faircap.org/)** — this model is a parametric
  re-implementation inspired by the Faircap open-source water filter project,
  founded by Mauricio Córdova (Faircap CIC), which pioneered the concept of an
  affordable, open-source, 3D-printable filter cap that screws onto standard
  PET bottle necks. The geometry here (PCO-1881 thread interface, filter
  housing) was written independently for this project, but the product concept
  and reference dimensions follow Faircap's published open design. See
  https://faircap.org/ for the upstream project and its licensing terms.
- **[BOSL2](https://github.com/BelfrySCAD/BOSL2)** by Revar Desmera and
  contributors — licensed under the BSD 2-Clause License. Used for solids and
  the PCO-1881 threading (`std.scad`, `threading.scad`). BOSL2 is **not
  vendored** in this repository; it is resolved at render time from
  `../../libs/BOSL2` on the build environment's library path.

See [NOTICE](NOTICE) for the full third-party attribution list.
