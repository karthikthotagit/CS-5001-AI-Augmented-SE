from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .llm import OllamaLLM
from .prompts import draft_code_prompt, plan_prompt, review_and_fix_prompt
from .tools import Tools
from .types import AgentConfig, RunResult
from .utils import strip_code_fences


class Agent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self.repo = Path(cfg.repo).resolve()
        self.tools = Tools(self.repo)

    def _log(self, message: Any) -> None:
        if self.cfg.verbose:
            print(message)

    def _llm(self) -> OllamaLLM:
        return OllamaLLM(model=self.cfg.model, host=self.cfg.host, temperature=self.cfg.temperature)

    def _call_llm(self, prompt: str) -> str:
        return self._llm().generate(prompt)

    def _multi_step_chain(self) -> Callable[[str], str]:
        """Return a simple Runnable-like callable built with langchain-core if available."""
        try:
            from langchain_core.runnables import RunnableLambda  # type: ignore
        except Exception:  # pragma: no cover
            return self._call_llm

        # Keep it minimal: a RunnableLambda that calls our existing OllamaLLM wrapper.
        return RunnableLambda(self._call_llm).invoke  # type: ignore[return-value]

    def _generate_project_files(self, desc: str, module_path: str) -> None:
        """Generate project scaffolding files using LLM."""
        print("📦 Generating project files...")
        
        run = self._multi_step_chain()
        
        # Generate requirements.txt
        req_prompt = f"""Given this project description: "{desc}"

The main module is at: {module_path}

Generate a requirements.txt file with the necessary Python dependencies.
Consider what libraries would be needed based on the description.

Respond ONLY with the contents of requirements.txt (package names and versions).
Example format:
requests>=2.31.0
pandas>=2.0.0

Requirements.txt content:"""
        
        try:
            requirements = run(req_prompt).strip()
            requirements = strip_code_fences(requirements)
            if requirements and len(requirements) < 1000:  # Sanity check
                self.tools.write("requirements.txt", requirements)
                print("  ✓ requirements.txt")
        except Exception as e:
            self._log(f"Could not generate requirements.txt: {e}")
        
        # Generate README.md
        readme_prompt = f"""Given this project description: "{desc}"

The main module is at: {module_path}

Generate a brief README.md file that includes:
1. Project title
2. Brief description
3. Installation instructions (pip install -r requirements.txt)
4. Basic usage example
5. Project structure

Keep it concise (under 200 lines).

README.md content:"""
        
        try:
            readme = run(readme_prompt).strip()
            readme = strip_code_fences(readme)
            if readme and len(readme) < 5000:  # Sanity check
                self.tools.write("README.md", readme)
                print("  ✓ README.md")
        except Exception as e:
            self._log(f"Could not generate README.md: {e}")
        
        # Generate .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Environment
.env
.env.local

# Logs
*.log
"""
        try:
            self.tools.write(".gitignore", gitignore_content)
            print("  ✓ .gitignore")
        except Exception as e:
            self._log(f"Could not generate .gitignore: {e}")

    def create_program(self, desc: str, module_path: str) -> RunResult:
        """Multi-step create:
        0) generate project scaffolding (requirements.txt, README.md, .gitignore)
        1) produce a plan
        2) draft code
        3) review and fix code
        4) write to disk
        """
        # Check if this is a new project (no existing code)
        existing = self.tools.read(module_path)
        is_new_project = not existing
        
        # Generate project files for new projects
        if is_new_project:
            self._generate_project_files(desc, module_path)

        run = self._multi_step_chain()

        p1 = plan_prompt(desc=desc, existing=existing, module_path=module_path)
        self._log(p1)
        plan = run(p1).strip()
        if not plan:
            return RunResult(False, "Model returned empty plan.")

        p2 = draft_code_prompt(desc=desc, existing=existing, module_path=module_path, plan=plan)
        self._log(p2)
        draft_raw = run(p2)
        self._log(draft_raw)
        draft = strip_code_fences(draft_raw)
        if not draft.strip():
            return RunResult(False, "Model returned empty module draft.")

        p3 = review_and_fix_prompt(desc=desc, module_path=module_path, plan=plan, code=draft)
        self._log(p3)
        final_raw = run(p3)
        self._log(final_raw)
        final_code = strip_code_fences(final_raw).rstrip() + "\n"
        if not final_code.strip():
            return RunResult(False, "Model returned empty final module.")

        self.tools.write(module_path, final_code)
        return RunResult(True, f"Wrote module: {module_path}")

    def commit_and_push(self, message: str, push: bool) -> RunResult:
        ok, out = self.tools.git_commit(message)
        if not ok:
            return RunResult(False, out)

        if push:
            ok2, out2 = self.tools.git_push()
            if not ok2:
                return RunResult(False, "Commit succeeded, but push failed:\n" + out2)
            return RunResult(True, "Commit and push succeeded.")

        return RunResult(True, "Commit succeeded.")
