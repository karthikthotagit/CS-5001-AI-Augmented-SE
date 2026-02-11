from __future__ import annotations


def plan_prompt(desc: str, existing: str, module_path: str) -> str:
    return (
        "You are a senior software engineer. You will update ONE Python module at the given path.\n"
        "Create a short, actionable implementation plan with ordered steps.\n"
        "Constraints:\n"
        "- Keep the solution minimal and readable\n"
        "- Assume standard library only unless the description requires otherwise\n"
        "- Do not write code yet\n"
        "- Output plain text only\n\n"
        f"TARGET MODULE PATH: {module_path}\n\n"
        f"DESCRIPTION:\n{desc}\n\n"
        "EXISTING MODULE (may be empty):\n"
        f"{existing}\n"
    )


def draft_code_prompt(desc: str, existing: str, module_path: str, plan: str) -> str:
    return (
        "You are a software engineer. Write a single Python module that satisfies the description.\n"
        "Follow the plan.\n"
        "Return ONLY the full module content.\n"
        "Rules:\n"
        "- Output raw Python only\n"
        "- No Markdown\n"
        "- No code fences\n"
        "- No explanations\n\n"
        f"TARGET MODULE PATH: {module_path}\n\n"
        f"PLAN:\n{plan}\n\n"
        f"DESCRIPTION:\n{desc}\n\n"
        "EXISTING MODULE (may be empty):\n"
        f"{existing}\n"
    )


def review_and_fix_prompt(desc: str, module_path: str, plan: str, code: str) -> str:
    return (
        "You are a meticulous code reviewer. Review the module for correctness, completeness, and Python syntax.\n"
        "If improvements are needed, output the corrected FULL module.\n"
        "If no changes are needed, output the original module unchanged.\n"
        "Return ONLY the full module content.\n"
        "Rules:\n"
        "- Output raw Python only\n"
        "- No Markdown\n"
        "- No code fences\n"
        "- No explanations\n\n"
        f"TARGET MODULE PATH: {module_path}\n\n"
        f"PLAN:\n{plan}\n\n"
        f"DESCRIPTION:\n{desc}\n\n"
        "CURRENT MODULE DRAFT:\n"
        f"{code}\n"
    )


# Backward compatible name used by older code paths
def program_prompt(desc: str, existing: str) -> str:
    return draft_code_prompt(desc=desc, existing=existing, module_path="<unspecified>", plan="(no plan provided)")
