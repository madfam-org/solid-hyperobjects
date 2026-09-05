# Maze Generator

Parametric maze generator for coasters, cubes, and cylinders (OpenSCAD + CadQuery).

Full parameter, preset, and assembly documentation: [docs/README.md](docs/README.md).

## License & attribution

This project is licensed under the CERN Open Hardware Licence Version 2 — Weakly
Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).

This cartridge has **no third-party dependencies**. The maze itself comes from
`maze_kernel.scad` and its verbatim Python twin inlined in the three `.py`
sources — a shared deterministic kernel (a 32-bit LCG plus an iterative
recursive backtracker) that is MADFAM's own authoring. Both engines walk cells
and neighbours in the same order and draw the PRNG at the same points, so the
CadQuery and OpenSCAD sides render the **same maze for the same `seed`**.

Earlier revisions of the `.scad` sources called dotSCAD's `mz_square`,
`mz_squarewalls` and `line2d`. Those calls are gone: dotSCAD's generator uses
its own RNG, which the CadQuery side could not reproduce, so the two engines
produced different mazes from the same parameters. Replacing it with the shared
kernel is what makes the cartridge dual-engine deterministic.

See [NOTICE](NOTICE) for the attribution statement.
