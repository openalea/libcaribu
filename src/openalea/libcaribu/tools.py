import subprocess
from pathlib import Path


class CommandFailed(Exception):
    def __init__(self, cmd, returncode, stdout, stderr, log=''):
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.log = log

    def __str__(self):
        msg = [f"Command failed: {' '.join(self.cmd)}",
               f"Exit code: {self.returncode}"]

        if self.stdout:
            msg.append("\n--- STDOUT ---\n" + self.stdout)

        if self.stderr:
            msg.append("\n--- STDERR ---\n" + self.stderr)

        if self.log:
            msg.append("\n--- LOG ---\n" + self.log)

        return "\n".join(msg)


def _run_tool(tool_name, workdir='.', args=None, log=None, verbose=False):
    workdir = Path(workdir).resolve()
    if not workdir.is_dir():
        raise NotADirectoryError(f"Invalid working directory: {workdir}")

    cmd = [tool_name]
    if args:
        if isinstance(args, str):
            args = [args]
        cmd += list(args)
    result = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)

    if log:
        log_path = workdir / log
        log = log_path.read_text() if log_path.is_file() else None
        if log:
            log_path.unlink()

    if verbose:
        print(result.stdout)
        print(result.stderr)

    if result.returncode != 0:
        raise CommandFailed(
            cmd,
            result.returncode,
            result.stdout,
            result.stderr,
            log
        )

    return result


def _clean_dir(workdir='.', files=None):
    workdir = Path(workdir).resolve()
    if not workdir.is_dir():
        raise NotADirectoryError(f"Invalid working directory: {workdir}")
    if files is not None:
        for file in files:
            path = workdir / file
            if path.exists():
                path.unlink()


def run_mcsail(*args, **kwds): return _run_tool("mcsail", log='mc-sail.log', *args, **kwds)
def run_periodise(*args, **kwds): return _run_tool("periodise", *args, **kwds)
def run_s2v(*args, **kwds): return _run_tool("s2v", log='s2v.log', *args, **kwds)
def run_canestrad(*args, **kwds): return _run_tool("canestrad", log='canestra.log', *args, **kwds)


def clean_canestrad(workdir='.'): _clean_dir(workdir, ('B.dat', 'E0.dat', 'canestra.log', 'Einc.vec', 'Eabs.vec', 'Etri.vec', 'Etri.vec0'))
