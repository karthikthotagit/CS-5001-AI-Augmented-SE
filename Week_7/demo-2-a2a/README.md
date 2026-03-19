# A2A Code Review

Demonstrates **A2A (Agent-to-Agent Protocol)** — Google's open standard for agents to discover and communicate with each other as peers over HTTP.

---

## What This Demonstrates

| Concept | Where it appears |
|---|---|
| **Agent Card** | `GET /.well-known/agent.json` on each agent — describes name, skills, endpoint |
| **Agent discovery** | `coordinator.py` — fetches cards from known endpoints |
| **Task delegation** | `coordinator.py` — `POST /tasks/send` to delegate work |
| **Context passing** | Analyzer output passed as `context` field to Reviewer |
| **Sequential pipeline** | Analyzer → Reviewer, each agent building on the last |

---

## A2A Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  WITHOUT A2A (Week 6)                                        │
│                                                              │
│  orchestrator.py → agent_1.run() → agent_2.run()            │
│                    (direct Python function calls)            │
│                                                              │
│  All agents live in the same process.                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  WITH A2A (this demo)                                        │
│                                                              │
│  demo_review.py ──HTTP──► Analyzer Agent  (port 8101)        │
│                 ──HTTP──► Reviewer Agent  (port 8102)        │
│                                                              │
│  Each agent is an independent HTTP server.                   │
│  The coordinator discovers them via their Agent Cards.       │
└──────────────────────────────────────────────────────────────┘
```

### A2A Protocol Flow

```
Coordinator                    Analyzer (:8101)     Reviewer (:8102)
──────────────────────────────────────────────────────────────────
GET /.well-known/agent.json ──►  {name, skills, endpoint}
GET /.well-known/agent.json ──────────────────────► {name, skills, endpoint}

POST /tasks/send ───────────►  handle(task)
                               LLM call
                 ◄── result ──  {status: "completed", output: "..."}

POST /tasks/send (+ context) ──────────────────────► handle(task)
                                                      LLM call (uses context)
                             ◄────── result ─────────  {status: "completed", ...}
```

---

## Agents

| Agent | Port | Skills | Description |
|---|---|---|---|
| **Analyzer** | 8101 | `code_analysis`, `structure_extraction` | Analyses code structure and complexity |
| **Reviewer** | 8102 | `code_review`, `style_checking`, `bug_detection` | Reviews code for quality issues |
| **Coordinator** | — | — | Discovers agents, orchestrates pipeline |

---

## Project Structure

```
demo-2-a2a/
├── demo_review.py         Entry point — discovers agents, runs review pipeline
├── coordinator.py         Discovery + pipeline orchestration
├── config.py              Ports + Ollama settings via .env
├── agents/
│   ├── base.py            BaseA2AAgent: FastAPI + A2A routes + LLM helper
│   ├── analyzer.py        Analyzer agent (port 8101)
│   ├── reviewer.py        Reviewer agent (port 8102)
│   ├── run_analyzer.py    Entry point: start Analyzer server
│   └── run_reviewer.py    Entry point: start Reviewer server
├── .env.example
└── requirements.txt
```

---

## Setup

**1. Pull the model**
```bash
ollama pull qwen3:0.6b
ollama serve
```

**2. Install dependencies**
```bash
cd Week_7/demo-2-a2a
pip install -r requirements.txt
```

**3. Configure (optional)**
```bash
cp .env.example .env
# Set OLLAMA_MODEL to any model with tool-calling support
```

---

## Usage

**Terminal 1 — start the Analyzer agent**
```bash
python agents/run_analyzer.py
# A2A Analyzer agent running on http://localhost:8101
```

**Terminal 2 — start the Reviewer agent**
```bash
python agents/run_reviewer.py
# A2A Reviewer agent running on http://localhost:8102
```

**Terminal 3 — run the review**
```bash
python demo_review.py /path/to/file.py
python demo_review.py /path/to/project/
```

---

## Agent Card Example

```json
GET http://localhost:8101/.well-known/agent.json

{
  "name": "Analyzer",
  "description": "Analyses Python code structure: purpose, functions, classes, complexity.",
  "version": "1.0.0",
  "endpoint": "http://localhost:8101",
  "skills": ["code_analysis", "structure_extraction"]
}
```

## Task Submission Example

```json
POST http://localhost:8101/tasks/send

{
  "task_id": "a1b2c3d4",
  "message": "/path/to/file.py",
  "context": ""
}

→ {
  "task_id": "a1b2c3d4",
  "status": "completed",
  "output": "- **Purpose**: ...\n- **Key functions**: ...",
  "agent": "Analyzer"
}
```

---

## Step-by-Step: What the Code Does

When you run `python demo_review.py /path/to/file.py`, here is exactly what happens:

---

### Step 1 — Agents start up (each in its own terminal)

```bash
python agents/run_analyzer.py   # port 8101
python agents/run_reviewer.py   # port 8102
```

Each runner creates the agent object and calls `uvicorn.run()`:

```python
# agents/run_analyzer.py
agent = AnalyzerAgent()
uvicorn.run(agent.app, host="0.0.0.0", port=8101, log_level="info")
```

**Inside `AnalyzerAgent.__init__` → `BaseA2AAgent.__init__`:**

```python
# agents/base.py → BaseA2AAgent.__init__
self.app = FastAPI(title=f"A2A Agent: {name}")
self._register_routes()
```

`_register_routes()` attaches exactly **two HTTP routes** to the FastAPI app:

| Route | Purpose |
|---|---|
| `GET /.well-known/agent.json` | Returns the Agent Card (who I am, what I can do) |
| `POST /tasks/send` | Accepts a task, runs `handle()`, returns the result |

The agents are now running as independent HTTP servers, waiting for requests.

---

### Step 2 — `demo_review.py` creates a coordinator and calls `discover()`

```python
coord = A2ACoordinator()
agents = coord.discover()
```

**Inside `coordinator.py → discover()`:**

```python
for endpoint in KNOWN_ENDPOINTS:           # ["http://localhost:8101", "http://localhost:8102"]
    resp = httpx.get(f"{endpoint}/.well-known/agent.json", timeout=5)
    card = resp.json()                     # Agent Card JSON
    self.agents.append(card)
