import numpy as np
from numpy.testing import assert_almost_equal
import pytest
import openalea.libcaribu.algos as lcal
import openalea.libcaribu.io as lcio


@pytest.fixture
def horizontal_triangle_scene(tmp_path):
    unit_triangle = ((0, 0, 0), (np.sqrt(2), 0, 0), (0, np.sqrt(2), 0))
    zenith_light = (100, (0, 0, -1))
    test_opts = lcio.set_opticals(leaf=(0.06, 0.04))
    return lcal.set_scene(tmp_path,
                          canopy=[unit_triangle],
                          lights=[zenith_light],
                          opts=test_opts)


@pytest.fixture
def vertical_triangle_scene(tmp_path):
    unit_triangle = [(0, 0, 0), (0, np.sqrt(2), 0), (0, 0, np.sqrt(2))]
    zenith_light = (100, (0, 0, -1))
    test_opts = lcio.set_opticals(leaf=(0.06, 0.04))
    return lcal.set_scene(tmp_path,
                          canopy=[unit_triangle],
                          lights=[zenith_light],
                          opts=test_opts)


@pytest.fixture
def inclined_triangle_scene(tmp_path):
    proj = np.cos(np.radians(45))
    unit_triangle = [(0, 0, 0), (0, np.sqrt(2), 0), (-np.sqrt(2) * proj, 0, proj * np.sqrt(2))]
    zenith_light = (100, (0, 0, -1))
    test_opts = lcio.set_opticals(leaf=(0.06, 0.04))
    return lcal.set_scene(tmp_path,
                          canopy=[unit_triangle],
                          lights=[zenith_light],
                          opts=test_opts)


def _set_lights(scene, lights):
    return lcal.set_scene(scene, lights=lights)


def _set_domain(scene, domain):
    pattern_string = lcio.canestra_pattern(domain)
    s = lcal.set_scene(scene, pattern=pattern_string)
    return s


def test_vertical_light(horizontal_triangle_scene):
    s = horizontal_triangle_scene

    # vertical light no intensity
    s = _set_lights(s, [(0, (0, 0, -1))])
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei'][0], 0, 0)

    # vertical light full intensity
    s = _set_lights(s, [(100, (0, 0, -1))])
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei'][0], 100, 0)


def test_vertical_scene(vertical_triangle_scene):
    s = vertical_triangle_scene

    # zenith light
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei'][0], 0, 0)

    # horizontal light : full intensity cannot be specified
    s = _set_lights(s, [(100, (-1, 0, 0))])
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei'][0], 0, 0)


def test_horizontal_light(horizontal_triangle_scene):
    s = horizontal_triangle_scene

    # horizontal light full intensity
    s = _set_lights(s, [(100, (-1, 0, 0))])
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei'][0], 0, 0)

    # horizontal light no intensity
    s = _set_lights(s, [(0, (-1, 0, 0))])
    res, _, _ = lcal.raycasting(s)

    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei'][0], 0, 0)

    # horizontal light full intensity, infinite canopy
    s = _set_lights(s, [(100, (-1, 0, 0))])
    domain = (-2, -2, 2, 2)
    s = _set_domain(s, domain)
    res, _, _ = lcal.toric_raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei'][0], 0, 0)


def test_diagonal_light(horizontal_triangle_scene):
    s = horizontal_triangle_scene

    # diagonal light full intensity perpendicular to the source
    emission = 100
    horizontal_irradiance = emission * np.cos(np.radians(45))
    s = _set_lights(s, [(horizontal_irradiance, (-1, 0, -1))])
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 3)
    assert_almost_equal(res['Ei'][0], horizontal_irradiance, 0)


def test_diagonal_light_inclined(inclined_triangle_scene):
    s = inclined_triangle_scene

    # full intensity perpendicular to the source, inclined triangle
    emission = 100
    horizontal_irradiance = emission * np.cos(np.radians(45))
    s = _set_lights(s, [(horizontal_irradiance, (-1, 0, -1))])
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 0)
    assert_almost_equal(res['Ei'][0], 100, 0)

    # full intensity on horizontal surface, inclined triangle
    s = _set_lights(s, [(100, (-1, 0, -1))])
    res, _, _ = lcal.raycasting(s)
    assert_almost_equal(res['area'][0], 1, 0)
    assert_almost_equal(res['Ei'][0], 141, 0)

