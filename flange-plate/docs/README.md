# Bolt-Circle Flange Plate

A round flange with a centered bore and a polar bolt circle, defined as a node
graph ([`flange.graph.json`](../flange.graph.json)) and compiled server-side by
the graph engine.

## Variants

| Mode | Part | Use |
| :-- | :-- | :-- |
| Drilled Flange | `flange` | Full bolt circle — bolt straight to a motor face, pipe flange or bearing mount |
| Blank Plate | `blank` | Bore only; mark and drill the pattern by hand |

## What it demonstrates

This is the cartridge that exercises the graph vocabulary beyond primitives:

- `profile_circle` → `extrude` — the sketch-then-extrude workflow
- `pattern_polar` — one bolt-hole cutter repeated around the circle, then cut
  from the plate in a single boolean
- `chamfer` on `>Z` — breaks the top edges, including around every hole

## Parameters

All seven controls are manifest **bindings** into node params. `edge_chamfer`
drives both variants' chamfer nodes at once.

**On bolt count and spacing:** the polar spacing is *derived* from the count —
`boltring.angle` is `{"expr": "360 / bolt_count"}` — so the circle is always
even and there is nothing to keep in sync. Moving `bolt_count` moves the
spacing with it, because the expression is emitted as arithmetic over the same
render-time parameter probe a binding uses, not folded to a constant.

This cartridge used to carry an eighth control, `bolt_spacing_deg`, because the
graph format had no expressions and a derived value had to be its own slider.
That was a trap rather than a feature: leaving it at 60° while raising the
count to 8 rendered *the six-bolt part*, byte for byte, with no warning — the
two extra holes landed exactly on top of existing ones. Graph v1.1 added
`{"expr": …}` (yantra4d lane G-EXPR) and the slider is gone.

## Interfaces

Declares two CDG interfaces — `bolt_circle` (`bolt_pattern`) and `center_bore`
(`socket`) — so it joins the works-with graph alongside the other cartridges
that speak the same geometry.

## License

CERN-OHL-W-2.0 — see the manifest `attribution` block.
