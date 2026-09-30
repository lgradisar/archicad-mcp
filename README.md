# archicad-mcp

An [MCP](https://modelcontextprotocol.io) server for **Graphisoft Archicad**. It lets MCP clients such as Claude Desktop or Claude Code work with an open Archicad project.

All tools are generated from the command definitions of the [Tapir Archicad add-on](https://github.com/ENZYME-APD/tapir-archicad-automation). Nothing is written by hand per command, so updating the two Tapir definition files updates the tool set.

## Requirements

- Archicad 25 to 29 with the [Tapir add-on](https://github.com/ENZYME-APD/tapir-archicad-automation/releases) installed. This repository ships the definitions of Tapir **1.5.9**.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.10 or newer.

## Install

```bash
git clone https://github.com/lgradisar/archicad-mcp.git
cd archicad-mcp
uv sync
```

## Add to Claude Desktop

Edit the config file:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Replace the two paths with the full path to `uv` (`where uv` on Windows, `which uv` on macOS) and to this repository:

```json
{
  "mcpServers": {
    "archicad-mcp": {
      "command": "C:/Users/you/.local/bin/uv.exe",
      "args": ["run", "--directory", "C:/path/to/archicad-mcp", "python", "src/server.py"]
    }
  }
}
```

Settings go into an optional `"env"` block in the same entry:

```json
"env": { "ARCHICAD_MCP_MODE": "safe", "ARCHICAD_MCP_GROUPS": "project,element,property,navigator" }
```

Restart Claude Desktop after changing the config. Claude Desktop caches the tool list, so after changing the mode or groups you may need to remove and re-add the server.

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `ARCHICAD_MCP_MODE` | `all` | `all`: every tool. `safe`: hides the dangerous tools listed below. `readonly`: only tools that read the project. |
| `ARCHICAD_MCP_GROUPS` | all groups | Comma-separated Tapir groups to expose, for example `project,element`. See the group list below. |
| `ARCHICAD_PORT` | scan 19723 to 19743 | Port of the Archicad JSON API. Set it when more than one Archicad is open. |
| `ARCHICAD_TIMEOUT` | `300` | Seconds to wait for Archicad to answer one command. |

Groups: `application`, `project`, `element`, `element-grouping`, `favorites`, `property`, `classification`, `attribute`, `ifc`, `library`, `teamwork`, `navigator`, `issue-management`, `revision-management`, `design-options`, `keynote`, `mep`, `solid-element-operation`, `script-ui`, `developer`.

## Tools

- **250 Tapir commands**, one tool each, with the Tapir input schema as the tool schema. See the [Tapir command reference](https://enzyme-apd.github.io/tapir-archicad-automation/archicad-addon/).
- **TestConnection**: reports the port, the Archicad version and the installed and shipped Tapir versions.
- **RunTapirCommand**: runs any Tapir command by name. Useful when the installed Tapir is newer than the shipped definitions. Hidden in `safe` mode.

Tools carry MCP hints: `Get*` commands are marked read-only; `Create*`, `Add*`, `Attach*` and `Clone*` commands as non-destructive.

### Please read before enabling everything

- The full tool list is large, roughly 110k tokens of tool definitions per conversation. Claude Code loads tools on demand, Claude Desktop does not. For Claude Desktop use `ARCHICAD_MCP_GROUPS` or `ARCHICAD_MCP_MODE=readonly`.
- Dangerous tools, hidden by `ARCHICAD_MCP_MODE=safe`: quitting Archicad, opening, closing and saving projects, all `Delete*` commands, `SetStories`, Teamwork send, receive, reserve and release, publishing, printing, IFC and BCF file operations, favorites import and export, library changes, `SetElementNotificationClient`, `GenerateDocumentation`, `ChangeDrawingLink`, dialogs that block Archicad, and `RunTapirCommand`.
- The model talks to Archicad through its JSON API, plain HTTP on `127.0.0.1` without authentication. This server adds no network listener, but it gives the model reach into files and Teamwork through the commands above. Approve tools one by one in your client instead of allowing everything.
- Arguments are validated against the Tapir schema before they are sent. Archicad validates them again.

## Troubleshooting

- **"Archicad is not running or the Tapir add-on is not loaded"**: open a project in Archicad. If Archicad is open, check that Tapir shows up in the add-on manager. Call `TestConnection`.
- **Several Archicad windows**: the first one that started answers. Set `ARCHICAD_PORT` to pick one.
- **Client reports a timeout**: the client may stop waiting before Archicad finishes. Archicad keeps working. Publishing, library reload, drawing updates, Teamwork and IFC commands can take longer. Check with `TestConnection` before repeating a modifying command.
- **"is not available in the installed Tapir add-on"**: your Tapir is older than the shipped definitions. Update the add-on.
- **Teamwork projects**: changes need reserved elements. `ReserveElements` is a dangerous tool and hidden in `safe` mode.

## Updating the Tapir definitions

```bash
uv run scripts/update_tapir.py 1.5.9
```

Pass the Tapir release tag. The script downloads `command_definitions.js` and `common_schema_definitions.js` into `src/tapir`, records the tag in `src/tapir/TAPIR_VERSION` and prints the number of commands it could parse. Check new commands against the lists in `src/tools/classification.py`.

## Custom tools

Add your own tools in `src/tools/custom_tools.py`. `tapir.client.run_command` sends any official Archicad JSON command, `tapir.client.run_tapir_command` any Tapir command. New Archicad commands are better contributed to Tapir directly.

## License

MIT
