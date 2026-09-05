# Keycap (`keyv2`)

A parametric keycap for mechanical keyboard switches. CadQuery / B-Rep.
CERN-OHL-W-2.0. Author: Innovaciones MADFAM.

## What it makes

One mode (`keycap`) producing one part (`keycap`): a hollow tapered shell with a
dished top, a skirt sized to the keyboard key pitch, and a switch stem fused to
the underside of the keytop. The legend, when enabled, is debossed into the top
face.

## The interfaces it implements

These are the dimensions other things mate to. Get them wrong and the cap either
does not fit the switch or fouls its neighbour on the board.

| Interface | Dimension |
| :-- | :-- |
| Key pitch | 19.05 mm per unit |
| Inter-cap gap | 0.5 mm per side — a 1u cap measures 18.05 mm, a 2u cap 37.10 mm |
| Cherry MX stem | 5.5 mm outer diameter, cross socket 4.1 mm arm length × 1.17 mm arm width, each widened by half `stem_slop` |
| Alps stem | 4.5 × 3.2 mm post, 3.2 × 1.2 mm socket, narrowed by the full `stem_slop` |
| Box Cherry stem | 6.0 mm square post carrying the same cross socket |
| Socket depth | runs from the base to `cap_height − keytop_thickness − 0.5 mm` |

Note the deliberate asymmetry in `stem_slop`: Cherry and Box **widen** the cross
by half the allowance, Alps **narrows** its socket by the whole of it. That is
how the two families behave on a printer, and it is not a typo.

## Profiles and rows

Five profile families, each with its own base height, top-face size, tilt and
dish shape. Height is `base + (row − 2) × 0.5 mm`; the row also shifts the tilt
by 2° per row. DSA is a uniform profile and stays flat at every row.

| `profile_id` | Family | Base height (row 2) | Dish |
| --: | :-- | --: | :-- |
| 0 | DCS | 9.5 mm | cylindrical |
| 1 | DSA | 8.0 mm | spherical |
| 2 | SA | 16.0 mm | spherical |
| 3 | OEM | 11.9 mm | cylindrical |
| 4 | Cherry | 9.4 mm | cylindrical |

## Parameters

| Parameter | Range (default) | Effect |
| :-- | :-- | :-- |
| `profile_id` | 0–4 (0) | profile family: base height, top face, tilt, dish shape |
| `row_id` | 1–4 (1) | keyboard row: +0.5 mm height and +2° tilt per row from row 2 |
| `key_size_id` | 0–3 (0) | 1u / 1.25u / 1.5u / 2u width on the pitch |
| `stem_type_id` | 0–2 (0) | Cherry MX / Alps / Box Cherry |
| `legend_enabled` | off | debosses the legend into the top face |
| `legend_text` | "A" | the characters to engrave |
| `font_size` | 3–10 (6) | glyph height in mm |
| `dish_depth` | 0–3 (1) | top dish depth; 0 leaves the top flat |
| `wall_thickness` | 1.5–5 (3) | skirt wall per side, inward; outer footprint unchanged |
| `keytop_thickness` | 0.5–2 (1) | top-face thickness; also shortens the stem socket |
| `stem_slop` | 0.1–0.6 (0.35) | printer fit allowance on the socket |
| `fn` | 0–64 (0) | tessellation hint for the export; the B-Rep kernel is exact |

Every parameter changes the mesh. `legend_text` and `font_size` are gated behind
`legend_enabled` in the UI, and reach the geometry only when the legend is on.

## Printing

Print upside down, cap top on the plate: the dished top becomes the first layer,
the skirt walls are vertical, and the stem is the only overhang — which the
support ribs carry. No supports are needed for a cap of default proportions.

`stem_slop` is the parameter to tune first. If the cap is loose on the switch,
lower it; if it will not seat, raise it. 0.05 mm steps are meaningful.

---

# Tecla (`keyv2`)

Una tecla paramétrica para interruptores de teclado mecánico. CadQuery / B-Rep.
CERN-OHL-W-2.0. Autoría: Innovaciones MADFAM.

## Qué produce

