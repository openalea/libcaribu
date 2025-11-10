"""utilities to write/read caribu files"""

from itertools import cycle
from collections.abc import Iterable

import numpy as np


def is_iterable(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes))


def optical_properties(soil=0.2, stem=0.13, leaf=(0.06, 0.07)):
    return {0: (soil,), 1: leaf, 2: (stem,)}


def can_label(plant=1, opt=1, opak=1, elt=0):
    """
    Encode numeric fields into a fixed-length can-format barcode string.

    The core part (plant, opak, elt) is always 12 characters.
    The 'opt' prefix can extend the total length beyond 12.

    Returns:
        str: encoded barcode string.
    """
    # Start with a 12-character base (for plant, opak, elt)
    label = ['0'] * 12

    label[:-11] = list(str(opt))

    fields = {
        'plant': (2, 6, plant),
        'opak': (7, 9, opak),
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
        s += " " + " ".join(f"{coord:.6f}" for coord in pt)

    return s


def canestra_scene(triangles, plant_ids=1, optical_ids=1, opticals=None):
    """ format triangles and associated labels as caribu canopy string content
    """
    if opticals is None:
        opticals = optical_properties()
    opak = {k: 0 if len(v) == 1 else 1 for k, v in opticals.items()}
    if not is_iterable(plant_ids):
        plant_ids = [plant_ids]
    if not is_iterable(optical_ids):
        optical_ids = [optical_ids]
    labels = [can_label(pid, optid, opak[optid]) for pid, optid in zip(plant_ids, cycle(optical_ids))]
    lines = [can_triangle(t, l) for t, l in zip(triangles, cycle(labels))]
    return '\n'.join(lines) + '\n'


def canestra_pattern(pattern_tuple):
    """ format pattern as caribu file string content
    """
    x1, y1, x2, y2 = pattern_tuple
    pattern_tuple = [(min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2))]
    pattern = '\n'.join([' '.join(map(str, pattern_tuple[0])),
                         ' '.join(map(str, pattern_tuple[1])), ' '])
    return pattern


def canestra_light(lights):
    """ format lights as caribu light file string content
    """

    def _as_string(light):
        e, p = light
        return ' '.join(map(str, [e] + list(p))) + '\n'

    lines = list(map(_as_string, lights))

    return ''.join(lines)


def canestra_opt(opticals=None):
    """ format species as caribu opt file string content
    """

    if opticals is None:
        opticals = optical_properties()
    soil = opticals.pop(0)
    n = len(opticals)
    o_string = 'n %s\n' % n
    o_string += "s d %s\n" % soil
    species_sorted_keys = sorted(opticals.keys())
    for key in species_sorted_keys:
        po = opticals[key]
        if sum(po) <= 0:
            raise ValueError('Caribu do not accept black body material (absorptance=1)')
        if len(po) == 1:
            o_string += f"e d {po[0]}   d -1 -1  d -1 -1\n"
        elif len(po) == 2:
            o_string += f"e d -1   d {po[0]} {po[1]}  d {po[0]} {po[1]}\n"
        elif len(po) == 4:
            o_string += f"e d -1   d {po[0]} {po[1]}  d {po[2]} {po[3]}\n"

    return o_string


def read_res(path):
    data_array = np.loadtxt(path, skiprows=2, dtype=str)
    data_array = np.atleast_2d(data_array)  # ensures 2D shape even if one triangle
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
