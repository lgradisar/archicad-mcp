"""Download the Tapir command definitions for a release tag.

Usage: uv run scripts/update_tapir.py 1.5.9
"""

import sys
import urllib.request
from pathlib import Path

REPO = "https://raw.githubusercontent.com/ENZYME-APD/tapir-archicad-automation"
FILES = ["command_definitions.js", "common_schema_definitions.js"]
TARGET = Path(__file__).resolve().parents[1] / "src" / "archicad_mcp" / "tapir"


def main(tag):
    for name in FILES:
        with urllib.request.urlopen(f"{REPO}/{tag}/docs/archicad-addon/{name}", timeout=60) as response:
            (TARGET / name).write_bytes(response.read())
    (TARGET / "TAPIR_VERSION").write_text(tag + "\n", newline="\n")

    from archicad_mcp.tapir import COMMANDS
    print(f"Tapir {tag}: {len(COMMANDS)} commands ready")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
