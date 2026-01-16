"""Low level implementation of caribu algorithm"""
import tempfile
import shutil
from copy import deepcopy
import openalea.libcaribu.io as lcio
import openalea.libcaribu.commands as lcmd
from pathlib import Path



def _set_as_file(source, dst):
    if isinstance(source, Path):
        shutil.copy(source, dst)
    else:
        dst.write_text(source)


def set_scene(scene_path=None, canopy=None, pattern=None, lights=None, sensors=None, opts=None, bands=None, soil=None):
    if scene_path is None:
        scene_path = Path(tempfile.mkdtemp(prefix='libcaribu-'))
    else:
        scene_path = Path(scene_path).resolve()
        scene_path.mkdir(exist_ok=True)
    if canopy:
        if not isinstance(canopy, (str, Path)):
            try:
                triangles, labels = canopy
                assert isinstance(labels[0], str)
                canopy = lcio.can_string(triangles, labels)
            except (TypeError, ValueError, AssertionError):
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
            bands = [Path(opt).stem if str(opt).endswith('.opt') else f'band{i+1}' for i, opt in enumerate(opts)]
        if not isinstance(bands, list):
            bands = [bands]
        assert len(bands) == len(opts)
        for opt, band in zip(opts, bands):
            _set_as_file(opt, scene_path / f'{band}.opt')
    if pattern:
        if not isinstance(pattern, (str, Path)):
            pattern = lcio.canestra_pattern(pattern)
        _set_as_file(pattern, scene_path / 'scene.8')
        # reset artifacts from periodise and s2v
        lcmd.clean_periodise(scene_path)
        lcmd.clean_s2v(scene_path)
    if sensors:
        if not isinstance(sensors, (str, Path)):
            sensors = lcio.canestra_sensor(sensors)
        _set_as_file(sensors, scene_path / 'scene.sensor')
    if soil:
        if not isinstance(soil, (str, Path)):
            try:
                triangles, labels = soil
                assert isinstance(labels[0], str)
                soil = lcio.can_string(triangles, labels)
            except (TypeError, ValueError, AssertionError):
                domain = lcio.read_pattern(scene_path / 'scene.8')
                soil = lcio.canestra_soil(domain, n_div=soil)
        _set_as_file(soil, scene_path / 'scene.soil')
    return scene_path


def clean_scene(scene_path):
    lcmd.clean_all_artifacts(scene_path)


def delete_scene(scene_path):
    temp_dir = Path(tempfile.gettempdir())
    if str(scene_path).startswith('libcaribu-') and temp_dir in scene_path.parents:
        shutil.rmtree(scene_path)


def check_scene_and_soil(scene_path, toric=False):
    scan, labs = lcio.read_can(scene_path / 'scene.soil')
    if not toric:
        out_path = scene_path / "scene_and_soil.can"
    else:
        out_path = scene_path / "motif_and_soil.can"
    if not out_path.exists():
        with out_path.open("wb") as out:
            for p in ("scene.can" if not toric else "motif.can", "scene.soil"):
                with (scene_path / p).open("rb") as f:
                    shutil.copyfileobj(f, out)
    return len(labs)


def get_default_scene():
    return set_scene(canopy=lcio.canestra_scene(), pattern=lcio.canestra_pattern(),
                     lights=lcio.canestra_light(), sensors=lcio.canestra_sensor(),
                     opts=lcio.canestra_opt(), soil=1)


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


def get_outputs(scene_path, nsoil=0):
    results = measures = soil = None
    etri = scene_path / "Etri.vec0"
    if etri.exists():
        results, soil = lcio.read_results(etri, nsoil)
    solem = scene_path / "solem.dat"
    if solem.exists():
        measures = lcio.read_measures(solem)
    return results, soil, measures


def raycasting(scene_path, band=None, soil=False, more_args=None, verbose=False):

    if band is None:
        band = next(scene_path.glob("*.opt")).stem

    args = ["-l", "scene.light",
            "-p", f"{band}.opt",
            "-A",
            "-1"]

    if not soil:
        nsoil = 0
        args += ["-M", "scene.can"]
    else:
        nsoil = check_scene_and_soil(scene_path, toric=False)
        args += ["-M", "scene_and_soil.can"]

    if more_args:
        if not isinstance(more_args, list):
            more_args = [more_args]
        args += more_args

    lcmd.clean_canestrad(scene_path)
    lcmd.run_canestrad(scene_path, args=args, verbose=verbose)
    results, soil, measures = get_outputs(scene_path, nsoil)
    return results, soil, measures


def toric_raycasting(scene_path, band=None, soil=False, more_args=None, verbose=False):

    if band is None:
        band = next(scene_path.glob("*.opt")).stem

    args = ["-8", "scene.8",
            "-l", "scene.light",
            "-p", f"{band}.opt",
            "-A",
            "-1"]

    if not soil:
        nsoil = 0
        args += ["-M", "motif.can"]
    else:
        nsoil = check_scene_and_soil(scene_path, toric=True)
        args += ["-M", "motif_and_soil.can"]

    if more_args:
        if not isinstance(more_args, list):
            more_args = [more_args]
        args += more_args

    if not (scene_path / 'motif.can').exists():
        periodise(scene_path)

    lcmd.clean_canestrad(scene_path)
    lcmd.run_canestrad(scene_path, args=args, verbose=verbose)
    results, soil, measures = get_outputs(scene_path, nsoil)
    return results, soil, measures


