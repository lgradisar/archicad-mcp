# archicad-mcp

`archicad-mcp` is an **MCP server** for **Graphisoft Archicad**. It lets AI clients like **Claude Desktop** read and change an open Archicad project.

It uses the **Tapir** add-on and its JSON commands. Every Tapir command becomes one tool, built automatically from the Tapir command definitions. Nothing is written by hand per command.

## Requirements

- Archicad 25 to 29
- The [Tapir Archicad Add-On](https://github.com/ENZYME-APD/tapir-archicad-automation)
- [uv](https://docs.astral.sh/uv/getting-started/installation/), a small tool that runs Python programs

## Installation

### 1. Install Tapir

Download the add-on for your Archicad version from the [Tapir releases page](https://github.com/ENZYME-APD/tapir-archicad-automation/releases) and follow the instructions there. This repository ships the definitions of Tapir **1.5.9**.

### 2. Install uv

Follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/). One command, no other setup.

### 3. Add archicad-mcp to Claude Desktop

Open the Claude Desktop config file in a text editor:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Pick one of the two options below.

#### Option A: Quick install

Nothing to download. Paste this block into the config file. `uvx` comes with uv. On the first start it fetches the server and everything it needs, which can take a minute.

```json
{
  "mcpServers": {
    "archicad-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/lgradisar/archicad-mcp", "archicad-mcp"]
    }
  }
}
```

#### Option B: From source

Use this if you want to read or change the code.

```bash
git clone https://github.com/lgradisar/archicad-mcp.git
cd archicad-mcp
uv sync
```

Then paste this block, with `YOUR_DIRECTORY` replaced by the full path to the `archicad-mcp` folder. On Windows write the path with forward slashes, for example `C:/Users/you/archicad-mcp`:

```json
{
  "mcpServers": {
    "archicad-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "YOUR_DIRECTORY", "archicad-mcp"]
    }
  }
}
```

If Claude Desktop says it cannot find `uvx` or `uv`, write the full path to the program as `command`. Find it with `where uvx` on Windows or `which uvx` on macOS.

To update a quick install later, run `uv cache clean archicad-mcp` and restart Claude Desktop. To update a source install, run `git pull` and `uv sync` in the folder.

### 4. Restart Claude Desktop

Open a project in Archicad, then ask Claude to run `TestConnection`. It answers with the Archicad and Tapir versions. The tools are listed behind the tools icon in the chat box of Claude Desktop.

## Settings

Settings are optional. They go into an `"env"` block in the config entry:

```json
"env": { "ARCHICAD_MCP_MODE": "safe", "ARCHICAD_MCP_GROUPS": "project,element,property,navigator" }
```

| Setting | Default | What it does |
|---|---|---|
| `ARCHICAD_MCP_SEARCH` | `1` | `1`: Claude sees three tools, `TestConnection`, `search_tools` and `call_tool`, and finds the Tapir tools by searching. Keeps the conversation small. `0`: Claude sees every tool directly. |
| `ARCHICAD_MCP_MODE` | `all` | `all`: every tool. `safe`: hides the dangerous tools (see Safety). `readonly`: only tools that read the project. |
| `ARCHICAD_MCP_GROUPS` | all groups | Only show tools from these groups, separated by commas, for example `project,element`. |
| `ARCHICAD_PORT` | automatic | Port of the Archicad JSON API. Set it when more than one Archicad is open. |
| `ARCHICAD_TIMEOUT` | `300` | Seconds to wait for Archicad to answer one command. |

Groups: `application`, `project`, `element`, `element-grouping`, `favorites`, `property`, `classification`, `attribute`, `ifc`, `library`, `teamwork`, `navigator`, `issue-management`, `revision-management`, `design-options`, `keynote`, `mep`, `solid-element-operation`, `script-ui`, `developer`.

Restart Claude Desktop after changing settings. If the tool list does not change, remove and re-add the server in the config.

## Tools

- **250 Tapir commands**, one tool each. See the [Tapir command list](https://enzyme-apd.github.io/tapir-archicad-automation/archicad-addon/). By default Claude finds them with `search_tools` and runs them with `call_tool`, so the full list never enters the conversation.
- **TestConnection**: reports the port, the Archicad version and the Tapir version.
- **RunTapirCommand**: runs any Tapir command by name. Useful when your Tapir is newer than the definitions shipped here. Only shown in `all` mode with no groups set.

## Safety

- With `ARCHICAD_MCP_SEARCH=0`, Claude sees 252 tools. That is a lot of text for every conversation in Claude Desktop. Combine it with `ARCHICAD_MCP_GROUPS` or `readonly` mode, or leave search on.
- Some tools can do real damage: quit Archicad, open, close and save projects, delete things, send to Teamwork, publish, print, write files, change libraries, or show dialogs that block Archicad until someone clicks. `ARCHICAD_MCP_MODE=safe` hides all of them, plus `RunTapirCommand`.
- Claude Desktop asks before each tool runs. Approve tools one by one instead of allowing everything.
- Arguments are checked against the Tapir definitions before they are sent. Archicad checks them again.

## Troubleshooting

- **"Archicad is not running or the Tapir add-on is not loaded"**: open a project in Archicad. If it is open, check that Tapir appears in the Add-On Manager.
- **Several Archicad windows open**: the first one that started answers. Set `ARCHICAD_PORT` to choose.
- **Claude reports a timeout**: Claude may stop waiting before Archicad finishes. Archicad keeps working. Publishing, library reload, drawing updates, Teamwork and IFC commands can take long. Check the result in Archicad before asking again.
- **"is not available in the installed Tapir add-on"**: your Tapir is older than the definitions shipped here. Update the add-on.
- **Teamwork projects**: changes need reserved elements. `ReserveElements` is a dangerous tool and hidden in `safe` mode.

## Updating the Tapir definitions

When a new Tapir version comes out:

```bash
uv run scripts/update_tapir.py 1.5.9
```

Replace `1.5.9` with the new version. The script downloads the two definition files into `src/archicad_mcp/tapir` and prints how many commands it found. Check new commands against the lists in `src/archicad_mcp/tools/classification.py`.

## Custom tools

You can add your own tools in `src/archicad_mcp/tools/custom_tools.py`. Use `client.run_command` for official Archicad JSON commands and `client.run_tapir_command` for Tapir commands. New Archicad commands are better contributed to Tapir directly.

## License

MIT
