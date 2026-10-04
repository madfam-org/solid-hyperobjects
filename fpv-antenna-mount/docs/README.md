# FPV Antenna Mount

**Holds a VTX antenna clear of the propellers** and routes it up or back,
generated with **CadQuery** (B-Rep). Sized to the antenna connector standard —
the **SMA** bulkhead or the tiny **U.FL** coax — so the exit hole and coax route
match the hardware.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Tube Mount** | `tube_mount` | Foot + leaning stalk with a top socket that captures a rigid tube / pagoda antenna. |
| **SMA Bulkhead Bracket** | `sma_bracket` | Foot + stalk capped by a bulkhead face for a **rear-mounted** SMA pigtail jack: the jack comes up the stalk's clearance bore (open through the foot), its shoulder seats on the cap's underside and the nut clamps it on top. |
| **Frame Clip** | `clip` | A bolt-free C-clip that snaps onto a frame plate and carries a short routing stalk. |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Connector | `connector` | SMA | `SMA` (6.5 mm exit) or `U.FL` (2.6 mm exit). |
| Stalk | `stalk_h` / `stalk_d` | 35 / 8 mm | Stalk height (prop clearance) and diameter. |
| Stalk | `back_angle` | 25° | Rearward lean (tube / SMA modes). |
| Base | `base_w` / `base_l` | 18 / 18 mm | Foot footprint. |
| Base | `bolt_d` / `bolt_span` | 2.2 / 12 mm | Base bolt holes (M2). In the SMA bracket they run ACROSS the lean (along X) and the span and foot widen as needed so the stalk never covers them. |
| Connector | `jack_body_d` | 9.5 mm | SMA bracket: the clearance bore up the stalk and through the foot for the jack's rear body and hex (9.5 clears a hex up to 8.2 mm across flats; read yours from the jack's drawing). |
| Tube / Clip | `tube_d` / `tube_len` | 4 / 28 mm | Tube socket size and depth (tube mode). |
| Tube / Clip | `clip_gap` | 4 mm | Frame-plate thickness the clip grips (clip mode). |

## Interfaces

The **antenna exit** hole is sized from `connector`: an SMA bulkhead barrel needs
a ~6.5 mm through-hole, U.FL just routes a ~2 mm coax. The coax runs down the
axial bore of the stalk. The stalk is built upright with its top feature (tube
socket or bulkhead cap), then the whole assembly is leaned back by `back_angle`
so the exit stays coaxial with the leaned stalk.

**SMA bracket (rear-mounted jack, owner decision O2(a)).** The Ø6.5 exit hole
runs only through the 3 mm cap. Below it a `jack_body_d` clearance bore runs the
whole stalk and opens through the foot, so a pigtail jack is fed up from below
(before the mount is bolted down) until its shoulder bears on the cap's
underside; its thread passes the cap and the nut and antenna go on top. The
stalk keeps a 1.6 mm wall round that bore. The foot's two bolt holes sit across
the lean (along X). A `bolt_span` that can hold the stalk round the smallest
bore is **kept** and the jack bore is capped to fit inside it
(`bolt_span − bolt_d − 7.2` mm; Studio warns when the cap engages); a span too
small for even that widens to `2·(stalk_r + bolt_r + 2)` (the 12 mm default becomes
18.9 mm). The foot widens to carry the holes, so the leaned stalk and the cap never
cover a bolt head. The front-mounted option (jack from above, shoulder on the cap's top) is
**not offered**: no frame claims it, and its nut would have to be threaded
inside the stalk bore.

**Mating frame.** `sma_bracket_jack_seat`: the cap's underside on the stalk
axis, `(0, h·sin a, h·cos a)` with `h = stalk_h` and `a` the clamped lean
(`let`; degree trig), normal `(0, −sin a, −cos a)` (down the stalk, toward the
jack), female, symmetry 0. Size key from `connector`: `SMA` → `sma-bulkhead`
(mates the catalog's `sma-bulkhead-jack.panel`), `U.FL` → `u-fl-cable-exit`
(a cable route with no catalog partner). Chain for an assembly:
`mount.sma_bracket_jack_seat ↔ sma-bulkhead-jack.panel`, then
`jack.coupling ↔ vtx-antenna-sma.connector`.

**Foot frame.** `sma_bracket_foot` puts the SMA bracket on a frame's 20 × 20 mm VTX
seat (catalog `fpv-frame-5in-x-225.rear_vtx_mount`), its two bolts through one 20 mm
row: origin `(0, −bolt_span/2, −3)` — the pattern's centre, on the foot's underside,
on the side away from the lean — normal `−z`, male, symmetry 4. Size key
`{bolt_span: "20" → vtx-mount-20x20}`: only at exactly 20 mm, and the cap above keeps
the holes at ±10 mm for every jack bore, bolt and stalk size. On the catalog frame,
`rotation_index` 3 puts the foot on the pattern's rear row with the antenna leaning
back. Preset **SMA Stalk on a 20x20 VTX Seat** sets it up.

**Known, not changed (tube mount and clip).** In `tube_mount` the coax bore is
still blind at the foot and the leaned stalk passes over the +Y bolt hole; in
`clip` the bore stops at the clip's top wall. Both are separate fixes.

## Presets

- **SMA Stalk 25°** — the standard rear-leaning SMA bracket.
- **Pagoda Tube Mount** — captures a rigid pagoda/tube antenna.
- **U.FL Frame Clip** — bolt-free clip for a light micro build.
- **SMA Stalk Upright** — the SMA bracket with no lean.
- **SMA Stalk 45°** — the steepest lean, 30 mm stalk.
- **SMA Stalk on a 20x20 VTX Seat** — `bolt_span` 20, for a frame's rear VTX pattern.
- **SMA 20x20 Seat, Largest Jack and Bolts** — the cap at its limit (jack 14, M4-size holes, 12 mm stalk at 45°): the holes stay 20 mm apart.

## Hyperobject Profile

- **Domain:** commercial
- **CDG interfaces:**
  - **Antenna Exit** (`socket`, *SMA / U.FL*) — the connector through-hole and
    coax route, defined by `connector` and `tube_d`. Matches the two dominant
    FPV antenna connector standards.
  - **Frame Fixing** (`bolt_pattern`, *internal*) — the base bolt holes or the
    snap clip, defined by `bolt_span`, `bolt_d`, `clip_gap`.
- **Material awareness:** `tolerance_by_material` is declared — the exit-hole and
  socket sizes are exposed so push-fit tightness can be tuned per material.
- **Societal benefit:** a VTX antenna that dips into the prop wash tears itself
  apart and kills the video link; on-demand mounts sized to the exact connector
  lift and lean the antenna clear.
- **License:** CERN-OHL-W-2.0

## Engine notes

- Engine: **CadQuery** (`main.py`). Exports STL / 3MF / STEP / GLB / GLTF / OBJ.
- Self-contained (sandbox-safe): parameters read via `PARAM(lambda: name,
  default)`; `target_part` dispatches which part to build; the final solid is
  assigned to `result`. Fillets are clamped and guarded. All modes render
  **watertight** in well under 20 s.
