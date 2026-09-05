# Modular Wall Tile — 25 mm Threaded Grid

A flat wall panel carrying a 25 mm square grid of internally threaded bores.
Accessories — hooks, bins, tool holders, brackets — screw straight into the
grid, so the thread is both the fastening and the locating feature and no
separate hardware is needed. Panels butt edge to edge and the interior-node
threads carry the seam connectors that keep the grid continuous across a joint.

MADFAM clean-room implementation under ADR-021 §4: the 25 mm mounting
**interface** is implemented from measured dimensions so third-party grid
accessories mate; the tile's **form** — its castellated silhouette, its
fixed-millimetre corner flats and its rear relief — is our own design. See
`../NOTICE` for the provenance statement and `CLEANROOM-VERIFICATION.md` for the
measured evidence.

## The interface

| Feature | Position | Thread | Diameters |
| :-- | :-- | :-- | :-- |
| Primary bore | centre of every cell | internal trapezoidal, 29° flank, 2.5 mm pitch | major Ø 22.54, minor Ø 20.15 mm |
| Secondary bore | every **interior** grid intersection | internal trapezoidal, 29° flank, 3 mm pitch | major Ø 6.95, minor Ø 4.48 mm |

Grid pitch is 25.0 mm on both axes for both classes. Panel thickness defaults to
6.4 mm and is itself an interface dimension: it is the thread engagement length
an accessory screws into.

Hole counts follow the grid exactly. Primary bores are `x_cells × y_cells`;
secondary bores are `(x_cells − 1) × (y_cells − 1)` — the interior intersections
only. At the 4 × 4 default that is 16 and 9.

**Both threads are true helices**, cut at full panel depth: a screw threads in
and holds. They are not stacks of concentric rings, which can be dimensionally
exact and still be un-threadable. `CLEANROOM-VERIFICATION.md` carries the proof.

## Parameters

| Id | Range | Default | What it does |
| :-- | :-- | :-- | :-- |
| `x_cells` | 1–12 | 4 | cells along X; one primary thread per cell |
| `y_cells` | 1–12 | 4 | cells along Y |
| `cell_size` | 20–35 mm | 25 | grid module. **25 mm IS the interface** — a panel at any other value will not accept third-party 25 mm-grid accessories. Below 25 the Ø22.54 thread is wider than the cell, so the value is held at 25 |
| `height` | 4–10 mm | 6.4 | panel thickness, and the thread engagement length |
| `fn` | 0–64 | 0 | tessellation; 0 uses the cartridge default of 32 — the value the interface tables are measured at, setting both facets and extrusion layers per thread turn |

The manifest carries three constraints: a `warning` above 96 cells, an `error`
above 120 cells (every bore is a full-depth helical thread, and beyond that the
render exceeds the platform's budget — split the wall into two panels, which
butt and bolt together), and an `error` below `cell_size` 25.

## Rendering

OpenSCAD, Manifold backend, builtins only — no library includes:

```
/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD --backend=Manifold \
  -o tile.stl -D x_cells=4 -D y_cells=4 -D cell_size=25 -D height=6.4 -D fn=0 \
  tile.scad
```

Each thread is one `linear_extrude(height, twist = -360·height/pitch, slices)`
of the 2-D trapezoidal tooth profile, which is a helix of that pitch by
construction. Manifold cuts them from the plate in seconds.

## Printing

Print flat on the bed, no supports. The bores are self-supporting: a trapezoidal
thread's overhang never exceeds the 29° flank. Three perimeters give the seam
nodes enough material for a connector to pull against. The rear relief means a
screw entering from the back starts square without a bench chamfer.

---

# Baldosa Modular de Pared — Cuadrícula Roscada de 25 mm

Un panel de pared plano con una cuadrícula cuadrada de 25 mm de barrenos
roscados internamente. Los accesorios — ganchos, cajas, portaherramientas,
soportes — se atornillan directamente en la cuadrícula, así que la rosca es a la
vez la fijación y el elemento de posicionamiento y no hace falta herraje aparte.
Los paneles se topan borde con borde y las roscas de los nodos interiores llevan
los conectores de junta que mantienen la cuadrícula continua en la unión.

