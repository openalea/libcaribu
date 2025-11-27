"""utilities to write/read caribu files"""

import numpy as np
from itertools import cycle
from io import StringIO
from pathlib import Path


def set_opticals(soil=0.2, leaf=(0.06, 0.07), stem=None):
    """
    Set monochromatic optical properties for soil and one or more optical species

    Args:
        soil: soil reflectance (default: 0.2)
        leaf: a (list of) tuples defining one or more leaf optical species. 2-tuples are for symmetric
            (reflectance, transmittance) properties, 4-tuples allow differentiating upper and lower faces.
        stem: a (list of) stem properties associated to optical species defined above. if None (default),
            stem reflectance is computed as sum(r_leaf_sup, t_leaf_sup)
    Returns:
        dict: {
            'soil': r_soil,
            'species': list of (r_stem, (r_leaf_sup, t_leaf_sup, r_leaf_inf, t_leaf_inf)) tuples
        }
        where r_* stands for reflectance, t_* transmittance, *_sup upper face of lead, *_inf lower face of leaf
    """
    if not isinstance(leaf, list):
        leaf = [leaf]
    if stem is None:
        stem = [sum(l[:2]) for l in leaf]
    if not isinstance(stem, list):
        stem = [stem]
    return {'soil': soil, 'species': list(zip(cycle(stem), leaf))}


def encode_labels(opt=1, plant=1, leaf=1, elt=0):
    opt = np.asarray(opt, dtype=np.int64)
    plant = np.clip(np.asarray(plant, dtype=np.int64), 0, 99999)
    leaf = np.clip(np.asarray(leaf, dtype=np.int64), 0, 99)
    elt = np.clip(np.asarray(elt, dtype=np.int64), 0, 999)

    labels = (
            opt * 100_000_000_000
            + plant * 100_000
            + leaf * 1_000
            + elt
    )

    return np.char.zfill(np.atleast_1d(labels).astype(str), 12)


