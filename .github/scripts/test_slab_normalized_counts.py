"""Count semantics and the production normalizer -> sandbox -> STL regression.

The integration test uses the real Yantra source selected by YANTRA4D_ROOT.
Its absence is an explicit skip, not a simulated normalizer or export success.
Run with the existing shared geometry environment, without installing packages.
"""
import ast
import importlib.util
import json
import math
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COUNTS = ('grip_count', 'dpad_count', 'face_count', 'stick_count',
          'system_count', 'rear_count', 'cell_count', 'bumper_count', 'trigger_count')


def count_function():
    tree = ast.parse((ROOT / 'slab-handheld/family.py').read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'count_value')
    namespace = {'math': math}
    exec(compile(ast.Module(body=[function], type_ignores=[]), '<count-value>', 'exec'), namespace)
    return namespace['count_value']


@pytest.mark.parametrize('value', [0, 0.0, 2, 2.0, 6.0])
def test_integral_api_numbers_keep_count_semantics(value):
    result = count_function()(value, 'bumper_count')
    assert type(result) is int and result == value


@pytest.mark.parametrize('value', [-1, -1.0, .5, 2.5, float('nan'),
                                   float('inf'), -float('inf'), '2', None])
def test_unsupported_counts_are_rejected_instead_of_truncated(value):
    with pytest.raises(ValueError, match='finite non-negative integer'):
        count_function()(value, 'bumper_count')


def test_every_count_is_validated_before_any_construction():
    tree = ast.parse((ROOT / 'slab-handheld/family.py').read_text())
    assignments = {n.targets[0].id: n.value for n in tree.body
                   if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
    for name in COUNTS:
        call = assignments[name]
        assert isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
        assert call.func.id == 'count_value'
        assert call.args[1].value == name


def test_real_api_normalizer_to_sandbox_native_export(tmp_path):
    selected = os.environ.get('YANTRA4D_ROOT')
    if not selected:
        pytest.skip('set YANTRA4D_ROOT to run the real API/native integration')
    pytest.importorskip('cadquery')
    trimesh = pytest.importorskip('trimesh')
    yantra = Path(selected).resolve()
    path = yantra / 'scripts/dev/render_commons_presets.py'
    assert path.is_file(), 'YANTRA4D_ROOT must select the actual native archive producer'
    spec = importlib.util.spec_from_file_location('slab_real_archive_regression', path)
    archive = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archive)
    manifest = json.loads((ROOT / 'slab-handheld/project.json').read_text())
    preset = next(p for p in manifest['presets'] if p['slug'] == 'asus-rog-ally-rc71l')
    resolved = archive.normalize_parameters(manifest, preset['values'])
    assert type(resolved['bumper_count']) is float and resolved['bumper_count'] == 2.0
    assert type(resolved['rear_count']) is float and resolved['rear_count'] == 2.0
    helpers = archive.native_helpers()
    helpers.PROJECTS_DIR = ROOT
    stl = tmp_path / 'front-shell.stl'
    ok, error = helpers.run_cadquery_part(ROOT / 'slab-handheld/main.py', stl,
                                        resolved, 'front_shell',
                                        runtime_env=archive.native_environment(ROOT))
    assert ok, error
    mesh = trimesh.load(stl, force='mesh')
    assert mesh.is_watertight and mesh.volume > 0 and len(mesh.faces) > 0

    # Fractional sliders are not rounded by the API. The source must reject
    # these after normalization too, rather than quietly changing the count.
    bad = archive.normalize_parameters(manifest, {**preset['values'], 'rear_count': 1.5})
    assert bad['rear_count'] == 1.5
    ok, error = helpers.run_cadquery_part(ROOT / 'slab-handheld/main.py', tmp_path / 'bad.stl',
                                        bad, 'front_shell',
                                        runtime_env=archive.native_environment(ROOT))
    assert not ok and 'rear_count must be a finite non-negative integer' in error
