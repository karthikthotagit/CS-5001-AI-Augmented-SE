"""
Ollama LLM Client

Thin wrapper around the Ollama /api/chat HTTP endpoint.
Returns the raw message dict so callers can inspect both
'content' and 'tool_calls' without re-parsing.
"""
from __future__ import annotations

import httpx

from config import OLLAMA_HOST, OLLAMA_MODEL


class OllamaClient:
    def __init__(
        self,
        host: str  = OLLAMA_HOST,
        model: str = OLLAMA_MODEL,
    ) -> None:
        self.host  = host
        self.model = model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """Send messages to Ollama. Returns the message dict
        (has 'content' and optionally 'tool_calls')."""
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.host}/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()["message"]
