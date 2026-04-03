# Git 协作规范设计

> 创建日期：2026-04-03
> 状态：评审中
> 作者：Lewis Yan
> 关联：Git 协作标准化

---

## 1. 分支模型

采用标准 Git Flow。

```
main ──────────────────────────── 生产环境（受保护，禁止直接 push）
  ↑
  │ ← hotfix/xxx（从 main 分出，修复完成需合并回 main + develop）
  │
develop ───────────────────────── 开发集成主线（受保护，禁止直接 push）
  ↑
  │ ← feature/xxx（从 develop 分出，功能完成后合并回 develop）
  │ ← bugfix/xxx（从 develop 分出，develop 上的 bug 修复）
```

### 分支命名规范

| 分支类型 | 命名格式 | 示例 |
|---------|---------|------|
| Feature | `feature/功能描述` 或 `feature/ISSUE号-功能描述` | `feature/PIS-123-user-auth` |
| Bugfix | `bugfix/问题描述` 或 `bugfix/ISSUE号-修复描述` | `bugfix/PIS-456-login-timeout` |
| Hotfix | `hotfix/紧急修复描述` | `hotfix/critical-payment-fix` |

### 分支生命周期

- **创建**：`git checkout develop && git pull && git checkout -b feature/xxx`
- **同步上游**：`git merge develop` 或 `git rebase develop`
- **完成合并后**：分支自动删除（GitHub/GitLab 设置 `delete branch after merge`）

---

## 2. PR/MR 流程

### 标准流程

```
1. 从 develop 创建分支
2. 开发并 commit（保持原子性）
3. Push 到远程
4. 创建 PR，填写模板
5. 指定 Reviewer
6. 等待 Review 通过
7. Jenkins CI 构建通过
8. 合并到 develop
9. 分支自动删除
```

### PR 模板

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
- [ ] 代码已通过 Pre-commit 检查
- [ ] 已添加必要的测试
- [ ] 文档已更新（如需）

## Reviewer 备注
<!-- 给 Reviewer 的补充说明 -->
```

### 合并标准

- 至少 **1 人** Approve
- **Jenkins CI** 构建通过
- 无未解决的 Conversation
- 分支已最新（解决与目标分支的冲突）

---

## 3. Code Review 规范

### 作者职责

- 代码逻辑复杂处添加必要注释
- 准备好回复 Review 意见
- **不要在 Review 前自行合并**
- 不要在 PR 中混入不相关的改动

### Reviewer 职责

- **24 小时内**完成 Review
- 聚焦：逻辑正确性、代码风格、安全隐患
- 评价客观，避免个人偏好带入
- 确认 Jenkins CI 状态

### 合并门槛

```
最低 1 人 Approve + CI 通过 → 可合并
```

---

## 4. Git Hooks

后端和前端分开管理，各自使用最合适的工具。

### 后端（Python）— pre-commit

**安装方式：**
```bash
cd backend
pip install pre-commit ruff
pre-commit install
```

**检查内容：**
- Python：`ruff`（替代 flake8 + black + isort，速度快 10-100x）
- 通用：禁止 debug 代码、敏感信息检查

**.pre-commit-config.yaml 示例：**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
      - id: ruff-format
```

### 前端（Node.js）— husky

**安装方式：**
```bash
cd web
npm install husky lint-staged -D
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
```

**package.json lint-staged 配置：**
```json
{
  "lint-staged": {
    "*.{js,vue,ts}": ["eslint --fix", "prettier --write"]
  }
}
```

---

## 5. Git Etiquette

### 鼓励的行为

```
✅ Commit Often — 小步提交，每次有清晰改动
✅ 保持 commit 原子性 — 一个 commit 只做一件事
✅ 提交前本地跑测试 — 不要把坏代码推向远程
✅ Review 通过后再合并 — 不要绕过 Review
✅ 功能完成后及时开 PR — 不要等代码变坏
✅ 同步上游分支 — 经常 pull/rebase develop 减少冲突
```

### 禁止的行为

```
❌ 不要 push WIP（未完成的工作）到远程主分支
❌ 不要强制 push（git push --force）到 main/develop
❌ 不要在 PR 里混入不相关的改动
❌ 不要跳过 Pre-commit 直接 commit
```

---

## 6. CI/CD 联动（Jenkins）

### Pre-commit（本地）

- 在开发者本地运行
- 不阻塞远程，但作为质量门槛
- 失败则无法 commit（可 --no-verify 绕过，但不推荐）

### Jenkins Pipeline

```
Push → 自动触发 Jenkins Build
  ├── Backend
  │     ├── 单元测试 (pytest)
  │     ├── 代码检查 (ruff)
  │     └── 构建
  │
  ├── Frontend
  │     ├── 依赖安装
  │     ├── ESLint 检查
  │     ├── 构建
  │     └── 预览部署
  │
  └── 结果通知（可选：邮件/Slack）
```

### 部署规则

| 合并目标 | 触发动作 |
|---------|---------|
| `main` | 自动部署到生产环境（可选，视团队节奏） |
| `develop` | 自动部署到测试环境 |

---

## 7. 分支保护规则

### main（生产环境）

- ❌ 禁止直接 push
- ❌ 禁止 force push
- ✅ 必须通过 PR 合并
- ✅ 必须有 CI 通过
- ✅ 必须有 1 人 Approve

### develop（开发主线）

- ❌ 禁止直接 push
- ❌ 禁止 force push
- ✅ 必须通过 PR 合并
- ✅ 必须有 CI 通过

### feature/bugfix/hotfix

- 可直接 push
- 鼓励通过 PR 协作

---

## 8. 工具链汇总

| 环节 | 工具 | 适用范围 |
|-----|------|---------|
| Git Hooks（后端） | pre-commit | backend/ |
| Git Hooks（前端） | husky + lint-staged | web/ |
| CI/CD | Jenkins | 全项目 |
| 代码风格（后端） | ruff（lint + format） | backend/ |
| 代码风格（前端） | eslint, prettier | web/ |

---

## 设计决策

1. **分支模型**：标准 Git Flow，平衡了规范性和灵活性
2. **Review 门槛**：1 人 Approve，门槛适中不过度拖延
3. **Hook 管理**：后端 pre-commit、前端 husky，各自用最合适的工具
4. **分支合并后自动删除**：保持仓库整洁
5. **CI 联动**：Jenkins 覆盖构建和测试，不重复造轮子
