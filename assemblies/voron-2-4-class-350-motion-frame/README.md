# Voron 2.4-class motion-frame subset (`voron-2-4-class-350-motion-frame`)

Assembly A of the Digital Twins programme (ASM-1 §7): a **producer** (a fabrication
machine model), checked by the keystone's `y4d-spec assembly check`.
Document licence: CERN-OHL-W-2.0.

## What it proves

That commons cartridges, keystone standard parts and an external GPL design can be
composed into one placed, closed type-level assembly:

- **A frame corner that must close.** Three 2020 extrusions (`frame_x` is the root,
  `frame_y` butts against it, the upright `frame_z` stands on it) and three corner
  braces from two different cartridges: two `tslot-corner` `corner_2way` braces and one
  `tslot-2020` `corner_bracket`. The braces form the loop X → Y → Z → X, so one brace mate
  is not used for placement and must close on its own. It closes only because the slot
  stations (`slot_station_mm` 30 on `frame_x`, 10 on `frame_y` and `frame_z`) and both
  cartridges' leg frames agree to within 0.05 mm and 0.5°. The tslot-2020 bracket uses
  `bracket_leg` 15, which puts its leg station 10 mm from the corner, the same station as
  the corner_2way brace. With the Y–Z bracket turned the other way round
  (`rotation_index` 1), the loop misses by 20 mm and 180°.
- **The motion stack.** On `frame_x`'s outer face, the stack rests on an MGN12 rail
  (`mgn12-rail`, 250 mm) and an MGN12H block (`mgn12h-carriage`). The **Voron
  Stealthburner** (`toolhead`) is bolted to the block's four M3 holes.
- **The A motor.** A NEMA 17 (`nema-17-48mm`) sits on a `nema-bracket`
  `extrusion_mount`, with a GT2 20T pulley (`gt2-pulley-20t-5mm`) on its 5 mm shaft.
- **Endstop and chain.** An `endstop-mount` `extrusion_endstop` carries an Omron D2F
  switch (`microswitch-d2f`), with `hole_span` 6.5 mm, the D2F pattern. A `chain-mount`
  `extrusion_bracket` anchors the drag chain.

