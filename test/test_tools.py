from openalea.libcaribu.tools import canestrad, mcsail, s2v, periodise
import pytest


tools = [mcsail, periodise, s2v, canestrad]


@pytest.mark.parametrize("tool", tools)
def test_tool_help_runs(tool):
    """Check that each binary runs and exits cleanly (or shows help)."""
    result=tool(args=['-h'])
    # Some programs exit 0, some 1 for help; just require no crash
    assert result.returncode == 0