def radiosity(scene_path, band=None, soil=False, more_args=None, verbose=False):

    if band is None:
        band = next(scene_path.glob("*.opt")).stem

    args = ["-l", "scene.light",
            "-p", f"{band}.opt",
            "-A",
            "-d", "-1"]

    if not soil:
        nsoil = 0
        args += ["-M", "scene.can"]
    else:
        nsoil = check_scene_and_soil(scene_path, toric=False)
        args += ["-M", "scene_and_soil.can"]

    if more_args:
        if not isinstance(more_args, list):
            more_args = [more_args]
        args += more_args

    lcmd.clean_canestrad(scene_path)
    lcmd.run_canestrad(scene_path, args=args, verbose=verbose)
    results, soil, measures = get_outputs(scene_path, nsoil)
    return results, soil, measures


def mixed_radiosity(scene_path, band=None, soil=False, sd=0, layers=2, height=1, more_args=None, verbose=False):

    if band is None:
        band = next(scene_path.glob("*.opt")).stem

    if not (scene_path / 'motif.can').exists():
        periodise(scene_path)
    if not(scene_path / f'{band}.spec').exists():
        s2v(scene_path, bands=band, layers=layers, height=height)

    mcsail(scene_path, band=band)

    args = ["-8", "scene.8",
            "-l", "scene.light",
            "-p", f"{band}.opt",
            "-A",
            "-d", str(sd),
            "-e", "mlsail.env"]

    if not soil:
        nsoil = 0
        args += ["-M", "motif.can"]
    else:
        nsoil = check_scene_and_soil(scene_path, toric=True)
        args += ["-M", "motif_and_soil.can"]

    if more_args:
        if not isinstance(more_args, list):
            more_args = [more_args]
        args += more_args

    lcmd.clean_canestrad(scene_path)
    lcmd.run_canestrad(scene_path, args=args, verbose=verbose)
    results, soil, measures = get_outputs(scene_path, nsoil)
    return results, soil, measures


def caribu(scene_path, bands=None, direct_only=True, toric=False, d_radiosity=0, layers=2, height=1,
           screen_size=None, sensors=False, soil=False, artifacts=False, outdir=None, verbose=False):
    """ Low level interface to caribu algorithms

    Args:
        - scene_path (Path) : a path to a dir containing scene data files with normalised names (scene.can, ...).
          See openalea.caribu.caribu_shell.set_scene for instanciation
        - bands (str or list of str): the name of the optical band to compute. If None (default), stem parts of *.opt files present in scene_path are used
        - direct_only (bool): consider only first order illumination (default true)
        - toric (bool): Consider a toric canopy. Needs a pattern file to be present in the scene_path to take effect
        - d_radiosity (float) : diameter for controling the mixed radiosity behavior. '-1' means 'no mixed radiosity' (pure radiosity, no sail),
         '0' (default) means 'no radiosity' (sail only), any other number defines the diameter of the spherical boundary
          between radiosity/non radiosity domain around primitives
        - layers: number of layers to be considered for discretising the scene for sail
        - height: height of the highest layer to use for sail
        - screen_size: the size (pixel) of the diagonal of the projection screen
        - soil: should soil computations be activated ? (default False). requires a scene.soil in the scene
        - sensors: should virtual sensor be activated ? (default False). requires a scene.sensor file in the scene_path
        - artifacts: should canestra debugging artifacts (B.dat, Bz.dat, ...) be generated (default False) ?
        - outdir: path where output files are written. If None (default), no output files are generated

    Returns:
        A {band_0: (result, measures), ...} dict containing the incident and absorbed flux of energy for all primitives
        """
    if bands is None:
        bands = [opt.stem for opt in scene_path.glob("*.opt")]

    if isinstance(bands, str):
        bands = [bands]
    else:
        bands = list(bands)

    if outdir:
        outdir = Path(outdir)
        outdir.mkdir(exist_ok=True)

    if not direct_only and d_radiosity >= 0:
        toric = True

    if toric:
        if not (scene_path / 'motif.can').exists():
            periodise(scene_path, verbose=verbose)
        if not all([(scene_path / f'{band}.vec').exists() for band in bands]):
            s2v(scene_path, bands=bands, layers=layers, height=height, verbose=verbose)


    args = []
    if screen_size:
        args += ["-L", str(screen_size)]
    if sensors:
        args += ['-C', 'scene.sensor']
    if verbose:
        args += ['-v', '2']
    if not artifacts:
        args += ['-n']

    res = {}
    FF_path = None
    for i, band in enumerate(bands):
        more_args = []
        more_args += args
        if direct_only:
            if i == 0:
                if toric:
                    res[band] = toric_raycasting(scene_path, band=band, soil=soil, more_args=more_args, verbose=verbose)
                else:
                    res[band] = raycasting(scene_path, band=band, soil=soil, more_args=more_args, verbose=verbose)
            else:
                opticals = lcio.read_opt(scene_path / f'{band}.opt')
                r, s, m = deepcopy(res[bands[0]])
                alpha = lcio.absorptance_from_labels(r['label'], opticals)
                r['Eabs'] = alpha * r['Ei']
                res[band] = r, s, m
        else:
            if i == 0:
                FF_path = scene_path / 'FF'
                FF_path.mkdir(exist_ok=True)
                more_args += ['-t', str(FF_path),
                              '-f', 'scene.FF']
            else:
                more_args += ['-t', str(FF_path),
                              '-w', 'scene.FF']
            if d_radiosity < 0:
                res[band] = radiosity(scene_path, band=band, soil=soil, more_args=more_args, verbose=verbose)
            else:
                res[band] = mixed_radiosity(scene_path, band=band, soil=soil, sd=d_radiosity, more_args=more_args, verbose=verbose)

        if outdir:
            shutil.copy(scene_path / 'Etri.vec0', outdir / f'{band}.vec0')
            if i == 0 and FF_path:
                shutil.copy(FF_path / 'scene.FF', outdir)

    return res