- **A 608 idler on an 8 mm axle.**
  - A `roller-bracket` `extrusion_bracket` (preset `idler_608_2020`: `shaft_dia` 8, axis
    35 mm above the face, web 8 × 20) stands on `frame_x`'s outer face at its a-end slot
    station (30 mm). It holds a catalog `shaft-8mm`.
  - A `bearing-608` rides on the axle's journal, and the `idler-608` `flat_idler` sits on
    the bearing's outer race.
  - Three mates: `extrusion_bracket_shaft_bore ↔ host_end`,
    `bearing_journal ↔ bore` and `outer_race ↔ flat_idler_bearing_seat`, all at
    `angle_deg` 0 (solid-hyperobjects#140, hyperobjects-spec#42).

Every mate states its rotation (`rotation_index`, or `angle_deg` for the continuous
shaft ↔ bore mate). The layout of the four b-end faces of `frame_x` was chosen so that
no two rendered parts intersect (see the evidence in the PR).

## What it does not claim

- **The Stealthburner is referenced, never copied.** It is an `external` component that
  names the [Voron-Stealthburner](https://github.com/VoronDesign/Voron-Stealthburner)
  repository, its licence (GPL-3.0) and the upstream commit the facts were taken from.
  Its only declared interface is the fact that it bolts to an MGN12H block (the
  catalog's `mgn12-carriage` pattern). In a real build that joint is made through the
  Voron 2.4 X-carriage frames (`x_frame_V2TR_MGN12_left/right` in
  [Voron-2](https://github.com/VoronDesign/Voron-2), GPL-3.0), which are not modelled
  either. No Voron geometry or CAD is in this repository.
- **It is not the Voron 2.4 frame drawing.** In a real 2.4 the X rail rides on the
  floating gantry's own X beam, and the motors sit in the A/B drive units. Here every
  motion part hangs from one frame extrusion, because the gantry's joints are Voron GPL
  parts that the commons does not carry. The positions are a static layout that proves
  the mates; they are not the printer's geometry.
- **Static.** No motion, belt path or tension is modelled. The motor's `rotation_index`
  fixes where its connector points; that is a choice, not a Voron fact.
- **No collision claim.** The keystone's `--collision` option is a stub in 0.4.0. It is
  not run and nothing here claims it.
- **The 608 idler is not a Voron part.** It is a commons idler, not taken from any Voron
  design, and no cited Voron 2.4 placement for it was found. Its position on `frame_x` is
  a layout choice, not a Voron fact. It was accepted as a layout convention on 2026-10-04.
  The Voron 2.4r2 assembly manual is being checked for a cited idler mount, which may move
  it in a later PR.
- **The idler's seat floor touches the 608's inner ring.** `idler-608`'s 3 mm seat floor
  is an annulus from r 4.2 to 11, so it contacts the face of the 608's stationary inner
  ring. Fixing it needs a cited inner-ring land diameter. It is accepted for now
  (P4-AUTH-D).

## Check it

```bash
pip install "hyperobjects-spec @ git+https://github.com/madfam-org/hyperobjects-spec@<SPEC_PIN>"
parts=$(python -c 'import hyperobjects_standard_parts as h, pathlib; print(pathlib.Path(h.__file__).parent / "parts")')
y4d-spec assembly check assemblies/voron-2-4-class-350-motion-frame/assembly.json \
    --commons . --standard-parts "$parts"
```

`SPEC_PIN` is in [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml). CI runs this
check on every PR (the `assemblies` job).

---

## Español

Ensamble A del programa de gemelos digitales (ASM-1 §7). Es un **productor**, es decir,
el modelo de una máquina de fabricación. Lo verifica `y4d-spec assembly check` del
keystone. Licencia del documento: CERN-OHL-W-2.0.

**Qué demuestra**

- **Una esquina del marco que tiene que cerrar.** Son tres perfiles 2020 con tres
  escuadras de dos cartuchos distintos (`tslot-corner` y `tslot-2020`). Forman un lazo
  X → Y → Z → X: una de las uniones no se usa para colocar piezas y tiene que cerrar por
  sí sola, con un margen de 0.05 mm y 0.5°. Con la escuadra Y–Z girada al revés, el lazo
  falla por 20 mm y 180°.
- **El movimiento.** Riel MGN12 y carro MGN12H sobre la cara exterior de `frame_x`, con
  el **Voron Stealthburner** atornillado al carro.
- **El motor A.** Un NEMA 17 sobre un `nema-bracket` `extrusion_mount`, con una polea
  GT2 20T en su flecha de 5 mm.
- **Final de carrera y cadena.** Un soporte de final de carrera con un microinterruptor
  Omron D2F, y un anclaje de cadena portacables.

Cada unión declara su rotación.

**Qué no afirma**

- **El Stealthburner se referencia, nunca se copia.** Es un componente `external` con su
  URL, su licencia (GPL-3.0) y el commit de origen. Solo declara que se atornilla a un
  carro MGN12H. En una impresora real lo hace a través de los marcos de carro X del
  Voron 2.4, que tampoco se modelan. Este repositorio no contiene geometría Voron.
- **No es el plano del marco del Voron 2.4.** Las posiciones son un arreglo estático
  que demuestra las uniones.
- **Es estático.** No modela movimiento, bandas ni tensión.
- **No hay verificación de colisiones.** `--collision` es un esbozo en la versión 0.4.0
  y no se ejecuta.
- **La polea loca 608 no es una pieza Voron.** Va sobre un eje de 8 mm en un soporte para
  perfil 2020, sobre la cara exterior de `frame_x`. Esa posición es una decisión de
  arreglo, no una colocación Voron citada; se aceptó como convención de arreglo el
  2026-10-04. Se revisa el manual de ensamble Voron 2.4r2 en busca de una colocación
  citada, que podría moverla en un PR posterior. El fondo del asiento de la polea toca el
  anillo interior del 608; se acepta por ahora.