Un modo (`keycap`) que produce una pieza (`keycap`): una carcasa hueca cónica
con plato cóncavo superior, un faldón dimensionado al paso del teclado, y un
vástago fusionado a la cara inferior de la superficie superior. La leyenda,
cuando se activa, se graba en bajorrelieve en la cara superior.

## Las interfaces que implementa

Son las dimensiones con las que encajan otras cosas. Si están mal, la tecla no
entra en el interruptor o roza con la tecla vecina.

| Interfaz | Dimensión |
| :-- | :-- |
| Paso de tecla | 19.05 mm por unidad |
| Separación entre teclas | 0.5 mm por lado — una tecla 1u mide 18.05 mm, una 2u mide 37.10 mm |
| Vástago Cherry MX | 5.5 mm de diámetro exterior, alojamiento en cruz de 4.1 mm de brazo × 1.17 mm de ancho, cada uno ensanchado por la mitad de `stem_slop` |
| Vástago Alps | poste de 4.5 × 3.2 mm, alojamiento de 3.2 × 1.2 mm, estrechado por el total de `stem_slop` |
| Vástago Box Cherry | poste cuadrado de 6.0 mm con el mismo alojamiento en cruz |
| Profundidad del alojamiento | de la base hasta `cap_height − keytop_thickness − 0.5 mm` |

Nótese la asimetría deliberada en `stem_slop`: Cherry y Box **ensanchan** la cruz
por la mitad de la holgura, Alps **estrecha** su alojamiento por el total. Así se
comportan ambas familias en la impresora; no es un error.

## Perfiles y filas

Cinco familias de perfil, cada una con su altura base, tamaño de cara superior,
inclinación y forma de plato. La altura es `base + (fila − 2) × 0.5 mm`; la fila
también desplaza la inclinación 2° por fila. DSA es un perfil uniforme y
permanece plano en todas las filas.

| `profile_id` | Familia | Altura base (fila 2) | Plato |
| --: | :-- | --: | :-- |
| 0 | DCS | 9.5 mm | cilíndrico |
| 1 | DSA | 8.0 mm | esférico |
| 2 | SA | 16.0 mm | esférico |
| 3 | OEM | 11.9 mm | cilíndrico |
| 4 | Cherry | 9.4 mm | cilíndrico |

## Parámetros

| Parámetro | Rango (predeterminado) | Efecto |
| :-- | :-- | :-- |
| `profile_id` | 0–4 (0) | familia de perfil: altura base, cara superior, inclinación, plato |
| `row_id` | 1–4 (1) | fila del teclado: +0.5 mm de altura y +2° de inclinación por fila desde la fila 2 |
| `key_size_id` | 0–3 (0) | ancho 1u / 1.25u / 1.5u / 2u sobre el paso |
| `stem_type_id` | 0–2 (0) | Cherry MX / Alps / Box Cherry |
| `legend_enabled` | apagado | graba la leyenda en la cara superior |
| `legend_text` | "A" | los caracteres a grabar |
| `font_size` | 3–10 (6) | altura del glifo en mm |
| `dish_depth` | 0–3 (1) | profundidad del plato; 0 deja la superficie plana |
| `wall_thickness` | 1.5–5 (3) | pared del faldón por lado, hacia dentro; la huella exterior no cambia |
| `keytop_thickness` | 0.5–2 (1) | grosor de la cara superior; también acorta el alojamiento |
| `stem_slop` | 0.1–0.6 (0.35) | holgura de impresión en el alojamiento |
| `fn` | 0–64 (0) | sugerencia de teselado para la exportación; el núcleo B-Rep es exacto |

Todos los parámetros cambian la malla. `legend_text` y `font_size` dependen de
`legend_enabled` en la interfaz y sólo llegan a la geometría con la leyenda
activada.

## Impresión

Imprimir boca abajo, con la cara superior sobre la cama: el plato cóncavo pasa a
ser la primera capa, las paredes del faldón quedan verticales, y el vástago es el
único voladizo — sostenido por las costillas de soporte. Una tecla de
proporciones predeterminadas no necesita soportes.

`stem_slop` es el primer parámetro a ajustar. Si la tecla queda floja sobre el
interruptor, bajarlo; si no entra, subirlo. Pasos de 0.05 mm son significativos.
