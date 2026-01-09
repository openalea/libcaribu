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
    test_opts = lcio.set_opticals(stem=0.1, leaf=(0.1, 0.2))
    return lcal.set_scene(tmp_path,
                          canopy=[lower_triangle, upper_triangle],
                          lights=[zenith_light],
                          opts=test_opts)


def _reverse_upper(scene):
    lower, upper = 0, 1
    triangles, labels = lcio.read_can(scene / 'scene.can')
    triangles = [
        triangles[lower],
        list(reversed(triangles[upper]))
    ]
    return lcal.set_scene(scene, canopy=lcio.can_string(triangles, labels))


def _reverse_lower(scene):
    lower, upper = 0, 1
    triangles, labels = lcio.read_can(scene / 'scene.can')
    triangles = [
        list(reversed(triangles[lower])),
        triangles[upper]
    ]
    return lcal.set_scene(scene, canopy=lcio.can_string(triangles, labels))


def _set_opaque(scene, lower=True, upper=True):
    triangles, _ = lcio.read_can(scene / 'scene.can')
    lcal.set_scene(scene, lcio.canestra_scene(triangles, leaf=[not lower, not upper]))
    return lcal.set_scene(scene)


def test_radiosity_translucent_flip(two_superposed_triangles_scene):
    s = two_superposed_triangles_scene
    lower, upper = 0, 1

    # upper / lower pointing facesup toward source
    res, _, _ = lcal.radiosity(s)
    assert_almost_equal(res['area'][upper], 1, 3)
    assert_almost_equal(res['Ei'][upper], 102, 0)
    assert_almost_equal(res['Eabs'][upper], 71, 0)
    assert_almost_equal(res['Ei_sup'][upper], 100, 0)
    assert_almost_equal(res['Ei_inf'][upper], 2, 0)

    assert_almost_equal(res['area'][lower], 1, 3)
    assert_almost_equal(res['Ei'][lower], 20, 0)
    assert_almost_equal(res['Eabs'][lower], 14, 0)
    assert_almost_equal(res['Ei_sup'][lower], 20, 0)
    assert_almost_equal(res['Ei_inf'][lower], 0, 0)

    # flip upper
    s = _reverse_upper(s)
    res, _, _ = lcal.radiosity(s)
    assert_almost_equal(res['area'][upper], 1, 3)
    assert_almost_equal(res['Ei'][upper], 102, 0)
    assert_almost_equal(res['Eabs'][upper], 71, 0)
    assert_almost_equal(res['Ei_sup'][upper], 2, 0)
    assert_almost_equal(res['Ei_inf'][upper], 100, 0)

    assert_almost_equal(res['area'][lower], 1, 3)
    assert_almost_equal(res['Ei'][lower], 20, 0)
    assert_almost_equal(res['Eabs'][lower], 14, 0)
    assert_almost_equal(res['Ei_sup'][lower], 20, 0)
    assert_almost_equal(res['Ei_inf'][lower], 0, 0)

    # flip upper and lower
    s = _reverse_lower(s)
    res, _, _ = lcal.radiosity(s)
    assert_almost_equal(res['area'][upper], 1, 3)
    assert_almost_equal(res['Ei'][upper], 102, 0)
    assert_almost_equal(res['Eabs'][upper], 71, 0)
    assert_almost_equal(res['Ei_sup'][upper], 2, 0)
    assert_almost_equal(res['Ei_inf'][upper], 100, 0)

    assert_almost_equal(res['area'][lower], 1, 3)
    assert_almost_equal(res['Ei'][lower], 20, 0)
    assert_almost_equal(res['Eabs'][lower], 14, 0)
    assert_almost_equal(res['Ei_sup'][lower], 0, 0)
    assert_almost_equal(res['Ei_inf'][lower], 20, 0)


def test_radiosity_full_occlusion(two_superposed_triangles_scene):
    s = two_superposed_triangles_scene
    lower, upper = 0, 1

    # vertical light, opaque material
    s = _set_opaque(s)
    res, _, _ = lcal.radiosity(s)

    assert_almost_equal(res['area'][lower], 1, 3)
    assert_almost_equal(res['Ei'][lower], 0, 0)

    assert_almost_equal(res['area'][upper], 1, 3)
    assert_almost_equal(res['Ei'][upper], 100, 0)

    # vertical light, translucent material of upper triangle
    s = _set_opaque(s, lower=True, upper=False)
    res, _, _ = lcal.radiosity(s)

    assert_almost_equal(res['area'][lower], 1, 3)
    assert_almost_equal(res['Ei'][lower], 20, 0)

    assert_almost_equal(res['area'][upper], 1, 3)
    assert_almost_equal(res['Ei'][upper], 102, 0)
