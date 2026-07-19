# 本地 Skill 软连接实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Agents 与 Claude 的本地 `xie-*` skill 从独立副本迁移为直接指向源码仓库的软连接。

**Architecture:** `sync-to-local.sh` 作为唯一安装入口，为 7 个固定 skill 创建绝对软连接。遇到旧副本时先移入目标目录同级的 `skills-backup/`，避免备份被枚举为可用 skill；正确链接重复执行时不做变更。

**Tech Stack:** Bash、`ln`、`mv`、`readlink`、`mktemp`、Python unittest。

## Global Constraints

- 所有对话、文档和代码注释使用中文。
- 只处理 `xie-xiaoshuo`、`xie-write`、`xie-review`、`xie-deslop`、`xie-learn`、`xie-import`、`xie-cover`。
- 不删除旧本地副本；迁移前必须备份。
- 仓库源码是唯一维护源。

---

### Task 1: 用回归测试定义软连接安装行为

**Files:**
- Create: `scripts/test-sync-to-local.sh`
- Modify: `scripts/validate.sh`

**Interfaces:**
- Consumes: `scripts/sync-to-local.sh [目标目录]`
- Produces: 可独立运行的软连接、备份和幂等性测试

- [ ] **Step 1: 写失败测试**

测试在 `mktemp -d` 创建的目标目录中预置 `xie-write/独有文件.txt`，运行安装脚本后断言 7 个入口均为软连接、链接目标正确、旧文件存在于目标同级的 `skills-backup`，并断言第二次执行不会增加备份目录。

- [ ] **Step 2: 运行测试并确认旧实现失败**

Run: `bash scripts/test-sync-to-local.sh`

Expected: FAIL，原因是旧实现创建普通目录而不是软连接。

- [ ] **Step 3: 把测试接入完整校验**

在 `scripts/validate.sh` 的 Python 测试之后运行：

```bash
bash "$ROOT/scripts/test-sync-to-local.sh"
```

### Task 2: 实现安全、幂等的软连接安装

**Files:**
- Modify: `scripts/sync-to-local.sh`
- Modify: `README.md`

**Interfaces:**
- Consumes: 可选目标目录参数，默认 `$HOME/.agents/skills`
- Produces: 7 个指向 `$ROOT/skills/<skill>` 的绝对软连接

- [ ] **Step 1: 实现目标判断与备份**

对每个 skill：

```bash
if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
  continue
fi

if [[ -e "$target" || -L "$target" ]]; then
  mkdir -p "$BACKUP_DIR"
  mv "$target" "$BACKUP_DIR/$skill"
fi
```

- [ ] **Step 2: 创建软连接**

```bash
ln -s "$source" "$target"
```

- [ ] **Step 3: 运行专项和完整校验**

Run: `bash scripts/test-sync-to-local.sh`

Expected: `软连接同步测试通过：7 个 skill`

Run: `./scripts/validate.sh`

Expected: 结构校验、全部 Python 测试和软连接同步测试通过。

- [ ] **Step 4: 更新 README**

明确本地安装现在创建软连接、源码修改即时生效、仓库移动后需重跑脚本，以及旧副本会备份到 skill 枚举根目录之外。

### Task 3: 迁移真实本地入口并验证

**Files:**
- Runtime targets: `/Users/yang/.agents/skills/xie-*`
- Runtime targets: `/Users/yang/.claude/skills/xie-*`

**Interfaces:**
- Consumes: 已通过测试的 `scripts/sync-to-local.sh`
- Produces: Agents 与 Claude 两端共 14 个软连接

- [ ] **Step 1: 迁移 Agents 入口**

Run: `./scripts/sync-to-local.sh /Users/yang/.agents/skills`

Expected: 7 个旧副本完成备份并替换为软连接。

- [ ] **Step 2: 迁移 Claude 入口**

Run: `./scripts/sync-to-local.sh /Users/yang/.claude/skills`

Expected: 7 个旧副本完成备份并替换为软连接。

- [ ] **Step 3: 验证链接与内容**

逐项用 `readlink` 确认链接目标，并用 `diff -qr` 确认通过两端入口读取的内容与仓库源码一致。

- [ ] **Step 4: 最终验证**

Run: `./scripts/validate.sh && git diff --check`

Expected: 所有命令退出码为 0，工作区只包含本计划内文件。

- [ ] **Step 5: 提交并推送**

```bash
git add README.md scripts/sync-to-local.sh scripts/test-sync-to-local.sh scripts/validate.sh docs/superpowers
git commit -m "改用软连接安装本地小说 skills"
git push origin main
```
