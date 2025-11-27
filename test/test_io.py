from importlib.resources import files
import openalea.libcaribu.io as lcio

data_dir = files('openalea.libcaribu.data')

def test_opticals():
    # from python
    opts = lcio.set_opticals()
    assert isinstance(opts, dict)
    assert opts['soil'] == 0.2
    stem, leaf = opts['species'][0]
    assert stem == 0.13
    assert leaf == (0.06, 0.07)
    opt_string = lcio.canestra_opt(opts)
    assert len(opt_string.splitlines()) == 3
    opts = lcio.read_opt(opt_string)
    assert isinstance(opts, dict)
    assert opts['soil'] == 0.2
    stem, leaf = opts['species'][0]
    assert stem == 0.13
    assert leaf == (0.06, 0.07)

    # from file
    opts = lcio.read_opt(data_dir / 'par.opt')
    assert isinstance(opts, dict)
    assert opts['soil'] == 0.15
    stem, leaf = opts['species'][0]
    assert stem == 0.1
    assert leaf == (0.1, 0.05)


def test_labels():
    labels = lcio.encode_labels(opt=1, plant=2, leaf=3, elt=4)
    assert labels[0] == "100000203004"
    opt, plant, leaf, elt = lcio.decode_labels(labels)
    assert opt[0] == 1 and plant[0] == 2 and leaf[0] == 3 and elt[0] == 4

    opticals = lcio.set_opticals(soil=0.3, leaf=(0.4, 0.1), stem=0.8)
    labels = lcio.encode_labels(opt=[0,1,1], leaf=[0, 0, 1]) # soil, stem, leaf
    asoil, astem, aleaf = lcio.absorptance_from_labels(labels, opticals)
    assert round(asoil, 1) == 0.7 and round(astem, 1) == 0.2 and round(aleaf, 1) == 0.5


def test_canopy():
    # from python
    triangles = [((0, 0, 0), (1, 0, 0), (0, 1, 0))]
    labels = lcio.encode_labels(opt=1, plant=1, leaf=1, elt=0)
    can_string = lcio.can_string(triangles, labels)
    assert len(can_string.splitlines()) == 1
    tris, labs = lcio.read_can(can_string)
    assert len(tris) == 1 and tris[0][1][0] == 1
    assert labs == labels[0]
    can_string = lcio.canestra_scene(triangles, plant=1, specie=1, leaf=True, element=0)
    assert len(can_string.splitlines()) == 1
    tris, labs = lcio.read_can(can_string)
    assert len(tris) == 1 and tris[0][1][0] == 1
    assert labs == labels[0]

    #from file
    triangles, labels = lcio.read_can(data_dir / 'filterT.can')
    assert len(triangles) == 192
    assert labels[0] == "100000101000"


def test_light():
    # from python
    lights = [(100, (0, 0, -1))]
    light_string = lcio.canestra_light(lights)
    assert len(light_string.splitlines()) == 1
    lights = lcio.read_light(light_string)
    nrj, vec = lights[0]
    assert nrj == 100 and vec[2] == -1

    # from file
    lights = lcio.read_light(data_dir / 'zenith.light')
    nrj, vec = lights[0]
    assert nrj == 1 and vec[2] == -1


def test_pattern():
    pattern=(0,0,1,1)
    pattern_string = lcio.canestra_pattern(pattern)
    assert len(pattern_string.splitlines()) == 3
    pattern = lcio.read_pattern(pattern_string)
    assert pattern == (0,0,1,1)

    pattern = lcio.read_pattern(data_dir / 'filter.8')
    assert pattern == (0,0,20,20)


def test_sensors():
    sensors = [((0, 0, 0), (1, 0, 0), (0, 1, 0))]
    sensor_string = lcio.canestra_sensor(sensors)
    assert len(sensor_string.splitlines()) == 2
    sensors, ids = lcio.read_sensors(sensor_string)
    assert sensors[0][1][0] == 1 and ids[0] == 0

    sensors, ids = lcio.read_sensors(data_dir / 'filterT.sensor')
    assert len(sensors) == 1
    assert sensors[0][1][2] == 20 and ids[0] == 1


def test_soil():
    domain = (0, 0, 1, 1)
    soil_string = lcio.canestra_soil(domain, n_div=2)
    assert len(soil_string.splitlines()) == 8  # n_div * n_div * 2
    triangles, labels = lcio.read_can(soil_string)
    assert labels[0] == "0" * 12
    x,y,_ = triangles.reshape(-1, 3).T
    assert (x.min(), y.min(), x.max(), y.max()) == domain