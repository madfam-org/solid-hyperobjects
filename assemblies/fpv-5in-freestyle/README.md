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
- **The camera cage on the side plates.**
  - The `fpv-camera-cage` (`cage`, micro, 30° tilt, `mount_width` 24; TPU intended) hangs
    on the frame's camera side plates by two ears.
  - Each ear's inner face bolts to a plate's **outer** face:
    `camera_plate_left_outer ↔ cage_ear_left` and
    `camera_plate_right_outer ↔ cage_ear_right`, both at `angle_deg` 0. The catalog
    places those faces at `camera_bay_width_mm` + 2 × `side_plate_thickness_mm` =
    19 + 2 × 2.5 = 24 mm apart (keystone `8c12194`). The ears are in
    solid-hyperobjects#133.
  - The two ear mates form a cycle, so it closes only when the cage's `mount_width`
    equals the plates' outer spacing. With ears at 19 mm (the inner spacing) the cycle
    misses by 5.0000 mm; at 25 mm it misses by 1.0000 mm.
- **The camera in the cage.**
  - The micro camera (`fpv-camera-micro-19mm`) seats **lens-first** on the cage's cradle
    floor: `cage_cradle_floor ↔ front_face`, `rotation_index` 0.
  - The floor carries the lens aperture and is tilted by the cage's `tilt` (30°), so the
    optical axis points 30° up from the frame's forward axis.
  - The validator cannot tell `front_face` from `back_face`: both close, and
    `back_face` would aim the camera 30° down. The face choice follows the cage geometry
    (#133), not the check.
- **The stack and the battery.**
  - `pcb-standoff` in `fc_stack` mode (30.5 × 30.5 M3) sits on the frame's stack mount.
  - `battery-pad` (`flat_pad`) sits on the top plate's strap station.
  - The pad's long axis follows the frame's fore-aft axis.

Every mate states its rotation.

## Requirements roll-up

`requirements_rollup` is true. The roll-up reports only what the cartridges declare:
today that is `motor-soft-mount`'s `soft_mount` part (FFF, TPU 95A). The cage is meant
to be printed in TPU, but `fpv-camera-cage` declares no material: no documentary
evidence for TPU has been recorded on it, so none is claimed.

## Gaps (documented, not claimed)

- **The antenna chain is not included in this round.** The rear-mount antenna mount
  (solid-hyperobjects#135) has merged and can join a later round.
- **No props and no flight-controller board.** Neither is in the brief.
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
- **La jaula de cámara.** La jaula (pensada en TPU; el cartucho no declara material)
  cuelga de las caras **exteriores** de las placas laterales por dos orejas, separadas
  24 mm (19 + 2 × 2.5). Las dos uniones forman un ciclo: con orejas a 19 mm falla por
  5 mm.
- **La cámara.** La cámara micro asienta con la lente al frente en la cuna de la jaula,
  a 30° hacia arriba.
- **La pila y la batería.** Los separadores de la pila (30.5 × 30.5 M3) van sobre el
  montaje de la pila, y la almohadilla de batería sobre la placa superior.

**Lo que no incluye**

- **La cadena de antena** queda fuera de esta ronda.
- **Verificación de colisiones.** `--collision` es un esbozo en la versión 0.4.0.
