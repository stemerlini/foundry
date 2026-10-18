# Foundry

A universal development workbench for Omarchy. A product is a tree of **elements**
(system → subsystems → components); every element goes through the same loop —
Describe · Research · Architect · Concept · Analyse · Lock · Design · Deliver — with each
gate's status computed from what exists. Requirements carry criteria on metrics; studies
run module tasks (Geant4, PIC, ngspice, KiCad, pytest, scripts…) and record runs whose
metrics pass or fail them; derived requirements roll up to their parents; any change marks
what depends on it stale. Notes and reports live in the Obsidian vault, papers in Citadel,
design data in the project's git repo.

See [PLAN.md](PLAN.md) for the vision, the model and the phases.

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/foundry templates
.venv/bin/foundry new ptel -t particle-telescope   # created under ~/Hardware
.venv/bin/foundry status -C ~/Hardware/ptel
.venv/bin/foundry run sensor-head/S001 --wait -C ~/Hardware/ptel
.venv/bin/foundry arch -C ~/Hardware/ptel
.venv/bin/foundry -C ~/Hardware/ptel               # TUI
.venv/bin/pytest
```

## Writing a module

A module is a `foundry.modules.api.Module` with tasks, tools, viewers, element kinds, file
kinds, toolchains and checks. Built-ins live in `src/foundry/modules/`; external packages
register through the `foundry.modules` entry-point group. A task builds a `Command` from a
`RunContext`; Foundry runs it, logs it, and reads `metrics.json` plus the task's `collect`.
