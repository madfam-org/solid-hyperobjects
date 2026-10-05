# solid-hyperobjects: status as of 2026-10-05

A dated snapshot for someone resuming from a fresh clone. **The
[open-PR list](https://github.com/madfam-org/solid-hyperobjects/pulls) is
authoritative**; when this file and GitHub disagree, GitHub wins. Operator
runbooks are kept privately. This repository deploys nothing itself: yantra4d
mounts it as its `projects/` submodule and picks up `main` through a commons
pin bump on its side.

## Where it stands

- `main` is `7de3a32e`; `SPEC_PIN` is the keystone at `142db18`.
- **Assembly A**, the Voron 2.4-class 350 motion system, is a posable kinematic
  twin: 235 components, 292/292 mates, 25 joints, 10 belt paths, 23/23 poses,
  collision-clean. Its ten printed cartridges carry graph twins (graph format
  1.1). See [Assemblies and graph twins](../README.md#assemblies-and-graph-twins).
- **Assembly B** is a 5-inch FPV freestyle frame.

## Landed recently

| PR | What it did |
|---|---|
| [#145](https://github.com/madfam-org/solid-hyperobjects/pull/145), [#147](https://github.com/madfam-org/solid-hyperobjects/pull/147) | `corner-idler-bracket`; A gains a blind-jointed top corner with the GT2 Z idler |
| [#150](https://github.com/madfam-org/solid-hyperobjects/pull/150)–[#155](https://github.com/madfam-org/solid-hyperobjects/pull/155), [#163](https://github.com/madfam-org/solid-hyperobjects/pull/163) | Original motion-system parts: XY joint (v2), Z drive housing, Z belt clamp, bed extrusion mount, A/B front idler and drive, X carriage |
| [#164](https://github.com/madfam-org/solid-hyperobjects/pull/164) | A becomes the full 2.4-class 350 motion system, posable under ASM-1 §9 |
| [#165](https://github.com/madfam-org/solid-hyperobjects/pull/165)–[#174](https://github.com/madfam-org/solid-hyperobjects/pull/174) | Graph twins of the ten printed cartridges in A, each held to its script by `--parity` |

## Open PRs, in merge order

None of them deploys.

| PR | Purpose | Precondition |
|---|---|---|
| [#175](https://github.com/madfam-org/solid-hyperobjects/pull/175) | Docs: assemblies, graph twins and related contracts in the entry docs, and this status file | CI green; any order |
| [#82](https://github.com/madfam-org/solid-hyperobjects/pull/82) | `flange-plate`: bolt spacing derived from the count | Older draft; not part of this queue |

## Next steps

1. **`SPEC_PIN` bump** after hyperobjects-spec#57 and #58 land, together with the
   other consumers (one keystone SHA everywhere). Sweep every cartridge and
   every assembly against the new SHA first.
2. **Commons hygiene** (queued): align the licence statements with what every
   cartridge declares (CERN-OHL-W-2.0) wherever one still differs, and fix the
   default drift in `gears`, `rubiks` and `microscope-slide-holder` in one PR.
3. **Kinematics for viewers** (decision pending): whether CI here publishes A's
   compiled kinematic model (`assembly.kinematics.json`, from hyperobjects-spec#57)
   for the platform to serve.
4. **yantra4d's commons bump** brings `7de3a32e` (A and its twins) into the
   platform; it follows yantra4d's render queue.

Known limits that each need their own PR are listed in
[`assemblies/README.md`](../assemblies/README.md) and the cartridge READMEs.

## Cross-repo contracts

The README's [Related repositories and contracts](../README.md#related-repositories-and-contracts)
table links the specific document on the other side of each contract: ASM-1 and
kinematics in hyperobjects-spec `docs/ASSEMBLIES.md`, graph format 1.x, the
Studio graph editor and render storage in yantra4d, the shell store in
asset-shells, and machine telemetry in pravara-mes.
