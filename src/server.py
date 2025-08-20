from fastmcp import FastMCP
from tools import custom_tools, register_tapir

mcp = FastMCP("archicad-mcp")

custom_tools.init_tools(mcp)
register_tapir.init_tapir(mcp)

if __name__ == "__main__":
    mcp.run()
