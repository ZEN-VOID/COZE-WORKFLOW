---
name: 子仓库同步推送
description: 将父仓库中 projects/<项目名> 的最新代码同步推送到对应的独立 GitHub 子仓库。
allowed-tools: Bash
argument-hint: "子仓库项目名 [可选: 提交信息]"
version: 1.0.0
last_updated: 2026-03-10
---
# 子仓库同步推送

## 📋 指令概述

从父仓库 `projects/<项目名>` 目录同步代码到对应的独立 GitHub 子仓库，执行 rsync → add → commit → push 流程。

**用法**: `/sub-push 漫剧大师极速版` 或 `/sub-push 漫剧大师极速版 修复生图节点`

### 核心特性

- **单向同步**: 父仓库 → 子仓库，以父仓库为准
- **自动克隆**: 子仓库本地不存在时自动从 GitHub 克隆
- **增量同步**: 使用 rsync 仅传输差异文件
- **安全推送**: 推送前自动校验敏感文件

## 📂 约定

- 子仓库本地存储路径: `~/.sub-repos/<项目名>/`
- 子仓库名称映射配置: `projects/<项目名>/.sub-repo`（内容为 GitHub 仓库全名，如 `ZEN-VOID/manga-master-express`）
- 若 `.sub-repo` 不存在，中止并提示用户创建

## 🚀 执行流程

### 0. 解析参数

```bash
# {{args}} 格式: "<项目名>" 或 "<项目名> <提交信息>"
# 第一个词为项目名，其余为提交信息

ARGS="{{args}}"
PROJECT_NAME=$(echo "$ARGS" | awk '{print $1}')
COMMIT_MSG=$(echo "$ARGS" | sed "s/^$PROJECT_NAME//;s/^ *//")
```

### 1. 预检查

```bash
PARENT_REPO=$(pwd)
SOURCE_DIR="${PARENT_REPO}/projects/${PROJECT_NAME}"
SUB_REPO_DIR="${HOME}/.sub-repos/${PROJECT_NAME}"

# 1a) 源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
  echo "错误: 项目目录不存在 → projects/${PROJECT_NAME}"
  echo "可用项目:"
  ls -1 projects/
  exit 1
fi

# 1b) .sub-repo 映射文件是否存在
SUB_REPO_CFG="${SOURCE_DIR}/.sub-repo"
if [ ! -f "$SUB_REPO_CFG" ]; then
  echo "错误: 未找到子仓库映射文件 → projects/${PROJECT_NAME}/.sub-repo"
  echo "请创建该文件，内容为 GitHub 仓库全名，例如:"
  echo "  echo 'ZEN-VOID/manga-master-express' > \"${SUB_REPO_CFG}\""
  exit 1
fi

REPO_FULL=$(cat "$SUB_REPO_CFG" | tr -d '[:space:]')
REPO_URL="https://github.com/${REPO_FULL}.git"
echo "目标子仓库: ${REPO_URL}"
```

### 2. 准备子仓库本地目录

```bash
mkdir -p "${HOME}/.sub-repos"

if [ ! -d "${SUB_REPO_DIR}/.git" ]; then
  echo "首次同步，克隆子仓库..."
  git clone "$REPO_URL" "$SUB_REPO_DIR"
else
  echo "拉取子仓库最新状态..."
  cd "$SUB_REPO_DIR" && git pull --rebase origin main
fi
```

### 3. 同步代码（父仓库 → 子仓库）

```bash
rsync -av --delete \
  --exclude='.git' \
  --exclude='.sub-repo' \
  --exclude='.DS_Store' \
  --exclude='__pycache__' \
  --exclude='.env' \
  "${SOURCE_DIR}/" "${SUB_REPO_DIR}/"

echo "同步完成 ✓"
```

### 4. 提交变更

```bash
cd "$SUB_REPO_DIR"
git add .

# 检查是否有实际变更
if git diff --cached --quiet; then
  echo "无变更，跳过提交。"
  exit 0
fi

# 生成提交信息
if [ -z "$COMMIT_MSG" ]; then
  COMMIT_MSG="sync: ${PROJECT_NAME} - $(date '+%Y-%m-%d %H:%M')"
fi

git commit -m "$COMMIT_MSG"
```

### 5. 推送到远程

```bash
cd "$SUB_REPO_DIR"
CURRENT_BRANCH=$(git branch --show-current)
git push origin "$CURRENT_BRANCH"
```

### 6. 推送后校验

```bash
cd "$SUB_REPO_DIR"
git status -sb
CURRENT_BRANCH=$(git branch --show-current)
echo "local  $(git rev-parse $CURRENT_BRANCH)"
echo "remote $(git rev-parse origin/$CURRENT_BRANCH)"
echo ""
echo "✓ 子仓库推送完成: https://github.com/${REPO_FULL}"
```

## 🔍 常见问题

- **首次使用**: 需先创建 `projects/<项目名>/.sub-repo` 文件，写入 GitHub 仓库全名（如 `ZEN-VOID/manga-master-express`）。
- **冲突**: 若子仓库有他人提交导致推送失败，先 `cd ~/.sub-repos/<项目名> && git pull --rebase` 解决冲突后重试。
- **无变更**: rsync 后若文件无差异，会自动跳过提交，这是正常现象。
- **敏感数据**: `.env` 已在 rsync 排除列表中，不会同步到子仓库。
