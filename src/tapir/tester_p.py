from parser import resolve_ref, tapir_commands
import json
from pathlib import Path


file_path = Path(__file__).with_name("command_definitions.js")
file_path_definitions = Path(__file__).with_name("common_schema_definitions.js")
with open(file_path, "r", encoding="utf-8") as f:
    data = f.read()
with open(file_path_definitions, "r", encoding="utf-8") as f:
    data_definitions = f.read()


data = data.replace("var gCommands = ", "").rstrip("; \n")
gCommands = json.loads(data)


schema = tapir_commands()
#commands = resolve_ref(schema, data_definitions)


for i in schema:
    
    input_schema = i.get("input_schema")
    input_schema_str = "Input schema (raw):\n" + json.dumps(input_schema, indent=2)
    
    print("\n")
    print(input_schema_str)
