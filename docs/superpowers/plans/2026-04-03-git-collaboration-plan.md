# Git 协作规范实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 建立标准 Git 协作规范，包含 Git Flow 分支模型、PR 模板、Code Review 流程、Git Hooks（后端 pre-commit + 前端 husky）

**架构概述：**
- 后端 Python 项目使用 `pre-commit` + `ruff` 管理 Git Hooks
- 前端 Node.js 项目使用 `husky` + `lint-staged` 管理 Git Hooks
- PR 模板放在 `.github/` 目录（GitHub 自动识别）
- Jenkins CI 配置在各自的 Jenkinsfile 中（后端已存在）

**技术栈：** pre-commit, ruff, husky, lint-staged

---

## 文件结构

```
backend/
  ├── .pre-commit-config.yaml      # 新建：pre-commit hooks 配置
  └── requirements.txt             # 修改：添加 pre-commit, ruff

web/
  ├── .husky/                       # 新建：husky git hooks 目录
  │   └── pre-commit               # 新建：pre-commit hook script
  ├── .lintstagedrc.json           # 新建：lint-staged 配置
  └── package.json                  # 修改：添加 husky, lint-staged

.github/
  └── PULL_REQUEST_TEMPLATE.md      # 新建：PR 模板
```

---

## 任务清单

### 任务 1：后端 pre-commit 配置（ruff）

**文件：**
- 创建：`backend/.pre-commit-config.yaml`
- 修改：`backend/requirements.txt`

- [ ] **Step 1: 创建 backend/.pre-commit-config.yaml**

```yaml
# 后端 pre-commit hooks 配置
# 安装方式：pip install pre-commit && pre-commit install
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=5000']
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 2: 验证文件创建**

命令：`cat backend/.pre-commit-config.yaml`
预期：显示上述 yaml 内容

- [ ] **Step 3: 添加依赖到 requirements.txt**

在 `backend/requirements.txt` 末尾添加：

```
# Git hooks
pre-commit>=3.0.0
ruff>=0.9.0
```

- [ ] **Step 4: 验证 requirements.txt 更新**

命令：`grep -E "pre-commit|ruff" backend/requirements.txt`
预期：显示 pre-commit 和 ruff 两行

- [ ] **Step 5: 提交**

```bash
git add backend/.pre-commit-config.yaml backend/requirements.txt
git commit -m "feat(git): add pre-commit with ruff for backend

- Add .pre-commit-config.yaml with ruff (lint + format)
- Add pre-commit and ruff to requirements.txt
- Ruff replaces flake8 + black + isort (10-100x faster)"
```

---

### 任务 2：前端 husky + lint-staged 配置

**文件：**
- 创建：`web/.husky/pre-commit`
- 创建：`web/.lintstagedrc.json`
- 修改：`web/package.json`

- [ ] **Step 1: 安装 husky 和 lint-staged**

```bash
cd web
npm install husky lint-staged -D
```

- [ ] **Step 2: 初始化 husky**

```bash
cd web
npx husky install
```

- [ ] **Step 3: 创建 .lintstagedrc.json**

```json
{
  "*.{js,vue,ts,jsx,tsx}": [
    "eslint --fix",
    "prettier --write"
  ],
  "*.{css,scss,vue}": [
    "prettier --write"
  ]
}
```

- [ ] **Step 4: 添加 husky pre-commit hook**

```bash
cd web
npx husky add .husky/pre-commit "npx lint-staged"
```

- [ ] **Step 5: 验证 .husky/pre-commit 内容**

命令：`cat web/.husky/pre-commit`
预期：包含 `npx lint-staged`

- [ ] **Step 6: 更新 package.json 添加 prepare script**

在 `web/package.json` 的 `scripts` 中添加：

```json
"prepare": "cd .. && husky install"
```

原有 scripts 示例：
```json
"scripts": {
  "dev": "vite --force",
  "prepare": "cd .. && husky install",
  ...
}
```

- [ ] **Step 7: 验证 lint-staged 配置**

命令：`cat web/.lintstagedrc.json`
预期：显示上述 json 内容

- [ ] **Step 8: 提交**

```bash
git add web/package.json web/.lintstagedrc.json web/.husky/
git commit -m "feat(git): add husky + lint-staged for frontend

- Add .husky/pre-commit hook running lint-staged
- Add .lintstagedrc.json for staged file linting
- Add prepare script for husky setup on npm install"
```

---

### 任务 3：PR 模板

**文件：**
- 创建：`.github/PULL_REQUEST_TEMPLATE.md`

- [ ] **Step 1: 创建 .github 目录**

```bash
mkdir -p .github
```

- [ ] **Step 2: 创建 .github/PULL_REQUEST_TEMPLATE.md**

```markdown
## 变更描述
<!-- 简述这次改动做了什么 -->

## 关联需求
<!-- 关联的 Issue 或需求链接 -->

## 变更类型
- [ ] Feature
- [ ] Bugfix
- [ ] Hotfix
- [ ] Refactor

## 自检清单
- [ ] 代码已通过 Pre-commit 检查（后端 ruff / 前端 lint-staged）
- [ ] 已添加必要的测试
- [ ] 文档已更新（如需）

## Reviewer 备注
<!-- 给 Reviewer 的补充说明 -->
```

- [ ] **Step 3: 验证模板创建**

命令：`cat .github/PULL_REQUEST_TEMPLATE.md`
预期：显示上述 markdown 内容

- [ ] **Step 4: 提交**

```bash
git add .github/PULL_REQUEST_TEMPLATE.md
git commit -m "docs: add PR template for standardized pull requests

- Add change description, related issues
- Add change type checklist (Feature/Bugfix/Hotfix/Refactor)
- Add self-check checklist for pre-commit compliance
- Add reviewer notes section"
```

---

## 实施后验证

所有任务完成后，验证步骤：

### 后端验证

```bash
cd backend
pip install pre-commit ruff
pre-commit install
# 测试运行
pre-commit run --all-files
```

预期：ruff 检查通过（无 error）

### 前端验证

```bash
cd web
# 首次 clone 后安装依赖
npm install
# 测试 pre-commit hook
git add .
git commit -m "test: verify husky hook"
```

预期：lint-staged 运行，eslint + prettier 检查通过

---

## Spec 覆盖检查

- ✅ 分支模型：规范文档（已在 spec 中定义，无需代码实现）
- ✅ PR/MR 模板：任务 3 创建 `.github/PULL_REQUEST_TEMPLATE.md`
- ✅ Code Review 规范：规范文档（已在 spec 中定义，无需代码实现）
- ✅ Git Hooks 后端（pre-commit + ruff）：任务 1
- ✅ Git Hooks 前端（husky + lint-staged）：任务 2
- ✅ CI/CD 联动：Jenkinsfile 已存在（后端 `backend/Jenkinsfile`），无需修改
- ✅ 分支保护规则：GitHub/GitLab 界面配置，不在代码库中

## 占位符扫描

无占位符，所有步骤均包含完整配置和命令。
