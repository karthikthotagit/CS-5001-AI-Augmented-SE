#!/usr/bin/env python3
"""
A2A Code Review — coordinator entry point.

Discovers the Analyzer and Reviewer agents via their Agent Cards,
then runs the sequential review pipeline:
  1. Analyzer  → reads the file, produces a structural analysis
  2. Reviewer  → receives the analysis as context, reviews for issues

Both agents must be running before calling this script:
    python agents/run_analyzer.py   # Terminal 1
    python agents/run_reviewer.py   # Terminal 2

Usage:
    python demo_review.py /path/to/file.py
    python demo_review.py /path/to/project/
"""
import argparse
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from coordinator import A2ACoordinator

console = Console()


def main(target: str) -> None:
    console.print(Panel.fit("[bold magenta]A2A Code Review[/]", subtitle="Agent-to-Agent protocol"))

    coord = A2ACoordinator()

    console.print("\n[bold]Discovering agents ...[/]")
    agents = coord.discover()

    if not agents:
        console.print(
            "\n[red]No agents found.[/] Start them first:\n"
            "  [dim]python agents/run_analyzer.py[/]\n"
            "  [dim]python agents/run_reviewer.py[/]"
        )
        sys.exit(1)

    results = coord.run_review(target)

    if "analysis" in results:
        console.print(Panel(Markdown(results["analysis"]), title="[bold blue]Analyzer Agent[/]", border_style="blue"))
    if "review" in results:
        console.print(Panel(Markdown(results["review"]), title="[bold magenta]Reviewer Agent[/]", border_style="magenta"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run A2A code review on a file or directory")
    parser.add_argument("target", help="File or directory to review")
    args = parser.parse_args()

    main(args.target)
