# Type-level assemblies (ASM-1 §2, §7)

Each `assemblies/<slug>/assembly.json` composes commons cartridges, keystone standard
parts and external designs into one placed assembly. Its mates are checked by the
keystone (`y4d-spec assembly check`, documented in hyperobjects-spec's
`docs/ASSEMBLIES.md`). CI's `assemblies` job checks every document on every PR, with
cartridges taken from this checkout and standard parts from the catalog bundled in
the pinned keystone.

| Slug | Kind | What it composes |
| :-- | :-- | :-- |

Rules for a document here:

- Every mate states its rotation (`rotation_index`, or `angle_deg` for continuous
  symmetry).
- A third-party design appears only as an `external` component. It carries its name,
  licence, URL and the interface facts it needs. Its geometry is never copied.
- An assembly is merged only when its check passes with zero errors.

Each directory must contain an `assembly.json`. A directory without one fails CI.
