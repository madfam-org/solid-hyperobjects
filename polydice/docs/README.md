# Polyhedral Dice Set — `polydice`

A parametric set of the five Platonic dice: **d4** (tetrahedron), **d6** (cube),
**d8** (octahedron), **d12** (dodecahedron) and **d20** (icosahedron). Each mode
produces one die — an exact regular polyhedron with its numerals debossed into
the centre of every face.

CadQuery (B-Rep). Licensed CERN-OHL-W-2.0. Clean-room re-creation under ADR-021;
see [`../NOTICE`](../NOTICE) and
[`CLEANROOM-VERIFICATION.md`](./CLEANROOM-VERIFICATION.md).

## Why these solids

A die is fair when every face is equivalent to every other face under a symmetry
of the solid. The five convex regular polyhedra are the only solids with that
property for 4, 6, 8, 12 and 20 faces, which is why the tabletop set is the set
it is. Fairness here is a property of the construction, not of a quality check:
the vertices come from exact coordinates and the faces are generated from them,
so all edges of a given die are equal and all faces are the same distance from
the centre by arithmetic, not by tolerance.

## Sizing

`die_size` means different things for the d4 and for the rest, and the reason is
geometric rather than arbitrary:

| Mode | `die_size` measures | At the default 20 mm |
| :-- | :-- | :-- |
| `d6`, `d8`, `d12`, `d20` | **face-to-face** (twice the inradius) — the standard way a die is quoted | a d20 20 mm across the flats |
| `d4` | **apex-to-base height** | a tetrahedron 20 mm tall |

A tetrahedron's inradius is one quarter of its height, not one half. Quoting a
d4 face-to-face would make a "20 mm d4" a 40 mm-tall object twice the size of
the d20 beside it in the same set. Height is the measure that puts the d4 in
scale with the rest, and it is the measure the recorded baseline used.

Derived dimensions at the nominal sizes:

| Mode | Size | Edge | Circumradius | Solid volume (before engraving) |
| :-- | --: | --: | --: | --: |
| `d4` | 20.000 (height) | 24.495 | 15.000 | 1732.05 mm³ |
| `d6` | 15.000 (f2f) | 15.000 | 12.990 | 3375.00 mm³ |
| `d8` | 15.000 (f2f) | 18.371 | 12.990 | 2922.84 mm³ |
| `d12` | 18.000 (f2f) | 8.083 | 11.326 | 4046.16 mm³ |
| `d20` | 20.000 (f2f) | 13.232 | 12.584 | 5054.06 mm³ |

## Numbering

The d6, d8, d12 and d20 are numbered so that **opposite faces sum to
`faces + 1`** — 7, 9, 13 and 21. That is the convention a player can verify by
hand, and the cartridge's test suite asserts it for every die.

The d4 has no opposite face, so the sum rule cannot apply. It uses the
**vertex-number convention**: each face carries the numbers of the three
vertices it touches, and the roll is read at the corner pointing up.

On dice with more than six faces the numerals **6** and **9** carry an
underline, because they are otherwise indistinguishable when the die lands the
other way up.

## Parameters

| id | range | default | effect |
| :-- | :-- | --: | :-- |
| `die_size` | 10–40 mm, step 1 | 20 | overall size (see Sizing); all linear dimensions scale with it, volume with its cube |
| `font_depth` | 0.2–1.5 mm, step 0.1 | 0.6 | how deep the numerals are cut, measured normal to the face |
| `font_size` | 3–12 mm, step 0.5 | 6 | numeral height, clamped to what fits on the face |
| `rounding_corner` | 0–5 mm, step 0.5 | 0 | vertex rounding radius in millimetres; 0 is sharp |
| `rounding_edge` | 0–3 mm, step 0.5 | 0 | edge fillet radius in millimetres; 0 is sharp |
| `fn` | 0–64, step 8 | 0 | widens the mouth of each engraved numeral by a shallow second pass; 0 leaves them plain-cut |
| `dice_gradient` | 0–1, step 1 | 0 | 1 cuts a shallow equatorial groove for a clean filament change on a two-tone print |

Three notes on the parameter space, all deliberate:

