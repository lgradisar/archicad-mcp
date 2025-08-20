def dynamic_command(input):
    from archicad import ACConnection

    conn = ACConnection.connect ()
    acc = conn.commands
    act = conn.types

    if isinstance(input, str):
        stripped = input.strip().lower()
        if stripped in ("", "null", "none"):
            input = None

    command = act.AddOnCommandId('TapirCommand', 'GetAddOnVersion')
    response = acc.ExecuteAddOnCommand(command, input)

    #response = acc.ExecuteAddOnCommand (act.AddOnCommandId ('TapirCommand', name), input or None)
    return response

input = {'input_schema': None}
test = dynamic_command(input)
print(test)