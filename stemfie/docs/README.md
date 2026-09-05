# STEMFIE-Compatible Construction Set

A **beam**, a right-angle **brace** and a **fastener** for an open construction
kit, generated with **CadQuery** (B-Rep). Everything is dimensioned on one grid
module, so any beam bolts to any other beam, at any hole, on any of the three
axes — and to parts printed elsewhere that follow the same standard.

**Compatible with the STEMFIE 10 mm block standard.** This cartridge is MADFAM's
own authoring: it implements that standard's *interface* — the functional
dimensions another part mates to — and gives everything non-functional a form of
our own. See [`../NOTICE`](../NOTICE) and
[`CLEANROOM-VERIFICATION.md`](CLEANROOM-VERIFICATION.md).

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Beam** | `beam` | A block-unit bar, holed on any combination of the three axes. |
| **Brace** | `brace` | A right-angle L plate that ties two beams at 90°. |
| **Fastener** | `fastener` | A pin (with collar) or a plain shaft that passes through the holes. |

## The interface

These are the numbers other parts depend on. They are not adjustable, and they
are what "compatible" means here.

| Quantity | Value |
| :--- | :--- |
| Block unit (BU, grid pitch) | 10.0 mm |
| Through-hole diameter | 4.2 mm |
| Hole pitch | 1 BU, at the centre of every cell |
| Beam cross-section | 10 × 10 mm per width / height unit |
| Brace plate thickness | 2.5 mm (BU / 4) per thickness unit |
| Brace arm angle | 90° |
| Fastener shank | 4.0 mm |
| Fastener collar | 5.7 mm |
| Shank-to-hole clearance | 0.2 mm diametral — a sliding fit, printable without reaming |

## Parameters

| Group | Parameter | Modes | Default | Range | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Dimensions | `length_units` | beam, fastener | 4 | 1–20 | Length in BU. Beam X extent / fastener Z extent = value × 10 mm. |
| Dimensions | `width_units` | beam | 1 | 1–4 | Beam Y extent in BU. |
| Dimensions | `height_units` | beam | 1 | 1–4 | Beam Z extent in BU. |
| Dimensions | `arm_a_units` | brace | 3 | 1–10 | Arm along X, in BU. |
| Dimensions | `arm_b_units` | brace | 3 | 1–10 | Arm along Y, in BU. |
| Dimensions | `thickness_units` | brace | 1 | 1–2 | Plate thickness, × 2.5 mm. |
| Features | `holes_x` / `holes_y` / `holes_z` | beam | on | — | The through-hole array on each axis, independently. |
| Features | `holes_enabled` | brace | on | — | The hole array along both arms. |
| Features | `fastener_type_id` | fastener | 0 | 0–1 | 0 = pin (collar), 1 = plain shaft. |
| Quality | `fn` | all | 0 | 0–64 | Tessellation hint. The geometry is B-Rep and exact; this affects mesh export only. |

Every parameter is scoped with `visible_in_modes`, so a mode only offers the
controls it consumes. `docs/test_parameters_change_geometry.py` asserts that
every visible parameter moves the geometry — and that `fn`, correctly, does not.

## Presets

- **5-Unit Beam** — `length_units = 5`. Offered in the Beam and Fastener modes,
  the two that consume the parameter.
- **90-Degree Brace** — the default 3 × 3 L; the UI's reset for the Brace mode.
- **Standard Pin** — a 2 BU pin.

## Hyperobject profile

- **Domain:** household
- **CDG interfaces:** `stemfie_beam_profile`, `stemfie_through_hole`,
  `stemfie_fastener_interface`
- **Commons licence:** CERN-OHL-W-2.0
- **Societal benefit:** an open construction kit for STEM education — a school
  can fabricate its own learning tools, and a part printed in one classroom fits
  a part printed in another.

## Printing notes

The 0.2 mm diametral clearance is a *design* clearance, not a print allowance.
On a printer that runs tight, holes come out undersize and the pin binds; print
one beam and one pin first and check the fit before running a class set. The
fastener's 0.8 mm lead-in taper is there to get a slightly-tight pin started.

---

# Conjunto de construcción compatible con STEMFIE

Una **viga**, una **escuadra** a 90° y un **sujetador** para un kit de
construcción abierto, generados con **CadQuery** (B-Rep). Todo está dimensionado
sobre un mismo módulo de rejilla, de modo que cualquier viga se atornilla a
cualquier otra, en cualquier agujero y en cualquiera de los tres ejes — incluso
con piezas impresas en otro lugar que sigan el mismo estándar.

