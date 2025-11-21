import pytest
import shutil
from pathlib import Path
import openalea.libcaribu.commands as lcmd

tools = [lcmd.run_mcsail, lcmd.run_periodise, lcmd.run_s2v, lcmd.run_canestrad]


@pytest.mark.parametrize("tool", tools)
def test_tool_help_runs(tool):
    """Check that each binary runs and exits cleanly (or shows help)."""
    result=tool(args=['-h'])
    # Some programs exit 0, some 1 for help; just require no crash
    assert result.returncode == 0


def test_clean(tmp_path):
    data_dir = Path(__file__).parent / "data"
    infiles = ["filterT.can", "zenith.light", "par.opt", "filter.8", "filterT.sensor"]
    for name in infiles:
        shutil.copy(data_dir / name, tmp_path)
    count = sum(1 for f in tmp_path.iterdir() if f.is_file())
    assert count == len(infiles)

    args = ["-M", "filterT.can",
            "-l", "zenith.light",
            "-p", "par.opt",
            "-C", "filterT.sensor",
            "-A",
            "-1"]
    lcmd.run_canestrad(tmp_path, args)
    count = sum(1 for f in tmp_path.iterdir() if f.is_file())
    assert count > len(infiles)

    lcmd.clean_canestrad(tmp_path)
    count = sum(1 for f in tmp_path.iterdir() if f.is_file())
    assert count == len(infiles)

    args = ["-m", "filterT.can",
            "-8", "filter.8"]
    lcmd.run_periodise(tmp_path, args)
    args = ["motif.can",
            "6",  # nb layers
            "21",  # canopy height
            "filter.8",
            "par"]
    lcmd.run_s2v(tmp_path, args)
    spectral = tmp_path / 'par.spec'
    shutil.copy(spectral, tmp_path / 'spectral')
    args = ["zenith.light"]
    lcmd.run_mcsail(tmp_path, args)
    args = ["-M", "motif.can",
            "-8", "filter.8",
            "-l", "zenith.light",
            "-p", "par.opt",
            "-A",
            "-d", "1",
            "-e", "mlsail.env"]
    lcmd.run_canestrad(tmp_path, args)
    count = sum(1 for f in tmp_path.iterdir() if f.is_file())
    assert count > len(infiles)

    lcmd.clean_all_artifacts(tmp_path)
    count = sum(1 for f in tmp_path.iterdir() if f.is_file())
    assert count == len(infiles)
