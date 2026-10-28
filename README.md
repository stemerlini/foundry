# Foundry

A universal development workbench for Omarchy. A product is a tree of **elements**
(system → subsystems → components); every element goes through the same loop —
Describe · Research · Architect · Concept · Analyse · Lock · Design · Deliver — with each
gate's status computed from what exists. Requirements carry criteria on metrics; studies
run module tasks (Geant4, IRENE AE9/AP9, PIC, ngspice, KiCad, pytest, scripts…) and record runs whose
metrics pass or fail them; derived requirements roll up to their parents; any change marks
what depends on it stale. Notes and reports live in the Obsidian vault, papers in Citadel,
design data in the project's git repo.

See [PLAN.md](PLAN.md) for the vision, the model and the phases.

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/foundry templates
.venv/bin/foundry new ptel -t hardware   # or software, publication; under ~/Hardware
.venv/bin/foundry status -C ~/Hardware/ptel
.venv/bin/foundry run S001 --wait -C ~/Hardware/ptel
.venv/bin/foundry arch -C ~/Hardware/ptel
.venv/bin/foundry -C ~/Hardware/ptel               # TUI
.venv/bin/pytest
```

## Working with an agent

Press `a` in the TUI: start a Claude Code session on the selected element, go to the one
already running (the top bar shows `◆ agent working`), or continue the last one after a
usage limit resets. The agent never commits: its changes wait in the Review tab (`8`) with
`.foundry/proposal.md`, which is also its handover to the next session.

```bash
foundry agent fee -t "size the ADC"   # new session (-w: own window)
foundry agent --continue              # resume the last session; --fork resumes a copy
foundry agent --sessions              # saved and running sessions
```

## Radiation environment (IRENE)

`tools/build-irene` builds AFRL's IRENE (AE9/AP9/SPM) from its source distribution into
`~/.local/opt/irene/<version>` and adds an `irene` command. A study with
`task = "irene.environment"` takes orbit elements, models (AE9, AP9, AE8, AP8) and a statistic
(mean, a percentile, or a Monte Carlo confidence level) and writes orbit-average/peak spectra,
Geant4 GPS source macros and total dose behind aluminium (`tid_<d>mm` metrics).

## Writing a module

A module is a `foundry.modules.api.Module` with tasks, tools, viewers, element kinds, file
kinds, toolchains and checks. Built-ins live in `src/foundry/modules/`; external packages
register through the `foundry.modules` entry-point group. A task builds a `Command` from a
`RunContext`; Foundry runs it, logs it, and reads `metrics.json` plus the task's `collect`.
