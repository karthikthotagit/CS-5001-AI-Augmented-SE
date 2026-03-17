"""
A2A Coordinator

Discovers available A2A agents, then orchestrates a sequential code-review
pipeline by delegating tasks via HTTP.

Discovery:
  Each agent exposes GET /.well-known/agent.json  →  Agent Card
  The coordinator fetches these to learn what agents are available.

Delegation:
  POST /tasks/send  with  {task_id, message, context}
  The agent returns      {task_id, status, output, agent}
"""
from __future__ import annotations

import uuid

import httpx
from rich.console import Console

from config import ANALYZER_PORT, REVIEWER_PORT

console = Console()

KNOWN_ENDPOINTS = [
    f"http://localhost:{ANALYZER_PORT}",
    f"http://localhost:{REVIEWER_PORT}",
]


class A2ACoordinator:
    def __init__(self) -> None:
        self.agents: list[dict] = []

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover(self) -> list[dict]:
        """Fetch Agent Cards from all known endpoints."""
        self.agents = []
        for endpoint in KNOWN_ENDPOINTS:
            try:
                resp = httpx.get(
                    f"{endpoint}/.well-known/agent.json", timeout=5
                )
                resp.raise_for_status()
                card = resp.json()
                card["endpoint"] = endpoint
                self.agents.append(card)
                console.print(
                    f"  [green]✓[/] [bold]{card['name']}[/]"
                    f"  skills={card['skills']}"
                    f"  → {endpoint}"
                )
            except Exception as exc:
                console.print(f"  [red]✗[/] {endpoint}: {exc}")
        return self.agents

    # ------------------------------------------------------------------
    # Task delegation
    # ------------------------------------------------------------------

    def send_task(
        self, endpoint: str, message: str, context: str = ""
    ) -> dict:
        """Send a task to an A2A agent and return the result dict."""
        payload = {
            "task_id": str(uuid.uuid4())[:8],
            "message": message,
            "context": context,
        }
        resp = httpx.post(
            f"{endpoint}/tasks/send", json=payload, timeout=120
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    def run_review(self, target: str) -> dict[str, str]:
        """
        Sequential review pipeline:
          Analyzer  →  Reviewer (receives Analyzer output as context)
        """
        analyzer = next(
            (a for a in self.agents if a["name"] == "Analyzer"), None
        )
        reviewer = next(
            (a for a in self.agents if a["name"] == "Reviewer"), None
        )

        results: dict[str, str] = {}

        if analyzer:
            console.print("\n[cyan]→ Analyzer[/]  sending task …")
            r = self.send_task(analyzer["endpoint"], message=target)
            results["analysis"] = r["output"]
            console.print("[green]  ✓ Analysis complete[/]")

        if reviewer:
            console.print("[cyan]→ Reviewer[/]  sending task (with analysis context) …")
            context = results.get("analysis", "")
            r = self.send_task(reviewer["endpoint"], message=target, context=context)
            results["review"] = r["output"]
            console.print("[green]  ✓ Review complete[/]")

        return results
