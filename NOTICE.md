# NOTICE — licence carve-outs

Cartridges in this repository are licensed **CERN-OHL-W-2.0** (ADR-011,
RFC 0038 §9), and each carries its own `LICENSE`. The exceptions below are the
cases where a cartridge's own licence is **not** the whole story, because files
or dependencies from an upstream project travel under their own terms.

Each cartridge listed here also carries a `<slug>/NOTICE` with the full
attribution; this file is the index, not a replacement for it.

## Removed pending clean-room re-creation (operator ruling 2026-09-04, ADR-021)

The operator ruled that any hyperobject whose origin licence is not
CERN-OHL-W-2.0 leaves the commons and is re-created from scratch, clean-room,
to the same final result. Five cartridges were removed from this repository at
this commit (their history stays in git and in the archived satellite repos);
their slugs are **reserved** and return only as clean-room implementations
verified against the recorded final result:

| Slug | Origin licence | Origin |
| :-- | :-- | :-- |
| `keyv2` | GPL-3.0 | rsheldiii/KeyV2 |
| `stemfie` | GPL-3.0-or-later | stemfie.org (Paulo Kiefe) |
| `multiboard` | CC-BY-NC-SA-4.0 | Multiboard (Keep Making) |
| `polydice` | BSD-2-Clause | (unattributed upstream) |
| `rugged-box` | CC-BY-NC-SA-4.0 (vendored `RuggedBoxV1.scad` + parameter sets) | Super Customizable Rugged Box (Iceman) |

Until each returns, the catalog counts **495** cartridges, honestly.

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
