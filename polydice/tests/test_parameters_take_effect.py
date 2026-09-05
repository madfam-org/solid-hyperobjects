"""Regression test: every mode is distinct and every parameter changes the mesh.

The recorded baseline this cartridge replaces was completely inert — all five
modes and all six geometry parameters produced one byte-identical mesh. SPEC.md
section 5 of the clean-room pack put it plainly: "Add a regression test that
renders all five modes and asserts the meshes differ. Had one existed, this
would never have shipped." This is that test.

Run:
    <venv>/bin/python -m pytest polydice/tests/test_parameters_take_effect.py

The venv needs cadquery; no other dependency. The test renders through the
same restricted-exec contract the platform's runner uses, so a parameter that
only works outside the sandbox fails here too.
"""

import hashlib
import math
import os
import sys
import tempfile

import cadquery as cq
import pytest

CART = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(CART, "main.py")

MODES = ["d4", "d6", "d8", "d12", "d20"]

DEFAULTS = {
    "die_size": 20,
    "font_depth": 0.6,
    "font_size": 6,
    "rounding_corner": 0,
    "rounding_edge": 0,
    "fn": 0,
    "dice_gradient": 0,
}

# Every geometry parameter, with two values that must produce different meshes.
# `fn` is tessellation-only, so it is checked on the exported mesh rather than
# on the solid — it legitimately does not change the B-Rep.
PARAM_PAIRS = {
    "die_size": (15, 25),
    "font_depth": (0.2, 1.5),
    "font_size": (3, 9),
    "rounding_corner": (0, 3),
    "rounding_edge": (0, 2),
    "dice_gradient": (0, 1),
    "fn": (0, 64),
}


def _sandbox_globals():
    """The runner's exec environment: restricted builtins, cq and math injected.

    Falls back to real builtins when the platform's commons_sandbox package is
    not importable, so the test still runs in a bare checkout — the point of
    the test is parameter sensitivity, not the sandbox itself.
    """
    try:
        sys.path.insert(
            0,
            "/Users/aldoruizluna/labspace/.stab-clones/y4d-s3/packages/commons-sandbox/src",
        )
        from commons_sandbox import build_sandbox_builtins

        builtins_obj = build_sandbox_builtins("CadQuery scripts")
    except Exception:  # pragma: no cover - environment-dependent
        import builtins as _b

        builtins_obj = _b
    return {
        "__builtins__": builtins_obj,
        "cq": cq,
        "math": math,
        "__file__": SCRIPT,
        "__name__": "__main__",
    }


def render(params, target_part):
    with open(SCRIPT, encoding="utf-8") as fh:
        src = fh.read()
    g = _sandbox_globals()
    g.update(params)
    g["target_part"] = target_part
    exec(src, g)  # noqa: S102 — the platform executes cartridges exactly this way
    result = g.get("result")
    assert result is not None, "the cartridge must assign `result`"
    return result


def mesh_digest(params, target_part):
    """Export to STL and hash it: two renders differ iff their meshes differ."""
    shape = render(params, target_part)
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        path = tmp.name
    try:
        cq.exporters.export(shape, path, "STL")
        with open(path, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()
    finally:
        os.unlink(path)


@pytest.mark.parametrize("mode", MODES)
def test_mode_renders_one_watertight_body(mode):
    shape = render(dict(DEFAULTS), mode)
    solids = shape.solids().size() if hasattr(shape, "solids") else 1
    assert solids == 1, f"{mode} produced {solids} solids, expected exactly 1"
    assert shape.val().isValid(), f"{mode} produced an invalid solid"


def test_all_five_modes_differ():
    """The defect that removed the baseline: five modes, one mesh."""
    digests = {m: mesh_digest(dict(DEFAULTS), m) for m in MODES}
    assert len(set(digests.values())) == len(MODES), (
        "modes must produce five different meshes, got: " + repr(digests)
    )


@pytest.mark.parametrize("param,values", sorted(PARAM_PAIRS.items()))
def test_parameter_changes_the_mesh(param, values):
    """Render at two values of one parameter; the meshes must differ."""
    lo, hi = values
    a = dict(DEFAULTS)
    a[param] = lo
    b = dict(DEFAULTS)
    b[param] = hi
    # d20 has the most faces, so a glyph-related parameter has the most to bite
    # on; die_size and the rounding parameters bite on any die.
    da = mesh_digest(a, "d20")
    db = mesh_digest(b, "d20")
    assert da != db, f"parameter {param!r} did not change the mesh ({lo} vs {hi})"


def test_face_numbering_sums_to_n_plus_one():
    """Opposite faces sum to faces + 1 on the d6, d8, d12 and d20."""
    sys.path.insert(0, CART)
    import main as cartridge

    for kind, n in (("d6", 6), ("d8", 8), ("d12", 12), ("d20", 20)):
        verts = cartridge._vertices(kind)
        faces = cartridge._faces_of(verts)
        assert len(faces) == n, f"{kind} has {len(faces)} faces, expected {n}"
        numbers = cartridge._numbering(kind, faces, verts)
        assert sorted(numbers) == list(range(1, n + 1)), (
            f"{kind} numbering is not 1..{n}: {sorted(numbers)}"
        )
        for i, fi in enumerate(faces):
            for j, fj in enumerate(faces):
                if i < j and cartridge._dot(fi["normal"], fj["normal"]) < -0.999999:
                    assert numbers[i] + numbers[j] == n + 1, (
                        f"{kind}: opposite faces {numbers[i]} and {numbers[j]} "
                        f"sum to {numbers[i] + numbers[j]}, expected {n + 1}"
                    )
