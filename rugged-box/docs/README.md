# Rugged Box

A sealed hinged carry case: a deep base, a shallower lid, a continuous gasket
ring between them, print-in-place knuckle hinges along the back, over-centre
latch straps along the front, and optional stacking feet. CadQuery (B-Rep)
hyperobject cartridge.

The case is sized by the **payload envelope** — the interior dimensions you set
are exactly the cavity you get, and the shell grows around it.

## Modes (parts)

| Mode | Parts | Description |
|------|-------|-------------|
| `complete` | bottom, top, latches, gasket | Every printable part, laid apart on one plate. A compound — the parts do not touch. |
| `bottom` | bottom | The base alone. |
| `top` | top | The lid alone, already flipped to print crown-down. |
| `latches` | latches | The latch straps, one separate body each. |
| `gasket` | gasket | The seal ring. Print in TPU. |
| `feet` | feet | Four stacking pads. |
| `closed-view` | bottom, top, latches | Assembled preview. Not a print target. |

Expected body counts, from the contract:

| Mode / part | Bodies |
|-------------|--------|
| `bottom`, `top`, `gasket` | 1 |
| `latches` | `numberOfLatches` |
| `feet` | 4 |
| `complete` | 3 + `numberOfLatches` (+ 4 when feet are on) |
| `closed-view` | 2 + `numberOfLatches` (+ 4 when feet are on) |

## The interfaces

These are the dimensions another part mates to. They are held constant so a lid,
a gasket or a replacement latch printed from this cartridge interchanges with one
printed from any other implementation of the same interface.

- **Seal.** The gasket ring's outer face sits **1.75 mm inside the shell face on
  every side** (3.5 mm on the diameter). Ring cross-section width = `rimWidthMm`
  (2.0 mm default); ring height and groove depth = `gasketSlotDepth`, default
  2.2 mm over a **1–5 mm** range. The ring, the groove in the base and the rim on
  the lid are three views of one interface and always agree.
- **Lid engagement.** The lid rim enters the base **`rimHeightMm` deep** (3.0 mm
  default) with **0.5 mm assembly clearance**.
- **Hinge.** Base knuckle radius `hingeRadiusMm` (4.0 mm default) against a lid
  knuckle **0.5 mm smaller** — the running clearance that lets a print-in-place
  hinge turn. The lid knuckle is **1 mm narrower** axially (0.5 mm per side).
- **Latch.** Catch **`latchSupportTotalWidth` wide** (25 mm default), **5 mm
  engagement**, **4 mm strap thickness**.
- **Feet.** 3 mm pad height, registering the base floor to the lid crown of the
  case stacked below.

## Key parameters

Every one of the 32 declared parameters reaches the geometry.

- **`internalBoxWidthXMm`, `internalboxLengthYMm`** — the payload footprint. The
  shell, the seal ring, the hinge placement and the latch placement all follow.
- **`internalBoxTopHeightZMm`, `internalboxBottomHeightZMm`** — payload depth in
  the lid and the base independently, so a shallow lid over a deep base works.
- **`boxWallWidthMm`, `boxChamferRadiusMm`** — wall/floor thickness and outer
  corner rounding (clamped to half the short side).
- **`boxSealType`** — 1 is the plain rim; 2 adds a drain relief outside the
  groove and a matching bead on the lid rim.
- **`gasketSlotWidth`, `gasketSlotDepth`, `rimWidthMm`, `rimHeightMm`** — the
  seal, as above.
- **`numSideSupportRibs`, `supportRibThickness`, `supportRibWidth`** — stiffener
  ribs on the long walls, inside and out. 0 removes them.
- **`countainerWidthXSections`, `boxLengthYSections`** and the two `...ToSkip`
  counts — the interior compartment grid. Skipping leading dividers merges the
  first cells into one larger compartment.
- **`numberOfHinges`, `hingeTotalWidthMm`, `hingeRadiusMm`, `hingeCenterOffsetMm`**
  — hinge count, width, radius and spread.
- **`numberOfLatches`, `latchSupportTotalWidth`, `latchCenterOffsetMm`,
  `latchClipCutoutAngle`, `latchOpenerLengthMultiplier`** — latch count, catch
  width, spread, clip grip and thumb-tab length.
- **`isFeetAdded`, `feetwidthMm`, `feetLengthMm`, `boxGapMm`** — stacking feet
  and their pockets.