Implementación de sala limpia de MADFAM bajo ADR-021 §4: la **interfaz** de
montaje de 25 mm se implementa a partir de dimensiones medidas para que los
accesorios de cuadrícula de terceros encajen; la **forma** de la baldosa — su
silueta almenada, sus chaflanes de esquina en milímetros fijos y su alivio
posterior — es diseño propio. Véase `../NOTICE` para la declaración de
procedencia y `CLEANROOM-VERIFICATION.md` para la evidencia medida.

## La interfaz

| Elemento | Posición | Rosca | Diámetros |
| :-- | :-- | :-- | :-- |
| Barreno primario | centro de cada celda | trapecial interna, flanco 29°, paso 2.5 mm | mayor Ø 22.54, menor Ø 20.15 mm |
| Barreno secundario | cada intersección **interior** | trapecial interna, flanco 29°, paso 3 mm | mayor Ø 6.95, menor Ø 4.48 mm |

El paso de la cuadrícula es de 25.0 mm en ambos ejes para ambas clases. El
grosor del panel es de 6.4 mm por defecto y es en sí una dimensión de interfaz:
es la longitud de rosca en la que se atornilla un accesorio.

Los conteos de barrenos siguen la cuadrícula exactamente. Los primarios son
`x_cells × y_cells`; los secundarios son `(x_cells − 1) × (y_cells − 1)` — sólo
las intersecciones interiores. Con el valor por defecto de 4 × 4 eso da 16 y 9.

**Ambas roscas son hélices reales**, cortadas a todo el espesor del panel: un
tornillo entra y sujeta. No son pilas de anillos concéntricos, que pueden ser
dimensionalmente exactas y aun así no admitir un tornillo.
`CLEANROOM-VERIFICATION.md` contiene la prueba.

## Parámetros

| Id | Rango | Por defecto | Qué hace |
| :-- | :-- | :-- | :-- |
| `x_cells` | 1–12 | 4 | celdas en X; una rosca primaria por celda |
| `y_cells` | 1–12 | 4 | celdas en Y |
| `cell_size` | 20–35 mm | 25 | módulo de la cuadrícula. **25 mm ES la interfaz** — un panel con otro valor no aceptará accesorios de cuadrícula de 25 mm de terceros. Por debajo de 25 la rosca de Ø22.54 es más ancha que la celda, así que el valor se mantiene en 25 |
| `height` | 4–10 mm | 6.4 | grosor del panel, y la longitud de rosca útil |
| `fn` | 0–64 | 0 | teselado; 0 usa el valor por defecto del cartucho (32), con el que se midieron las tablas de interfaz, y fija facetas y capas de extrusión por vuelta |

El manifiesto lleva tres restricciones: un `warning` por encima de 96 celdas, un
`error` por encima de 120 celdas (cada barreno es una rosca helicoidal a todo el
espesor, y más allá el render supera el presupuesto de la plataforma — divide la
pared en dos paneles, que se topan y se atornillan entre sí), y un `error` por
debajo de `cell_size` 25.

## Renderizado

OpenSCAD, backend Manifold, sólo funciones nativas — sin bibliotecas incluidas:

```
/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD --backend=Manifold \
  -o tile.stl -D x_cells=4 -D y_cells=4 -D cell_size=25 -D height=6.4 -D fn=0 \
  tile.scad
```

Cada rosca es un `linear_extrude(height, twist = -360·height/pitch, slices)` del
perfil trapecial en 2-D, que por construcción es una hélice de ese paso.
Manifold las corta de la placa en segundos.

## Impresión

Imprime plano sobre la cama, sin soportes. Los barrenos se autosoportan: el
voladizo de una rosca trapecial nunca excede el flanco de 29°. Tres perímetros
dan a los nodos de junta material suficiente para que un conector tire contra
ellos. El alivio posterior hace que un tornillo que entra por detrás arranque a
escuadra sin achaflanar a mano.
