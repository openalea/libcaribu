"""
Test caribu legacy test suite, using only commands
"""
import pytest
import shutil
import numpy as np
from pathlib import Path
import openalea.libcaribu.commands as lcmd

data_dir = Path(__file__).parent / "data"

def count_valid(scene):
    arr = np.loadtxt(scene, comments="#", ndmin=1, dtype=str)
    return arr.shape[0]


@pytest.fixture
def caribu_test_scene(tmp_path): # regenerated at each test
    for name in ["filterT.can", "zenith.light", "par.opt", "filter.8", "filterT.sensor"]:
        shutil.copy(data_dir / name, tmp_path)
    return tmp_path


def test_projection_non_toric_scene(caribu_test_scene):
    args = ["-M", "filterT.can",
            "-l", "zenith.light",
            "-p", "par.opt",
            "-A",
            "-1"]
    lcmd.run_canestrad(caribu_test_scene, args)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'projection_non_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)



def test_sensor_non_toric_scene(caribu_test_scene):
    args = ["-M", "filterT.can",
            "-l", "zenith.light",
            "-p", "par.opt",
            "-C", "filterT.sensor",
            "-A",
            "-1"]
    lcmd.run_canestrad(caribu_test_scene, args)
    resfile = caribu_test_scene / "solem.dat"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'sensor_non_toric_scene.dat')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_projection_toric_scene(caribu_test_scene):
    args = ["-m", "filterT.can",
            "-8", "filter.8"]
    lcmd.run_periodise(caribu_test_scene, args)
    scene_8 = caribu_test_scene / "motif.can"
    assert scene_8.exists()
    args = ["-M", "motif.can",
            "-8", "filter.8",
            "-l", "zenith.light",
            "-p", "par.opt",
            "-A",
            "-1"]
    lcmd.run_canestrad(caribu_test_scene, args)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'projection_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_radiosity_non_toric_scene(caribu_test_scene):
    args = ["-M", "filterT.can",
            "-l", "zenith.light",
            "-p", "par.opt",
            "-A",
            "-d", "-1"]
    lcmd.run_canestrad(caribu_test_scene, args)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'radiosity_non_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_projection_sail_toric_scene(caribu_test_scene):

    args = ["-m", "filterT.can",
            "-8", "filter.8"]
    lcmd.run_periodise(caribu_test_scene, args)
    args = ["motif.can",
            "6",
            "21",
            "filter.8",
            "par"]
    lcmd.run_s2v(caribu_test_scene, args)
    leafarea = caribu_test_scene / 'leafarea'
    assert leafarea.exists()
    spectral = caribu_test_scene / 'par.spec'
    assert spectral.exists()
    shutil.copy(spectral, caribu_test_scene / 'spectral')
    args = ["zenith.light"]
    lcmd.run_mcsail(caribu_test_scene, args)
    mcsailenv = caribu_test_scene / 'mlsail.env'
    assert mcsailenv.exists()
    args = ["-M", "motif.can",
            "-8", "filter.8",
            "-l", "zenith.light",
            "-p", "par.opt",
            "-A",
            "-d", "0",
            "-e", "mlsail.env"]
    lcmd.run_canestrad(caribu_test_scene, args)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'projection_sail_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)


def test_nested_radiosity_toric_scene(caribu_test_scene):

    args = ["-m", "filterT.can",
            "-8", "filter.8"]
    lcmd.run_periodise(caribu_test_scene, args)
    args = ["motif.can",
            "6",  # nb layers
            "21",  # canopy height
            "filter.8",
            "par"]
    lcmd.run_s2v(caribu_test_scene, args)
    spectral = caribu_test_scene / 'par.spec'
    assert spectral.exists()
    shutil.copy(spectral, caribu_test_scene / 'spectral')
    args = ["zenith.light"]
    lcmd.run_mcsail(caribu_test_scene, args)
    args = ["-M", "motif.can",
            "-8", "filter.8",
            "-l", "zenith.light",
            "-p", "par.opt",
            "-A",
            "-d", "1",
            "-e", "mlsail.env"]
    lcmd.run_canestrad(caribu_test_scene, args)
    resfile = caribu_test_scene / "Etri.vec0"
    assert resfile.exists()
    expected = np.loadtxt(data_dir / 'nested_radiosity_toric_scene.vec0')
    res = np.loadtxt(resfile)
    np.testing.assert_allclose(res, expected)