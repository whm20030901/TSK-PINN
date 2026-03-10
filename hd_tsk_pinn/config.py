from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import ast


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    try:
        return ast.literal_eval(value)
    except Exception:
        return value.strip('"').strip("'")


def load_simple_yaml(path: str | Path) -> Dict[str, Any]:
    """Parse a small YAML subset used by this repository.

    Supports nested mappings and lists via indentation. It is intentionally
    minimal to avoid external dependencies in constrained environments.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    root: Dict[str, Any] = {}
    stack: List[tuple[int, Any]] = [(-1, root)]

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]

        if stripped.startswith("- "):
            item = stripped[2:]
            if not isinstance(parent, list):
                raise ValueError(f"Invalid list item placement: {line}")
            parent.append(_parse_scalar(item))
            continue

        if ":" not in stripped:
            raise ValueError(f"Invalid line (missing ':'): {line}")

        key, raw = stripped.split(":", 1)
        key = key.strip()
        raw = raw.strip()

        if raw == "":
            # decide dict or list by peeking next meaningful line
            child: Any = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(raw)

    return root


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def load_config(config_path: str | Path) -> Dict[str, Any]:
    cfg = load_simple_yaml(config_path)
    extends = cfg.pop("extends", None)
    if extends:
        parent = Path(config_path).parent / str(extends)
        base = load_config(parent)
        return deep_merge(base, cfg)
    return cfg
