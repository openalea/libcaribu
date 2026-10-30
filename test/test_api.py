"""Test api contract used in caribu"""
import inspect
import openalea.libcaribu.commands as lcmd
import openalea.libcaribu.algos as lcal
import openalea.libcaribu.io as lcio


def check_contract(module, func_name, module_name, fun_args=None):
    # 1. Test func_name exists in module
    func = getattr(module, func_name, None)
    assert func is not None, f"{func_name} not found in {module.__name__}"

    # 2. Test it is callable
    assert callable(func), f"{func_name} must be callable"

    # 3. Test function belongs to the expected module
    assert func.__module__ == module_name, \
        f"run.__module__ is {func.__module__}, expected '{module_name}'"

    # 4. Test signature
    if fun_args is not None:
        sig = inspect.signature(func)
        params = sig.parameters.keys()
        for args in fun_args:
            assert args in params, f"{args} should be a named arg of {func_name}"


def test_commands():
    for cmd_name in ('run_periodise', 'run_s2v', 'run_mcsail', 'run_canestrad'):
        check_contract(lcmd,
                      cmd_name,
                      'openalea.libcaribu.commands',
                      ['workdir','args', 'log', 'verbose'])


def test_scene():
    check_contract(lcal,
                  'set_scene',
                  'openalea.libcaribu.algos',
                  ('scene_path', 'canopy', 'pattern', 'lights', 'sensors', 'opts', 'bands', 'soil')
                  )


def test_io():
    for func_name in ('read_results', 'read_measures'):
        check_contract(lcio, func_name, 'openalea.libcaribu.io')
