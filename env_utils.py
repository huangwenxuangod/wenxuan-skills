from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "env_utils.py").exists() and (candidate / "README.md").exists():
            return candidate
    return start.resolve()


def get_wenxuan_output_dir(cwd: Path | None = None) -> Path:
    base = (cwd or Path.cwd()).resolve()
    return base / "wenxuan-output"


def load_project_env(project_root: Path, extra_paths: Iterable[Path] | None = None) -> list[str]:
    loaded: list[str] = []
    candidates = [
        project_root / ".env",
        project_root / ".env.local",
    ]
    if extra_paths:
        candidates.extend(extra_paths)

    for candidate in candidates:
        if not candidate.exists() or not candidate.is_file():
            continue
        for raw_line in candidate.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
                loaded.append(key)
    return loaded
