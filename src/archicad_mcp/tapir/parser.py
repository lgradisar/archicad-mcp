import json
import re
from pathlib import Path

HERE = Path(__file__).parent
UNROLL_DEPTH = 2


def load_js(filename):
    text = (HERE / filename).read_text(encoding="utf-8-sig")
    text = re.sub(r"^\s*var \w+ = ", "", text).strip().removesuffix(";")
    return json.loads(text)


def tapir_version():
    return (HERE / "TAPIR_VERSION").read_text().strip()


# Schema handling

def inline(node, defs, stack=()):
    """Replace every "#/Name" reference with the definition itself.

    A local description next to a $ref wins over the definition's one.
    Recursive definitions are unrolled UNROLL_DEPTH times, then left as a plain object.
    """
    if isinstance(node, list):
        return [inline(item, defs, stack) for item in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        name = node["$ref"].removeprefix("#/")
        if stack.count(name) >= UNROLL_DEPTH:
            return {"type": "object", "description": defs[name].get("description", name)}
        merged = {**defs[name], **{key: value for key, value in node.items() if key != "$ref"}}
        return inline(merged, defs, stack + (name,))
    return {key: inline(value, defs, stack) for key, value in node.items()}


def flatten_root_union(schema):
    """Tool schemas must be a plain object at the root; merge a root oneOf/anyOf into one."""
    branches = schema.get("oneOf") or schema.get("anyOf")
    if not branches:
        return schema
    properties = {}
    options = []
    for branch in branches:
        properties.update(branch.get("properties", {}))
        options.append("(" + ", ".join(branch.get("required", [])) + ")")
    description = f"{schema.get('description', '')} Provide exactly one of: {' or '.join(options)}.".strip()
    return {"type": "object", "description": description, "properties": properties, "additionalProperties": False}


def tool_schema(input_scheme, defs):
    if input_scheme is None:
        return {"type": "object", "properties": {}, "additionalProperties": False}
    return flatten_root_union(inline(input_scheme, defs))


def tapir_commands():
    defs = load_js("common_schema_definitions.js")
    commands = []
    for group in load_js("command_definitions.js"):
        for cmd in group["commands"]:
            commands.append({
                "name": cmd["name"],
                "group": group["name"].removesuffix(" Commands").lower().replace(" ", "-"),
                "version": cmd["version"],
                "description": cmd["description"],
                "schema": tool_schema(cmd.get("inputScheme"), defs),
            })
    return commands
