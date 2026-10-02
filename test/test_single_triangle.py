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
    triangles, labels = lcio.read_can(scene / 'scene.can')
    triangles = [list(reversed(points)) for points in triangles]
    return lcal.set_scene(scene, canopy=lcio.can_string(triangles, labels))


def _set_translucent(scene, material):
    opts = lcio.set_opticals(leaf=material)
    triangles, _ = lcio.read_can(scene / 'scene.can')
    lcal.set_scene(scene, lcio.canestra_scene(triangles, leaf=True))
    return lcal.set_scene(scene, opts=opts)


def _set_opaque(scene, material):
    opts = lcio.set_opticals(stem=material)
    triangles, _ = lcio.read_can(scene / 'scene.can')
    lcal.set_scene(scene, lcio.canestra_scene(triangles, leaf=False))
    return lcal.set_scene(scene, opts=opts)


def test_raycasting_translucent_triangle(single_triangle_scene):
    s = single_triangle_scene
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 0)


def test_raycasting_flipped_translucent_triangle(single_triangle_scene):
    s = _reverse_triangles(single_triangle_scene)
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 0, 0)


def test_raycasting_opaque_triangle(single_triangle_scene):
    s = _set_opaque(single_triangle_scene, 0.1)
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 0)
    # flip
    s = _reverse_triangles(s)
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)


def test_reflectance_equals_transmittance(single_triangle_scene):
    s = _set_translucent(single_triangle_scene, (0.05, 0.05))
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 90, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], -1, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)


def test_product_equality(single_triangle_scene):
    # reflectance_product == transmittance_product
    s = _set_translucent(single_triangle_scene, (0.05, 0.01, 0.01, 0.05))
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Eabs'][0], 94, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei_sup'][0], -1, 0)
    assert_almost_equal(res['Ei_inf'][0], -1, 0)


def test_special_translucent(single_triangle_scene):
    # full reflectance, mirror
    s = _set_translucent(single_triangle_scene, (1., 0.))
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 3)
    assert_almost_equal(res['Eabs'][0], 0, 3)

    # semi reflectance
    s = _set_translucent(single_triangle_scene, (0.5, 0.))
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 3)
    assert_almost_equal(res['Eabs'][0], 50, 0)


def test_asymmetric_material(single_triangle_scene):
    s = _set_translucent(single_triangle_scene, (0.1, 0., 0.2, 0.))
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 0)
    assert_almost_equal(res['Eabs'][0], 90, 0)

    # flip
    s = _reverse_triangles(s)
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei_sup'][0], 0, 0)
    assert_almost_equal(res['Ei_inf'][0], 100, 0)
    assert_almost_equal(res['Eabs'][0], 80, 0)