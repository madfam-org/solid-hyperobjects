# Chronos-SCARA (scara-robotics)

**Status: research-stage.** This is a parametric research project. All three
declared modes now render — every one of the ten declared parts builds its own
watertight solid on both backends, and the two kernels agree — but the pack
still ships no presets, no assembly steps and no verification stages, so it is
not yet a finished Yantra4D Commons pack.

## What is here

- `robot.scad` — OpenSCAD (BOSL2) source for all three modes. The
  `harmonic_drive` mode is a strain-wave gear study (wave generator,
  flexspline, circular spline); `kinematic_chain` is the SCARA linkage
  (shoulder link, elbow link, Z spindle, end-effector mount); `sensorium` is
  the reference-anchor set (two endstop brackets and a Z-probe mount). Each
  part has its own `render_mode` branch — see the dispatch table at the top of
  the file. The BOSL2 include is a library-path include
  (`include <BOSL2/std.scad>`), resolved through `OPENSCADPATH` — which the
  commons CI points at this repo's own `libs/` tree, and the platform worker
  points at its own.
- `robot.py` — CadQuery equivalent of the same ten parts, dispatched on the
  `target_part` the platform injects. The kinematic and sensorium parts are
  built primitive-for-primitive against the OpenSCAD side (faceted `.polygon()`
  discs rather than analytic circles), so the two kernels agree to within
  4e-6 % of volume and 0 mm of bounding box on all seven.
- `project.json` — Yantra4D manifest (Chronos-SCARA, CERN-OHL-W-2.0),
  including lineage attribution to PyBot, RepRap Morgan, and MySCARABot.
- `docs/research/` — design essay: *SCARA Robotics: 4D Hyperobject
  Synthesis*.

## What is not here (yet)

- Presets, assembly steps, or `verification` stages.
- The linkage and sensorium parts are dimensioned studies driven by the
  manifest parameters (`link1_length`, `link2_length`, `z_travel`,
  `rail_width`, `motor_frame_size`, `bore_diameter`), not
  production-engineered hardware: no fillets, no bearing seats, no fastener
  torque analysis.

## License

CERN Open Hardware Licence Version 2 — Weakly Reciprocal (see `LICENSE`).
