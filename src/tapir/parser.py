import json
from pathlib import Path

def load_json_file(filename, var_name=None):
    file_path = Path(__file__).with_name(filename)
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    if var_name:
        data = data.replace(f"var {var_name} = ", "").rstrip("; \n")

    return json.loads(data)


def resolve_ref(schema, definitions, seen=None):
    """
    Recursively resolve $ref entries like "#/Elements" using common schema definitions.
    """
    if seen is None:
        seen = set()

    if isinstance(schema, dict):
        if "$ref" in schema:
            ref = schema["$ref"]
            if ref.startswith("#/"):
                key = ref[2:]
                if key in seen:  # cycle detected
                    return definitions[key]
                seen.add(key)
                return resolve_ref(definitions[key], definitions, seen)
        return {k: resolve_ref(v, definitions, seen) for k, v in schema.items()}

    elif isinstance(schema, list):
        return [resolve_ref(item, definitions, seen) for item in schema]

    return schema




def tapir_commands():
    gCommands = load_json_file("command_definitions.js", var_name="gCommands")
    gSchemaDefinitions = load_json_file("common_schema_definitions.js", var_name="gSchemaDefinitions")


    parsed_commands = []

    for group in gCommands:
        tag = group["name"]
        for cmd in group["commands"]:
            in_schema = cmd.get("inputScheme")
            in_resolved  = resolve_ref(in_schema, gSchemaDefinitions)  if in_schema  is not None else None
            
            parsed_commands.append({
                "name": cmd["name"],
                "tag": tag,
                "description": cmd["description"],
                "input_schema": in_resolved
            })

    return parsed_commands