"""
Tool handlers — pure Python functions, one per tool.

Function names must match the tool names in schemas.py exactly;
app.py dispatches by name using getattr(handlers, name).

No MCP imports here — these are plain functions that can be
tested independently of the MCP server.
"""
import subprocess
from pathlib import Path

MAX_FILE_CHARS = 8_000


def read_file(path: str) -> str:
    return Path(path).read_text(errors="replace")[:MAX_FILE_CHARS]


def list_directory(path: str) -> str:
    entries = sorted(Path(path).iterdir(), key=lambda e: (e.is_file(), e.name))
    lines   = [f"{'DIR ' if e.is_dir() else 'FILE'} {e.name}" for e in entries]
    return "\n".join(lines) or "(empty)"


def grep_code(pattern: str, path: str) -> str:
    result = subprocess.run(
        ["grep", "-rH", "--include=*.py", "-n", pattern, path],
        capture_output=True, text=True, timeout=15,
    )
    return result.stdout.strip() or "No matches found."
