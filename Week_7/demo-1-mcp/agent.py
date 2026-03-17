"""
MCPAgent — orchestrator

Composes MCPSession, AgenticLoop, and OllamaClient.
Connects to a running MCP server via HTTP/SSE.

Usage:
    async with MCPAgent() as agent: ...                              # default port
    async with MCPAgent("http://localhost:8050/sse") as agent: ...  # explicit URL
"""
from __future__ import annotations

from client.loop import AgenticLoop
from client.session import MCPSession, DEFAULT_URL
from llm import OllamaClient


class MCPAgent:
    def __init__(self, url: str = DEFAULT_URL) -> None:
        self._session = MCPSession(url)
        self._loop: AgenticLoop | None = None

    async def analyse(self, target: str, verbose: bool = False) -> str:
        task = (
            f"Analyse the Python code at: {target}\n\n"
            "Use the available tools to explore the code. Then provide:\n"
            "1. What the code does (2-3 sentences)\n"
            "2. Quality or style issues found\n"
            "3. Three concrete improvement suggestions"
        )
        return await self._loop.run(task, verbose=verbose)

    async def list_tools(self) -> list[dict]:
        return await self._session.list_tools()

    async def __aenter__(self) -> "MCPAgent":
        await self._session.__aenter__()
        self._loop = AgenticLoop(self._session, OllamaClient())
        return self

    async def __aexit__(self, *args) -> None:
        await self._session.__aexit__(*args)
