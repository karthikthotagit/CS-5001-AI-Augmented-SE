"""
Agentic Tool Loop

Drives the LLM ↔ MCP round-trip:
  1. Send task + tool schemas to the LLM
  2. LLM returns tool_calls  → execute each via MCPSession → append results
  3. Send updated history back to the LLM
  4. Repeat until the LLM returns a plain-text response (no tool_calls)

Depends on MCPSession (tool execution) and OllamaClient (LLM calls) only
via their public interfaces — no MCP or httpx imports here.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.session import MCPSession
    from llm import OllamaClient


class AgenticLoop:
    def __init__(self, session: "MCPSession", llm: "OllamaClient") -> None:
        self.session = session
        self.llm     = llm

    async def run(self, task: str, verbose: bool = False) -> str:
        tools    = await self.session.tools_for_ollama()
        messages = [{"role": "user", "content": task}]

        def log(msg: str) -> None:
            if verbose:
                print(f"  {msg}")

        while True:
            log(f"[LLM]  Sending {len(messages)} message(s) …")
            msg = await self.llm.chat(messages, tools=tools)

            tool_calls = msg.get("tool_calls")
            if not tool_calls:
                return msg.get("content", "")

            # Record the assistant's decision in history
            messages.append({
                "role": "assistant",
                "content": msg.get("content", ""),
                "tool_calls": tool_calls,
            })

            # Execute each requested tool via MCP
            for tc in tool_calls:
                fn   = tc["function"]
                name = fn["name"]
                args = fn["arguments"]
                log(f"[MCP]  {name}({args})")
                result = await self.session.call_tool(name, **args)
                messages.append({"role": "tool", "content": result})
