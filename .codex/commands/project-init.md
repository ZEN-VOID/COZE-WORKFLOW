---
name: 项目骨架初始化
description: 基于 examples 模板初始化一个新的 projects/<项目名>/ 项目骨架，支持多项目并存与按项目隔离开发
allowed-tools: Bash, Read, Write
argument-hint: "<项目名>"
version: 1.0.0
last_updated: 2026-03-09
---

# 项目骨架初始化

## 📋 指令概述

**项目骨架初始化**用于在仓库根目录下快速创建一个新的具体项目目录：`projects/<项目名>/`。

该指令默认以 `examples/` 作为模板来源，复制一套可运行的工作流开发骨架到目标项目目录，并保持多项目并存、相互隔离的开发方式。

## 🎯 目标

- 在 `projects/` 下创建新的独立项目目录
- 复用 `examples/` 中已经沉淀好的配置、脚本和目录结构
- 避免污染模板目录
- 支持后续按具体项目路径进行开发和修改

## 🚀 执行流程

### 1. 校验参数

必须提供项目名参数 `{{args}}`。

校验规则：

- 不能为空
- 支持中文、字母、数字、点、下划线和短横线
- 不允许包含空白字符、路径分隔符或其他明显非法路径字符
- 最终目标目录为：`projects/{{args}}`

如果未提供项目名，直接终止并提示正确用法。

```bash
if [ -z "{{args}}" ]; then
  echo "错误: 必须提供项目名。"
  echo "用法: /project-init <项目名>"
  exit 1
fi

if printf '%s' "{{args}}" | grep -Eq '[[:space:]/\\\\:*?\"<>|]'; then
  echo "错误: 项目名不能包含空格、斜杠或非法路径字符。"
  exit 1
fi
```

### 2. 解析路径

统一在仓库根目录下创建项目目录：

```bash
PROJECT_NAME="{{args}}"
PROJECTS_DIR="projects"
TEMPLATE_DIR="examples"
TARGET_DIR="${PROJECTS_DIR}/${PROJECT_NAME}"
```

### 3. 前置检查

检查项：

- `examples/` 是否存在
- `projects/` 是否存在，不存在则创建
- 目标项目目录是否已存在

规则：

- 若 `TARGET_DIR` 已存在且非空，则默认拒绝覆盖并退出
- 若模板目录不存在，则直接报错退出

```bash
if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "错误: 未找到模板目录 $TEMPLATE_DIR"
  exit 1
fi

mkdir -p "$PROJECTS_DIR"

if [ -e "$TARGET_DIR" ] && [ "$(find "$TARGET_DIR" -mindepth 1 | head -n 1)" ]; then
  echo "错误: 目标项目目录已存在且非空: $TARGET_DIR"
  exit 1
fi
```

### 4. 复制模板骨架

从 `examples/` 复制项目骨架到 `projects/<项目名>/`。

复制时排除以下内容：

- `.DS_Store`
- `__pycache__`
- `.env`
- `.env.local`
- 运行时缓存文件

推荐使用 `rsync`，若不可用则退回 `cp -R`。

```bash
mkdir -p "$TARGET_DIR"

if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude '.DS_Store' \
    --exclude '__pycache__' \
    --exclude '.env' \
    --exclude '.env.local' \
    --exclude '*.pyc' \
    "${TEMPLATE_DIR}/" "${TARGET_DIR}/"
else
  cp -R "${TEMPLATE_DIR}/." "${TARGET_DIR}/"
  find "$TARGET_DIR" -name '.DS_Store' -delete
  find "$TARGET_DIR" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
  rm -f "${TARGET_DIR}/.env" "${TARGET_DIR}/.env.local"
fi
```

### 5. 项目级轻量定制

初始化后对新项目做最小定制：

- 将 `README.md` 的标题替换为项目名
- 将 README 中模板目录相关描述替换为当前项目目录说明
- 确保 `.env.example` 中保留占位形式，不写死当前机器路径
- 在项目 README 中明确当前目录就是该项目的工作目录

