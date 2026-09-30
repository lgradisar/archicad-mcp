import json

import anyio
import jsonschema
from fastmcp.exceptions import ToolError
from fastmcp.tools import Tool, ToolResult

from tapir import COMMANDS, client
from tools import classification


def to_result(response):
    structured = response if isinstance(response, dict) else None
    return ToolResult(content=json.dumps(response), structured_content=structured)


class TapirTool(Tool):
    command: str

    async def run(self, arguments):
        arguments = arguments or {}
        try:
            jsonschema.validate(arguments, self.parameters)
        except jsonschema.ValidationError as error:
            raise ToolError(f"Invalid arguments for {self.name}: {error.message}")
        response = await anyio.to_thread.run_sync(
            client.run_tapir_command, self.command, arguments, abandon_on_cancel=True
        )
        return to_result(response)


def make_tool(cmd):
    name = cmd["name"]
    return TapirTool(
        name=name,
        title=name,
        command=name,
        description=classification.description(name, cmd["description"]),
        parameters=cmd["schema"],
        tags={cmd["group"]} | classification.tags(name),
        annotations=classification.annotations(name),
    )


async def run_any_tapir_command(command: str, parameters: dict | None = None) -> ToolResult:
    """Run any Tapir command by name, including commands newer than this server's definitions.
    Parameters must follow the Tapir documentation for that command."""
    response = await anyio.to_thread.run_sync(
        client.run_tapir_command, command, parameters or {}, abandon_on_cancel=True
    )
    return to_result(response)


def init_tapir(mcp):
    tools = [make_tool(cmd) for cmd in COMMANDS]
    tools.append(Tool.from_function(
        run_any_tapir_command, name="RunTapirCommand", title="RunTapirCommand", tags={"dangerous"}
    ))
    for tool in tools:
        mcp.add_tool(tool)
    return tools
