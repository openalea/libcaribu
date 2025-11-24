"""Low level implementation of caribu algorithm"""

import shutil
import openalea.libcaribu.io as lcio
import openalea.libcaribu.commands as lcmd
from pathlib import Path
from copy import deepcopy


def _set_as_file(source, dst):
    if isinstance(source, Path):
        shutil.copy(source, dst)
    else:
        dst.write_text(source)


def set_scene(scene_path, canopy=None, pattern=None, lights=None, sensors=None, opts=None, bands=None):
    scene_path = Path(scene_path).resolve()
    scene_path.mkdir(exist_ok=True)
    if canopy:
        if not isinstance(canopy, (str, Path)):
            try:
                triangles, labels = canopy
                canopy = lcio.can_string(triangles, labels)
            except (TypeError, ValueError):
                canopy = lcio.canestra_scene(canopy)
        _set_as_file(canopy, scene_path / 'scene.can')
    if lights:
        if not isinstance(lights, (str, Path)):
            lights = lcio.canestra_light(lights)
        _set_as_file(lights, scene_path / 'scene.light')
    if opts:
        if not isinstance(opts, list):
            opts = [opts]
        for i, opt in enumerate(opts):
            if not isinstance(opt, (str, Path)):
                opts[i] = lcio.canestra_opt(opt)
        if bands is None:
            bands = [Path(opt).stem if str(opt).endswith('.opt') else f'band{i}' for i, opt in enumerate(opts)]
        if not isinstance(bands, list):
            bands = [bands]
        assert len(bands) == len(opts)
        for opt, band in zip(opts, bands):
            _set_as_file(opt, scene_path / f'{band}.opt')
    if pattern:
        if not isinstance(pattern, (str, Path)):
            pattern = lcio.canestra_pattern(pattern)
        _set_as_file(pattern, scene_path / 'scene.8')
    if sensors:
        if not isinstance(sensors, (str, Path)):
            sensors = lcio.canestra_sensor(sensors)
        _set_as_file(sensors, scene_path / 'scene.sensor')
    return scene_path


def set_default_scene(scene_path='./_cscene'):
    return set_scene(scene_path, canopy=lcio.canestra_scene(), pattern=lcio.canestra_pattern(),
                     lights=lcio.canestra_light(), sensors=lcio.canestra_sensor(), opts=lcio.canestra_opt())


def periodise(scene_path, verbose=False):
    args = ["-m", "scene.can",
            "-8", "scene.8"]
    lcmd.clean_periodise(scene_path)
    status = lcmd.run_periodise(scene_path, args=args, verbose=verbose)
    return status


def s2v(scene_path, bands=None, layers=2, height=1, verbose=False):

    if bands is None:
        bands = [opt.stem for opt in scene_path.glob("*.opt")]

    if isinstance(bands, str):
        bands = [bands]
    else:
        bands = list(bands)
    args = ["motif.can",
            str(layers),
            str(height),
            "scene.8"]
    args += bands

    lcmd.clean_s2v(scene_path)
    status = lcmd.run_s2v(scene_path, args=args, verbose=verbose)
    return status


def mcsail(scene_path, band=None):
    if band is None:
        band = next(scene_path.glob("*.opt")).stem
    lcmd.clean_mcsail(scene_path)
    shutil.copy(scene_path / f"{band}.spec", scene_path / 'spectral')
    args = ["scene.light"]
    status = lcmd.run_mcsail(scene_path, args=args)
    return status


def get_outputs(scene_path):
    results = measures = None
    etri = scene_path / "Etri.vec0"
    if etri.exists():
        results = lcio.read_results(etri)
    solem = scene_path / "solem.dat"
    if solem.exists():
        measures = lcio.read_measures(solem)
    return results, measures


def raycasting(scene_path, band=None, more_args=None, verbose=False):

    if band is None:
        band = next(scene_path.glob("*.opt")).stem

    args = ["-M", "scene.can",
            "-l", "scene.light",
            "-p", f"{band}.opt",
            "-A",
            "-1"]

    if more_args:
        if not isinstance(more_args, list):
            more_args = [more_args]
        args += more_args

    lcmd.clean_canestrad(scene_path)
    lcmd.run_canestrad(scene_path, args=args, verbose=verbose)
    results, measures = get_outputs(scene_path)
    return results, measures


