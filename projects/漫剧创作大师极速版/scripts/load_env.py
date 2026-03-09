#!/usr/bin/env python3
"""
加载项目环境变量脚本
通过 coze_workload_identity.Client 获取项目环境变量并输出 export 语句
使用方式: eval $(python load_env.py)
"""

import os
import sys
from pathlib import Path

from dotenv import dotenv_values

workspace_path = os.getenv("COZE_WORKSPACE_PATH", str(Path(__file__).resolve().parents[1]))
app_dir = os.path.join(workspace_path, 'src')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)


def load_file_env(root_dir: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for filename in (".env", ".env.local"):
        file_path = root_dir / filename
        if not file_path.exists():
            continue
        file_values = dotenv_values(file_path)
        for key, value in file_values.items():
            if key and value is not None:
                values[key] = value
    return values


def load_identity_env() -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        from coze_workload_identity import Client

        client = Client()
        env_vars = client.get_project_env_vars()
        client.close()
        for env_var in env_vars:
            values[env_var.key] = env_var.value
    except Exception as exc:
        print(f"# Skip workload identity env: {exc}", file=sys.stderr)
    return values


root_dir = Path(workspace_path)
merged_env = load_file_env(root_dir)
merged_env.update(load_identity_env())
merged_env.setdefault("COZE_WORKSPACE_PATH", str(root_dir))

loaded_count = 0
for key, value in merged_env.items():
    if os.getenv(key):
        continue
    escaped = value.replace("'", "'\\''")
    print(f"export {key}='{escaped}'")
    loaded_count += 1

print(f"# Loaded {loaded_count} environment variables", file=sys.stderr)
