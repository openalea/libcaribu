import subprocess
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

def mcsail(*args, **kwds): return _run_tool("mcsail",*args, **kwds)
def periodise(*args, **kwds): return _run_tool("periodise",*args, **kwds)
def s2v(*args, **kwds): return _run_tool("s2v",*args, **kwds)
def canestrad(*args, **kwds): return _run_tool("canestrad",*args, **kwds)
