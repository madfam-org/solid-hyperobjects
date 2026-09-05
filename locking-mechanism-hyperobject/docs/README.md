# Parametric Locking Mechanism

Open-source parametric locking mechanisms for 3D-printed enclosures, tools, and devices. Three distinct mechanism types cover common retention needs from delicate battery covers to heavy-duty toolbox latches.

## Modes

| Mode | Description |
|------|-------------|
| **Snap-Fit Latch** | Cantilever beam with hook — the most common 3D-printed latch type. A flexible arm deflects during insertion and snaps into a striker plate. |
| **Over-Center Lock** | Pivoting lever arm that locks past the center-point. Provides strong holding force and a positive tactile click. |
| **Compliant Bistable Lock** | A curved flexure beam that snaps between two stable positions (locked/unlocked). No pivots or loose parts — the entire mechanism is monolithic. |

## Hyperobject Profile

| Field | Value |
|-------|-------|
| **Domain** | Industrial |
| **License** | CERN-OHL-W-2.0 |
| **Material Awareness** | Shrinkage compensation, tolerance-by-material |

### CDG Interfaces

- **Latch Hook Profile** — Cross-section profile of the hook engagement geometry. Parameters: `latch_width`, `hook_depth`.
- **Striker Plate Bolt Pattern** — Mounting hole pattern for the receiving plate. Parameters: `base_length`, `latch_width`.
- **Actuation Lever Rail** — Linear rail defining lever travel. Parameters: `lever_length`.

## Print Tips

| Material | Use Case | Notes |
|----------|----------|-------|
| **PLA** | Prototyping, low-cycle latches | Stiff but brittle — good for fit checks, breaks after repeated flexing |
| **PETG** | General-purpose enclosure clips | Good balance of flexibility and strength, moderate fatigue life |
| **ABS** | Structural latches, toolbox clips | Higher temperature resistance, good fatigue life with acetone vapor smoothing |
| **Nylon (PA)** | High-cycle snap-fits | Best fatigue resistance — ideal for battery covers and latches that open/close frequently |

### General Guidelines

- Print snap-fit arms **flat on the build plate** with layers parallel to the beam axis for maximum flexural strength.
- Use **0.2mm layer height or finer** for the hook engagement surface.
- Set clearance parameter to **0.3mm** for well-calibrated printers, **0.5mm** for looser tolerances.
- The compliant bistable mode works best with **flexible materials** (PETG, Nylon) — PLA may crack at the arch apex.
