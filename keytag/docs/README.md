# Keychain / Tag

Last Updated: 2026-09-29

A flat keychain tag with an embossed or debossed name/number and a ring hole,
generated with **CadQuery** (B-Rep). The personalization gateway: pick a shape,
type a label, print.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Tag** | `tag` | A flat tag + one text line. |
| **Two-Line Tag** | `tag_2line` | The same tag with a second text line. |
| **Luggage Tag** | `luggage_tag` | A larger tag with a strap slot and room for a longer label. |

Shapes: **rounded rectangle**, **circle**, **dog tag**, **bone**.

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Shape & Size | `shape` | rounded_rect | Tag outline. |
| Shape & Size | `size` | 45 mm | Nominal length. |
| Shape & Size | `thick` | 3.0 mm | Plate thickness. |
| Text | `text` | KEY-01 | Primary line. |
| Text | `text2` | (empty) | Second line (two-line / luggage). |
| Text | `text_mode` | deboss | Debossed or embossed. |
| Text | `text_depth` | 0.8 mm | Deboss depth / emboss height. |
| Ring Hole | `hole_dia` | 5.0 mm | Ring hole (or strap-slot width on luggage). |
| Ring Hole | `hole_pos` | 6.0 mm | Inset from the leading edge. |

## Text robustness

Text uses **Liberation Sans**, supplied by the shared render environment's
`fonts-liberation` package. Install that family before rendering locally. The
[cartridge source](../main.py) selects it explicitly: CadQuery's default Arial
request can fall back to different installed families on different hosts, changing
glyph outlines and even mesh validity. A local Linux reproduction with Liberation
Mono left four boundary edges in the luggage preset; the six shipped default and
preset renders pass with Liberation Sans under the same verifier.

The boolean result is validated with `.val().isValid()` inside the sandbox.
If a requested text operation produces an invalid solid, the script tries the
other mode (emboss/deboss), then a blank plate. This fallback does not establish
mesh validity: the [commons render gate](../../CONTRIBUTING.md) separately checks
B-Rep validity, watertightness, positive volume and the declared body count.
Arbitrary user-entered text and every parameter combination are not exhaustively
verified. Inspect the result before printing, especially when fallback changes
or omits a label.

## Presets

- **Numbered Key Tag** — a debossed rounded-rect key tag.
- **Pet Bone Tag** — an embossed bone tag.
- **Address Luggage Tag** — a two-line luggage tag with a strap slot.

## Hyperobject Profile

- **Domain:** household
- **CDG interface:** **Tag Outline + Text** (`profile`, internal) — defined by
  `shape`, `size`, `text`, `text_mode`.
- **Material awareness:** `tolerance_by_material` — text legibility and depth depend
  on filament/printer; tune `text_depth`.
- **Societal benefit:** the gateway print for personalization — a named, numbered,
  or labelled tag anyone can make in seconds.
- **License:** CERN-OHL-W-2.0

## Engine notes

- Engine: **CadQuery** (`main.py`). Exports STL / 3MF / STEP / GLB / GLTF / OBJ.
- Self-contained (sandbox-safe): parameters read via a `PARAM(lambda: name,
  default)` guard; final solid assigned to `result`.
- The [manifest](../project.json) defines the three modes and three presets checked
  by the render gate; a local pass still requires the authoritative Linux CI verdict.
