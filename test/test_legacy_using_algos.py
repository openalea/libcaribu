"""
Test caribu legacy test suite, using libcaribu.algos
"""
import pytest
import numpy as np
from pathlib import Path
import openalea.libcaribu.algos as lcal

data_dir = Path(__file__).parent / "data"


@pytest.fixture(scope="module") # tmp_path is kept between tests
def caribu_test_scene(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("caribu_test_scene")
    lcal.set_scene(tmp_path,
                   canopy=data_dir / "filterT.can",
                   pattern=data_dir / "filter.8",
                   lights=data_dir / "zenith.light",
                   sensors=data_dir / "filterT.sensor",
                   opts=data_dir / "par.opt")
    return tmp_path


def test_projection_non_toric_scene(caribu_test_scene):
    lcal.raycasting(caribu_test_scene)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'projection_non_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_sensor_non_toric_scene(caribu_test_scene):
    args = ["-C", "scene.sensor"]
    lcal.raycasting(caribu_test_scene, more_args=args)
    resfile = caribu_test_scene / "solem.dat"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'sensor_non_toric_scene.dat')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_projection_toric_scene(caribu_test_scene):
    lcal.toric_raycasting(caribu_test_scene)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'projection_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_radiosity_non_toric_scene(caribu_test_scene):
    lcal.radiosity(caribu_test_scene)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'radiosity_non_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_projection_sail_toric_scene(caribu_test_scene):
    lcal.periodise(caribu_test_scene)
    lcal.s2v(caribu_test_scene, layers=6, height=21)
    lcal.mixed_radiosity(caribu_test_scene, sd=0)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'projection_sail_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_nested_radiosity_toric_scene(caribu_test_scene):
    lcal.periodise(caribu_test_scene)
    lcal.s2v(caribu_test_scene, layers=6, height=21)
    lcal.mixed_radiosity(caribu_test_scene, sd=1)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'nested_radiosity_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)