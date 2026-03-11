---
name: GitHub全量同步推送
description: 一键推送所有子仓库 + 父仓库。顺序：先逐个子仓库同步推送，再父仓库 add → commit → push。
allowed-tools: Bash
argument-hint: "可选: 提交信息"
version: 9.0.0
last_updated: 2026-03-10
---
# GitHub全量同步推送

## 📋 指令概述

**全量同步推送**按照「先子后父」的顺序，将所有已配置 `.sub-repo` 的子项目同步到各自的独立 GitHub 仓库，最后再将父仓库整体提交推送。

### 执行顺序与原因

1. **先推子仓库** — 子仓库代码来源于 `projects/<项目名>/`，先确保各子仓库远端已同步最新
2. **再推父仓库** — 父仓库包含子仓库的源目录和 `.sub-repo` 映射，作为整体归档兜底

### 核心特性

- **全量覆盖**: 自动扫描所有含 `.sub-repo` 的子项目，逐个同步
- **先子后父**: 子仓库全部成功后才推送父仓库
- **失败隔离**: 单个子仓库失败不阻塞其余，但会汇总报告
- **自动提交**: 未提供参数时自动生成带时间戳的提交信息

## 🚀 执行流程

### Phase 0. 预检查父仓库远程

```bash
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "错误: 父仓库未配置 Git 远程 origin。"
  echo "请先执行: git remote add origin <repo-url>"
  exit 1
fi
```

### Phase 1. 子仓库同步推送

扫描 `projects/` 下所有含 `.sub-repo` 的子项目，逐个执行 rsync → commit → push。

```bash
PARENT_REPO=$(pwd)
FAILED_SUBS=""
PUSHED_SUBS=""

for SUB_REPO_CFG in projects/*/.sub-repo; do
  [ -f "$SUB_REPO_CFG" ] || continue

  PROJECT_DIR=$(dirname "$SUB_REPO_CFG")
  PROJECT_NAME=$(basename "$PROJECT_DIR")
  REPO_FULL=$(cat "$SUB_REPO_CFG" | tr -d '[:space:]')
  REPO_URL="https://github.com/${REPO_FULL}.git"
  SUB_REPO_DIR="${HOME}/.sub-repos/${PROJECT_NAME}"

  echo ""
  echo "========== 子仓库: ${PROJECT_NAME} =========="
  echo "目标: ${REPO_URL}"

  # 1) 准备本地子仓库目录
  mkdir -p "${HOME}/.sub-repos"
  if [ ! -d "${SUB_REPO_DIR}/.git" ]; then
    echo "首次同步，克隆子仓库..."
    if ! git clone "$REPO_URL" "$SUB_REPO_DIR"; then
      echo "✗ 克隆失败: ${PROJECT_NAME}"
      FAILED_SUBS="${FAILED_SUBS} ${PROJECT_NAME}"
      continue
    fi
  else
    cd "$SUB_REPO_DIR" && git pull --rebase origin main 2>/dev/null || true
  fi

  # 2) rsync 同步
  rsync -av --delete \
    --exclude='.git' \
    --exclude='.sub-repo' \
    --exclude='.DS_Store' \
    --exclude='__pycache__' \
    --exclude='.env' \
    "${PARENT_REPO}/${PROJECT_DIR}/" "${SUB_REPO_DIR}/"

  # 3) 提交 + 推送
  cd "$SUB_REPO_DIR"
  git add .

  if git diff --cached --quiet; then
    echo "✓ 无变更，跳过: ${PROJECT_NAME}"
    PUSHED_SUBS="${PUSHED_SUBS} ${PROJECT_NAME}(无变更)"
    continue
  fi

  if [ -n "{{args}}" ]; then
    SUB_MSG="{{args}}"
  else
    SUB_MSG="sync: ${PROJECT_NAME} - $(date '+%Y-%m-%d %H:%M')"
  fi

  git commit -m "$SUB_MSG"
  CURRENT_BRANCH=$(git branch --show-current)

  if git push origin "$CURRENT_BRANCH"; then
    echo "✓ 推送成功: ${PROJECT_NAME}"
    PUSHED_SUBS="${PUSHED_SUBS} ${PROJECT_NAME}(已推送)"
  else
    echo "✗ 推送失败: ${PROJECT_NAME}"
    FAILED_SUBS="${FAILED_SUBS} ${PROJECT_NAME}"
  fi

  cd "$PARENT_REPO"
done
```

### Phase 1.5 子仓库结果汇总

```bash
echo ""
echo "========== 子仓库汇总 =========="
if [ -n "$PUSHED_SUBS" ]; then
  echo "成功:${PUSHED_SUBS}"
fi
if [ -n "$FAILED_SUBS" ]; then
  echo "失败:${FAILED_SUBS}"
  echo "⚠ 存在子仓库推送失败，父仓库仍将继续推送。"
fi
```

### Phase 2. 父仓库提交推送

```bash
cd "$PARENT_REPO"
echo ""
echo "========== 父仓库推送 =========="

git add .

if git diff --cached --quiet; then
  echo "父仓库无变更，跳过提交。"
else
  if [ -n "{{args}}" ]; then
    MSG="{{args}}"
  else
    MSG="项目同步更新 - $(date '+%Y-%m-%d %H:%M')"
  fi

  git commit -m "$MSG"
fi

CURRENT_BRANCH=$(git branch --show-current)
git push origin $CURRENT_BRANCH
```

### Phase 3. 推送后校验

```bash
cd "$PARENT_REPO"
echo ""
echo "========== 校验 =========="
git status -sb
CURRENT_BRANCH=$(git branch --show-current)
echo "local  $(git rev-parse $CURRENT_BRANCH)"
echo "remote $(git rev-parse origin/$CURRENT_BRANCH)"
```

判定规则：
- `git status -sb` 仅显示 `## branch...origin/branch`（无文件变更行）= 本地无挂起改动
- local 与 remote 哈希一致 = 推送已完成
- 若 VS Code 仍显示变更计数，通常是 UI 缓存；执行 `Git: Refresh` 或 `Developer: Reload Window`

## 🔍 常见问题

- **无子仓库**: 若 `projects/` 下没有任何 `.sub-repo` 文件，Phase 1 自动跳过，仅推送父仓库。
- **子仓库推送失败**: 失败会记录并汇总，但不阻塞父仓库推送。修复后重新执行即可。
- **首次使用子仓库**: 需先在 `projects/<项目名>/` 下创建 `.sub-repo` 文件，内容为 GitHub 仓库全名（如 `ZEN-VOID/manga-master-express`）。
- **推送被拒**: 如果远程有新提交，请先执行 `git pull`。

## ⚠️ 最佳实践

- **敏感数据**: `.env` 已在 rsync 排除列表中，不会同步到子仓库。推送前请确保 `.gitignore` 覆盖所有敏感文件。
- **大文件**: 避免提交超过 100MB 的大文件（除非配置了 Git LFS）。
- **新增子项目**: 只需在项目目录下创建 `.sub-repo` 文件，下次执行本命令即自动纳入推送。
