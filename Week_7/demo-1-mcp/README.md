# MCP Code Analysis

Demonstrates **MCP (Model Context Protocol)** — Anthropic's open standard for connecting AI agents to external tools via a structured, language-agnostic protocol. An LLM-driven agent analyses Python codebases by invoking file-system tools exposed over a local MCP server.

---

## Prerequisites

- [Ollama](https://ollama.com/) running locally
- A model with tool-calling support (eg: `qwen3:0.6b`)
- Python 3.10+

---

## Setup

**1. Start Ollama and pull a model**
```bash
ollama serve
ollama pull qwen3:0.6b
```

**2. Install dependencies**
```bash
cd Week_7/demo-1-mcp
pip install -r requirements.txt
```

**3. Configure (optional)**
```bash
cp .env.example .env
# Set OLLAMA_MODEL to any model with tool-calling support
```

---

## Usage

The server runs independently over HTTP/SSE and accepts connections from any MCP client —
this agent, Claude Desktop, Cursor, or any other tool.

**Terminal 1 — start the server**
```bash
python server/http_app.py
# MCP server listening on http://localhost:8050/sse
```

**Terminal 2 — Client 1: LLM-driven code analysis**
```bash
python demo_client1.py /path/to/project/
python demo_client1.py /path/to/a/file
python demo_client1.py server/app.py
python demo_client1.py server/app.py --verbose
```

**Terminal 2 — Client 2: programmatic code search (no LLM)**
```bash
python demo_client2.py "import asyncio" /path/to/project/
python demo_client2.py "import asyncio" /path/to/a/file
python demo_client2.py "def " .
```

**Connecting Claude Desktop** — add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "code-tools": {
      "url": "http://localhost:8050/sse"
    }
  }
}
```

---

## Architecture

The server runs on a port over HTTP/SSE. Any MCP-compatible client can connect to it —
this agent, Claude Desktop, Cursor, or any tool that speaks MCP.

```
┌──────────────────────────────────────────────────────────────────┐
│  HTTP / SSE transport                                            │
│                                                                  │
│  server/http_app.py  running on :8050                           │
│         ▲                                                        │
│         ├── demo_client1.py  (Client 1 — LLM-driven)            │
│         ├── demo_client2.py  (Client 2 — programmatic)          │
│         ├── Claude Desktop                                       │
│         └── Cursor / any MCP client                             │
│                                                                  │
│  Multiple clients can connect to the same running server.        │
└──────────────────────────────────────────────────────────────────┘
```

### Two Clients, One Server

Both clients connect to the same MCP server via `MCPSession`. The server is unaware of which client is calling it.

| | Client 1 (`client/`) | Client 2 (`client2/`) |
|---|---|---|
| **Use case** | Code analysis | Code search |
| **Who decides tool calls** | LLM (based on task + schemas) | Python (hardcoded sequence) |
| **LLM required** | Yes | No |
| **Entry point** | `python demo_client1.py <path>` | `python demo_client2.py <pattern> <path>` |
| **Key file** | `client/loop.py` | `client2/search.py` |

---

### Client 1 — `client/` (LLM-driven)

The client is split across two files: `client/session.py` (connection and tool calls) and `client/loop.py` (agentic loop logic).

#### `client/session.py` — MCPSession

Manages the MCP connection lifecycle and exposes three methods:

| Method | What it does |
|---|---|
| `list_tools()` | Sends `tools/list` to the server; returns `[{name, description}]` |
| `tools_for_ollama()` | Same as `list_tools()` but converts each schema to Ollama's `{"type": "function", "function": {...}}` format so the LLM can understand them |
| `call_tool(name, **args)` | Sends `tools/call` to the server with the tool name and arguments; returns the result as a plain string |

On `__aenter__`, it opens an SSE connection to the running server and performs the MCP handshake (`session.initialize()`).

#### `client/loop.py` — AgenticLoop

Runs the tool-calling loop. The full message history is kept in a `messages` list that grows with each round-trip:

```
messages = [
  {role: "user",      content: "Analyse server/app.py ..."}   ← initial task

  # --- round 1 ---
  {role: "assistant", tool_calls: [{read_file}, {list_directory}]}   ← LLM requests tools
  {role: "tool",      content: "<file content>"}                     ← MCP result
  {role: "tool",      content: "<directory listing>"}                ← MCP result

  # --- round 2 ---
  {role: "assistant", content: "Here is the analysis ..."}    ← no tool_calls → loop ends
]
```

Each iteration:
1. `llm.chat(messages, tools)` — full history + tool schemas sent to Ollama
2. If the response contains `tool_calls` → execute each via `session.call_tool()`, append results, continue
3. If the response contains only `content` → return it as the final answer

---

### Client 2 — `client2/search.py` (programmatic)

**Use case:** find all occurrences of a pattern in a codebase and read every matched file.

Python explicitly controls every tool call — the sequence is always the same regardless of input:

```
Step 1 — grep_code(pattern, path)
         → returns matched lines with file paths and line numbers

