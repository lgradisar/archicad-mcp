import anyio
from fastmcp.tools import Tool
from mcp.types import ToolAnnotations

from archicad_mcp.tapir import client, parser


def connection_info():
    product = client.run_command("API.GetProductInfo")
    tapir = client.run_tapir_command("GetAddOnVersion", {})
    return {
        "port": client.find_port(),
        "archicad_version": product["version"],
        "archicad_build": product["buildNumber"],
        "language": product["languageCode"],
        "tapir_installed": tapir.get("version"),
        "tapir_definitions": parser.tapir_version(),
    }


async def test_connection() -> dict:
    """Check the connection to Archicad and report the Archicad and Tapir versions."""
    return await anyio.to_thread.run_sync(connection_info)


def init_tools(mcp):
    tool = Tool.from_function(
        test_connection,
        name="TestConnection",
        title="TestConnection",
        tags={"readonly"},
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
    )
    mcp.add_tool(tool)
    return [tool]
