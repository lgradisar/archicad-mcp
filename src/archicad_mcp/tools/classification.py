import re

from mcp.types import ToolAnnotations

NOT_READ_ONLY = {"GetScriptUIResult", "GetPointFromUser"}
READ_ONLY = {"FilterElements"}
ADDITIVE_PREFIXES = ("Create", "Add", "Attach", "Clone")

DANGEROUS_PREFIXES = ("Delete", "Save", "Close", "Open", "Import", "Export", "Teamwork", "Publish", "Print", "Quit", "Show")
DANGEROUS = {
    "IFCFileOperation", "GenerateDocumentation", "ChangeDrawingLink", "SetStories",
    "AddFilesToEmbeddedLibrary", "SetLibraries", "ReserveElements", "ReleaseElements",
    "SetElementNotificationClient", "GetPointFromUser",
}

SLOW = {
    "ReloadLibraries", "PublishPublisherSet", "UpdateDrawings", "UpdateZones",
    "GenerateDocumentation", "TeamworkSend", "TeamworkReceive", "IFCFileOperation",
}
INTERACTIVE = {"ShowAlert", "ShowScriptUI", "GetPointFromUser"}

SLOW_NOTE = " May take longer than the client's time limit; if the client reports a timeout, Archicad is still working."
INTERACTIVE_NOTE = " Blocks Archicad until the user responds in the Archicad window."


def is_read_only(name):
    return (name.startswith("Get") and name not in NOT_READ_ONLY) or name in READ_ONLY


def is_dangerous(name):
    return name.startswith(DANGEROUS_PREFIXES) or name in DANGEROUS


def tags(name):
    result = set()
    if is_read_only(name):
        result.add("readonly")
    if is_dangerous(name):
        result.add("dangerous")
    return result


def annotations(name):
    if is_read_only(name):
        return ToolAnnotations(readOnlyHint=True, destructiveHint=False)
    if name.startswith(ADDITIVE_PREFIXES) and not is_dangerous(name):
        return ToolAnnotations(destructiveHint=False)
    return None


def description(name, text):
    if name in SLOW:
        text += SLOW_NOTE
    if name in INTERACTIVE:
        text += INTERACTIVE_NOTE
    words = " ".join(re.findall(r"[A-Z][a-z]+|[A-Z]+(?![a-z])|\d+", name)).lower()
    return f"{text} Keywords: {words}."
