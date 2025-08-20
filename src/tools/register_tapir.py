from tapir import COMMANDS
import json

def init_tapir(mcp):

    for cmd in COMMANDS:        
        name = cmd["name"]
        tag = cmd["tag"]
        description = cmd.get("description", "")
        input_schema = cmd.get("input_schema")
        
        if not input_schema:
            input_schema_str = "Input schema: None"
        else:
            input_schema_str =json.dumps(input_schema, indent=2)

        @mcp.tool(
            name=name,
            description=description,
            tags=[tag],
        )
        def dynamic_command(input, _name=name, _input_schema=input_schema_str):
            from archicad import ACConnection

            conn = ACConnection.connect()
            acc = conn.commands
            act = conn.types

            if isinstance(input, str):
                stripped = input.strip()
                if stripped.lower() in ("", "null", "none"):
                    input = None
                else:
                    input = json.loads(stripped)

            if isinstance(input, dict) and list(input.keys()) == ["input"]:
                input = input["input"]            
            
            params = {} if (input is None and isinstance(_input_schema, dict)) else input
            
            command = act.AddOnCommandId('TapirCommand', _name)
            response = acc.ExecuteAddOnCommand(command, params)
            return response
