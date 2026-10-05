# Type-level assemblies (ASM-1 §2, §7)

Each `assemblies/<slug>/assembly.json` composes commons cartridges, keystone standard
parts and external designs into one placed assembly. Its mates are checked by the
keystone (`y4d-spec assembly check`, documented in hyperobjects-spec's
`docs/ASSEMBLIES.md`). CI's `assemblies` job checks every document on every PR, with
cartridges taken from this checkout and standard parts from the catalog bundled in
the pinned keystone.

| Slug | Kind | What it composes |
| :-- | :-- | :-- |
| [`voron-2-4-class-350-motion-frame`](./voron-2-4-class-350-motion-frame/) | producer | the full Voron 2.4-class 350 motion system, posable (ASM-1 §9): the blind-jointed 350 frame cube, four top corners with GT2 Z idlers, four MGN9 Z rails, four belt-reduction Z drives, the fixed bed and plate, the flying gantry on four Z joints, the MGN12 X rail, X carriage and toolhead proxy; joints `x_carriage`, `gantry_y`, `gantry_z` bound to Klipper's corexy axes; A/B, Z and reduction belts as paths |
| [`fpv-5in-freestyle`](./fpv-5in-freestyle/) | product | a 5-inch X frame (catalog class), four 2207 motors on TPU soft-mount pods, the camera cage (TPU intended) on the side plates with a micro camera in its cradle, stack standoffs, a battery pad, the antenna chain (mount on the rear VTX pattern, SMA jack, antenna) |

Rules for a document here:

- Every mate states its rotation (`rotation_index`, or `angle_deg` for continuous
  symmetry).
- A third-party design appears only as an `external` component. It carries its name,
  licence, URL and the interface facts it needs. Its geometry is never copied.
- An assembly is merged only when its check passes with zero errors.

Each directory must contain an `assembly.json`. A directory without one fails CI.
