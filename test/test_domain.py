from numpy.testing import assert_almost_equal
import pytest
import openalea.libcaribu.algos as lcal
import openalea.libcaribu.io as lcio


@pytest.fixture
def scene(tmp_path):
    triangle = ((0, 1, 0), (0, 0, 0), (1, 0, 0))
    zenith_light = (100, (0, 0, -1))
    test_opts = lcio.set_opticals(leaf=(0.06, 0.07))
    return lcal.set_scene(tmp_path,
                          canopy=[triangle],
                          lights=[zenith_light],
                          opts=test_opts)


def _set_domain(scene, domain):
    pattern_string = lcio.canestra_pattern(domain)
    s = lcal.set_scene(scene, pattern=pattern_string)
    # update periodic scene
    lcal.periodise(s)
    return s


def test_triangle_inside(scene):
    domain = (-2, -2, 2, 2)
    s = _set_domain(scene, domain)
    res, _, _ = lcal.toric_raycasting(s)

    assert_almost_equal(res['area'][0], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 3)


def test_triangle_outside(scene):

    # just on the right
    domain = (-2, -2, 0, 2)
    s = _set_domain(scene, domain)
    res, _, _ = lcal.toric_raycasting(s)

    assert_almost_equal(res['area'][0], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 3)

    # just on the left
    domain = (2, -2, 4, 2)
    s = _set_domain(scene, domain)
    res, _, _ = lcal.toric_raycasting(s)

    assert_almost_equal(res['area'][0], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 3)

    # further on the left
    domain = (12, -2, 14, 2)
    s = _set_domain(scene, domain)
    res, _, _ = lcal.toric_raycasting(s)

    assert_almost_equal(res['area'][0], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 3)

    # both directions
    domain = (12, 12, 14, 14)
    s = _set_domain(scene, domain)
    res, _, _ = lcal.toric_raycasting(s)

    assert_almost_equal(res['area'][0], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][0], 100, 0)
    assert_almost_equal(res['Ei_inf'][0], 0, 3)


# def test_with_splitting():
#     domain = (-2, -2, 0, 2)
#     s = _set_domain(scene, domain)
#     res, _, _ = lcal.toric_raycasting(s)
#     print res
#
#     assert_almost_equal(res['area'][0], 1, 3)
#     assert_almost_equal(res['Ei_sup'][0], 100, 0)
#     assert_almost_equal(res['Ei_inf'][0], 0, 3)