- **`BoxPolygonStyle`** — faceting of the cylindrical features (hinge knuckles,
  latch pivots, corner pilasters): 8 flats, 16 flats, or a true curve. The
  knuckle polygon is inscribed, so the hinge interface diameter is unchanged at
  every setting.

## Printing

Print the base, the lid, the latch straps and the gasket. The `top` mode already
lies crown-down, so the seam face is up and the rim needs no support. The hinge
knuckles print in place with 0.5 mm running clearance — free them with a gentle
first rotation. Print the gasket in TPU and press it into the base groove.

## Design notes

The seal, hinge fit, latch catch and payload envelope are a published interface.
The shell silhouette — the belt rib running the seam line right around both
halves, the corner pilasters, the waisted latch strap with its thumb ramp, the
stadium-shaped foot pads — is MADFAM's own form. See `NOTICE` and
`docs/CLEANROOM-VERIFICATION.md`.

## Licence

CERN-OHL-W-2.0. Original MADFAM work, authored clean-room; nothing is vendored.
See `LICENSE` and `NOTICE`.

---

# Caja Resistente (español)

Un estuche sellado con bisagras: una base profunda, una tapa más baja, un anillo
de junta continuo entre ambas, bisagras de nudillo impresas en sitio en la parte
trasera, pestillos de sobrecentro al frente y pies apilables opcionales.
Cartucho hiperobjeto en CadQuery (B-Rep).

El estuche se dimensiona por el **volumen útil**: las medidas interiores que
indiques son exactamente la cavidad que obtienes, y la carcasa crece alrededor.

## Modos (piezas)

| Modo | Piezas | Descripción |
|------|--------|-------------|
| `complete` | bottom, top, latches, gasket | Todas las piezas imprimibles, separadas en una placa. Es un compuesto: las piezas no se tocan. |
| `bottom` | bottom | Solo la base. |
| `top` | top | Solo la tapa, ya volteada para imprimir con la corona abajo. |
| `latches` | latches | Los pestillos, cada uno como cuerpo separado. |
| `gasket` | gasket | El anillo de junta. Imprimir en TPU. |
| `feet` | feet | Cuatro pies apilables. |
| `closed-view` | bottom, top, latches | Vista ensamblada. No es para imprimir. |

## Las interfaces

Son las medidas a las que se acopla otra pieza. Se mantienen constantes para que
una tapa, una junta o un pestillo impreso desde este cartucho sea intercambiable
con uno impreso desde cualquier otra implementación de la misma interfaz.

- **Sello.** La cara exterior del anillo queda **1.75 mm dentro de la cara de la
  carcasa en cada lado** (3.5 mm en el diámetro). Ancho de sección del anillo =
  `rimWidthMm` (2.0 mm por defecto); altura del anillo y profundidad de la ranura
  = `gasketSlotDepth`, 2.2 mm por defecto en un rango de **1 a 5 mm**. El anillo,
  la ranura de la base y el borde de la tapa son tres vistas de una sola interfaz
  y siempre concuerdan.
- **Encaje de la tapa.** El borde de la tapa entra **`rimHeightMm`** (3.0 mm por
  defecto) con **0.5 mm de holgura de ensamble**.
- **Bisagra.** Radio del nudillo de la base `hingeRadiusMm` (4.0 mm por defecto)
  contra un nudillo de tapa **0.5 mm menor** — la holgura de giro que permite una
  bisagra impresa en sitio. El nudillo de la tapa es **1 mm más angosto** (0.5 mm
  por lado).
- **Pestillo.** Enganche de **`latchSupportTotalWidth`** (25 mm por defecto),
  **5 mm de agarre**, **4 mm de grosor de correa**.
- **Pies.** 3 mm de altura, para registrar el piso de la base con la corona de la
  tapa del estuche de abajo.

## Parámetros

Los 32 parámetros declarados llegan a la geometría. Ver la tabla en inglés
arriba; los identificadores son los mismos.

## Impresión

Imprime la base, la tapa, los pestillos y la junta. El modo `top` ya viene
acostado con la corona abajo, así que la cara del sello queda arriba y el borde
no necesita soportes. Las bisagras se imprimen en sitio con 0.5 mm de holgura:
liéralas con un primer giro suave. Imprime la junta en TPU y presiónala en la
ranura de la base.

## Licencia

CERN-OHL-W-2.0. Obra original de MADFAM, autoría de sala limpia; no se incluye
material de terceros. Ver `LICENSE` y `NOTICE`.