def toric_raycasting(scene_path, band=None, more_args=None, verbose=False):

    if band is None:
        band = next(scene_path.glob("*.opt")).stem

    args = ["-M", "motif.can",
            "-8", "scene.8",
            "-l", "scene.light",
            "-p", f"{band}.opt",
            "-A",
            "-1"]
    if more_args:
        if not isinstance(more_args, list):
            more_args = [more_args]
        args += more_args

    if not (scene_path / 'motif.can').exists():
        periodise(scene_path)

    lcmd.clean_canestrad(scene_path)
    lcmd.run_canestrad(scene_path, args=args, verbose=verbose)
    results, measures = get_outputs(scene_path)
    return results, measures


def radiosity(scene_path, band=None, more_args=None, verbose=False):

    if band is None:
        band = next(scene_path.glob("*.opt")).stem

    args = ["-M", "scene.can",
            "-l", "scene.light",
            "-p", f"{band}.opt",
            "-A",
            "-d", "-1"]
    if more_args:
        if not isinstance(more_args, list):
            more_args = [more_args]
        args += more_args

    lcmd.clean_canestrad(scene_path)
    lcmd.run_canestrad(scene_path, args=args, verbose=verbose)
    results, measures = get_outputs(scene_path)
    return results, measures


def mixed_radiosity(scene_path, band=None, sd=0, layers=2, height=1, more_args=None, verbose=False):

    if band is None:
        band = next(scene_path.glob("*.opt")).stem

    if not (scene_path / 'motif.can').exists():
        periodise(scene_path)
    if not(scene_path / f'{band}.spec').exists():
        s2v(scene_path, bands=band, layers=layers, height=height)

    mcsail(scene_path, band=band)

    args = ["-M", "motif.can",
            "-8", "scene.8",
            "-l", "scene.light",
            "-p", f"{band}.opt",
            "-A",
            "-d", str(sd),
            "-e", "mlsail.env"]
    if more_args:
        if not isinstance(more_args, list):
            more_args = [more_args]
        args += more_args

    lcmd.clean_canestrad(scene_path)
    lcmd.run_canestrad(scene_path, args=args, verbose=verbose)
    results, measures = get_outputs(scene_path)
    return results, measures


def caribu(scene_path, bands=None, toric=False, direct_only=True, sphere_diameter=-1, layers=2, height=1, with_sensors=False, no_artifact=True, verbose=False):

    if bands is None:
        bands = [opt.stem for opt in scene_path.glob("*.opt")]

    if isinstance(bands, str):
        bands = [bands]
    else:
        bands = list(bands)

    if sphere_diameter >= 0:
        toric = True
        if not all([(scene_path / f'{band}.vec').exists() for band in bands]):
            s2v(scene_path, bands=bands, layers=layers, height=height, verbose=verbose)

    if toric and not (scene_path / 'motif.can').exists():
        periodise(scene_path, verbose=verbose)

    args = []
    if with_sensors:
        args += ['-C', 'scene.sensor']
    if verbose:
        args += ['-v', '2']
    if no_artifact:
        args += ['-n']

    res = {}
    for i, band in enumerate(bands):
        more_args = []
        more_args += args
        if direct_only:
            if i == 0:
                if toric:
                    res[band] = toric_raycasting(scene_path, band=band, more_args=more_args, verbose=verbose)
                else:
                    res[band] = raycasting(scene_path, band=band, more_args=more_args, verbose=verbose)
            else:
                opticals = lcio.read_opt(scene_path / f'{band}.opt')
                r, m = deepcopy(res[bands[0]])
                alpha = lcio.absorptance_from_labels(r['label'], opticals)
                r['Eabs'] = alpha * r['Ei']
                res[band] = r, m
        else:
            if i == 0:
                FF_path = scene_path / 'FF'
                FF_path.mkdir(exist_ok=True)
                more_args += ['-f', FF_path]
            else:
                more_args += ['-w', FF_path]
            if sphere_diameter < 0:
                res[band] = radiosity(scene_path, band=band, more_args=more_args, verbose=verbose)
            else:
                res[band] = mixed_radiosity(band=band, sd=sphere_diameter, more_args=more_args, verbose=verbose)