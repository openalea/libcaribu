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


@pytest.fixture
def four_superposed_triangles_scene(tmp_path):
    # a two time two stack of sticked triangles
    dz = 1e-5
    z1 = 0.25
    z2 = 0.75
    lower_triangle_layer1 = [(0, 0, z1), (np.sqrt(2), 0, z1), (0, np.sqrt(2), z1)]
    upper_triangle_layer1 = [(0, 0, z1 + dz), (np.sqrt(2), 0, z1 + dz), (0, np.sqrt(2), z1 + dz)]
    lower_triangle_layer2 = [(0, 0, z2), (np.sqrt(2), 0, z2), (0, np.sqrt(2), z2)]
    upper_triangle_layer2 = [(0, 0, z2 + dz), (np.sqrt(2), 0, z2 + dz), (0, np.sqrt(2), z2 + dz)]
    zenith_light = (100, (0, 0, -1))
    test_opts = lcio.set_opticals(soil=0.2, stem=0.1, leaf=(0.06, 0.04))
    return lcal.set_scene(tmp_path,
                          canopy=[lower_triangle_layer1, upper_triangle_layer1,
                                  lower_triangle_layer2, upper_triangle_layer2],
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


def _translate_upper(scene, dx, dy):
    lower, upper = 0, 1
    triangles, labels = lcio.read_can(scene / 'scene.can')
    triangles = [
        triangles[lower],
        [(x + dx, y + dy, z) for x,y,z in triangles[upper]]
    ]
    return lcal.set_scene(scene, canopy=lcio.can_string(triangles, labels))

def _set_domain_and_soil(scene, domain):
    pattern_string = lcio.canestra_pattern(domain)
    s = lcal.set_scene(scene, pattern=pattern_string, soil=1)
    return s


def test_raycasting_full_occlusion(two_superposed_triangles_scene):
    s = two_superposed_triangles_scene
    lower, upper = 0, 1
    res, _, _ = lcal.raycasting(s)

    assert_almost_equal(res['area'][lower], 1, 3)
    assert_almost_equal(res['Eabs'][lower], 0, 0)
    assert_almost_equal(res['Ei'][lower], 0, 0)

    assert_almost_equal(res['area'][upper], 1, 3)
    assert_almost_equal(res['Eabs'][upper], 70, 0)
    assert_almost_equal(res['Ei'][upper], 100, 0)


def test_raycasting_relieved_occlusion(two_superposed_triangles_scene):
    s = two_superposed_triangles_scene
    s = _translate_upper(s, 10, 10)
    lower, upper = 0, 1
    res, _, _ = lcal.raycasting(s)

    assert_almost_equal(res['area'][lower], 1, 3)
    assert_almost_equal(res['Eabs'][lower], 70, 0)
    assert_almost_equal(res['Ei'][lower], 100, 0)

    assert_almost_equal(res['area'][upper], 1, 3)
    assert_almost_equal(res['Eabs'][upper], 70, 0)
    assert_almost_equal(res['Ei'][upper], 100, 0)


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


def test_all_radiosity_four_superposed_triangles_scene(four_superposed_triangles_scene):
    s = four_superposed_triangles_scene
    lower1, upper1, lower2, upper2 = list(range(4))

    # pure radiosity
    res, _, _ = lcal.radiosity(s)
    assert_almost_equal(res['Ei'][upper2], 100, 0)
    assert_almost_equal(res['Ei'][lower2], 4, 0)
    assert_almost_equal(res['Ei'][upper1], 0.1, 1)
    assert_almost_equal(res['Ei'][lower1], 0, 0)

    # direct + pure layer, dense canopy
    domain = (0, 0, np.sqrt(2), np.sqrt(2))
    s = _set_domain_and_soil(s, domain)
    res, _, _ = lcal.mixed_radiosity(s, layers=2, height=1, sd=0, soil=True)
    assert_almost_equal(res['Ei'][upper2], 103, 0)
    assert_almost_equal(res['Ei'][lower2], 4, 0)
    assert_almost_equal(res['Ei'][upper1], 4, 0)
    assert_almost_equal(res['Ei'][lower1], 4, 0)

    # direct + mixed radiosity, dense canopy (20% soil reflectance)
    domain = (0, 0, np.sqrt(2), np.sqrt(2))
    s = _set_domain_and_soil(s, domain)
    res, _, _ = lcal.mixed_radiosity(s, layers=2, height=1, sd=0.1, soil=True)
    assert_almost_equal(res['Ei'][upper2], 101, 0)
    assert_almost_equal(res['Ei'][lower2], 7, 0)
    assert_almost_equal(res['Ei'][upper1], 2, 0)
    assert_almost_equal(res['Ei'][lower1], 3, 0)

    # direct + pure layer, sparse canopy (20% soil reflectance)
    domain = (-10, -10, 10, 10)
    s = _set_domain_and_soil(s, domain)
    res, _, _ = lcal.mixed_radiosity(s, layers=2, height=1, sd=0, soil=True)
    assert_almost_equal(res['Ei'][upper2], 120, 0)
    assert_almost_equal(res['Ei'][lower2], 20, 0)
    assert_almost_equal(res['Ei'][upper1], 20, 0)
    assert_almost_equal(res['Ei'][lower1], 20, 0)

    # direct + mixed radiosity, sparse canopy
    domain = (-10, -10, 10, 10)
    s = _set_domain_and_soil(s, domain)
    res, _, _ = lcal.mixed_radiosity(s, layers=2, height=1, sd=0.1, soil=True)
    assert_almost_equal(res['Ei'][upper2], 101, 0)
    assert_almost_equal(res['Ei'][lower2], 24, 0)
    assert_almost_equal(res['Ei'][upper1], 1, 0)
    assert_almost_equal(res['Ei'][lower1], 20, 0)