- **`rounding_corner` is millimetres**, matching `rounding_edge`. The manifest
  exposes a 0–5 range that reads as millimetres, so millimetres is what it
  means. Rounding is applied to the bare polyhedron *before* the numerals are
  cut; filleting after a text cut is the standard way to lose watertightness.
- **`dice_gradient` has geometry.** The parameter was declared but had nothing
  behind it. Rather than drop a declared parameter, it now cuts an equatorial
  groove — a real feature for the two-tone print its tooltip describes, and a
  visible change in the mesh.
- **`fn` is not a facet count here.** It is an OpenSCAD-flavoured knob carried
  over from a mesh kernel; a B-Rep kernel has no facet count, and the platform
  calls its exporter with the default tessellation, so a cartridge cannot route
  `fn` to the mesher. Rather than leave a declared parameter inert — exactly the
  defect that removed this slug's predecessor — it is given the meaning it can
  honestly carry: it widens the mouth of each engraved numeral by a shallow
  second pass, so the glyph holds paint and reads at a glance. The effect is
  small, geometric and real; 0 leaves the numerals plain-cut.

`font_size` is clamped to the largest circle that fits on the face. A 12 mm
numeral on a 10 mm d20 would otherwise cut the die apart; the clamp means every
combination in the parameter space produces a printable die.

## Printing

Sharp corners print cleanly at 0.2 mm layers face-down; the d4 and d8 rest on a
face and need no support. A little `rounding_edge` (0.5–1 mm) makes a die roll
better and reads as a "cushioned" die. The 0.6 mm default engraving depth takes
paint or ink well; at 0.2 mm the numerals are visible but hold little pigment.

---

# Conjunto de dados poliédricos — `polydice`

Un conjunto paramétrico de los cinco dados platónicos: **d4** (tetraedro),
**d6** (cubo), **d8** (octaedro), **d12** (dodecaedro) y **d20** (icosaedro).
Cada modo produce un dado — un poliedro regular exacto con sus numerales
grabados en hueco en el centro de cada cara.

CadQuery (B-Rep). Licencia CERN-OHL-W-2.0. Recreación en sala limpia bajo
ADR-021; véase [`../NOTICE`](../NOTICE) y
[`CLEANROOM-VERIFICATION.md`](./CLEANROOM-VERIFICATION.md).

## Por qué estos sólidos

Un dado es justo cuando cada cara es equivalente a las demás bajo una simetría
del sólido. Los cinco poliedros regulares convexos son los únicos que tienen esa
propiedad para 4, 6, 8, 12 y 20 caras, y por eso el conjunto de mesa es el que
es. Aquí la equidad es una propiedad de la construcción, no de un control de
calidad: los vértices provienen de coordenadas exactas y las caras se generan a
partir de ellos, de modo que todas las aristas de un dado son iguales y todas
las caras equidistan del centro por aritmética, no por tolerancia.

## Dimensionado

`die_size` significa cosas distintas para el d4 y para el resto, por una razón
geométrica y no arbitraria:

| Modo | `die_size` mide | Con el valor por defecto de 20 mm |
| :-- | :-- | :-- |
| `d6`, `d8`, `d12`, `d20` | **cara a cara** (el doble del inradio) — la forma estándar de medir un dado | un d20 de 20 mm entre caras |
| `d4` | **altura del ápice a la base** | un tetraedro de 20 mm de alto |

El inradio de un tetraedro es un cuarto de su altura, no la mitad. Medir el d4
cara a cara convertiría un «d4 de 20 mm» en un objeto de 40 mm de alto, el doble
que el d20 que lo acompaña en el mismo juego. La altura es la medida que pone al
d4 a escala con el resto, y es la que usaba la línea base registrada.

Dimensiones derivadas en los tamaños nominales:

| Modo | Tamaño | Arista | Circunradio | Volumen del sólido (antes del grabado) |
| :-- | --: | --: | --: | --: |
| `d4` | 20.000 (altura) | 24.495 | 15.000 | 1732.05 mm³ |
| `d6` | 15.000 (c-a-c) | 15.000 | 12.990 | 3375.00 mm³ |
| `d8` | 15.000 (c-a-c) | 18.371 | 12.990 | 2922.84 mm³ |
| `d12` | 18.000 (c-a-c) | 8.083 | 11.326 | 4046.16 mm³ |
| `d20` | 20.000 (c-a-c) | 13.232 | 12.584 | 5054.06 mm³ |

