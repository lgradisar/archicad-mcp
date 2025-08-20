# archicad-mcp

`archicad-mcp` is a framework that runs an **MCP server** for **Graphisoft Archicad**.  
It uses the **Tapir** add-on with its additional JSON commands to let MCP clients like **Anthropic’s Claude** interact with Archicad.


## Installation

### Tapir

For `archicad-mcp` to work, the [Tapir Archicad Add-On](https://github.com/tlorantfy/tapir-archicad-automation) is required. Please follow the installation instructions provided in that repository.

This package also depends on two Tapir files that define the JSON command structure used to automatically compile MCP-ready tools:

- [Tapir Command Definitions file](https://github.com/ENZYME-APD/tapir-archicad-automation/blob/main/docs/archicad-addon/command_definitions.js)  
- [Tapir Common Schema Definitions file](https://github.com/ENZYME-APD/tapir-archicad-automation/blob/main/docs/archicad-addon/common_schema_definitions.js)  

These files are located under the `src/mcp_server/tapir` folder.  
If you encounter mismatched commands, update the files directly from the Tapir repository.


### FastMCP Server

#### 1. It is recommended to use `uv` for installation.

Clone the repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

To set up the project and its virtual environment, simply run:

```bash
uv sync
```

#### 2. Add to Claude config manually

On Windows:  
`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "archicad-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "YOUR_DIRECTORY/archicad-mcp",
        "python",
        "-m",
        "server"
      ],
      "env": {
        "PYTHONPATH": "YOUR_DIRECTORY/archicad-mcp/src"
      }
    }
  }
}
```


## Supported Tools

### Tapir JSON Commands
See the full list of [Tapir JSON Commands](https://enzyme-apd.github.io/tapir-archicad-automation/archicad-addon/).

### Custom Tools
This repository also supports adding your custom tools, either from the [official JSON commands](https://archicadapi.graphisoft.com/JSONInterfaceDocumentation/#Introduction) or other sources.  
They can be defined in the `src/mcp_server/tools/custom_tools.py` file.

For new Archicad-specific commands that are not part of the official JSON commands, it is recommended to contribute them directly to the Tapir repository instead.





