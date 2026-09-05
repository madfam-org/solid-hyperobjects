# Rubik's Hyperobject — Hoja de Ruta / Roadmap

---

## Estado Actual — ¿Qué tan cerca estamos?

### Cobertura del universo de puzzles giratorios

| Categoría | Formas | Estado | Cobertura |
|-----------|--------|--------|-----------|
| **Cubo NxN** | 2×2 a 9×9 | ✅ Implementado | 100% |
| **Esfera** | Bandas horizontales rotatorias | ✅ Implementado | 70% (falta rotación vertical) |
| **Sólidos Platónicos** | Tetraedro, Octaedro, Dodecaedro, Icosaedro | ❌ No implementado | 0% |
| **Puzzles de esquina** | Skewb, Ivy Cube, Redi Cube | ❌ No implementado | 0% |
| **Puzzles con forma (Shape Mods)** | Mirror, Windmill, Fisher, Axis | ❌ No implementado | 0% |
| **Puzzles cúbicos especiales** | Square-1, Bandaged, Void | ❌ No implementado | 0% |
| **Mega/Mini variantes** | Megaminx, Pyraminx, Skewb | ❌ No implementado | 0% |
| **Formas novedosas** | Gear Cube, Mixup, Crazy | ❌ No implementado | 0% |

### Lo que SÍ tenemos (completado)

- ✅ Cubo paramétrico NxN (2-9) con rotación independiente de TODAS las capas
- ✅ Esfera con bandas rotatorias
- ✅ Vista explosionada con factor ajustable
- ✅ Mecanismo funcional imprimible (rieles T, cavidades de resorte, tornillos M3)
- ✅ Sistema CDG de insertos intercambiables (socket + pin de alineación)
- ✅ 5 estilos de adhesivos (color, táctil, rayas, tablero, concéntrico)
- ✅ Notación embossed (U/D/F/B/L/R) en cubies centrales
- ✅ 6 colores de cara parametrizables
- ✅ 3 presets de accesibilidad (daltonismo, alto contraste, monocromático táctil)
- ✅ 3 animaciones (resolver, explosionar, morfar)
- ✅ 5 pasos de ensamble para impresión 3D
- ✅ 56 parámetros, 6 modos, 13 presets

### Lo que FALTA para capturar el universo completo

El cubo NxN es solo UNA familia dentro de un universo de ~50+ formas de puzzle giratorio comercialmente producidas. Para ser un verdadero hiperobjeto "Bounded 4D" del espacio completo, necesitamos:

1. **Rotación por vértices** (Skewb, Pyraminx) — fundamentalmente diferente a la rotación por caras
2. **Geometría no-cúbica** (dodecaedro, tetraedro) — requiere primitivas geométricas distintas
3. **Modificaciones de forma** (Mirror, Windmill) — misma topología que el cubo pero geometría distorsionada
4. **Mecanismos especiales** (Square-1 con cambio de forma, Gear Cube con engranajes)

### Estimación de completitud

**Formas cuboidales** (cubo NxN, rectángulos): **95%** ✅
**Formas esféricas**: **40%** (falta rotación multi-eje)
**Sólidos Platónicos**: **0%** ❌
**Puzzles de esquina**: **0%** ❌
**Shape Mods**: **0%** ❌
**Formas novedosas**: **0%** ❌

**Completitud global estimada: ~25%** del universo manufacturable de puzzles giratorios.

---

## Tareas Diferidas — Prioridad 7-9

### P7: Sólidos Platónicos y más poliedros (ALTA prioridad diferida)

Nuevos modos SCAD, cada uno con su propia geometría base:

| Forma | Archivo | Caras | Tipo de rotación | Complejidad |
|-------|---------|-------|-----------------|-------------|
| **Pyraminx** | `pyraminx.scad` | 4 triángulos | Vértice (4 ejes) | Media |
| **Megaminx** | `megaminx.scad` | 12 pentágonos | Cara (12 ejes) | Alta |
| **Skewb** | `skewb.scad` | 6 cuadrados (rotación diagonal) | Vértice (4 ejes) | Media |
| **Octaedro** | `octahedron.scad` | 8 triángulos | Cara (8 ejes) | Alta |
| **Icosaedro** | `icosahedron.scad` | 20 triángulos | Cara (20 ejes) | Muy alta |

