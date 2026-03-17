"""
Analyzer A2A Agent (port 8101)

Skills: code_analysis, structure_extraction

Given a file or directory path, this agent reads the source code and
produces a structured analysis: purpose, functions/classes, complexity.
"""
from pathlib import Path

from agents.base import BaseA2AAgent, Task
from config import ANALYZER_PORT


class AnalyzerAgent(BaseA2AAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Analyzer",
            description="Analyses Python code structure: purpose, functions, classes, complexity.",
            skills=["code_analysis", "structure_extraction"],
            port=ANALYZER_PORT,
        )

    async def handle(self, task: Task) -> str:
        target = task.message.strip()
        p = Path(target)

        if p.is_file():
            content  = p.read_text(errors="replace")[:6_000]
            file_info = f"File: {p.name} ({p.stat().st_size} bytes)"
        elif p.is_dir():
            py_files = sorted(p.glob("**/*.py"))
            content  = "\n\n".join(
                f"# {f.name}\n{f.read_text(errors='replace')[:2_000]}"
                for f in py_files[:3]
            )
            file_info = f"Directory: {p.name} ({len(py_files)} Python files)"
        else:
            return f"Path not found: {target}"

        prompt = (
            f"{file_info}\n\n"
            f"Code:\n{content}\n\n"
            "Provide a concise structured analysis using bullet points:\n"
            "- **Purpose**: what does this code do?\n"
            "- **Key functions / classes** found\n"
            "- **Complexity**: Low / Medium / High — brief reason\n"
            "- **Lines of code** (estimate)\n"
        )
        return await self.llm_call(prompt)
