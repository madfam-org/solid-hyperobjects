# Documentacion del Cubo de Rubik Parametrico

Bienvenido al hub de documentacion del hiperobjeto Rubik's Cube — un puzzle parametrico completamente configurable con modos de cubo, esfera, vista explosionada y pieza individual. Elige la guia segun tu nivel de experiencia.

## Guias

| Documento | Descripcion | Audiencia |
|-----------|-------------|-----------|
| [Primeros pasos](getting_started.md) | Guia paso a paso desde el configurador hasta tu primer cubo | Principiantes |
| [Diseno mecanico](mechanical_design.md) | Referencia tecnica: dimensiones de cubies, mecanismo central, interfaces CDG | Ingenieros |

## Recursos adicionales

| Recurso | Descripcion |
|---------|-------------|
| [README del proyecto](../README.md) | Resumen general, inicio rapido, enlaces |
| [Configurador web](https://app.yantra4d.com/project/rubiks-hyperobject) | Visualizador 3D interactivo con descarga STL |

## Estructura del proyecto

```
rubiks-hyperobject/
  project.json            Manifiesto (fuente de verdad)
  rubiks_cube.scad        Cubo NxN parametrico
  rubiks_sphere.scad      Variante esferica
  rubiks_exploded.scad    Vista explosionada
  cubie.scad              Pieza individual
  index.ts                Exportacion de cartridge
  docs/
    index.md              Hub de documentacion
    getting_started.md    Guia para principiantes
    mechanical_design.md  Referencia tecnica
  tests/
    README.md             Documentacion de pruebas
  exports/                STL exportados de referencia
```

---

# Parametric Rubik's Cube Documentation

Welcome to the Rubik's Cube hyperobject documentation hub — a fully configurable parametric puzzle with cube, sphere, exploded view, and single piece modes. Choose the guide that matches your experience level.

## Guides

| Document | Description | Audience |
|----------|-------------|----------|
| [Getting started](getting_started.md) | Step-by-step guide from the configurator to your first cube | Beginners |
| [Mechanical design](mechanical_design.md) | Technical reference: cubie dimensions, core mechanism, CDG interfaces | Engineers |

## Additional resources

| Resource | Description |
|----------|-------------|
| [Project README](../README.md) | General overview, quick start, links |
| [Web configurator](https://app.yantra4d.com/project/rubiks-hyperobject) | Interactive 3D viewer with STL download |

## Project structure

```
rubiks-hyperobject/
  project.json            Manifest (source of truth)
  rubiks_cube.scad        Parametric NxN cube
  rubiks_sphere.scad      Spherical variant
  rubiks_exploded.scad    Exploded view
  cubie.scad              Single piece
  index.ts                Cartridge export
  docs/
    index.md              Documentation hub
    getting_started.md    Beginner guide
    mechanical_design.md  Technical reference
  tests/
    README.md             Test documentation
  exports/                Reference STL exports
```