**Dependencias**: Cada forma necesita:
- Módulo de pieza base (equivalente a `cubie()` pero para triángulos/pentágonos)
- Lógica de adyacencia para determinar caras expuestas
- Sistema de rotación adaptado a la topología del sólido
- Mecanismo interno específico (el eje central difiere para cada sólido)

**Estimación**: 2-3 semanas por forma. Pyraminx y Skewb primero (más simples).

### P8: Reproductor de secuencias de estados (MEDIA prioridad diferida)

**Qué es**: Definir algoritmos de resolución como secuencias de movimientos (ej. "R U R' U'") y reproducirlos como animación paso a paso.

**Qué requiere del platform**:
- Soporte para animaciones secuenciales (no solo interpolación from→to)
- Parser de notación Rubik's (R, U, F, D, B, L, R', U2, etc.)
- Cada paso = un frame con un solo parámetro de rotación cambiado
- UI de reproducción con play/pause/step

**Estimación**: 1 semana de trabajo en plataforma + 1 semana de integración.

### P9: Metadata de simulación física (BAJA prioridad, aspiracional)

**Qué es**: Declarar propiedades de material (densidad ABS, constante de resorte, coeficiente de fricción) para que la plataforma pueda eventualmente simular:
- Torque de rotación
- Tensión de resorte
- Fuerza de snap
- Desgaste mecánico

**Qué requiere del platform**: Sistema de simulación de materiales que no existe actualmente.

**Estimación**: No planificable hasta que el platform tenga capacidades de simulación.

---

## Hoja de Ruta Futura (orden sugerido)

### Sprint A: Pyraminx + Skewb (próximo)
- `pyraminx.scad` — tetraedro con rotación de vértices
- `skewb.scad` — cubo con rotación diagonal
- 2 nuevos modos + parámetros de rotación específicos
- **Impacto**: Sube la cobertura de 25% a ~40%

### Sprint B: Megaminx (después de Sprint A)
- `megaminx.scad` — dodecaedro con 12 caras pentagonales
- Geometría compleja: 62 piezas visibles
- **Impacto**: Sube la cobertura a ~50%

### Sprint C: Shape Mods (después de Sprint B)
- Reutilizar la topología del cubo NxN pero con transformaciones geométricas:
  - Mirror Cube: escalar cubies asimétricamente
  - Windmill Cube: rotar la capa central 45°
  - Fisher Cube: cortar diagonal en vez de paralelo
- **Impacto**: Sube la cobertura a ~65% (muchas variantes con poco código nuevo)

### Sprint D: Reproducción de secuencias (después de Sprint C)
- Parser de notación Rubik's en el platform
- Animación paso a paso
- Biblioteca de algoritmos predefinidos (PLL, OLL, F2L)
- **Impacto**: Transforma el proyecto de herramienta de diseño a herramienta educativa

### Sprint E: Formas exóticas (futuro lejano)
- Square-1 (cambio de forma)
- Gear Cube (engranajes)
- Crazy Cube (círculos internos)
- Void Cube (sin centro)
- **Impacto**: Completa la cobertura al ~90%+

---

## Current State — How Close Are We?

### Coverage of the Twisty Puzzle Universe

