"""
Base A2A Agent — FastAPI server implementing the A2A protocol.

Every A2A agent exposes:
  GET  /.well-known/agent.json  →  Agent Card (who I am, what I can do)
  POST /tasks/send              →  Submit a task (message + optional context)

The coordinator uses the Agent Card for discovery and /tasks/send for delegation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import OLLAMA_HOST, OLLAMA_MODEL


# ---------------------------------------------------------------------------
# Shared data models (follow A2A protocol schema)
# ---------------------------------------------------------------------------

class Task(BaseModel):
    task_id: str
    message: str                   # the request sent to this agent
    context: str = ""              # optional: prior agent output to build on


class TaskResult(BaseModel):
    task_id: str
    status: str                    # "completed" | "failed"
    output: str
    agent: str


class AgentCard(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"
    endpoint: str
    skills: list[str]


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class BaseA2AAgent(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        skills: list[str],
        port: int,
    ) -> None:
        self.name        = name
        self.description = description
        self.skills      = skills
        self.port        = port
        self.app         = FastAPI(title=f"A2A Agent: {name}")
        self._register_routes()

    # ------------------------------------------------------------------
    # Route registration
    # ------------------------------------------------------------------

    def _register_routes(self) -> None:
        agent = self

        @self.app.get("/.well-known/agent.json", response_model=AgentCard)
        async def agent_card() -> AgentCard:
            return AgentCard(
                name=agent.name,
                description=agent.description,
                endpoint=f"http://localhost:{agent.port}",
                skills=agent.skills,
            )

        @self.app.post("/tasks/send", response_model=TaskResult)
        async def send_task(task: Task) -> TaskResult:
            try:
                output = await agent.handle(task)
                return TaskResult(
                    task_id=task.task_id,
                    status="completed",
                    output=output,
                    agent=agent.name,
                )
            except Exception as exc:
                return TaskResult(
                    task_id=task.task_id,
                    status="failed",
                    output=str(exc),
                    agent=agent.name,
                )

    # ------------------------------------------------------------------
    # LLM helper — shared by all agents
    # ------------------------------------------------------------------

    async def llm_call(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
            )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    # ------------------------------------------------------------------
    # Subclasses implement this
    # ------------------------------------------------------------------

    @abstractmethod
    async def handle(self, task: Task) -> str:
        """Process an incoming task and return a text result."""
        ...
