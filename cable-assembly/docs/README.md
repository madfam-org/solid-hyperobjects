# Cable assembly / Cable ensamblado

A routing and fit archetype, with standard mating-shell bounds and generic
housing, boot and ferrite shapes. No electrical internals are modeled.

## Frame and parts

| Input | Geometry |
|---|---|
| Standard-part +Z mating direction | Outward local endpoint tangent (A −X, B +X) |
| Shell width / height | Across local endpoint Y / Z after rotation |
| `length` | Straight jacket span between housing backs, mm |
| `path` | Straight, bowed spline, S spline or helical coil |

The `cable` mode fuses jacket, boots and endpoints into one body. `envelope`
is the axis-aligned bounding box of that complete routing volume, including the ferrite and housings.
`connector_a` and `connector_b` expose each endpoint separately for fixtures.
The shared functions `connector_plug`, `strain_relief`, `cable_jacket`,
`coil_cord` and `cable_ferrite` live in `commons-lib/hardware/cables.py`;
`main.py` is generated from `family.py` by `tools/inline_parts.py`.

## Presets and provenance

`tools/presets/cable_assembly.py` reads connector bounds from the keystone's
standard-parts catalog at `SPEC_PIN`. The exact 25.4 mm/in factor converts
D-sub and F-type inch dimensions. The housing dimensions and unreported
lengths are archetypes, exposed as advanced parameters. IEC cord ends use the
inlet's recess envelope, and claim no C7/C13 standard conformance. HDMI's
unreported shell depth is an archetype. The F-type envelope has no real thread.

The USB, coiled controller cord, AV and link presets are explicitly archetypes.
Named cable records use only sourced `features.cable_length_mm` and
`connector_a` / `connector_b`. A missing connector becomes an explicitly generic
proprietary end. The published cable length is mapped to straight jacket span;
unknown source endpoint conventions and all routing details are fallback rules,
so overall tip-to-tip length is not asserted as the product's length.

The coil uses half-integer turns, with centerline radius `(OD − jacket)/2`.
Its two actual endpoints retain their half-turn offset. Tangent spline leads are swept in one operation with the helix; they do not silently close onto a fictitious axis.
The animation varies coil pitch while maintaining separation between turns.

## Limits

There are no contact pins except the RCA central envelope, no conductive
materials, electrical ratings, strain simulation or counterfeit shell details.
Named connector identities remain unresolved where the catalog has no source.
The functional fit surface does not prove mating tolerances or electrical safety.
