import os

from fastmcp import FastMCP

from tools import custom_tools, register_tapir


def hidden_tools(tools, env):
    mode = env.get("ARCHICAD_MCP_MODE", "all").strip().lower()
    groups = {group.strip().lower() for group in env.get("ARCHICAD_MCP_GROUPS", "").split(",") if group.strip()}
    hidden = set()
    for tool in tools:
        if tool.name == "TestConnection":
            continue
        if groups and not tool.tags & groups:
            hidden.add(tool.name)
        elif mode == "safe" and "dangerous" in tool.tags:
            hidden.add(tool.name)
        elif mode == "readonly" and "readonly" not in tool.tags:
            hidden.add(tool.name)
    return hidden


def create_server(env=os.environ):
    mcp = FastMCP("archicad-mcp", dereference_schemas=False)
    tools = custom_tools.init_tools(mcp) + register_tapir.init_tapir(mcp)
    hidden = hidden_tools(tools, env)
    if hidden:
        mcp.disable(names=hidden)
    return mcp


if __name__ == "__main__":
    create_server().run(show_banner=False)
