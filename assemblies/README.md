# Type-level assemblies (ASM-1 §2, §7)

Each `assemblies/<slug>/assembly.json` composes commons cartridges, keystone standard
parts and external designs into one placed assembly. Its mates are checked by the
keystone (`y4d-spec assembly check`, documented in hyperobjects-spec's
[`docs/ASSEMBLIES.md`](https://github.com/madfam-org/hyperobjects-spec/blob/main/docs/ASSEMBLIES.md)). CI's `assemblies` job checks every document on every PR with
`--collision`, with cartridges taken from this checkout and standard parts from the
catalog bundled in the pinned keystone. An overlap that is part of the design is declared
in the document's `allowed_overlaps`; any other overlap fails.

| Slug | Kind | What it composes |
| :-- | :-- | :-- |
| [`voron-2-4-class-350-motion-frame`](./voron-2-4-class-350-motion-frame/) | producer | the full Voron 2.4-class 350 motion system, posable (ASM-1 §9): the blind-jointed 350 frame cube, four top corners with GT2 Z idlers, four MGN9 Z rails, four belt-reduction Z drives, the fixed bed and plate, the flying gantry on four Z joints, the MGN12 X rail, X carriage and toolhead proxy; joints `x_carriage`, `gantry_y`, `gantry_z` bound to Klipper's corexy axes; A/B, Z and reduction belts as paths. 235 components, 292 mates, 25 joints, 10 belt paths, 23 poses, collision-clean; its ten printed cartridges carry graph twins |
| [`fpv-5in-freestyle`](./fpv-5in-freestyle/) | product | a 5-inch X frame (catalog class), four 2207 motors on TPU soft-mount pods, the camera cage (TPU intended) on the side plates with a micro camera in its cradle, stack standoffs, a battery pad, the antenna chain (mount on the rear VTX pattern, SMA jack, antenna) |

Rules for a document here:

- Every mate states its rotation (`rotation_index`, or `angle_deg` for continuous
  symmetry).
- A third-party design appears only as an `external` component. It carries its name,
  licence, URL and the interface facts it needs. Its geometry is never copied.
- An assembly is merged only when its check passes with zero errors.

Each directory must contain an `assembly.json`. A directory without one fails CI.

## Where these documents are consumed

- **Kinematics.** The keystone's reference forward kinematics (`pose()`) and golden pose
  files (`hyperobjects.assembly-poses` 1.0.0) are described in
  [`docs/ASSEMBLIES.md`](https://github.com/madfam-org/hyperobjects-spec/blob/main/docs/ASSEMBLIES.md).
  A viewer poses A from machine-axis values through its `machine` bindings.
- **Shells.** A solid-commons release publishes each assembly as an assembly shell, which
  [asset-shells](https://github.com/madfam-org/asset-shells/blob/main/README.md) re-validates
  with its pinned keystone before storing it and adding its twin-graph edges.
- **Graph twins.** The printed cartridges' graph twins are edited in Yantra4D Studio as forks;
  see [the graph-cartridge guide](https://github.com/madfam-org/yantra4d/blob/main/docs/guides/graph-cartridges.md).
