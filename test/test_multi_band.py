import numpy as np
from numpy.testing import assert_almost_equal
import pytest
import openalea.libcaribu.algos as lcal
import openalea.libcaribu.io as lcio


@pytest.fixture
def two_superposed_triangles_scene(tmp_path):
    lower_triangle = ((0, 0, 0), (np.sqrt(2), 0, 0), (0, np.sqrt(2), 0))
    upper_triangle = ((0, 0, 1e-5), (np.sqrt(2), 0, 1e-5), (0, np.sqrt(2), 1e-5))
    zenith_light = (100, (0, 0, -1))
    test_opts = [lcio.set_opticals(stem=0.1),   # band1
                 lcio.set_opticals(stem=0.2)]   # band2
    return lcal.set_scene(tmp_path,
                          canopy=[lower_triangle, upper_triangle],
                          lights=[zenith_light],
                          opts=test_opts)


@pytest.fixture
def two_triangles_scene(tmp_path):
    lower_triangle = ((0, 0, 0), (np.sqrt(2), 0, 0), (0, np.sqrt(2), 0))
    upper_triangle = ((0, 0, 0), (-np.sqrt(2), 0, 0), (0, -np.sqrt(2), 0))
    zenith_light = (100, (0, 0, -1))
    test_opts = [lcio.set_opticals(stem=0.1),   # band1
                 lcio.set_opticals(stem=0.2)]   # band2
    return lcal.set_scene(tmp_path,
                          canopy=[lower_triangle, upper_triangle],
                          lights=[zenith_light],
                          opts=test_opts)


@pytest.fixture
def three_superposed_triangles_scene(tmp_path):
    lower_triangle = ((0, 0, 0), (np.sqrt(2), 0, 0), (0, np.sqrt(2), 0))
    middle_triangle = ((0, 0, 0.5), (np.sqrt(2), 0, 0.5), (0, np.sqrt(2), 0.5))
    upper_triangle = ((0, 0, 1), (np.sqrt(2), 0, 1), (0, np.sqrt(2), 1))
    zenith_light = (100, (0, 0, -1))
    test_opts = [lcio.set_opticals(stem=0.1, soil=0.2),   # band1
                 lcio.set_opticals(stem=0.2, soil=0.1)]   # band2
    return lcal.set_scene(tmp_path,
                          canopy=[lower_triangle, middle_triangle, upper_triangle],
                          lights=[zenith_light],
                          opts=test_opts)


def _set_opaque(scene):
    triangles, _ = lcio.read_can(scene / 'scene.can')
    lcal.set_scene(scene, lcio.canestra_scene(triangles, leaf=False))
    return lcal.set_scene(scene)


def _set_domain(scene, domain):
    pattern_string = lcio.canestra_pattern(domain)
    s = lcal.set_scene(scene, pattern=pattern_string)
    return s


def test_raycasting_two_triangles_no_occlusion(two_triangles_scene):
    s = two_triangles_scene
    s = _set_opaque(s)
    lower, upper = 0, 1
    res = lcal.caribu(s)

    for band in ("band1", "band2"):
        r, _, _ = res[band]
        assert_almost_equal(r['area'][lower], 1, 3)
        assert_almost_equal(r['Ei'][lower], 100, 0)

        assert_almost_equal(r['area'][upper], 1, 3)
        assert_almost_equal(r['Ei'][upper], 100, 0)

        if band == "band1":
            assert_almost_equal(r['Eabs'][upper], 90, 0)
        else:
            assert_almost_equal(r['Eabs'][upper], 80, 0)


def test_radiosity_two_triangles_full_occlusion(two_superposed_triangles_scene):
    s = two_superposed_triangles_scene
    s = _set_opaque(s)
    lower, upper = 0, 1
    x_res = lcal.caribu(s, direct_only=False, d_radiosity=-1)


    for band in ("band1", "band2"):
        res, _, _ = x_res[band]
        assert_almost_equal(res['area'][lower], 1, 3)
        assert_almost_equal(res['Ei_sup'][lower], 0, 0)
        assert_almost_equal(res['Ei_inf'][lower], -1, 3)

        assert_almost_equal(res['area'][upper], 1, 3)
        assert_almost_equal(res['Ei_sup'][upper], 100, 0)
        assert_almost_equal(res['Ei_inf'][upper], -1, 3)
        if band == "band1":
            assert_almost_equal(res['Eabs'][upper], 90, 0)
        else:
            assert_almost_equal(res['Eabs'][upper], 80, 0)

            
def test_mixed_radiosity_three_triangles_full_occlusion(three_superposed_triangles_scene):

    s = three_superposed_triangles_scene
    domain = (0, 0, 2, 2)
    s = _set_opaque(s)
    s = _set_domain(s, domain)
    lower, middle, upper = 0, 1, 2
    x_res = lcal.caribu(s, direct_only=False, d_radiosity=0.6, layers=3, height=1.2)

    for band in ("band1", "band2"):
        res, _, _ = x_res[band]
        assert_almost_equal(res['area'][0], 1, 3)
        # assert_almost_equal(res['Ei_sup'][0], -1, 0)
        # assert_almost_equal(res['Ei_inf'][0], -1, 3)

        assert_almost_equal(res['area'][2], 1, 3)
        # assert_almost_equal(res['Ei_sup'][2], -1, 0)
        # assert_almost_equal(res['Ei_inf'][2], -1, 3)
        # TODO radiosity result