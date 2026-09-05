# Diseno Mecanico — Cubo de Rubik Parametrico

Referencia tecnica para ingenieros y makers avanzados. Cubre las formulas de dimensionamiento, el mecanismo central y las interfaces CDG.

## Formulas de dimensionamiento de cubies

Todas las dimensiones derivan de tres parametros fundamentales:

| Simbolo | Parametro | Valor por defecto |
|---------|-----------|-------------------|
| N | Tamano de cuadricula | 3 |
| S | Dimension total (mm) | 57 |
| C | Holgura entre cubies (mm) | 0.3 |

### Tamano de cubie

```
cubie_size = (S - (N + 1) * C) / N
```

Para el cubo estandar 3x3: `(57 - 4 * 0.3) / 3 = 18.6 mm`

### Paso (pitch)

```
pitch = cubie_size + C
```

Distancia centro a centro entre cubies adyacentes: `18.6 + 0.3 = 18.9 mm`

### Offset de cuadricula

```
grid_offset = -(N - 1) / 2 * pitch
```

Centra la cuadricula en el origen.

## Mecanismo central

El mecanismo central consiste en:

| Componente | Formula | 3x3 Estandar |
|------------|---------|---------------|
| Esfera central (diametro) | `S * 0.28` | 15.96 mm |
| Diametro de ejes | `cubie_size * 0.18` | 3.35 mm |
| Longitud de ejes | `S * 0.48` | 27.36 mm |

Los 6 ejes se extienden a lo largo de los ejes +/-X, +/-Y, +/-Z desde la esfera central.

## Redondeo seguro

El radio de redondeo esta limitado para evitar geometria invalida:

```
safe_rounding = min(corner_rounding, cubie_size / 2 - 0.01)
```

## Interfaces CDG

### 1. Cavidad de Cubie (pocket)

Define la geometria de encaje entre cubies adyacentes. Los parametros que la controlan son N, size, clearance y corner_rounding.

### 2. Montaje de Exhibicion (socket)

Interface para bases de exhibicion. Depende del parametro size para determinar la superficie de apoyo.

### 3. Mecanismo Central (rail)

Los ejes actuan como rieles sobre los que se deslizan los cubies. Los parametros N y size determinan la longitud y el diametro.

## Vista explosionada

La explosion desplaza cada cubie hacia afuera desde el centro:

```
explosion_offset = (explode_factor / 100) * base_position * 0.6
```

El factor 0.6 mantiene la explosion visualmente proporcionada sin que los cubies se alejen demasiado del contexto.

## Variante esferica

La esfera se divide en `sphere_band_count` bandas horizontales. Cada banda se genera como la interseccion de la esfera completa con un corte entre dos planos Z.

---

# Mechanical Design — Parametric Rubik's Cube

Technical reference for engineers and advanced makers. Covers dimensioning formulas, core mechanism, and CDG interfaces.

## Cubie dimensioning formulas

All dimensions derive from three fundamental parameters:

| Symbol | Parameter | Default |
|--------|-----------|---------|
| N | Grid size | 3 |
| S | Overall dimension (mm) | 57 |
| C | Cubie clearance (mm) | 0.3 |

### Cubie size

```
cubie_size = (S - (N + 1) * C) / N
```

For the standard 3x3 cube: `(57 - 4 * 0.3) / 3 = 18.6 mm`

### Pitch

```
pitch = cubie_size + C
```

Center-to-center distance between adjacent cubies: `18.6 + 0.3 = 18.9 mm`

### Grid offset

```
grid_offset = -(N - 1) / 2 * pitch
```

Centers the grid at the origin.

## Core mechanism

The core mechanism consists of:

| Component | Formula | Standard 3x3 |
|-----------|---------|---------------|
| Central sphere (diameter) | `S * 0.28` | 15.96 mm |
| Axle diameter | `cubie_size * 0.18` | 3.35 mm |
| Axle length | `S * 0.48` | 27.36 mm |

The 6 axles extend along the +/-X, +/-Y, +/-Z axes from the central sphere.

## Safe rounding

The rounding radius is clamped to avoid invalid geometry:

```
safe_rounding = min(corner_rounding, cubie_size / 2 - 0.01)
```

## CDG Interfaces

### 1. Cubie Socket (pocket)

Defines the interlocking geometry between adjacent cubies. Controlled by the N, size, clearance, and corner_rounding parameters.

### 2. Display Stand Mount (socket)

Interface for display bases. Depends on the size parameter to determine the contact surface.

### 3. Core Mechanism (rail)

Axles act as rails on which cubies slide. The N and size parameters determine length and diameter.

## Exploded view

Explosion displaces each cubie outward from the center:

```
explosion_offset = (explode_factor / 100) * base_position * 0.6
```

The 0.6 factor keeps the explosion visually proportional without cubies drifting too far from context.

## Spherical variant

The sphere is divided into `sphere_band_count` horizontal bands. Each band is generated as the intersection of the full sphere with a cut between two Z planes.
