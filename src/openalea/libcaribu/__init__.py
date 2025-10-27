from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("openalea.libcaribu")
except PackageNotFoundError:
    # package is not installed
    pass
