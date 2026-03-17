"""
Reviewer A2A Agent (port 8102)

Skills: code_review, style_checking, bug_detection

Given a file or directory path (and optionally the Analyzer's output as
context), this agent reviews the code for quality, style, and bugs.
"""
from pathlib import Path

from agents.base import BaseA2AAgent, Task
from config import REVIEWER_PORT


class ReviewerAgent(BaseA2AAgent):
    def __init__(self) -> None:
        super().__init__(
            name="Reviewer",
            description="Reviews Python code for quality, style, and correctness issues.",
            skills=["code_review", "style_checking", "bug_detection"],
            port=REVIEWER_PORT,
        )

    async def handle(self, task: Task) -> str:
        target = task.message.strip()
        p = Path(target)

        if p.is_file():
            content = p.read_text(errors="replace")[:6_000]
        elif p.is_dir():
            py_files = sorted(p.glob("**/*.py"))
            content  = "\n\n".join(
                f"# {f.name}\n{f.read_text(errors='replace')[:2_000]}"
                for f in py_files[:3]
            )
        else:
            return f"Path not found: {target}"

        analysis_section = (
            f"Prior analysis from Analyzer agent:\n{task.context}\n\n"
            if task.context else ""
        )

        prompt = (
            f"{analysis_section}"
            f"Code to review:\n{content}\n\n"
            "Review this code. For each finding state the severity "
            "(Critical / High / Medium / Low):\n"
            "1. Bugs or logic errors\n"
            "2. Security issues\n"
            "3. Style / readability problems\n"
            "4. Performance concerns\n\n"
            "Provide 3-5 specific, actionable findings. Be concise."
        )
        return await self.llm_call(prompt)
