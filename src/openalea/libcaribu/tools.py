import subprocess
import numpy as np
from pathlib import Path

def _run_tool(tool_name, workdir='.', args=None):
    workdir = Path(workdir).resolve()
    if not workdir.is_dir():
        raise NotADirectoryError(f"Invalid working directory: {workdir}")
    cmd = [tool_name]
    if args:
        cmd += list(args)

    result = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result

def run_mcsail(*args, **kwds): return _run_tool("mcsail", *args, **kwds)
def run_periodise(*args, **kwds): return _run_tool("periodise", *args, **kwds)
def run_s2v(*args, **kwds): return _run_tool("s2v", *args, **kwds)
def run_canestrad(*args, **kwds): return _run_tool("canestrad", *args, **kwds)

def read_res(path):
    data_array = np.loadtxt(path, skiprows=2, dtype=str)
    # assuming columns: index label area Eabs Ei_sup Ei_inf
    idx = data_array[:, 0].astype(float)
    label = np.array([l.zfill(12) for l in data_array[:, 1]])
    area, Eabs, Ei_sup, Ei_inf = data_array[:, 2:].astype(float).T

    data = {
        'index': idx.tolist(),
        'label': label.tolist(),
        'area': area.tolist(),
        'Eabs': Eabs.tolist(),
        'Ei_sup': Ei_sup.tolist(),
        'Ei_inf': Ei_inf.tolist(),
    }
    return data