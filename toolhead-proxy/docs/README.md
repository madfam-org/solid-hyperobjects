# Toolhead Proxy

> **A proxy, not a toolhead.** This is a deliberately simple stand-in body for a 3-D
> printer's toolhead, made for a machine's **digital twin**. It has no extruder, hotend, fans
> or ducts. Its sizes are **labelled conventions**, chosen to bound a typical toolhead
> generously. They are not measurements of any real toolhead.

It is generated with **CadQuery** (B-Rep) and gives the twin three things:
- **a body to show:** a block and a round nozzle;
- **a body the collision check can test:** `y4d-spec assembly check --collision`;
- **the nozzle tip's frame** (`nozzle_tip`), which the twin poses from the machine's reported
  position and which a camera view can project.

It bolts to an X carriage's toolhead face with four M3 screws on a 20 mm square (interface
key `toolhead-mount-20x20-m3`), as the commons `x-carriage` presents it.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and configurator:
[Yantra4D](https://app.yantra4d.com).

> **Why a proxy.** A Voron 2.4-class printer uses the StealthBurner toolhead. Its files are
> GPL-3.0 and kept apart from the printer's own guide. The *Voron 2.4r2 build guide*,
> version 2023-07-04 (VoronDesign/Voron-2 @ `a192410`, GPL-3.0), points to them on
> pp. 146–147 and is cited here by page only.
>
> The programme's owner decision **D3** (2026-10-04) calls for original proxy bodies in the
> twin instead of upstream files. Accordingly:
> - no StealthBurner or Voron geometry, STL, CAD or manual was read, copied, traced or
>   derived;
> - nothing here claims to match a StealthBurner's size or nozzle position.
>
> It is licensed CERN-OHL-W-2.0.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Toolhead Proxy** | `toolhead_proxy` | The single body: a block in front of the carriage face and a nozzle under it. |

## Parameters

Every parameter is a **convention**: a declared, adjustable size, not a sourced fact.

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Body | `body_w` | 56 mm | Across the X axis. It counts in the X travel budget: the body's half-width is `body_w` / 2. |
| Body | `body_d` | 56 mm | Forward from the carriage's toolhead face. |
| Body | `body_top` | 25 mm | From the mount pattern's centre up to the top. The minimum is 12, to cover the pattern. |
| Body | `body_drop` | 70 mm | From the mount pattern's centre down to the block's underside. |
| Nozzle | `nozzle_drop` | 78 mm | From the mount pattern's centre down to the nozzle tip. A machine twin that puts Z = 0 at the bed follows this number. |
| Nozzle | `nozzle_reach` | 28 mm | From the toolhead face forward to the nozzle axis. The default is mid-depth. |

### Sources and conventions

**Cited facts**
- **The mount pattern** (key `toolhead-mount-20x20-m3`): four M3 on a 20 mm square, the
  MGN12H block's own pattern (HIWIN MG series: MGN12H B 20, C 20, M3).

**Conventions (not sourced)**
- Every parameter above.
- The nozzle: a Ø8 round body, then a 3 mm cone to a Ø3 flat tip. The tip's area is 7.1 mm²,
  so the frame gate can find its face.
- The pattern is marked by four Ø3.4 blind holes, 8 deep, from the mount face. The proxy
  models no screws.
- Ø3.4 is the house M3 clearance (0.2 mm per side).

## Interfaces

Model frame:
- **Origin:** the centre of the mount pattern, on the face that bears on the carriage.
- **+x:** along the X axis the carriage runs on.
- **+y:** up.
- **+z:** forward, away from the carriage, through the block.

| Interface | Type | Polarity / key / symmetry | Where |
| :--- | :--- | :--- | :--- |
| `toolhead_proxy_mount` | `bolt_pattern` | male, `toolhead-mount-20x20-m3`, 4 | The back face, at the origin. The normal is −z, into the carriage. It mates the `x-carriage`'s `x_carriage_toolhead`. |
| `nozzle_tip` | `boss` (the tip's flat end) | no key, symmetry 0 | (0, −`nozzle_drop`, `nozzle_reach`): (0, −78, 28) at the defaults. The normal is the nozzle axis, pointing out of the tip toward the bed (−y). The x_axis is +x, along the machine's X axis. |

`nozzle_tip` mates nothing. It is the frame a twin poses and projects: the machine's
reported position (Klipper's toolhead `position`) is the position of this point.

**Gate results.** The render-time frame gate checks both interfaces at the defaults and at
each of the four presets: **10 of 10 pass**.

**The body's extents at the defaults,** in the model frame:

| Axis | Extent |
| :--- | :--- |
| x | −28 to 28 |
| y | −78 (the tip) to 25 |
| z | 0 to 56 |

The volume is about 298 cm³.

## Presets

| Preset | Values | Use |
| :--- | :--- | :--- |
| **Standard** | the defaults | — |
| **Compact** | a 46 × 46 body, `body_top` 20, `body_drop` 58, tip 66 below and 23 ahead | Where X travel is tight. |
| **Long Hotend** | tip 92 below | — |
| **Generous Envelope** | a 66 × 66 body, `body_top` 35, `body_drop` 80, tip 88 below and 33 ahead | A more conservative collision body. |

## Hyperobject Profile

- **Domain:** industrial.
- **Material awareness:** none. The proxy is for the twin, not for printing as a working part.
- **Societal benefit:** an open stand-in for a printer toolhead. A machine's twin can show and
  collision-check a toolhead and pose its nozzle tip without copying a GPL design. Every size
  is declared and adjustable, and both frames are machine-checked against the rendered body.
- **License:** CERN-OHL-W-2.0.

## Engine notes

- **Engine:** CadQuery (`main.py`), one body.
- **Sandbox-safe:** it reads `PARAM(lambda: name, default)`, dispatches on `target_part`, and
  assigns the solid to `result`.
- **Keystone needed:** a keystone with the key `toolhead-mount-20x20-m3` (hyperobjects-spec#53,
  lane P6-XCAR). Until `SPEC_PIN` moves past it, `y4d-spec check` reports that key as unknown.

## Resumen (es)

**Un sustituto, no un cabezal.** Es un cuerpo deliberadamente simple que representa el cabezal
de una impresora 3D en el gemelo digital de la máquina:
- **Uso:** dar algo que mostrar y que verificar en colisiones, y el marco `nozzle_tip` de la
  punta de la boquilla, que el gemelo posiciona y proyecta.
- **Montaje:** se atornilla a la cara de cabezal de un carro X con cuatro M3 en un cuadrado
  de 20 mm (clave `toolhead-mount-20x20-m3`).
- **Tamaños:** todos son convenciones declaradas y ajustables; no son medidas de ningún
  cabezal real.

Es un diseño original, conforme a la decisión D3 del programa. No se leyó ni se copió ninguna
geometría, archivo ni manual de StealthBurner o Voron. La guía de armado de la Voron 2.4r2
(GPL-3.0) se cita solo por página (pp. 146–147). Licencia CERN-OHL-W-2.0.
