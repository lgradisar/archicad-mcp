import json
import os
import socket
import threading
import urllib.request

from fastmcp.exceptions import ToolError

from archicad_mcp.tapir import parser

PORTS = range(19723, 19744)

_lock = threading.Lock()
_port = None


class ArchicadError(ToolError):
    def __init__(self, error):
        super().__init__(f"Archicad error {error.get('code')}: {error.get('message')}")


def setting(name, default):
    value = os.environ.get(name) or default
    try:
        return float(value)
    except ValueError:
        raise ToolError(f"{name} must be a number, not '{value}'")


# Connection

def _listening(port):
    try:
        socket.create_connection(("127.0.0.1", port), timeout=0.3).close()
        return True
    except OSError:
        return False


def find_port():
    global _port
    if _port is None:
        candidates = [int(setting("ARCHICAD_PORT", 0))] if os.environ.get("ARCHICAD_PORT") else PORTS
        _port = next((port for port in candidates if _listening(port)), None)
    if _port is None:
        where = f"port {os.environ['ARCHICAD_PORT']}" if os.environ.get("ARCHICAD_PORT") else "ports 19723-19743"
        raise ToolError(
            f"Archicad is not running or the Tapir add-on is not loaded (no JSON API on 127.0.0.1, {where}). "
            "Start Archicad or check ARCHICAD_PORT."
        )
    return _port


def post(command, parameters):
    body = {"command": command, "parameters": parameters}
    request = urllib.request.Request(
        f"http://127.0.0.1:{find_port()}",
        json.dumps(body).encode("utf-8"),
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=setting("ARCHICAD_TIMEOUT", 300)) as response:
        return json.loads(response.read())


# Commands

def run_command(command, parameters=None):
    global _port
    if not _lock.acquire(timeout=10):
        raise ToolError(
            "Archicad is still executing a previous command. Wait and retry. "
            "Do not re-issue modifying commands blindly."
        )
    try:
        reply = post(command, parameters or {})
    except OSError as error:
        if isinstance(getattr(error, "reason", error), TimeoutError):
            raise ToolError(
                f"Archicad did not answer within {setting('ARCHICAD_TIMEOUT', 300):.0f} s. "
                "It may be busy or showing a dialog. Do not retry modifying commands blindly."
            )
        _port = None
        raise ToolError("Lost connection to Archicad. Retry once it is running.")
    finally:
        _lock.release()

    if not reply.get("succeeded"):
        raise ArchicadError(reply.get("error", {}))
    return reply["result"]


def tapir_command_id(name):
    return {"addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": name}}


def tapir_command_available(name):
    try:
        return run_command("API.IsAddOnCommandAvailable", tapir_command_id(name))["available"]
    except Exception:
        return True  # if the check itself fails, report the original error


def installed_tapir_version():
    try:
        parameters = {**tapir_command_id("GetAddOnVersion"), "addOnCommandParameters": {}}
        return run_command("API.ExecuteAddOnCommand", parameters)["addOnCommandResponse"]["version"]
    except Exception:
        return None


def run_tapir_command(name, parameters):
    try:
        result = run_command("API.ExecuteAddOnCommand", {**tapir_command_id(name), "addOnCommandParameters": parameters})
    except ArchicadError:
        if tapir_command_available(name):
            raise
        installed = installed_tapir_version()
        if installed is None:
            raise ToolError("The Tapir add-on is not loaded in Archicad. Install Tapir and restart Archicad.")
        raise ToolError(
            f"{name} is not available in the installed Tapir add-on ({installed}). "
            f"This server's definitions are for Tapir {parser.tapir_version()}. Update the Tapir add-on."
        )

    response = result.get("addOnCommandResponse")
    if isinstance(response, dict) and "error" in response:
        error = response["error"]
        raise ToolError(f"Tapir error {error.get('code')}: {error.get('message')}")
    return response