def decode_labels(labels):
    labels = np.asarray(labels, dtype=np.int64)

    elt = labels % 1000
    plant = (labels // 100_000) % 100000
    leaf = ((labels - plant * 100_000) // 1_000) % 1_000
    opt = labels // 100_000_000_000

    return opt, plant, leaf, elt


def absorptance_from_labels(labels, opticals):
    opt, _, leaf, _ = decode_labels(labels)
    is_leaf = leaf.astype(bool)
    asoil = 1 - np.sum(opticals['soil'])
    aleaf = np.array([1 - np.sum(po[:2]) for _, po in opticals['species']])
    astem = np.array([1 - np.sum(po) for po, _ in opticals['species']])
    idx = opt - 1  # shift to 0-based for species
    return np.where(opt == 0,
                    asoil,
                    np.where(is_leaf,
                             aleaf[idx],
                             astem[idx]
                             ))


def can_string(triangles, labels):
    out = []
    for tri, label in zip(np.asarray(triangles), cycle(labels.tolist())):
        coords = " ".join(f"{c:.6f}" for c in tri.reshape(-1))
        out.append(f"p 1 {label} 3 {coords}\n")
    return "".join(out)


def canestra_scene(triangles=None, plant=1, specie=1, leaf=True, element=0):
    """ format triangles and associated properties as caribu canopy string content
    """
    if triangles is None:
        triangles = [[(0, 0, 0), (np.sqrt(2), 0, 0), (0, np.sqrt(2), 0)]]
    labels = encode_labels(specie, plant, leaf, element)
    return can_string(triangles, labels)


def canestra_sensor(triangles=None):
    if triangles is None:
        triangles = [[(0, 0, 0.01), (np.sqrt(2), 0, 0.01), (0, np.sqrt(2), 0.01)]]
    header = f'#{len(triangles)}\n'
    sensors = can_string(triangles, np.arange(len(triangles)))
    return header + sensors


def canestra_pattern(pattern_tuple=None):
    """ format pattern as caribu file string content
    """
    if pattern_tuple is None:
        pattern_tuple = (0, 0, np.sqrt(2), np.sqrt(2))
    x1, y1, x2, y2 = pattern_tuple
    pattern_tuple = [(min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2))]
    pattern = '\n'.join([' '.join(map(str, pattern_tuple[0])),
                         ' '.join(map(str, pattern_tuple[1])), ' '])
    return pattern


def canestra_light(lights=None):
    """ format lights as caribu light file string content
    """
    if lights is None:
        lights = [(1, (0, 0, -1))]

    def _as_string(light):
        e, p = light
        return ' '.join(map(str, [e] + list(p))) + '\n'

    lines = list(map(_as_string, lights))

    return ''.join(lines)


def canestra_opt(opticals=None):
    """ format species as caribu opt file string content
    """

    if opticals is None:
        opticals = set_opticals()
    soil = opticals['soil']
    n = len(opticals['species'])
    o_string = 'n %s\n' % n
    o_string += "s d %s\n" % soil
    for stem, leaf in opticals['species']:
        if len(leaf) == 2:
            o_string += f"e d {stem}   d {leaf[0]} {leaf[1]}  d {leaf[0]} {leaf[1]}\n"
        elif len(leaf) == 4:
            o_string += f"e d {stem}   d {leaf[0]} {leaf[1]}  d {leaf[2]} {leaf[3]}\n"

    return o_string


def triangulate_domain(domain, n_div=1):
    xmin, ymin, xmax, ymax = domain

    # grid points
    xs = np.linspace(xmin, xmax, n_div + 1)
    ys = np.linspace(ymin, ymax, n_div + 1)

    # create grid
    X, Y = np.meshgrid(xs, ys, indexing="ij")

    # lower-left corner of each cell
    x0 = X[:-1, :-1]
    y0 = Y[:-1, :-1]

    # other corners of each cell
    x1 = X[1:, :-1]
    y1 = Y[1:, :-1]

    x2 = X[1:, 1:]
    y2 = Y[1:, 1:]

    x3 = X[:-1, 1:]
    y3 = Y[:-1, 1:]

    # stack triangles
    tri1 = np.stack([
        np.stack([x0, y0, np.zeros_like(x0)], axis=-1),
        np.stack([x1, y1, np.zeros_like(x1)], axis=-1),
        np.stack([x2, y2, np.zeros_like(x2)], axis=-1)
    ], axis=-2)

    tri2 = np.stack([
        np.stack([x0, y0, np.zeros_like(x0)], axis=-1),
        np.stack([x2, y2, np.zeros_like(x2)], axis=-1),
        np.stack([x3, y3, np.zeros_like(x3)], axis=-1)
    ], axis=-2)

    triangles = np.concatenate([tri1.reshape(-1, 3, 3),
                                tri2.reshape(-1, 3, 3)], axis=0)

    return triangles


def canestra_soil(domain=None, n_div=1):
    if domain is None:
        domain = (0, 0, np.sqrt(2), np.sqrt(2))
    triangles = triangulate_domain(domain, n_div)
    labels = encode_labels(0, 0, 0, range(len(triangles)))
    return can_string(triangles, labels)


def read_results(path, nsoil=0):
    data_array = np.loadtxt(path, skiprows=2, dtype=str)
    data_array = np.atleast_2d(data_array)  # ensures 2D shape even if one triangle
    # assuming columns: index label area Eabs Ei_sup Ei_inf
    idx = data_array[:, 0].astype(float)
    label = np.array([l.zfill(12) for l in data_array[:, 1]])
    area, Eabs, Ei, Ei_sup, Ei_inf = data_array[:, 2:].astype(float).T

    if nsoil == 0:
        soil_data = None
        data = {
            'index': idx,
            'label': label,
            'area': area,
            'Ei': Ei,
            'Eabs': Eabs,
            'Ei_sup': Ei_sup,
            'Ei_inf': Ei_inf,
        }
    else:
        data = {
            'index': idx[:-nsoil],
            'label': label[:-nsoil],
            'area': area[:-nsoil],
            'Ei': Ei[:-nsoil],
            'Eabs': Eabs[:-nsoil],
            'Ei_sup': Ei_sup[:-nsoil],
            'Ei_inf': Ei_inf[:-nsoil],
        }
        soil_data = {
            'index': idx[-nsoil:],
            'label': label[-nsoil:],
            'area': area[-nsoil:],
            'Ei': Ei[-nsoil:],
        }
    return data, soil_data


def read_measures(path):
    data_array = np.loadtxt(path, dtype=float)
    data_array = np.atleast_2d(data_array)  # ensures 2D shape even if one triangle
    id, eio, ei, area = data_array.T

    data = {
        'sensor_id': id,
        'area': area,
        'Ei0': eio,
        'Ei': ei
    }
    return data


def read_opt(source):
    """Reader for *.opt file format used by canestra.

    Args:
        source (str): Path to the .opt file or str with file content

    Returns:
        dict: {
            'soil': r_soil,
            'species': list of (r_stem, (r_leaf_sup, t_leaf_sup, r_leaf_inf, t_leaf_inf)) tuples
        }
        where r_* stands for reflectance, t_* transmittance, *_sup upper face of lead, *_inf lower face of leaf
    """
    soil_reflectance = None
    species = []

    if isinstance(source, Path) or source.endswith('.opt'):
        infile = open(Path(source), 'r')
    else:
        infile = StringIO(source)

    with infile:
        for line in infile:
            line = line.strip()
            if line.startswith('s'):
                soil_reflectance = float(line.split()[2])

            elif line.startswith('e'):
                fields = line.split()
                # extract indices 2,4,5,7,8
                values = [float(fields[i]) for i in (2, 4, 5, 7, 8)]
                stem, leaf = values[0], tuple(values[1:])
                if leaf[2:] == leaf[:2]:
                    leaf = leaf[:2]
                species.append((stem, leaf))

    return {'soil': soil_reflectance, 'species': species}


def read_can(source):
    if isinstance(source, Path) or source.endswith('.can'):
        infile = Path(source)
    else:
        infile = StringIO(source)

    can = np.loadtxt(infile, comments="#", ndmin=2, dtype=str)
    labels = can[:, 2]
    triangles = can[:, -9:].astype(float).reshape(-1, 3, 3)
    return triangles, labels


def read_sensors(source):
    if isinstance(source, Path) or source.endswith('.sensor'):
        infile = Path(source)
    else:
        infile = StringIO(source)

    can = np.loadtxt(infile, comments="#", ndmin=2, dtype=str)
    ids = can[:, 2].astype(int)
    triangles = can[:, -9:].astype(float).reshape(-1, 3, 3)
    return triangles, ids


def read_soil(source):
    if isinstance(source, Path) or source.endswith('.soil'):
        infile = Path(source)
    else:
        infile = StringIO(source)
    soil = np.loadtxt(infile, comments="#", ndmin=2, dtype=str)
    labels = soil[:, 2]
    triangles = soil[:, -9:].astype(float).reshape(-1, 3, 3)
    return triangles, labels


def read_light(source):
    """Reader for *.light file format used by canestra

    Args:
        file_path: (str) a path to the file

    Returns:
        (list of tupl   es) a list of (Energy, (vx, vy, vz)) tuples defining light
    """
    if isinstance(source, Path) or source.endswith('.light'):
        data = np.loadtxt(source)
    else:
        data = np.loadtxt(StringIO(source))

    # Ensure 2D even if there's only one line
    data = np.atleast_2d(data)

    return [(row[0], tuple(row[1:4])) for row in data]


def read_pattern(source):
    """Reader for *.8 file format used by canestra

    Args:
        file_path: (str) a path to the file

    Returns:
        (tuple of floats) 2D Coordinates ( xmin, ymin, xmax, ymax) of the domain bounding the scene
    """
    if isinstance(source, Path) or source.endswith('.8'):
        data = np.loadtxt(source)
    else:
        data = np.loadtxt(StringIO(source))
    return tuple(data.reshape(-1))