推荐执行逻辑：

```bash
README_FILE="${TARGET_DIR}/README.md"

if [ -f "$README_FILE" ]; then
  PROJECT_NAME="$PROJECT_NAME" README_FILE="$README_FILE" python3 - <<'PY'
from pathlib import Path
import os

project_name = os.environ["PROJECT_NAME"]
readme_path = Path(os.environ["README_FILE"])
content = readme_path.read_text(encoding="utf-8")

lines = content.splitlines()
if lines:
    lines[0] = f"# {project_name}"
else:
    lines = [f"# {project_name}"]

content = "\\n".join(lines)
content = content.replace(
    "1. 复制 `/Volumes/CODE/COZE-WORKFLOW/examples/.env.example:1` 为 `.env`",
    "1. 复制 `./.env.example` 为 `.env`",
)
content = content.replace(
    "2. 设置 `COZE_WORKSPACE_PATH` 为当前 `examples/` 绝对路径",
    f"2. 设置 `COZE_WORKSPACE_PATH` 为当前项目目录绝对路径（如 `projects/{project_name}`）",
)
lines = content.splitlines()

marker = "## 项目说明"
extra = [
    "",
    "## 项目说明",
    "",
    f"- 当前项目目录：`projects/{project_name}`",
    "- 该目录用于当前具体项目的独立开发、配置与调试",
    "- 如需沉淀通用能力，请优先回流到 `examples/` 或仓库级规范",
]

if marker not in content:
    lines.extend(extra)

readme_path.write_text("\\n".join(lines).rstrip() + "\\n", encoding="utf-8")
PY
fi

ENV_EXAMPLE_FILE="${TARGET_DIR}/.env.example"

if [ -f "$ENV_EXAMPLE_FILE" ]; then
  PROJECT_NAME="$PROJECT_NAME" ENV_EXAMPLE_FILE="$ENV_EXAMPLE_FILE" python3 - <<'PY'
from pathlib import Path
import os

project_name = os.environ["PROJECT_NAME"]
env_path = Path(os.environ["ENV_EXAMPLE_FILE"])
content = env_path.read_text(encoding="utf-8")
content = content.replace(
    "COZE_WORKSPACE_PATH=/absolute/path/to/examples",
    f"COZE_WORKSPACE_PATH=/absolute/path/to/projects/{project_name}",
)
env_path.write_text(content, encoding="utf-8")
PY
fi
```

### 6. 结果确认

输出以下信息：

- 项目名称
- 项目路径
- 下一步建议命令

```bash
echo "项目初始化完成"
echo "项目名: $PROJECT_NAME"
echo "项目路径: $TARGET_DIR"
echo "下一步:"
echo "  cd $TARGET_DIR"
echo "  cp .env.example .env"
echo "  bash scripts/local_run.sh -m flow -i '{\"input_text\":\"你好\"}'"
```

## 🔧 推荐执行脚本

如需一次性执行，建议使用以下 Bash 流程：

