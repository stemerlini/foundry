"""The escape hatch: run any Python script as a study.

The script gets its context through environment variables and writes metrics to
``$FOUNDRY_OUTPUTS/../metrics.json`` (or ``foundry.metrics.write``). Any analysis starts
here and becomes a module only when it is reused across projects.
"""

from __future__ import annotations

import json
import sys

from .api import Command, FileKind, Module, Param, RunContext, Task


def command(ctx: RunContext) -> Command:
    script = ctx.study.dir / ctx.params["file"]
    interpreter = ctx.params.get("python") or sys.executable
    return Command(
        [interpreter, str(script)],
        env={
            "FOUNDRY_PROJECT": str(ctx.project.root),
            "FOUNDRY_ELEMENT": str(ctx.element_dir),
            "FOUNDRY_STUDY": ctx.study.key,
            "FOUNDRY_RUN_ID": ctx.run_id,
            "FOUNDRY_RUN_DIR": str(ctx.run_dir),
            "FOUNDRY_OUTPUTS": str(ctx.outputs_dir),
            "FOUNDRY_PARAMS": json.dumps(ctx.params),
            "FOUNDRY_INPUTS": json.dumps({k: str(v) for k, v in ctx.inputs.items()}),
        },
        cwd=ctx.study.dir,
    )


module = Module(
    id="script",
    title="Script",
    description="Run a Python script with the study's inputs, parameters and outputs.",
    tasks=[
        Task(
            id="main",
            title="Python script",
            command=command,
            params=(
                Param("file", str, "run.py", help="script, relative to the study folder"),
                Param("python", str, None, help="interpreter (default: Foundry's)"),
            ),
        )
    ],
    file_kinds=[FileKind("Python", ("*.py",), "λ"), FileKind("Notebook", ("*.ipynb",), "λ")],
)
