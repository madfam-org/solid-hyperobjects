# Pruebas del Cubo de Rubik Parametrico

## Auditoria E2E en navegador

Las pruebas E2E de Playwright para el hiperobjeto Rubik's estan en la infraestructura de pruebas del studio de yantra4d:

```
apps/studio/e2e/tests/23-browser-audit/rubiks-hyperobject.spec.js
```

### Como ejecutar

Desde la raiz del monorepo yantra4d, con el stack Docker corriendo (`docker compose up`):

```bash
cd apps/studio
npx playwright test --project=audit -g "Rubik"
```

### Cobertura esperada

| Seccion | Pruebas | Que cubre |
|---------|---------|-----------|
| A. Carga y Navegacion | 4 | Carga inicial, modo por defecto (cubo), cambio a esfera/explosionado/cubie |
| B. Controles de Parametros | 6 | Deslizador N, rotaciones de capas, factor de explosion, presets |
| C. Renderizado 3D | 4 | Render de cubo/esfera, re-render al cambiar N, info del modelo |
| D. Exportacion | 2 | Formatos disponibles, descarga STL |
| E. Ensamble | 2 | Panel de pasos, navegacion entre pasos |
| F. Accesibilidad | 1 | Auditoria axe |

### Dependencias

- Playwright (`@playwright/test`)
- Backend Docker con OpenSCAD
- Fixtures del studio (`apps/studio/e2e/fixtures/`)
- Helpers compartidos de auditoria (`apps/studio/e2e/tests/23-browser-audit/audit-helpers.js`)

### Notas

- Las pruebas requieren el stack Docker completo con OpenSCAD para renderizado real.
- Ejecutar con `--project=audit` — los proyectos por defecto excluyen la suite de auditoria.
- Las pruebas se saltan automaticamente via `skipIfNoBackend()` si Docker no esta corriendo.

---

# Parametric Rubik's Cube Tests

## E2E Browser Audit

The Playwright E2E tests for the Rubik's hyperobject live in the yantra4d studio app's test infrastructure:

```
apps/studio/e2e/tests/23-browser-audit/rubiks-hyperobject.spec.js
```

### Running

From the yantra4d monorepo root, with the Docker stack running (`docker compose up`):

```bash
cd apps/studio
npx playwright test --project=audit -g "Rubik"
```

### Expected coverage

| Section | Tests | What it covers |
|---------|-------|----------------|
| A. Loading & Navigation | 4 | Initial load, default mode (cube), switch to sphere/exploded/cubie |
| B. Parameter Controls | 6 | N slider, layer rotations, explode factor, presets |
| C. 3D Rendering | 4 | Cube/sphere render, re-render on N change, model info |
| D. Export | 2 | Available formats, STL download |
| E. Assembly | 2 | Assembly steps panel, step navigation |
| F. Accessibility | 1 | Axe audit |

### Dependencies

- Playwright (`@playwright/test`)
- Docker backend with OpenSCAD
- Studio app fixtures (`apps/studio/e2e/fixtures/`)
- Shared audit helpers (`apps/studio/e2e/tests/23-browser-audit/audit-helpers.js`)

### Notes

- Tests require the full Docker stack with OpenSCAD for real rendering.
- Run with `--project=audit` — default browser projects exclude the audit suite.
- Tests auto-skip via `skipIfNoBackend()` if Docker is not running.
