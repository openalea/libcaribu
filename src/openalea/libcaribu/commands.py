import subprocess
import functools
from pathlib import Path


class CommandFailed(Exception):
    def __init__(self, wd, cmd, returncode, stdout, stderr, log=''):
        self.wd = wd
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.log = log

    def __str__(self):
        msg = [f"Command failed: {' '.join(self.cmd)}",
               f"working directory: {self.wd}",
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
        if log:
            print(log)

    if result.returncode != 0:
        raise CommandFailed(
            workdir,
            cmd,
            result.returncode,
            result.stdout,
            result.stderr,
            log
        )

    return result


def _clean_artifacts(workdir='.', artifacts=None, verbose=False):
    workdir = Path(workdir).resolve()
    if not workdir.is_dir():
        raise NotADirectoryError(f"Invalid working directory: {workdir}")
    if artifacts is not None:
        for artifact in artifacts:
            matches = list(workdir.glob(artifact))
            for path in matches:
                if path.exists():
                    if verbose:
                        print(f'Clean artifact: {artifact} from dir {workdir}')
                    path.unlink()


@functools.wraps(_run_tool) # propagate signature
def run_mcsail(*args, **kwds): return _run_tool("mcsail", log='mc-sail.log', *args, **kwds)
@functools.wraps(_run_tool)
def run_periodise(*args, **kwds): return _run_tool("periodise", *args, **kwds)
@functools.wraps(_run_tool)
def run_s2v(*args, **kwds): return _run_tool("s2v", log='s2v.log', *args, **kwds)
@functools.wraps(_run_tool)
def run_canestrad(*args, **kwds): return _run_tool("canestrad", log='canestra.log', *args, **kwds)


@functools.wraps(_clean_artifacts)
def clean_canestrad(workdir='.'): _clean_artifacts(workdir, ('_scene.can', 'trinf.can','B.dat', 'E0.dat', 'solem.dat', 'Einc.vec', 'Eabs.vec', 'Etri.vec', 'Etri.vec0'))
@functools.wraps(_clean_artifacts)
def clean_periodise(workdir='.'): _clean_artifacts(workdir, ('Bz.dat', 'motif.can'))
@functools.wraps(_clean_artifacts)
def clean_mcsail(workdir='.'): _clean_artifacts(workdir, ('spectral', 'mlsail.env', 'Mcoef.dat', 'Mvec.dat', 'proflux.dat', 'profout'))
@functools.wraps(_clean_artifacts)
def clean_s2v(workdir='.'): _clean_artifacts(workdir, ('*.spec', 'cropchar', 'leafarea', 'out.dang', 's2v.can', 's2v.area'))


def clean_all_artifacts(workdir='.'):
    clean_canestrad(workdir)
    clean_periodise(workdir)
    clean_mcsail(workdir)
    clean_s2v(workdir)
