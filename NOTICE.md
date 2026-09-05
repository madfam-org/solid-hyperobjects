# NOTICE — licence carve-outs

Cartridges in this repository are licensed **CERN-OHL-W-2.0** (ADR-011,
RFC 0038 §9), and each carries its own `LICENSE`. The exceptions below are the
cases where a cartridge's own licence is **not** the whole story, because files
or dependencies from an upstream project travel under their own terms.

Each cartridge listed here also carries a `<slug>/NOTICE` with the full
attribution; this file is the index, not a replacement for it.

## Vendored NonCommercial upstream

### `rugged-box`

> Carries vendored upstream files under a NonCommercial license, so commercial
> use is constrained by those files' terms despite the cartridge's own license —
> see the cartridge's `NOTICE` and the `license_exposure` field in the JSON
> catalog.

Specifically: `RuggedBoxV1.scad` and the `RuggedBoxV1.txt` parameter sets
(including the "Golden Benchy Case" preset) are the vendored upstream source of
*Super Customizable Rugged Box in OpenSCAD* by **Iceman**
(https://www.printables.com/model/1073708-super-customizable-rugged-box-in-openscad),
licensed **CC BY-NC-SA 4.0**, and remain under those terms. Selling prints made
from those vendored files is forbidden by the upstream licence.

The modular `rugged_*.scad` wrappers are derived from that design;
`rugged_core.scad` is an independent native BOSL2 rewrite.

This is the only cartridge in the commons with a known NonCommercial exposure.
It is tracked in the platform's `KNOWN_NC_EXPOSURE` map
(`scripts/qa/check_licenses.py`) and surfaced per-cartridge in the catalog as
`license_exposure`.

## Copyleft dependency, not vendored

### `gridfinity` → `gridfinity_extended`

`gridfinity_extended_openscad` (author **ostat**, upstream
https://github.com/ostat/gridfinity_extended_openscad, consumed via the fork
https://github.com/madfam-org/gridfinity_extended_openscad) is licensed
**GPL-3.0**. It is **not** copied into this repository: it is a git submodule at
`gridfinity/gridfinity_extended`, fetched at build time, and its contents remain
under GPL-3.0. See `gridfinity/NOTICE`.

## Third-party libraries, not vendored

The `libs/*` submodules are third-party OpenSCAD libraries resolved at render
time. No source from them is distributed here; each keeps its own licence:

| Submodule | Upstream | Licence |
| :-- | :-- | :-- |
| `libs/BOSL2` | BelfrySCAD/BOSL2 | BSD-2-Clause |
| `libs/NopSCADlib` | nophead/NopSCADlib | GPL-3.0 |
| `libs/Round-Anything` | Irev-Dev/Round-Anything | MIT |
| `libs/threads-scad` | rcolyer/threads-scad | CC0-1.0 |
| `libs/MCAD` | openscad/MCAD | LGPL-2.1 |
| `libs/dotSCAD` | JustinSDK/dotSCAD | LGPL-3.0 |

Licence identifiers above are the upstreams' own; each submodule ships its
licence text in its own tree once initialised.

## Standards implemented (not licence carve-outs)

Several cartridges implement openly published standards whose reference
implementations are permissively licensed and credited in the cartridge's
`NOTICE` — Gridfinity (Zack Freedman / Voidstar Lab, MIT),
`gridfinity_openscad` (vector76, MIT), and others. Implementing a standard is
not a licence exposure; those attributions live with their cartridges.
