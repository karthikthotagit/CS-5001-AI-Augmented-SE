#!/usr/bin/env python3
"""
Client 2 — programmatic code search (no LLM).

Python explicitly orchestrates every tool call — grep for the pattern,
then read each matched file. No LLM involved.

Usage:
    python demo_client2.py "def " .
    python demo_client2.py "import asyncio" /path/to/project/
"""
import argparse
import asyncio

from rich.console import Console
from rich.panel import Panel

from client.session import DEFAULT_URL, MCPSession
from client2.search import SearchClient

console = Console()


async def main(pattern: str, path: str, server_url: str) -> None:
    console.print(Panel.fit("[bold yellow]MCP Code Search — Client 2[/]", subtitle=server_url))

    async with MCPSession(server_url) as session:
        result = await SearchClient(session).search(pattern, path)

    console.print(f"\n[bold]Pattern:[/] {result['pattern']}  [bold]Path:[/] {result['path']}\n")
    console.print(Panel(result["matches"] or "No matches found.", title="Matches", border_style="yellow"))

    for filepath, content in result["files_read"].items():
        console.print(Panel(content, title=f"[dim]{filepath}[/]", border_style="dim"))

    if result["truncated"]:
        console.print("[dim](results truncated — showing first 5 files)[/]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search code via MCP (programmatic, no LLM)")
    parser.add_argument("pattern", help="Pattern to search for")
    parser.add_argument("path", help="Directory to search in")
    parser.add_argument("--server-url", default=DEFAULT_URL, metavar="URL", help=f"MCP server SSE URL (default: {DEFAULT_URL})")
    args = parser.parse_args()

    asyncio.run(main(args.pattern, args.path, args.server_url))
