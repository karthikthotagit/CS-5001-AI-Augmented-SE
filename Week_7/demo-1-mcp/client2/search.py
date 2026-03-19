"""
Programmatic MCP Client — Code Search

Use case: search a codebase for a pattern, read every matched file,
and return a structured report.

Python orchestrates every tool call explicitly — no LLM is involved.
Compare with client/loop.py where the LLM decides what to call and when.

  client/loop.py   → LLM receives tool schemas → LLM decides → loop
  client2/search.py → Python hardcodes the sequence → grep → read → report
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.session import MCPSession

MAX_FILES = 5   # cap file reads to avoid flooding the terminal


class SearchClient:
    """
    Programmatic client: searches for a pattern via MCP tools and
    returns a structured report without involving an LLM.

    Tool call sequence (always the same, decided by Python):
      1. grep_code(pattern, path)       → find matching lines
      2. read_file(path) × N            → read each matched file (up to MAX_FILES)
    """

    def __init__(self, session: "MCPSession") -> None:
        self.session = session

    async def search(self, pattern: str, path: str) -> dict:
        """Search for pattern in path and return a structured report."""

        # Step 1 — find matches
        raw_matches = await self.session.call_tool(
            "grep_code", pattern=pattern, path=path
        )

        # Step 2 — extract unique file paths from grep output
        #   grep output lines: "path/to/file.py:42:   def foo():"
        files: list[str] = []
        for line in raw_matches.splitlines():
            if ":" in line:
                filepath = line.split(":")[0]
                if filepath not in files:
                    files.append(filepath)

        # Step 3 — read each matched file (capped)
        file_contents: dict[str, str] = {}
        for filepath in files[:MAX_FILES]:
            file_contents[filepath] = await self.session.call_tool(
                "read_file", path=filepath
            )

        return {
            "pattern":  pattern,
            "path":     path,
            "matches":  raw_matches,
            "files_read": file_contents,
            "truncated": len(files) > MAX_FILES,
        }
