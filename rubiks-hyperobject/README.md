# Cubo de Rubik Parametrico — Hiperobjeto Yantra4D

Un cubo de Rubik completamente parametrico modelado como Hiperobjeto Acotado 4D. Cuatro dimensiones de variacion: tamano de cuadricula (NxN), estados de rotacion de capas, vista explosionada y forma geometrica (cubo o esfera).

## Que es

Este proyecto genera cubos de Rubik parametricos usando OpenSCAD y la biblioteca BOSL2. Cada aspecto del puzzle es configurable: desde el tamano de cuadricula (2x2 Pocket hasta 5x5 Professor), pasando por las rotaciones de capas individuales, hasta la forma general (cubo clasico o variante esferica).

## 4 Dimensiones de Variacion

| Dimension | Parametro | Rango |
|-----------|-----------|-------|
| Tamano de cuadricula | N | 2-5 (Pocket a Professor) |
| Rotacion de capas | rotate_top/front/right | 0, 90, 180, 270 grados |
| Vista explosionada | explode_factor | 0-200% |
| Forma geometrica | Modo: cubo o esfera | 2 variantes |

## 4 Modos

| Modo | Que genera | Partes |
|------|-----------|--------|
| **Cubo** | Cubo NxN completo con rotaciones de capas | cubies + core + stickers + frame |
| **Esfera** | Variante esferica con bandas rotatorias | segmentos + core + bandas |
| **Explosionado** | Vista despiece del cubo | cubies + core |
| **Cubie** | Pieza individual para impresion | 1 cubie |

## 3 Interfaces CDG

| Interfaz | Tipo | Proposito |
|----------|------|-----------|
| Cavidad de Cubie | pocket | Geometria de encaje entre cubies |
| Montaje de Exhibicion | socket | Base para exhibir el cubo |
| Mecanismo Central | rail | Ejes y esfera central |

## Configurador web

Abre el configurador, ajusta los controles y descarga tu STL:

**[Abrir en Yantra4D](https://app.yantra4d.com/project/rubiks-hyperobject)**

## Inicio rapido

### Opcion A: Configurador web (recomendado)

1. Abre [Yantra4D Studio](https://app.yantra4d.com/project/rubiks-hyperobject)
2. Elige un modo (Cubo, Esfera, Explosionado o Cubie)
3. Ajusta N para cambiar el tamano de cuadricula
4. Rota capas con los controles de rotacion
5. Presiona **Generar** y luego **Exportar**

### Opcion B: OpenSCAD local

```bash
# Cubo estandar 3x3
openscad -o rubiks_3x3.stl rubiks_cube.scad

# Cubo 5x5
openscad -o rubiks_5x5.stl -D "N=5" -D "size=80" rubiks_cube.scad

# Vista explosionada
openscad -o exploded.stl rubiks_exploded.scad

# Variante esferica
openscad -o sphere.stl rubiks_sphere.scad
```

## Documentacion

- [Primeros pasos](docs/getting_started.md) — Guia para principiantes
- [Diseno mecanico](docs/mechanical_design.md) — Referencia tecnica
- [Indice](docs/index.md) — Hub de documentacion

## Licencia

CERN Open Hardware Licence v2 — Weakly Reciprocal (CERN-OHL-W-2.0). Ver [LICENSE](LICENSE).

---

# Parametric Rubik's Cube — Yantra4D Hyperobject

A fully parametric Rubik's Cube modeled as a Bounded 4D Hyperobject. Four dimensions of variation: grid size (NxN), layer rotation states, exploded view, and geometric shape (cube or sphere).

## What is it

This project generates parametric Rubik's cubes using OpenSCAD and the BOSL2 library. Every aspect of the puzzle is configurable: from grid size (2x2 Pocket to 5x5 Professor), through individual layer rotations, to overall shape (classic cube or spherical variant).

## 4 Dimensions of Variation

| Dimension | Parameter | Range |
|-----------|-----------|-------|
| Grid size | N | 2-5 (Pocket to Professor) |
| Layer rotation | rotate_top/front/right | 0, 90, 180, 270 degrees |
| Exploded view | explode_factor | 0-200% |
| Geometric shape | Mode: cube or sphere | 2 variants |

## 4 Modes

| Mode | What it generates | Parts |
|------|------------------|-------|
| **Cube** | Complete NxN cube with layer rotations | cubies + core + stickers + frame |
| **Sphere** | Spherical variant with rotating bands | segments + core + bands |
| **Exploded** | Disassembled cube view | cubies + core |
| **Cubie** | Single piece for printing | 1 cubie |

## 3 CDG Interfaces

| Interface | Type | Purpose |
|-----------|------|---------|
| Cubie Socket | pocket | Interlocking geometry between cubies |
| Display Stand Mount | socket | Base for displaying the cube |
| Core Mechanism | rail | Axles and central sphere |

## Web configurator

Open the configurator, adjust the controls, and download your STL:

**[Open in Yantra4D](https://app.yantra4d.com/project/rubiks-hyperobject)**

## Quick start

### Option A: Web configurator (recommended)

1. Open [Yantra4D Studio](https://app.yantra4d.com/project/rubiks-hyperobject)
2. Choose a mode (Cube, Sphere, Exploded, or Cubie)
3. Adjust N to change grid size
4. Rotate layers with the rotation controls
5. Press **Generate** then **Export**

### Option B: Local OpenSCAD

```bash
# Standard 3x3 cube
openscad -o rubiks_3x3.stl rubiks_cube.scad

# 5x5 cube
openscad -o rubiks_5x5.stl -D "N=5" -D "size=80" rubiks_cube.scad

# Exploded view
openscad -o exploded.stl rubiks_exploded.scad

# Spherical variant
openscad -o sphere.stl rubiks_sphere.scad
```

## Documentation

- [Getting started](docs/getting_started.md) — Beginner guide
- [Mechanical design](docs/mechanical_design.md) — Technical reference
- [Index](docs/index.md) — Documentation hub

## License

CERN Open Hardware Licence v2 — Weakly Reciprocal (CERN-OHL-W-2.0). See [LICENSE](LICENSE).
