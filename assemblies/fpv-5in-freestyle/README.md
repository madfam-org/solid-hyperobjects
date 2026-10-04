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
- **The camera mount.**
  - The `fpv-camera-cage` (`cage`, micro, 30° tilt; TPU intended) mounts by its tabs to the
    frame's camera side plates.
  - The micro camera (`fpv-camera-micro-19mm`) sits in the cage's cradle.
  - The cage's tabs reach the frame through two mates, which form a cycle that must
    close.
  - The cage is **not** mated into the frame's 19–20 mm camera bay. At micro size the
    cage is about 23.8 mm wide, so that mate would be physically false.
- **The stack and the battery.**
  - `pcb-standoff` in `fc_stack` mode (30.5 × 30.5 M3) sits on the frame's stack mount.
  - `battery-pad` (`flat_pad`) sits on the top plate's strap station.
  - The pad's long axis follows the frame's fore-aft axis.

Every mate states its rotation.

## Requirements roll-up

`requirements_rollup` is true. The roll-up reports only what the cartridges declare:
today that is `motor-soft-mount`'s `soft_mount` part (FFF, TPU 95A). The owner's brief
asks for a TPU camera mount, but `fpv-camera-cage` declares no material yet: no
documentary evidence for TPU has been recorded on it, so none is claimed here.

## Status and gaps

- **The camera mates wait for new interfaces** (lane P4-AUTH-C):
  - the frame's side-plate interfaces and the camera's planar back face (keystone
    catalog);
  - the cage's tab and cradle frames (cartridge).
  Until they merge, the check fails on those three mates, and the assembly is not
  merged.
- **The antenna chain is not included.**
  - The catalog chain mount → `sma-bulkhead-jack` → `vtx-antenna-sma` closes.
  - Two interfaces are still missing: the mount's SMA seat, and an interface that ties
    `fpv-antenna-mount` to the frame. The catalog frame has no antenna-mount station.
- **No props or flight-controller board.** Neither is in the brief. A board on the
  standoffs also needs a framed standoff top.
- **No collision claim.** `--collision` is a stub in keystone 0.4.0 and is not run.

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
- **La cámara.** La jaula (pensada en TPU; el cartucho aún no declara material) se monta con sus pestañas en las placas laterales del
  marco, y la cámara micro va en su cuna. La jaula **no** entra en el hueco de cámara de
  19–20 mm, porque mide unos 23.8 mm de ancho.
- **La pila y la batería.** Los separadores de la pila (30.5 × 30.5 M3) van sobre el
  montaje de la pila, y la almohadilla de batería sobre la placa superior.

**Pendientes**

- **Las uniones de la cámara** esperan las interfaces nuevas del carril P4-AUTH-C. Hasta
  que lleguen, la verificación falla y el ensamble no se fusiona.
- **La cadena de antena no se incluye.** Faltan el asiento SMA de la montura y una
  interfaz que la fije al marco.
- **No hay verificación de colisiones.** `--collision` es un esbozo en la versión 0.4.0.