```bash
set -e

if [ -z "{{args}}" ]; then
  echo "错误: 必须提供项目名。"
  echo "用法: /project-init <项目名>"
  exit 1
fi

if printf '%s' "{{args}}" | grep -Eq '[[:space:]/\\\\:*?\"<>|]'; then
  echo "错误: 项目名不能包含空格、斜杠或非法路径字符。"
  exit 1
fi

PROJECT_NAME="{{args}}"
PROJECTS_DIR="projects"
TEMPLATE_DIR="examples"
TARGET_DIR="${PROJECTS_DIR}/${PROJECT_NAME}"

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "错误: 未找到模板目录 $TEMPLATE_DIR"
  exit 1
fi

mkdir -p "$PROJECTS_DIR"

if [ -e "$TARGET_DIR" ] && [ "$(find "$TARGET_DIR" -mindepth 1 | head -n 1)" ]; then
  echo "错误: 目标项目目录已存在且非空: $TARGET_DIR"
  exit 1
fi

mkdir -p "$TARGET_DIR"

if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude '.DS_Store' \
    --exclude '__pycache__' \
    --exclude '.env' \
    --exclude '.env.local' \
    --exclude '*.pyc' \
    "${TEMPLATE_DIR}/" "${TARGET_DIR}/"
else
  cp -R "${TEMPLATE_DIR}/." "${TARGET_DIR}/"
  find "$TARGET_DIR" -name '.DS_Store' -delete
  find "$TARGET_DIR" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
  rm -f "${TARGET_DIR}/.env" "${TARGET_DIR}/.env.local"
fi

README_FILE="${TARGET_DIR}/README.md"

if [ -f "$README_FILE" ]; then
  PROJECT_NAME="$PROJECT_NAME" README_FILE="$README_FILE" python3 - <<'PY'
from pathlib import Path
import os

project_name = os.environ["PROJECT_NAME"]
readme_path = Path(os.environ["README_FILE"])
content = readme_path.read_text(encoding="utf-8")
lines = content.splitlines()

if lines:
    lines[0] = f"# {project_name}"
else:
    lines = [f"# {project_name}"]

content = "\\n".join(lines)
content = content.replace(
    "1. 复制 `/Volumes/CODE/COZE-WORKFLOW/examples/.env.example:1` 为 `.env`",
    "1. 复制 `./.env.example` 为 `.env`",
)
content = content.replace(
    "2. 设置 `COZE_WORKSPACE_PATH` 为当前 `examples/` 绝对路径",
    f"2. 设置 `COZE_WORKSPACE_PATH` 为当前项目目录绝对路径（如 `projects/{project_name}`）",
)
lines = content.splitlines()

marker = "## 项目说明"
extra = [
    "",
    "## 项目说明",
    "",
    f"- 当前项目目录：`projects/{project_name}`",
    "- 该目录用于当前具体项目的独立开发、配置与调试",
    "- 如需沉淀通用能力，请优先回流到 `examples/` 或仓库级规范",
]

if marker not in content:
    lines.extend(extra)

readme_path.write_text("\\n".join(lines).rstrip() + "\\n", encoding="utf-8")
PY
fi

ENV_EXAMPLE_FILE="${TARGET_DIR}/.env.example"

if [ -f "$ENV_EXAMPLE_FILE" ]; then
  PROJECT_NAME="$PROJECT_NAME" ENV_EXAMPLE_FILE="$ENV_EXAMPLE_FILE" python3 - <<'PY'
from pathlib import Path
import os

project_name = os.environ["PROJECT_NAME"]
env_path = Path(os.environ["ENV_EXAMPLE_FILE"])
content = env_path.read_text(encoding="utf-8")
content = content.replace(
    "COZE_WORKSPACE_PATH=/absolute/path/to/examples",
    f"COZE_WORKSPACE_PATH=/absolute/path/to/projects/{project_name}",
)
env_path.write_text(content, encoding="utf-8")
PY
fi

echo "项目初始化完成"
echo "项目名: $PROJECT_NAME"
echo "项目路径: $TARGET_DIR"
echo "下一步:"
echo "  cd $TARGET_DIR"
echo "  cp .env.example .env"
echo "  bash scripts/local_run.sh -m flow -i '{\"input_text\":\"你好\"}'"
```

## 📌 使用方式

```bash
/project-init 漫剧创作大师极速版
```

执行后将生成：

```text
projects/
└── 漫剧创作大师极速版/
    ├── AGENTS.md
    ├── README.md
    ├── config/
    ├── scripts/
    ├── src/
    └── ...
```

## ⚠️ 注意事项

- 该指令默认**不覆盖**已存在的项目目录
- 该指令默认从 `examples/` 复制模板，因此应保持 `examples/` 始终为最新可复用骨架
- 如果后续多个项目都需要同类能力改动，应优先回流模板，而不是只修改单个项目
- 初始化完成后，后续开发应优先在 `projects/<项目名>/` 下进行
