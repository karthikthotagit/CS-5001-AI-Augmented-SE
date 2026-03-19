#!/usr/bin/env python3
"""
Client 1 — LLM-driven code analysis.

The agent connects to the MCP server, asks the LLM to analyse the target,
and the LLM decides which tools to call (read_file, list_directory, grep_code).

Usage:
    python demo_client1.py server/app.py
    python demo_client1.py server/app.py --verbose
    python demo_client1.py /path/to/project/
"""
import argparse
import asyncio

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agent import MCPAgent
from client.session import DEFAULT_URL

console = Console()


async def main(target: str, verbose: bool, server_url: str) -> None:
    console.print(Panel.fit("[bold cyan]MCP Code Analysis — Client 1[/]", subtitle=server_url))

    async with MCPAgent(server_url) as agent:
        if verbose:
            tools = await agent.list_tools()
            console.print(f"[dim]Tools: {[t['name'] for t in tools]}[/]")
        report = await agent.analyse(target, verbose=verbose)

    console.print(Panel(Markdown(report), title="Analysis Report", border_style="green"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse Python code via MCP (LLM-driven)")
    parser.add_argument("target", help="File or directory to analyse")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print MCP tool calls as they execute")
    parser.add_argument("--server-url", default=DEFAULT_URL, metavar="URL", help=f"MCP server SSE URL (default: {DEFAULT_URL})")
    args = parser.parse_args()

    asyncio.run(main(args.target, args.verbose, args.server_url))
