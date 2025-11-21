"""utilities to write/read caribu files"""

import numpy as np
from itertools import cycle
from collections.abc import Iterable
from io import StringIO
from pathlib import Path



def is_iterable(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes))


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


def can_label(plant=1, opt=1, isleaf=1, elt=0):
    """
    Encode numeric fields into a fixed-length can-format barcode string.

    The core part (plant, isleaf, elt) is always 12 characters.
    The 'opt' prefix can extend the total length beyond 12.

    Returns:
        str: encoded barcode string.
    """
    # Start with a 12-character base (for plant, opak, elt)
    label = ['0'] * 12

    label[:-11] = list(str(opt))

    fields = {
        'plant': (2, 6, plant),
        'isleaf': (7, 9, isleaf),
        'elt': (10, 12, elt)
    }

    for name, (start, end, value) in fields.items():
        value_str = str(value)
        length = end - start + 1

        # Truncate or pad to fit field width
        if len(value_str) > length:
            value_str = value_str[-length:]  # keep rightmost digits
        else:
            value_str = value_str.zfill(length)

        # Place into the label (convert to 0-based index)
        label[start - 1:end] = value_str

    return ''.join(label)


def decode_label(label):
    opt = int(''.join(label[:-11]))
    plant = int(''.join(label[-11:-6]))
    leaf = int(''.join(label[-6:-3]))
    elt = int(''.join(label[-3:]))
    return opt, plant, leaf, elt


def po_from_label(label, opticals):
    opt, _, leaf, _ = decode_label(label)
    is_leaf = bool(leaf)
    if opt == 0:
        return opticals['soil']
    elif is_leaf:
        return opticals['species'][opt][1]
    else:
        return opticals['species'][opt][0]


def absorptance_from_label(label, opticals):
    po = po_from_label(label, opticals)
    if len(po) < 4:
        return 1 - sum(po)
    else:
        return 1 - sum(po[:2])

def can_triangle(triangle, label):
    """
    Create a formatted line representing a labeled triangle.

    triangle: iterable of 3 (x, y, z) tuples
    label: a can label identifier (str)

    Returns:
        str: formatted line (safe for C++ reading)
    """
    # Always treat label as string
    s = f"p 1 {label} 3"

    # Format coordinates with high precision (use repr for exact float string)
    for pt in triangle:
        s += " " + " ".join(f"{coord:.15g}" for coord in pt)

    return s


def canestra_scene(triangles=None, plant=1, is_leaf=True, specie=1):
    """ format triangles and associated labels as caribu canopy string content
    """
    if triangles is None:
        triangles = [[(0, 0, 0), (np.sqrt(2), 0, 0), (0, np.sqrt(2), 0)]]
    if not is_iterable(plant):
        plant = [plant]
    if not is_iterable(specie):
        specie = [specie]
    isleaf = np.atleast_1d(is_leaf).astype(int)
    labels = [can_label(pid, optid, ileaf) for pid, optid, ileaf  in zip(plant, cycle(specie), cycle(isleaf))]
    lines = [can_triangle(t, l) for t, l in zip(triangles, cycle(labels))]
    return '\n'.join(lines) + '\n'


def canestra_sensor(triangles=None):
    if triangles is None:
        triangles = [[(0, 0, 0.01), (np.sqrt(2), 0, 0.01), (0, np.sqrt(2), 0.01)]]
    lines = [f'#{len(triangles)}']
    lines += [can_triangle(t, i) for i,t in enumerate(triangles)]
    return '\n'.join(lines) + '\n'


def canestra_pattern(pattern_tuple=None):
    """ format pattern as caribu file string content
    """
    if pattern_tuple is None:
        pattern_tuple = (0 , 0, np.sqrt(2), np.sqrt(2))
    x1, y1, x2, y2 = pattern_tuple
    pattern_tuple = [(min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2))]
    pattern = '\n'.join([' '.join(map(str, pattern_tuple[0])),
                         ' '.join(map(str, pattern_tuple[1])), ' '])
    return pattern


def canestra_light(lights=None):
    """ format lights as caribu light file string content
    """
    if lights is None:
        lights = [(100, (0, 0, -1))]

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


def read_results(path):
    data_array = np.loadtxt(path, skiprows=2, dtype=str)
    data_array = np.atleast_2d(data_array)  # ensures 2D shape even if one triangle
    # assuming columns: index label area Eabs Ei_sup Ei_inf
    idx = data_array[:, 0].astype(float)
    label = np.array([l.zfill(12) for l in data_array[:, 1]])
    area, Eabs, Ei, Ei_sup, Ei_inf = data_array[:, 2:].astype(float).T

    data = {
        'index': idx,
        'label': label,
        'area': area,
        'Ei': Ei,
        'Eabs': Eabs,
        'Ei_sup': Ei_sup,
        'Ei_inf': Ei_inf,
    }
    return data

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
                species.append((stem, leaf))

    return {'soil': soil_reflectance, 'species': species}
