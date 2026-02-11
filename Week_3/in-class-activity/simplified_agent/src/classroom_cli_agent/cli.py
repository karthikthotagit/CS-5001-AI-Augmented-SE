from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from .agent import Agent
from .llm import OllamaLLM
from .types import AgentConfig
from .utils import ensure_repo_path

DEFAULT_MODEL = "devstral-small-2:24b-cloud"
DEFAULT_HOST = "http://localhost:11434"
VERSION = "0.3.0"


def sanitize_name(text: str) -> str:
    """Convert text to a valid directory/file name."""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s-]+', '_', text)
    return text.strip('_')


def infer_project_structure(description: str, model: str, host: str) -> dict:
    """Use LLM to infer project structure from description."""
    prompt = f"""Given this project description, provide a JSON response with:
1. A short, descriptive project name (2-4 words, lowercase with underscores)
2. The appropriate Python module path (e.g., src/app.py, src/calculator.py, src/main.py)

Description: "{description}"

Consider:
- If it's a Streamlit/web app/dashboard, use src/app.py
- If it's a specific tool (calculator, prime checker, etc.), name the module accordingly
- Otherwise use src/main.py

Respond ONLY with valid JSON in this exact format:
{{"project_name": "name_here", "module_path": "src/file.py"}}"""

    llm = OllamaLLM(model=model, host=host, temperature=0.0)
    
    try:
        response = llm.generate(prompt)
        # Try to extract JSON from response
        # Handle case where LLM adds markdown code blocks
        response = response.strip()
        if response.startswith('```'):
            # Extract content between ```json and ```
            lines = response.split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith('```'):
                    if in_json:
                        break
                    in_json = True
                    continue
                if in_json:
                    json_lines.append(line)
            response = '\n'.join(json_lines)
        
        result = json.loads(response)
        
        # Validate and sanitize
        project_name = sanitize_name(result.get('project_name', 'project'))
        module_path = result.get('module_path', 'src/main.py')
        
        # Ensure module_path starts with src/ and ends with .py
        if not module_path.startswith('src/'):
            module_path = f'src/{module_path}'
        if not module_path.endswith('.py'):
            module_path = f'{module_path}.py'
        
        return {
            'project_name': project_name,
            'module_path': module_path
        }
    
    except (json.JSONDecodeError, KeyError, Exception) as e:
        # Fallback to simple extraction if LLM fails
        print(f"⚠️  LLM inference failed ({e}), using fallback...")
        words = description.lower().split()
        stop_words = {'a', 'an', 'the', 'with', 'for', 'to', 'in', 'on', 'of', 'and', 'or', 'create', 'make'}
        key_words = [w for w in words[:4] if w not in stop_words]
        project_name = '_'.join(key_words) if key_words else 'project'
        
        # Simple rule-based fallback
        desc_lower = description.lower()
        if 'streamlit' in desc_lower or 'web' in desc_lower or 'dashboard' in desc_lower:
            module_path = 'src/app.py'
        elif 'calculator' in desc_lower:
            module_path = 'src/calculator.py'
        else:
            module_path = 'src/main.py'
        
        return {
            'project_name': sanitize_name(project_name),
            'module_path': module_path
        }


def generate_repo_name(project_name: str) -> str:
    """Generate repository path with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"output/{project_name}_{timestamp}"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cca",
        description="Classroom CLI agent - Natural language code generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple - just describe what you want
  cca create "calculator with basic operations"
  cca create "streamlit weather dashboard"
  
  # With custom repo
  cca create "todo app" --repo output/my_todo
  
  # Commit changes
  cca commit --repo output/calculator_20240210_120000
  cca commit --repo output/calculator_20240210_120000 --push
        """
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    p.add_argument("--repo", help="Repository path (auto-generated if not provided)")
    p.add_argument(
        "--model",
        default=os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL),
        help=f"Ollama model (default: {DEFAULT_MODEL})",
    )
    p.add_argument(
        "--host",
        default=os.environ.get("OLLAMA_HOST", DEFAULT_HOST),
        help=f"Ollama host (default: {DEFAULT_HOST})",
    )
    p.add_argument(
        "--temperature",
        type=float,
        default=float(os.environ.get("OLLAMA_TEMPERATURE", "0.0")),
        help="Sampling temperature (default: 0.0)",
    )
    p.add_argument("--verbose", action="store_true", help="Verbose output")

    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="Create or update a module from natural language description")
    c.add_argument("description", help="What to create (e.g., 'calculator app')")
    c.add_argument("--module", help="Module path (auto-inferred if not provided)")

    cm = sub.add_parser("commit", help="Commit and optionally push changes")
    cm.add_argument("message", nargs='?', help="Commit message (auto-generated if not provided)")
    cm.add_argument("--push", action="store_true", help="Also run git push")

    return p


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    
    # Handle create command with LLM-powered inference
    if args.cmd == "create":
        print(f"Analyzing project description with LLM...\n")
        
        # Use LLM to infer project structure
        structure = infer_project_structure(
            args.description, 
            args.model,
            args.host
        )
        
        # Auto-generate repo if not provided
        if not args.repo:
            args.repo = generate_repo_name(structure['project_name'])
            print(f"Repository: {args.repo}")
        
        # Auto-infer module if not provided
        if not args.module:
            args.module = structure['module_path']
            print(f"Module: {args.module}")
        
        # Initialize git repo
        repo_path = Path(args.repo)
        if not repo_path.exists():
            repo_path.mkdir(parents=True, exist_ok=True)
            git_dir = repo_path / '.git'
            if not git_dir.exists():
                import subprocess
                subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
                print(f"Initialized git repository")
        
        print(f"\n{'='*60}")
        print(f"Creating: {args.description}")
        print(f"{'='*60}\n")
    
    # Handle commit command
    if args.cmd == "commit":
        if not args.repo:
            print("Error: --repo is required for commit command", file=sys.stderr)
            return 1
        
        # Auto-generate commit message if not provided
        if not args.message:
            args.message = "Update project"
            print(f"💬 Auto-generating commit message: {args.message}")
    
    ensure_repo_path(args.repo)

    cfg = AgentConfig(
        repo=args.repo,
        model=args.model,
        host=args.host,
        temperature=args.temperature,
        verbose=args.verbose,
    )
    agent = Agent(cfg)

    try:
        if args.cmd == "create":
            r = agent.create_program(args.description, args.module)
        else:  # commit
            r = agent.commit_and_push(args.message, args.push)

        stream = sys.stdout if r.ok else sys.stderr
        print(r.details, file=stream)
        
        # Show next steps for create command
        if args.cmd == "create" and r.ok:
            print(f"\n{'='*60}")
            print(f"Success! Next steps:")
            print(f"1. Review code: {args.repo}/{args.module}")
            print(f"2. Commit: cca commit --repo {args.repo}")
            print(f"{'='*60}\n")
        
        return 0 if r.ok else 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        print(str(e) or e.__class__.__name__, file=sys.stderr)
        return 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
