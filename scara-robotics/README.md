# Chronos-SCARA (scara-robotics)

**Status: research-stage.** This is a parametric research project, not a
completed Yantra4D Commons pack. Expect gaps: it currently ships a single
geometry source per backend and a research essay, without the full mode /
preset / assembly coverage of finished Commons packs.

## What is here

- `robot.scad` — OpenSCAD (BOSL2) study of a strain-wave (harmonic) gear
  joint: wave generator, flexspline, and circular spline. Note the BOSL2
  include uses a platform-relative path (`../../libs/BOSL2/std.scad`) and
  is resolved by the Yantra4D build environment, not by this repo alone.
- `robot.py` — CadQuery equivalent of the same harmonic-drive geometry.
- `project.json` — Yantra4D manifest (Chronos-SCARA, CERN-OHL-W-2.0),
  including lineage attribution to PyBot, RepRap Morgan, and MySCARABot.
- `docs/research/` — design essay: *SCARA Robotics: 4D Hyperobject
  Synthesis*.

## What is not here (yet)

- The full SCARA arm (linkages, Z-axis, actuator mounts) — only the
  harmonic-drive joint is modeled.
- Render/validation CI, presets, assembly steps, or verification stages.

## License

CERN Open Hardware Licence Version 2 — Weakly Reciprocal (see `LICENSE`).