Step 2 — extract unique file paths from grep output

Step 3 — read_file(path) for each matched file (up to 5)
         → returns file contents

Step 4 — return structured report {matches, files_read}
```

No LLM, no dynamic decision-making. The value of MCP here is that the same server tools
are reused — `grep_code` and `read_file` are called over the same MCP protocol, from a
completely different client with a completely different purpose.

---

## Project Structure

```
demo-1-mcp/
├── demo_client1.py     Entry point — Client 1 (LLM-driven analysis)
├── demo_client2.py     Entry point — Client 2 (programmatic search)
├── agent.py            Orchestrator — composes session, loop, and LLM client
├── llm.py              Ollama HTTP client
├── config.py           Configuration — reads OLLAMA_HOST / OLLAMA_MODEL / MCP_PORT from .env
├── server/
│   ├── app.py          MCP server — tool registration and request handling
│   ├── http_app.py     MCP server (HTTP/SSE) — exposes app.py on MCP_PORT
│   ├── handlers.py     Tool implementations — read_file, list_directory, grep_code
│   └── schemas.py      Tool definitions — names, descriptions, input schemas
├── client/
│   ├── session.py      MCP session — HTTP/SSE transport, list_tools, call_tool
│   └── loop.py         Agentic loop — LLM ↔ MCP round-trip until completion
├── client2/
│   └── search.py       Programmatic client — grep + read, no LLM
├── .env.example
└── requirements.txt
```

### Responsibilities

| Module | Responsibility |
|---|---|
| `demo_client1.py` | Entry point for Client 1 — argument parsing, runs LLM-driven analysis |
| `demo_client2.py` | Entry point for Client 2 — argument parsing, runs programmatic search |
| `agent.py` | Composition — wires `MCPSession`, `AgenticLoop`, and `OllamaClient` |
| `client/session.py` | MCP protocol — HTTP/SSE transport, tool invocation |
| `client/loop.py` | LLM-driven loop — sends task + schemas to LLM, executes tool_calls |
| `client2/search.py` | Programmatic client — hardcoded grep → read sequence, no LLM |
| `llm.py` | LLM interface — HTTP calls to Ollama `/api/chat` |
| `server/app.py` | MCP server — tool registration and request handling |
| `server/http_app.py` | Raw ASGI app — routes `/sse` and `/messages/` to the MCP SSE transport |
| `server/handlers.py` | Tool logic — pure Python functions, no MCP dependency |
| `server/schemas.py` | Tool contracts — names, descriptions, and JSON Schema definitions |

---

## Available Tools

| Tool | Description |
|---|---|
| `read_file` | Read the contents of a source file (capped at 8 000 chars) |
| `list_directory` | List files and subdirectories at a given path |
| `grep_code` | Search for a text pattern across `.py` files |

To add a tool: define its schema in `server/schemas.py` and implement a matching
function in `server/handlers.py`. No other files require modification.

---

## Comparison with Week 6

| | Week 6 (context-gather) | Client 1 — `client/loop.py` | Client 2 — `client2/search.py` |
|---|---|---|---|
| **Tool location** | Same process, imported directly | Separate process via MCP | Separate process via MCP |
| **Tool selection** | Python hardcodes the calls | LLM decides based on tool schemas | Python hardcodes the calls |
| **LLM required** | Yes | Yes | No |
| **LLM calls** | One call with all context pre-assembled | Multiple; loop ends when LLM returns no tool_calls | None |
| **Use case** | Code analysis | Code analysis | Code search |
| **Replaceability** | Tools tightly coupled to the agent | Server replaceable with any MCP implementation | Server replaceable with any MCP implementation |
