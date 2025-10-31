from openalea.libcaribu.tools import (run_canestrad, run_mcsail,
                                      run_s2v, run_periodise)
import pytest


tools = [run_mcsail, run_periodise, run_s2v, run_canestrad]


@pytest.mark.parametrize("tool", tools)
def test_tool_help_runs(tool):
    """Check that each binary runs and exits cleanly (or shows help)."""
    result=tool(args=['-h'])
    # Some programs exit 0, some 1 for help; just require no crash
    assert result.returncode == 0
