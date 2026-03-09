import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml


def get_workspace_path() -> Path:
    configured = os.getenv("COZE_WORKSPACE_PATH", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def resolve_workspace_path(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path
    return (get_workspace_path() / path).resolve()


def load_yaml_file(path_str: str) -> Dict[str, Any]:
    file_path = resolve_workspace_path(path_str)
    with file_path.open("r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML 配置必须是对象: {file_path}")
    return data


def load_json_file(path_str: str) -> Dict[str, Any]:
    file_path = resolve_workspace_path(path_str)
    with file_path.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    if not isinstance(data, dict):
        raise ValueError(f"JSON 配置必须是对象: {file_path}")
    return data


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = deep_merge(current, value)
        else:
            merged[key] = value
    return merged
