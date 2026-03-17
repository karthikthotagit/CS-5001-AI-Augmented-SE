#!/usr/bin/env python3
"""
MCP Server — HTTP / SSE transport

Exposes the same tools as app.py (stdio) over HTTP + Server-Sent Events,
so any MCP-compatible client can connect by URL — not just the process
that spawned the server.

    Claude Desktop  ─┐
    Cursor          ─┼──► http://localhost:8050/sse
    agent.py        ─┘

Usage:
    python server/http_app.py          # starts on MCP_PORT (default 8050)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from mcp.server.sse import SseServerTransport

from server.app import app   # reuse the same registered MCP Server instance
from config import MCP_PORT

sse = SseServerTransport("/messages/")


class MCPHttpApp:
    """
    Raw ASGI app — routes two paths to the MCP SSE transport:

      GET  /sse          — opens the SSE stream; MCP client connects here
      POST /messages/... — MCP client sends JSON-RPC messages here
    """

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            return

        path = scope.get("path", "")

        if path == "/sse":
            async with sse.connect_sse(scope, receive, send) as streams:
                await app.run(
                    streams[0],
                    streams[1],
                    app.create_initialization_options(),
                )

        elif path.startswith("/messages/"):
            await sse.handle_post_message(scope, receive, send)


http_app = MCPHttpApp()


if __name__ == "__main__":
    print(f"MCP server listening on http://localhost:{MCP_PORT}/sse")
    uvicorn.run(http_app, host="0.0.0.0", port=MCP_PORT)
