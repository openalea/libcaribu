import numpy as np
from numpy.testing import assert_almost_equal
import pytest
import openalea.libcaribu.algos as lcal
import openalea.libcaribu.io as lcio


@pytest.fixture
def single_triangle_scene(tmp_path):
    unit_triangle = ((0, 0, 0), (np.sqrt(2), 0, 0), (0, np.sqrt(2), 0))
    zenith_light = (100, (0, 0, -1))
    test_opts = lcio.set_opticals(leaf=(0.06, 0.04))
    return lcal.set_scene(tmp_path,
                          canopy=[unit_triangle],
                          lights=[zenith_light],
                          opts=test_opts)


def _reverse_triangles(scene):
    triangles, _ = lcio.read_can(scene / 'scene.can')
    triangles = [list(reversed(points)) for points in triangles]
    return lcal.set_scene(scene, canopy=triangles)


def test_raycasting_translucent_triangle(single_triangle_scene):
    s = single_triangle_scene
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 0)


def test_raycasting_flipped_translucent_triangle(single_triangle_scene):
    s = _reverse_triangles(single_triangle_scene)
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 0, 0)


def test_raycasting_opaque_triangle(single_triangle_scene):
    scene = single_triangle_scene
    triangles, _ = lcio.read_can(scene / 'scene.can')
    s = lcal.set_scene(scene, lcio.canestra_scene(triangles, leaf=False))
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 0)
    # flip
    s = _reverse_triangles(s)
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 0, 0)

def test_reflectance_equals_transmittance(single_triangle_scene):
    opts = lcio.set_opticals(leaf=(0.05, 0.05))
    s = lcal.set_scene(single_triangle_scene, opts=opts)
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], -1, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)


def test_product_equality(single_triangle_scene):
    # reflectance_product == transmittance_product
    opts = lcio.set_opticals(leaf=(0.05, 0.01, 0.01, 0.05))
    s = lcal.set_scene(single_triangle_scene, opts=opts)
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 94, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], -1, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)