| Category | Shapes | Status | Coverage |
|----------|--------|--------|----------|
| **NxN Cube** | 2×2 to 9×9 | ✅ Implemented | 100% |
| **Sphere** | Horizontal rotating bands | ✅ Implemented | 70% (missing vertical rotation) |
| **Platonic Solids** | Tetrahedron, Octahedron, Dodecahedron, Icosahedron | ❌ Not implemented | 0% |
| **Corner-turning puzzles** | Skewb, Ivy Cube, Redi Cube | ❌ Not implemented | 0% |
| **Shape Mods** | Mirror, Windmill, Fisher, Axis | ❌ Not implemented | 0% |
| **Special cubes** | Square-1, Bandaged, Void | ❌ Not implemented | 0% |
| **Mega/Mini variants** | Megaminx, Pyraminx, Skewb | ❌ Not implemented | 0% |
| **Novel shapes** | Gear Cube, Mixup, Crazy | ❌ Not implemented | 0% |

### What We HAVE (completed)

- ✅ Parametric NxN cube (2-9) with independent ALL-layer rotation
- ✅ Sphere with rotating bands
- ✅ Exploded view with adjustable factor
- ✅ Functional printable mechanism (T-tracks, spring cavities, M3 screws)
- ✅ CDG insert system (interchangeable face tiles with alignment pins)
- ✅ 5 sticker styles (color, tactile dots, stripes, checkerboard, concentric)
- ✅ Embossed notation (U/D/F/B/L/R) on center cubies
- ✅ 6 parametric face colors
- ✅ 3 accessibility presets (colorblind, high contrast, monochrome tactile)
- ✅ 3 animations (solve, explode, morph)
- ✅ 5 assembly steps for 3D printing
- ✅ 56 parameters, 6 modes, 13 presets

### What's MISSING for full universe capture

The NxN cube is only ONE family within a universe of ~50+ commercially-produced twisty puzzle shapes. To be a true "Bounded 4D" hyperobject of the complete space, we need:

1. **Vertex-turning** (Skewb, Pyraminx) — fundamentally different from face-turning
2. **Non-cubic geometry** (dodecahedron, tetrahedron) — requires different geometric primitives
3. **Shape modifications** (Mirror, Windmill) — same topology as cube but distorted geometry
4. **Special mechanisms** (Square-1 with shape-shifting, Gear Cube with gears)

### Estimated completeness

**Cuboidal shapes** (NxN cube, cuboids): **95%** ✅
**Spherical shapes**: **40%** (missing multi-axis rotation)
**Platonic Solids**: **0%** ❌
**Corner-turning puzzles**: **0%** ❌
**Shape Mods**: **0%** ❌
**Novel shapes**: **0%** ❌

**Overall estimated completeness: ~25%** of the manufacturable twisty puzzle universe.

---

## Deferred Tasks — Priority 7-9

### P7: Platonic Solids and More Polyhedra (HIGH deferred priority)

New SCAD modes, each with its own base geometry:

| Shape | File | Faces | Rotation Type | Complexity |
|-------|------|-------|---------------|------------|
| **Pyraminx** | `pyraminx.scad` | 4 triangles | Vertex (4 axes) | Medium |
| **Megaminx** | `megaminx.scad` | 12 pentagons | Face (12 axes) | High |
| **Skewb** | `skewb.scad` | 6 squares (diagonal rotation) | Vertex (4 axes) | Medium |
| **Octahedron** | `octahedron.scad` | 8 triangles | Face (8 axes) | High |
| **Icosahedron** | `icosahedron.scad` | 20 triangles | Face (20 axes) | Very high |

**Estimate**: 2-3 weeks per shape. Pyraminx and Skewb first (simplest).

### P8: State Sequence Player (MEDIUM deferred priority)

Requires platform-level animation sequencing support. Not currently available.

### P9: Physics Simulation Metadata (LOW deferred priority)

Requires platform-level material simulation. Not currently available.

---

## Future Roadmap (suggested order)

### Sprint A: Pyraminx + Skewb → coverage 25% → ~40%
### Sprint B: Megaminx → coverage ~40% → ~50%
### Sprint C: Shape Mods (Mirror, Windmill, Fisher) → coverage ~50% → ~65%
### Sprint D: State sequence player → educational transformation
### Sprint E: Exotic shapes (Square-1, Gear, Crazy, Void) → coverage ~65% → ~90%+
