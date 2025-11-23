from math import sqrt
from numpy.testing import assert_almost_equal
import pytest
import openalea.libcaribu.algos as lcal
import openalea.libcaribu.io as lcio

@pytest.fixture
def single_triangle_scene(tmp_path):
    return lcal.set_default_scene(tmp_path)


@pytest.fixture
def flipped_single_triangle_scene(tmp_path):
    scene = lcal.set_default_scene(tmp_path)
    points = [(0, 0, 0), (sqrt(2), 0, 0), (0, sqrt(2), 0)]
    triangles = [list(reversed(points))]
    scene = lcal.set_scene(scene, canopy=lcio.canestra_scene(triangles))
    return scene


def test_raycasting_translucent_triangle(single_triangle_scene):

    s = single_triangle_scene
    opticals = lcio.set_opticals(leaf=(0.06, 0.04))
    lcal.set_scene(s, opts=lcio.canestra_opt(opticals))
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 0)


def test_raycasting_flipped_translucent_triangle(flipped_single_triangle_scene):

    s = flipped_single_triangle_scene
    opticals = lcio.set_opticals(leaf=(0.06, 0.04))
    lcal.set_scene(s, opts=lcio.canestra_opt(opticals))
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei_inf'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 0, 0)


def test_reflectance_equals_transmittance(single_triangle_scene):
    s = single_triangle_scene
    opticals = lcio.set_opticals(leaf=(0.05, 0.05))
    lcal.set_scene(s, opts=lcio.canestra_opt(opticals))
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], -1, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)


def test_product_equality(single_triangle_scene):
    s = single_triangle_scene
    # reflectance_product == transmittance_product
    opticals = lcio.set_opticals(leaf=(0.05, 0.01, 0.01, 0.05))
    lcal.set_scene(s, opts=lcio.canestra_opt(opticals))
    res, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 94, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], -1, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)

