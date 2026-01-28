import numpy as np
from numpy.testing import assert_almost_equal
import pytest
import openalea.libcaribu.algos as lcal
import openalea.libcaribu.io as lcio


@pytest.fixture
def degenerated_scene_factory(tmp_path):

    def _degenerated_scene(name):
        unit_triangle = ((0, 0, 0), (np.sqrt(2), 0, 0), (0, np.sqrt(2), 0))
        base_triangle = ((0, 0, 0), (1, 0, 0), (0, 1, 0))
        if name == 'flat_triangle_merged_vertices':
            triangles = [[(0, 0, 0), (1, 0, 0), (1, 0, 0)]]
        elif name == 'flat_triangle_colinear_vertices':
            triangles = [[(0, 0, 0), (1, 0, 0), (0.5, 0, 0)]]
        elif name == 'flat_triangle_too_small':
            triangles = [[(0, 0, 0), (1, 0, 0), (0, 1e-7, 0)]]
        elif name == 'two_triangles_merged':
            triangles = [unit_triangle] * 2
        elif name == 'two_triangles_one_flat':
            flat_triangle = [(10, 0, 0), (11, 0, 0), (11, 0, 0)]
            triangles = [unit_triangle, flat_triangle]
        elif name == 'two_triangles_one_flat_inside_domain':
            flat_triangle = [(0, 1, 0), (1, 0, 0), (1, 0, 0)]
            triangles = [base_triangle, flat_triangle]
        elif name == 'two_triangles_one_flat_outside_domain':
            flat_triangle = [(2, 1, 0), (3, 0, 0), (3, 0, 0)]
            triangles = [base_triangle, flat_triangle]
        else:
            triangles = [unit_triangle]

        zenith_light = (100, (0, 0, -1))
        test_opts = lcio.set_opticals(soil=0.2, leaf=(0.06, 0.04))
        return lcal.set_scene(tmp_path,
                              canopy=triangles,
                              lights=[zenith_light],
                              opts=test_opts)

    return _degenerated_scene


def _set_domain(scene, domain):
    pattern_string = lcio.canestra_pattern(domain)
    s = lcal.set_scene(scene, pattern=pattern_string)
    return s


def test_raycasting_flat_triangle_merged_vertices(degenerated_scene_factory):
    scene = degenerated_scene_factory('flat_triangle_merged_vertices')
    res, _, _ = lcal.raycasting(scene)
    assert_almost_equal(res['area'][0], 0, 3)
    assert np.isnan(res['Ei'][0])
    assert np.isnan(res['Eabs'][0])
    assert np.isnan(res['Ei_sup'][0])
    assert np.isnan(res['Ei_inf'][0])


def test_raycasting_flat_triangle_colinear_vertices(degenerated_scene_factory):
    scene = degenerated_scene_factory('flat_triangle_colinear_vertices')
    res, _, _ = lcal.raycasting(scene)
    assert_almost_equal(res['area'][0], 0, 3)
    assert np.isnan(res['Ei'][0])
    assert np.isnan(res['Eabs'][0])
    assert np.isnan(res['Ei_sup'][0])
    assert np.isnan(res['Ei_inf'][0])


def test_raycasting_flat_triangle_too_small(degenerated_scene_factory):
    scene = degenerated_scene_factory('flat_triangle_too_small')
    res, _, _ = lcal.raycasting(scene)
    assert_almost_equal(res['area'][0], 0, 3)
    assert np.isnan(res['Ei'][0])
    assert np.isnan(res['Eabs'][0])
    assert np.isnan(res['Ei_sup'][0])
    assert np.isnan(res['Ei_inf'][0])


def test_two_triangles_merged(degenerated_scene_factory):
    scene = degenerated_scene_factory('two_triangles_merged')

    # raycasting
    res, _, _ = lcal.raycasting(scene)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei'][1], 0, 0)

    # radiosity
    res, _, _ = lcal.radiosity(scene)
    assert_almost_equal(res['Ei'][0], 100, 0)
    assert_almost_equal(res['Ei'][1], 0, 0)


def test_raycasting_two_triangles_one_flat(degenerated_scene_factory):
    scene = degenerated_scene_factory('two_triangles_one_flat')
    unit, flat = 0, 1
    res, _, _ = lcal.raycasting(scene)
    assert_almost_equal(res['area'][unit], 1, 3)
    assert_almost_equal(res['Ei'][unit], 100, 0)

    assert_almost_equal(res['area'][flat], 0, 3)
    assert np.isnan(res['Ei'][flat])


def test_toric_raycasting_two_triangles_one_flat_inside_domain(degenerated_scene_factory):
    scene = degenerated_scene_factory('two_triangles_one_flat_inside_domain')
    scene = _set_domain(scene, (-2, -2, 2, 2))
    base, flat = 0, 1
    res, _, _ = lcal.toric_raycasting(scene)

    assert_almost_equal(res['area'][base], 0.5, 3)
    assert_almost_equal(res['Ei'][base], 100, 0)

    assert_almost_equal(res['area'][flat], 0, 3)
    assert np.isnan(res['Ei'][flat])


def test_toric_raycasting_two_triangles_one_flat_outside_domain(degenerated_scene_factory):
    scene = degenerated_scene_factory('two_triangles_one_flat_outside_domain')
    scene = _set_domain(scene, (-2, -2, 2, 2))
    base, flat = 0, 1
    res, _, _ = lcal.toric_raycasting(scene)

    assert_almost_equal(res['area'][base], 0.5, 3)
    assert_almost_equal(res['Ei'][base], 100, 0)

    assert_almost_equal(res['area'][flat], 0, 3)
    assert np.isnan(res['Ei'][flat])

def test_radiosity_two_triangles_one_flat_outside_domain(degenerated_scene_factory):
    scene = degenerated_scene_factory('two_triangles_one_flat_outside_domain')
    base, flat = 0, 1
    res, _, _ = lcal.radiosity(scene)

    assert_almost_equal(res['area'][base], 0.5, 3)
    assert_almost_equal(res['Ei'][base], 100, 0)

    assert_almost_equal(res['area'][flat], 0, 3)
    assert np.isnan(res['Ei'][flat])


def test_mixed_radiosity_two_triangles_one_flat_outside_domain(degenerated_scene_factory):
    scene = degenerated_scene_factory('two_triangles_one_flat_outside_domain')
    base, flat = 0, 1
    scene = _set_domain(scene, (-2, -2, 2, 2))
    res, _, _ = lcal.mixed_radiosity(scene, layers=2, height=1, sd=1)

    assert_almost_equal(res['area'][base], 0.5, 3)
    assert_almost_equal(res['Ei'][base], 100, 0)

    assert_almost_equal(res['area'][flat], 0, 3)
    assert np.isnan(res['Ei'][flat])