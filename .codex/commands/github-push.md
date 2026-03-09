---
name: GitHub同步推送
description: 快速将本地项目同步推送到GitHub仓库。执行标准的 add -> commit -> push 流程，移除冗余的检查步骤。
allowed-tools: Bash
argument-hint: "可选: 提交信息"
version: 8.1.0
last_updated: 2026-01-08
---
# GitHub同步推送

## 📋 指令概述

**GitHub同步推送**是一个高效的Git操作工具，专注于快速完成代码同步。它移除了繁琐的文档引用检查，直接执行核心的 Git 同步流程。

### 核心特性

- **极速同步**: 仅执行核心 Git 操作，无额外扫描
- **自动提交**: 自动生成带时间戳的提交信息（如未提供）
- **智能推送**: 自动识别当前分支并推送
- **零阻塞**: 消除因全库扫描导致的卡顿

## 🚀 执行流程

### 1. 添加变更

将所有本地修改（新增、修改、删除）添加到暂存区。

```bash
git add .
```

### 2. 提交变更

创建提交。如果用户未提供参数，则自动生成带时间戳的提交信息。

```bash
# 如果用户提供了参数 {{args}}，则使用参数作为提交信息
# 否则使用默认格式: "项目同步更新 - YYYY-MM-DD HH:MM"

if [ -n "{{args}}" ]; then
    MSG="{{args}}"
else
    MSG="项目同步更新 - $(date '+%Y-%m-%d %H:%M')"
fi

git commit -m "$MSG"
```

### 3. 推送到远程

自动检测当前分支并执行推送。

```bash
# 获取当前分支名
CURRENT_BRANCH=$(git branch --show-current)

# 推送到远程同名分支
git push origin $CURRENT_BRANCH
```

### 4. 推送后快速校验（防“UI挂起”误判）

用最小成本确认“本地与远端是否已对齐”，避免把编辑器缓存误判为未推送。

```bash
# 1) 工作区是否干净
git status -sb

# 2) 本地/远端提交是否一致（同分支）
CURRENT_BRANCH=$(git branch --show-current)
echo "local  $(git rev-parse $CURRENT_BRANCH)"
echo "remote $(git rev-parse origin/$CURRENT_BRANCH)"
```

判定规则：
- `git status -sb` 仅显示 `## branch...origin/branch`（无文件变更行）= 本地无挂起改动
- local 与 remote 哈希一致 = 推送已完成
- 若 VS Code 仍显示变更计数，通常是 UI 缓存；执行 `Git: Refresh` 或 `Developer: Reload Window`

## 🔍 常见问题

- **无变更**: 如果没有文件修改，`git commit` 会提示 nothing to commit，这是正常现象。
- **推送被拒**: 如果远程有新提交，请先执行 `git pull`。
- **编辑器仍显示“挂起/变更计数”**: 先按第 4 步校验 Git 真实状态；若已对齐，刷新编辑器 Git 视图即可。

## ⚠️ 最佳实践

- **敏感数据**: 推送前请确保 `.env` 等敏感文件已被 `.gitignore` 忽略。
- **大文件**: 避免提交超过 100MB 的大文件（除非配置了 Git LFS）。
