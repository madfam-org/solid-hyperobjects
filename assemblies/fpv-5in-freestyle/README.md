# 5-inch FPV freestyle quadcopter (`fpv-5in-freestyle`)

Assembly B of the Digital Twins programme (ASM-1 §7). It is a **product** (a thing that
is made), and the keystone's `y4d-spec assembly check` validates it.
Document licence: CERN-OHL-W-2.0.

## What it proves

- **The frame is a catalog class.** It is the generic 5-inch X frame
  (`fpv-frame-5in-x-225`, the root), a COTS class defined by its shared facts: a 225 mm
  motor-to-motor diagonal, 16 × 16 M3 motor mounts, a 30.5 × 30.5 stack and 20 mm strap
  slots. It is not a copied vendor design.
- **Four motor chains:** frame arm → TPU pod → motor.
  - The four `motor-soft-mount` pods (`soft_mount`, `motor_pattern` 16x16) clamp the
    arms on their `arm_clamp` faces.
  - Four 2207 motors (`motor-2207`) bolt to the pods' `motor_bolt_pattern`.
  - The frame's motor-mount `x_axis` points outward along each arm, so every pod aligns
    at `rotation_index` 0.
- **The camera between the side plates.**
  - The micro camera (`fpv-camera-micro-19mm`) bolts by its side screws to the frame's
    side plates: `camera_plate_left ↔ side_face_left` and
    `camera_plate_right ↔ side_face_right` (hyperobjects-spec#38). That is how a micro
    camera sits in this frame class.
  - The two plate mates form a cycle. The second mate closes only when the 19 mm body
    width equals the frame's `camera_bay_width_mm`, which defaults to 19. With a 20 mm
    bay the cycle misses by 1.0000 mm.
  - The left mate sets the tilt: `angle_deg` −30, which aims the optical axis 30° up.
  - The right plate faces the opposite way, so the same physical tilt reads +30 there.
    The document states +30, the angle the geometry realises.
  - The validator does not check the angle of a symmetry-0 mate that closes a cycle; it
    checks only origin and axis. The stated +30 is therefore documentation that matches
    the measured value, not something the check enforces.
- **The stack and the battery.**
  - `pcb-standoff` in `fc_stack` mode (30.5 × 30.5 M3) sits on the frame's stack mount.
  - `battery-pad` (`flat_pad`) sits on the top plate's strap station.
  - The pad's long axis follows the frame's fore-aft axis.

Every mate states its rotation.

## Requirements roll-up

`requirements_rollup` is true. The roll-up reports only what the cartridges declare:
today that is `motor-soft-mount`'s `soft_mount` part (FFF, TPU 95A).

## Gaps (documented, not claimed)

- **The TPU camera mount is not in this assembly.** The owner's brief asks for
  `fpv-camera-cage`, but the cage as modelled cannot attach to this frame:
  - it is about 23.8 mm wide, and its tab faces stand about 29.8 mm apart;
  - the side plates are 19–20 mm apart, so the tabs miss by 10.8 mm
    (hyperobjects-spec#38, P4-AUTH-C).

  How the cage should attach is an open owner decision. A cage with no mate to the frame
  would be unreachable and would fail the check, so it is left out.
- **Camera in the cage, proven separately.** `cage_cradle_floor ↔ front_face` (the camera
  seats lens-first) closes on its own (solid-hyperobjects#126). It joins this document
  once the cage has a frame attachment. A render probe found that, at a tilt above 0, a
  19 × 19 × 20 camera body on that floor intersects the cage's base block; this was
  reported to P4-AUTH-C.
- **The antenna chain is not included.** The antenna mount is stopped pending an owner
  design decision.
- **No props and no flight-controller board.** Neither is in the brief. A board on the
  standoffs also needs a framed standoff top.
- **No collision claim.** `--collision` is a stub in keystone 0.4.0. It is not run.

## Check it

```bash
pip install "hyperobjects-spec @ git+https://github.com/madfam-org/hyperobjects-spec@<SPEC_PIN>"
parts=$(python -c 'import hyperobjects_standard_parts as h, pathlib; print(pathlib.Path(h.__file__).parent / "parts")')
y4d-spec assembly check assemblies/fpv-5in-freestyle/assembly.json --commons . --standard-parts "$parts"
```

`SPEC_PIN` is in [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml). CI runs this
check on every PR (the `assemblies` job).

---

## Español

Ensamble B del programa de gemelos digitales (ASM-1 §7). Es un **producto**.
Licencia del documento: CERN-OHL-W-2.0.

**Qué demuestra**

- **El marco.** Es el marco X genérico de 5 pulgadas del catálogo: una clase COTS, no un
  diseño copiado.
- **Las cuatro cadenas de motor.** Cada una va del brazo del marco a una base de TPU
  (`motor-soft-mount`) y de ahí a un motor 2207. Todas alinean con `rotation_index` 0.
- **La cámara.** La cámara micro se atornilla por sus tornillos laterales a las dos
  placas laterales del marco, con 30° de inclinación hacia arriba. Las dos uniones
  forman un ciclo que cierra solo si el ancho del hueco es de 19 mm.
- **La pila y la batería.** Los separadores de la pila (30.5 × 30.5 M3) van sobre el
  montaje de la pila, y la almohadilla de batería sobre la placa superior.

**Lo que no incluye**

- **La montura de cámara de TPU (`fpv-camera-cage`).** Tal como está modelada, no puede
  fijarse al marco: sus pestañas quedan a unos 29.8 mm y las placas a 19–20 mm. Es una
  decisión pendiente del dueño. La cámara en la cuna se demuestra por separado (#126).
- **La cadena de antena.** Está detenida por una decisión de diseño del dueño.
- **Verificación de colisiones.** `--collision` es un esbozo en la versión 0.4.0.
