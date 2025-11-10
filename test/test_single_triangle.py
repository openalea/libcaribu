from math import sqrt
from numpy.testing import assert_almost_equal
import pytest
import openalea.libcaribu.io as lcio
import openalea.libcaribu.tools as lc


def raycasting(scene_path):
    args = ["-M", "scene.can",
            "-l", "scene.light",
            "-p", "scene.opt",
            "-A",
            "-1"]
    lc.run_canestrad(scene_path, args)
    resfile = scene_path / "Etri.vec0"
    return lcio.read_res(resfile)


@pytest.fixture
def single_triangle_scene(tmp_path):
    points = [(0, 0, 0), (sqrt(2), 0, 0), (0, sqrt(2), 0)]
    lights = [(100, (0, 0, -1))]
    triangles = [points]
    scene_file = tmp_path / 'scene.can'
    scene_file.write_text(lcio.canestra_scene(triangles))
    light_file = tmp_path / 'scene.light'
    light_file.write_text(lcio.canestra_light(lights))
    return tmp_path


@pytest.fixture
def flipped_single_triangle_scene(tmp_path):
    points = [(0, 0, 0), (sqrt(2), 0, 0), (0, sqrt(2), 0)]
    lights = [(100, (0, 0, -1))]
    triangles = [reversed(points)]
    scene_file = tmp_path / 'scene.can'
    scene_file.write_text(lcio.canestra_scene(triangles))
    light_file = tmp_path / 'scene.light'
    light_file.write_text(lcio.canestra_light(lights))
    return tmp_path


def test_raycasting_translucent_triangle(single_triangle_scene):

    s = single_triangle_scene
    opt_file = s / 'scene.opt'
    opticals = lcio.optical_properties(leaf=(0.06, 0.04))
    opt_file.write_text(lcio.canestra_opt(opticals))

    res = raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 0)


def test_raycasting_flipped_translucent_triangle(flipped_single_triangle_scene):

    s = flipped_single_triangle_scene
    opt_file = s / 'scene.opt'
    opticals = lcio.optical_properties(leaf=(0.06, 0.04))
    opt_file.write_text(lcio.canestra_opt(opticals))

    res = raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei_inf'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 0, 0)


def test_reflectance_equals_transmittance(single_triangle_scene):
    s = single_triangle_scene
    opt_file = s / 'scene.opt'
    opticals = lcio.optical_properties(leaf=(0.05, 0.05))
    opt_file.write_text(lcio.canestra_opt(opticals))
    res = raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei_sup'][0], -1, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)


def test_product_equality(single_triangle_scene):
    s = single_triangle_scene
    opt_file = s / 'scene.opt'
    # reflectance_product == transmittance_product
    opticals = lcio.optical_properties(leaf=(0.05, 0.01, 0.01, 0.05))
    opt_file.write_text(lcio.canestra_opt(opticals))
    res = raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 94, 0)
    assert_almost_equal(res['Ei_sup'][0], -1, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)

