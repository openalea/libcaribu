import numpy as np
from numpy.testing import assert_almost_equal
import pytest
import openalea.libcaribu.algos as lcal
import openalea.libcaribu.io as lcio


@pytest.fixture
def box_scene(tmp_path):
    # a closed tetrahedron
    xz_face = [(0, 0, 0), (1, 0, 0), (0, 0, 1)]
    yz_face = [(0, 0, 0), (0, 0, 1), (0, 1, 0)]
    xy_face = [(0, 0, 0), (0, 1, 0), (1, 0, 0)]
    xyz_face = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    triangles = [xz_face, yz_face, xy_face, xyz_face]
    zenith_light = (100, (0, 0, -1))
    # no transmittance
    test_opts = lcio.set_opticals(stem=0.1, leaf=(0.1, 0.))
    return lcal.set_scene(tmp_path,
                          canopy=triangles,
                          lights=[zenith_light],
                          opts=test_opts)


def _set_opaque(scene):
    triangles, _ = lcio.read_can(scene / 'scene.can')
    lcal.set_scene(scene, lcio.canestra_scene(triangles, leaf=False))
    return lcal.set_scene(scene)


def test_raycasting_closed_box(box_scene):
    s = box_scene
    res, _, _ = lcal.raycasting(s)

    assert_almost_equal(res['area'][0], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][0], 0, 3)
    assert_almost_equal(res['Ei_inf'][0], 0, 3)
    assert_almost_equal(res['Eabs'][0], 0, 3)

    assert_almost_equal(res['area'][1], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][1], 0, 3)
    assert_almost_equal(res['Ei_inf'][1], 0, 3)
    assert_almost_equal(res['Eabs'][1], 0, 3)

    assert_almost_equal(res['area'][2], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][2], 0, 3)
    assert_almost_equal(res['Ei_inf'][2], 0, 0)
    assert_almost_equal(res['Eabs'][2], 0, 0)

    assert_almost_equal(res['area'][3], 0.866, 3)  # TODO
    assert_almost_equal(res['Ei_sup'][3], 57.6, 0)
    assert_almost_equal(res['Ei_inf'][3], 0, 3)
    assert_almost_equal(res['Eabs'][3], 57.6 * 0.9, 0)


def test_raycasting_opaque_box(box_scene):
    s = box_scene
    s = _set_opaque(s)
    res, _, _ = lcal.raycasting(s)

    assert_almost_equal(res['area'][0], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][0], 0, 3)
    assert_almost_equal(res['Ei_inf'][0], -1, 3)
    assert_almost_equal(res['Ei'][0], 0, 3)
    assert_almost_equal(res['Eabs'][0], 0, 3)

    assert_almost_equal(res['area'][1], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][1], 0, 3)
    assert_almost_equal(res['Ei_inf'][1], -1, 3)
    assert_almost_equal(res['Eabs'][1], 0, 3)

    assert_almost_equal(res['area'][2], 0.5, 3)
    assert_almost_equal(res['Ei_sup'][2], 0, 1)  # 0.07 : loss of accuracy !
    assert_almost_equal(res['Ei_inf'][2], -1, 0)
    assert_almost_equal(res['Eabs'][2], 0, 0)

    assert_almost_equal(res['area'][3], 0.866, 3)
    assert_almost_equal(res['Ei_sup'][3], 57.6, 0)
    assert_almost_equal(res['Ei_inf'][3], -1, 3)
    assert_almost_equal(res['Eabs'][3], 57.6 * 0.9, 0)

