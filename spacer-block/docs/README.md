# Parametric Spacer Block

A machinist-style spacer/riser block, and the **first graph-engine cartridge**
in the Hyperobjects Commons: its geometry is not a script but a node graph
([`spacer.graph.json`](../spacer.graph.json)), compiled server-side into a
sandboxed CadQuery program by yantra4d's graph engine.

## Variants

| Mode | Part | Use |
| :-- | :-- | :-- |
| Bored Spacer | `spacer` | Slides over a bolt or rod (default bore clears M8) |
| Solid Block | `spacer_solid` | Plain riser / setup block |

Both variants come from the same graph: the solid chain chamfers the base box
directly, the bored chain cuts a centered cylinder first.

## Verification

Both variants are designed as one connected block. The
[manifest](../project.json) declares one body so disconnected geometry fails the
shared [cartridge gate](../../CONTRIBUTING.md#the-bar-your-pr-has-to-clear).
The gate renders both default modes; this cartridge currently has no presets.
This declaration does not certify every parameter combination or printability.

## Parameters

Every control is a manifest **binding** into the graph:

- `width` / `depth` / `height` → the `base` box dimensions
- `bore_radius` → the `bore` cylinder radius (4.25 mm clears M8, 3.25 mm clears M6)
- `chamfer_size` → binds **both** chamfer nodes at once (one parameter, two node params)

## Graph format

The document follows `packages/schemas/graph.schema.json` (version 1.x):
typed nodes (`box`, `cylinder`, `cut`, `chamfer`, …), inputs referencing node
ids, and an `outputs` map from part ids to nodes. The transpiler emits only
validated literals — a graph cartridge is a *safer* authoring surface than a
raw script.

## License

CERN-OHL-W-2.0 — see the manifest `attribution` block.
