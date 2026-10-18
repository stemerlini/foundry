"""Start a Claude Code session to work on a project with the human in the loop.

The session's behaviour comes from the ``foundry`` skill and the project's
``.claude/settings.json`` (which blocks committing, locking and deciding); this module only
builds the opening brief for the selected element and the command that opens it.
"""

from __future__ import annotations

import shutil

from . import decisions, gates, review
from .model import Element
from .project import Project

APP_ID = "org.omarchy.foundry-agent"


def brief(project: Project, element: Element, task: str = "") -> str:
    g = gates.gates(project, element)
    cur = gates.current(g)
    where = element.title + (f" ({element.path})" if element.path else " (the system)")
    lines = [
        f"Foundry project \"{project.name}\" at {project.root}.",
        f"Focus: {where}; next gate: "
        + (f"{cur.title} — {cur.detail}." if cur else "none, every gate is done."),
    ]
    open_q = [d.key for d in decisions.all_decisions(project) if d.status == "proposed"]
    if open_q:
        lines.append(f"Decisions waiting for me: {', '.join(open_q)}.")
    if review.changes(project):
        lines.append("There are unreviewed changes in the working tree (see the proposal).")
    lines.append(task.strip() or "Load the foundry skill, summarise where this element stands, "
                 "and propose the next piece of work. Wait for my go-ahead before you start.")
    return "\n".join(lines)


def command(project: Project, element: Element, task: str = "") -> list[str]:
    """``claude`` started in the project folder with the brief."""
    name = f"foundry · {project.id}" + (f"/{element.path}" if element.path else "")
    return ["claude", "-n", name, brief(project, element, task)]


def window_command(project: Project, element: Element, task: str = "") -> list[str]:
    """The same session in its own Omarchy terminal window."""
    inner = ["sh", "-c", 'cd "$1" && shift && exec "$@"', "sh", str(project.root),
             *command(project, element, task)]
    if shutil.which("omarchy-launch-tui"):
        return ["omarchy-launch-tui", f"--app-id={APP_ID}", *inner]
    return ["xdg-terminal-exec", f"--app-id={APP_ID}", "-e", *inner]


# What every project carries so any Claude Code session started in it follows the rules,
# however it was started. Written by `foundry new` and, if missing, by `foundry agent`.
SETTINGS = """{
  "permissions": {
    "deny": [
      "Bash(git commit *)",
      "Bash(git push *)",
      "Bash(git reset *)",
      "Bash(git checkout *)",
      "Bash(git restore *)",
      "Bash(git tag *)",
      "Bash(git rebase *)",
      "Bash(foundry lock *)",
      "Bash(foundry decide *)",
      "Bash(foundry approve *)",
      "Bash(foundry reject *)"
    ]
  }
}
"""
CLAUDE_MD = """# Foundry project

This folder is a Foundry project. Load the `foundry` skill before changing anything here.
The user reviews and approves your work in Foundry's Review tab; committing, locking and
deciding are theirs.
"""


def ensure_files(project: Project) -> list[str]:
    """Write the agent guardrails if a project lacks them. Returns the files written."""
    written = []
    for rel, text in ((".claude/settings.json", SETTINGS), ("CLAUDE.md", CLAUDE_MD)):
        path = project.root / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            written.append(rel)
    return written