**Compatible con el estándar de bloque de 10 mm STEMFIE.** Este cartucho es
autoría propia de MADFAM: implementa la *interfaz* de ese estándar — las
dimensiones funcionales con las que otra pieza acopla — y da forma propia a todo
lo no funcional. Ver [`../NOTICE`](../NOTICE) y
[`CLEANROOM-VERIFICATION.md`](CLEANROOM-VERIFICATION.md).

Parte del **Commons de Hiperobjetos Yantra4D**. Visualizador y configurador
oficial: [Yantra4D](https://app.yantra4d.com).

## Modos

| Modo | Pieza | Descripción |
| :--- | :--- | :--- |
| **Viga** | `beam` | Barra en unidades de bloque, perforada en cualquier combinación de los tres ejes. |
| **Escuadra** | `brace` | Placa en L a 90° que une dos vigas. |
| **Sujetador** | `fastener` | Pin (con collarín) o eje liso que pasa por los agujeros. |

## La interfaz

Estos son los números de los que dependen las demás piezas. No son ajustables, y
son lo que aquí significa «compatible».

| Cantidad | Valor |
| :--- | :--- |
| Unidad de bloque (BU, paso de rejilla) | 10.0 mm |
| Diámetro del agujero pasante | 4.2 mm |
| Paso entre agujeros | 1 BU, al centro de cada celda |
| Sección de la viga | 10 × 10 mm por unidad de ancho / alto |
| Grosor de la placa de la escuadra | 2.5 mm (BU / 4) por unidad de grosor |
| Ángulo de la escuadra | 90° |
| Vástago del sujetador | 4.0 mm |
| Collarín del sujetador | 5.7 mm |
| Holgura vástago-agujero | 0.2 mm diametral — ajuste deslizante, imprimible sin escariar |

## Parámetros

| Grupo | Parámetro | Modos | Predeterminado | Rango | Notas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Dimensiones | `length_units` | viga, sujetador | 4 | 1–20 | Largo en BU. Extensión X de la viga / Z del sujetador = valor × 10 mm. |
| Dimensiones | `width_units` | viga | 1 | 1–4 | Extensión Y de la viga en BU. |
| Dimensiones | `height_units` | viga | 1 | 1–4 | Extensión Z de la viga en BU. |
| Dimensiones | `arm_a_units` | escuadra | 3 | 1–10 | Brazo sobre X, en BU. |
| Dimensiones | `arm_b_units` | escuadra | 3 | 1–10 | Brazo sobre Y, en BU. |
| Dimensiones | `thickness_units` | escuadra | 1 | 1–2 | Grosor de placa, × 2.5 mm. |
| Características | `holes_x` / `holes_y` / `holes_z` | viga | activado | — | El arreglo de agujeros en cada eje, de forma independiente. |
| Características | `holes_enabled` | escuadra | activado | — | El arreglo de agujeros a lo largo de ambos brazos. |
| Características | `fastener_type_id` | sujetador | 0 | 0–1 | 0 = pin (con collarín), 1 = eje liso. |
| Calidad | `fn` | todos | 0 | 0–64 | Sugerencia de teselado. La geometría es B-Rep y exacta; esto solo afecta la exportación de malla. |

Cada parámetro está acotado con `visible_in_modes`, de modo que un modo solo
ofrece los controles que consume. `docs/test_parameters_change_geometry.py`
verifica que cada parámetro visible mueva la geometría — y que `fn`,
correctamente, no lo haga.

## Preajustes

- **Viga de 5 unidades** — `length_units = 5`. Se ofrece en los modos Viga y
  Sujetador, los dos que consumen el parámetro.
- **Escuadra a 90 grados** — la L 3 × 3 predeterminada; el botón de reinicio del
  modo Escuadra.
- **Pin estándar** — un pin de 2 BU.

## Perfil de hiperobjeto

- **Dominio:** hogar
- **Interfaces CDG:** `stemfie_beam_profile`, `stemfie_through_hole`,
  `stemfie_fastener_interface`
- **Licencia del commons:** CERN-OHL-W-2.0
- **Beneficio social:** un kit de construcción abierto para educación STEM — una
  escuela puede fabricar sus propias herramientas de aprendizaje, y una pieza
  impresa en un aula encaja con una impresa en otra.

## Notas de impresión

La holgura de 0.2 mm es una holgura de *diseño*, no una tolerancia de impresión.
En una impresora que imprime apretado, los agujeros salen por debajo de medida y
el pin agarra; imprima una viga y un pin primero y verifique el ajuste antes de
correr un juego para toda la clase. El chaflán de entrada de 0.8 mm del sujetador
existe para poder empezar a meter un pin un poco apretado.