## Numeración

El d6, el d8, el d12 y el d20 se numeran de modo que **las caras opuestas suman
`caras + 1`** — 7, 9, 13 y 21. Es la convención que un jugador puede verificar a
mano, y la batería de pruebas del cartucho la comprueba en cada dado.

El d4 no tiene cara opuesta, así que la regla de la suma no aplica. Usa la
**convención de numeración por vértice**: cada cara lleva los números de los tres
vértices que toca, y la tirada se lee en la esquina que queda hacia arriba.

En los dados de más de seis caras, los numerales **6** y **9** llevan subrayado,
porque de otro modo no se distinguen cuando el dado cae al revés.

## Parámetros

| id | rango | por defecto | efecto |
| :-- | :-- | --: | :-- |
| `die_size` | 10–40 mm, paso 1 | 20 | tamaño general (véase Dimensionado); todas las dimensiones lineales escalan con él, el volumen con su cubo |
| `font_depth` | 0.2–1.5 mm, paso 0.1 | 0.6 | profundidad de grabado de los numerales, medida normal a la cara |
| `font_size` | 3–12 mm, paso 0.5 | 6 | altura del numeral, limitada a lo que cabe en la cara |
| `rounding_corner` | 0–5 mm, paso 0.5 | 0 | radio de redondeo en los vértices, en mm; 0 es vivo |
| `rounding_edge` | 0–3 mm, paso 0.5 | 0 | radio de redondeo en las aristas, en mm; 0 es vivo |
| `fn` | 0–64, paso 8 | 0 | ensancha la boca de cada numeral grabado con una segunda pasada superficial; 0 los deja de corte recto |
| `dice_gradient` | 0–1, paso 1 | 0 | 1 graba una ranura ecuatorial para un cambio limpio de filamento en una impresión bicolor |

Tres notas sobre el espacio de parámetros, todas deliberadas:

- **`rounding_corner` está en milímetros**, igual que `rounding_edge`. El
  manifiesto expone un rango 0–5 que se lee como milímetros, así que milímetros
  significa. El redondeo se aplica al poliedro desnudo *antes* de grabar los
  numerales; redondear después de un corte de texto es la forma habitual de
  perder la estanqueidad.
- **`dice_gradient` tiene geometría.** El parámetro estaba declarado pero no
  tenía nada detrás. En lugar de eliminar un parámetro declarado, ahora graba
  una ranura ecuatorial — una función real para la impresión bicolor que
  describe su tooltip, y un cambio visible en la malla.
- **`fn` no es aquí un recuento de facetas.** Es una perilla de sabor OpenSCAD
  heredada de un núcleo de mallas; un núcleo B-Rep no tiene recuento de facetas
  y la plataforma llama a su exportador con el teselado por defecto, así que un
  cartucho no puede encaminar `fn` al mallador. En lugar de dejar inerte un
  parámetro declarado — justo el defecto que retiró al predecesor de este slug —
  se le da el significado que sí puede sostener honestamente: ensancha la boca
  de cada numeral grabado con una segunda pasada superficial, de modo que el
  glifo retiene pintura y se lee de un vistazo. El efecto es pequeño,
  geométrico y real; 0 los deja de corte recto.

`font_size` se limita al mayor círculo que cabe en la cara. Un numeral de 12 mm
en un d20 de 10 mm partiría el dado; el límite garantiza que toda combinación
del espacio de parámetros produzca un dado imprimible.

## Impresión

Las esquinas vivas imprimen bien a capas de 0.2 mm con una cara abajo; el d4 y
el d8 se apoyan en una cara y no necesitan soportes. Un poco de `rounding_edge`
(0.5–1 mm) hace que el dado ruede mejor y se lee como un dado «amortiguado». La
profundidad de grabado por defecto de 0.6 mm admite bien pintura o tinta; a
0.2 mm los numerales se ven pero retienen poco pigmento.
