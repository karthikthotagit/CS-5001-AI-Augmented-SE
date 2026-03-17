"""
Tool schemas — the only place tool names, descriptions, and parameter
shapes are defined. server/app.py and server/handlers.py both derive
from this file; nothing else needs to change when a tool is added.
"""

TOOLS = [
    {
        "name": "read_file",
        "description": "Read the content of a source file (capped at 8 000 chars).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute or relative file path"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and subdirectories inside a directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "grep_code",
        "description": "Search for a text pattern inside Python files under a directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Search term or regex"},
                "path":    {"type": "string", "description": "Root directory to search"},
            },
            "required": ["pattern", "path"],
        },
    },
]
