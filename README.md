# openalea.libcaribu

[![CI Status](https://github.com/openalea/libcaribu/actions/workflows/openalea_ci.yml/badge.svg)](https://github.com/openalea/libcaribu/actions/workflows/openalea_ci.yml?query=branch%3Amaster)
[![Anaconda version](https://anaconda.org/openalea3/openalea.libcaribu/badges/version.svg)](https://anaconda.org/openalea3/openalea.libcaribu)
[![Latest release date](https://anaconda.org/openalea3/openalea.libcaribu/badges/latest_release_date.svg)](https://anaconda.org/openalea3/openalea.libcaribu)
[![Platforms](https://anaconda.org/openalea3/openalea.libcaribu/badges/platforms.svg)](https://anaconda.org/openalea3/openalea.libcaribu)
[![License](https://anaconda.org/openalea3/openalea.libcaribu/badges/license.svg)](https://anaconda.org/openalea3/openalea.libcaribu)
[![Downloads](https://anaconda.org/openalea3/openalea.libcaribu/badges/downloads.svg)](https://anaconda.org/openalea3/openalea.libcaribu)

---

## What is openalea.libcaribu?

openalea.libcaribu is a companion package of openalea.caribu dedicated to the compilation/installation of caribu c++ extension.
It also provides a low level pythonic interface to these extensions (read/write input and output files, launch commands)

## Installation

### Users

```bash
mamba create -n caribu -c openalea3 -c conda-forge openalea.libcaribu 
``` 

### Developers


```bash
git clone 'https://github.com/openalea/libcaribu.git'
cd libcaribu
mamba create -n libcaribu -f ./conda/environment.yml
mamba activate libcaribu
pip install -e .[test] -vv --no-build-isolation
```

On Windows, the conda compilers (`c-compiler`, `cxx-compiler`) use MSVC: Visual Studio 2022
or its Build Tools, with the "Desktop development with C++" workload, must be installed.

## License

**LibCaribu** is released under the open source **CeCILL-C license**.  
See the [LICENSE](LICENSE) file.
