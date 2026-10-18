"""User configuration: ``~/.config/foundry/config.toml`` (known projects, defaults)."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

import tomli_w

CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "foundry/config.toml"
DEFAULT_PROJECTS_ROOT = Path.home() / "Hardware"


def load() -> dict:
    try:
        return tomllib.loads(CONFIG.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def save(data: dict) -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(tomli_w.dumps(data))


def projects_root() -> Path:
    return Path(load().get("projects_root", DEFAULT_PROJECTS_ROOT)).expanduser()


def known_projects() -> list[Path]:
    """Remembered projects plus any project folder directly under the projects root."""
    paths = [Path(p).expanduser() for p in load().get("projects", [])]
    root = projects_root()
    if root.is_dir():
        paths += [d for d in sorted(root.iterdir()) if (d / "foundry.toml").is_file()]
    seen, found = set(), []
    for p in paths:
        p = p.resolve()
        if p not in seen and (p / "foundry.toml").is_file():
            seen.add(p)
            found.append(p)
    return found


def remember(path: Path) -> None:
    data = load()
    path = path.resolve()
    projects = [p for p in data.get("projects", []) if Path(p).expanduser().resolve() != path]
    data["projects"] = [str(path), *projects][:30]
    save(data)


def vault() -> Path | None:
    """The Obsidian vault, if configured (``vault = "..."`` in config.toml) and present."""
    path = load().get("vault")
    if not path:
        return None
    path = Path(path).expanduser()
    return path if path.is_dir() else None