```

For each known endpoint, a GET request is sent to `/.well-known/agent.json`.
Each agent responds with its Agent Card:

```json
{
  "name": "Analyzer",
  "description": "Analyses Python code structure ...",
  "version": "1.0.0",
  "endpoint": "http://localhost:8101",
  "skills": ["code_analysis", "structure_extraction"]
}
```

The coordinator collects both cards and now knows which agents are available
and what they can do — without any hardcoded agent logic.

---

### Step 3 — Coordinator delegates to the Analyzer

```python
# coordinator.py → run_review()
r = self.send_task(analyzer["endpoint"], message=target)
```

**Inside `send_task()`:**

```python
payload = {
    "task_id": str(uuid.uuid4())[:8],   # e.g. "a1b2c3d4"
    "message": "/path/to/file.py",       # the file to analyse
    "context": "",                        # no prior context yet
}
resp = httpx.post(f"{endpoint}/tasks/send", json=payload, timeout=120)
```

The request hits the Analyzer agent's `POST /tasks/send` route.

**Inside `BaseA2AAgent → send_task` route handler:**

```python
# agents/base.py
output = await agent.handle(task)
return TaskResult(task_id=..., status="completed", output=output, agent="Analyzer")
```

It calls `handle(task)`, which is implemented in `AnalyzerAgent`:

```python
# agents/analyzer.py → handle()
content = p.read_text(errors="replace")[:6_000]   # read the file directly
prompt  = f"File: {p.name} ...\nCode:\n{content}\nProvide a structured analysis ..."
return self.llm_call(prompt)                        # calls Ollama
```

Back in the coordinator: `results["analysis"] = r["output"]`

---

### Step 4 — Coordinator delegates to the Reviewer (with context)

```python
# coordinator.py → run_review()
r = self.send_task(reviewer["endpoint"], message=target, context=results["analysis"])
```

The same `send_task()` call, but now `context` contains the Analyzer's full output.

**Inside `ReviewerAgent → handle()`:**

```python
# agents/reviewer.py → handle()
analysis_section = f"Prior analysis from Analyzer agent:\n{task.context}\n\n"

prompt = (
    f"{analysis_section}"                  # ← Analyzer's output injected here
    f"Code to review:\n{content}\n\n"
    "Review this code for bugs, security, style, performance ..."
)
return self.llm_call(prompt)
```

The Reviewer builds a prompt that **includes the Analyzer's output as context**,
so the LLM can reference the structural analysis when identifying issues.

Back in the coordinator: `results["review"] = r["output"]`

---

### Step 5 — `demo_review.py` prints both results

```python
console.print(Panel(Markdown(results["analysis"]), title="Analyzer Agent", border_style="blue"))
console.print(Panel(Markdown(results["review"]),   title="Reviewer Agent", border_style="magenta"))
```

---

### Full execution timeline

```
demo_review.py (coordinator)   Analyzer (:8101)               Reviewer (:8102)
──────────────────────────────────────────────────────────────────────────────
discover()
  GET /.well-known/agent.json ──►  AgentCard JSON
  GET /.well-known/agent.json ──────────────────────────────────────────────►
                                                              AgentCard JSON

run_review(target)
  send_task(analyzer, msg)  ──► POST /tasks/send
                                  handle(task)
                                    read file
                                    llm_call(prompt) ──► Ollama /api/chat
                                                    ◄──  LLM response
                              ◄── TaskResult{output}

  send_task(reviewer, msg,   ───────────────────────────────► POST /tasks/send
            context=analysis)                                   handle(task)
                                                                  read file
                                                                  llm_call(analysis+code)
                                                                         ──► Ollama
                                                                        ◄──  response
                             ◄──────────────────────────────── TaskResult{output}

print results
```

---

## How Context Passing Works

The Reviewer receives the Analyzer's output via the `context` field:

```python
# coordinator.py
analysis_result = send_task(analyzer_endpoint, message=target)

# Analyzer's output is injected as context for the Reviewer
review_result = send_task(
    reviewer_endpoint,
    message=target,
    context=analysis_result["output"],   # ← A2A context passing
)
```

Inside the Reviewer agent, this context is prepended to the LLM prompt:
```
Prior analysis from Analyzer agent:
  - Purpose: ...
  - Key functions: ...

Code to review:
  <source code>

Review this code for bugs, style, security ...
```

---

## Stack

- **Protocol:** [A2A (Agent-to-Agent)](https://google.github.io/A2A/) — custom lightweight implementation
- **API:** [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **HTTP:** [httpx](https://www.python-httpx.org/) (coordinator → agents)
- **LLM:** `qwen3:0.6b` via [Ollama](https://ollama.com/) REST API
