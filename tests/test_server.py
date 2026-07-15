import asyncio

from mcp_server.server import mcp


def test_default_mcp_surface_is_one_read_only_tool():
    tools = asyncio.run(mcp.list_tools())
    assert [tool.name for tool in tools] == ["route_and_load"]
