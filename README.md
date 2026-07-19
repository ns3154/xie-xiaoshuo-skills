# 写小说 Skills

这是个人中文网文协作 skill 项目，当前包含一个总入口和六个子技能：

- `xie-xiaoshuo`：写小说总入口，负责意图判断和路由。
- `xie-write`：正文、续写、改稿、大纲与写作记忆回写。
- `xie-review`：审稿、终审、送审包装与项目清理。
- `xie-deslop`：去 AI 味、清理模板腔与模型退化。
- `xie-learn`：扫榜、拆文、对标与方法沉淀。
- `xie-import`：导入旧稿并反向生成写作记忆。
- `xie-cover`：小说封面生成、迭代与尺寸检查。

## 目录结构

```text
skills/
  xie-xiaoshuo/
  xie-write/
  xie-review/
  xie-deslop/
  xie-learn/
  xie-import/
  xie-cover/
scripts/
  sync-to-local.sh
  validate.sh
```

## 本地安装

默认在 `~/.agents/skills` 中创建指向本仓库源码的软连接：

```bash
./scripts/sync-to-local.sh
```

指定目标目录：

```bash
./scripts/sync-to-local.sh ~/.claude/skills
```

软连接安装后，修改本仓库的 `skills/` 会立即反映到本地入口，不需要再次同步。若移动或删除本仓库，需要重新运行脚本以重建链接。

如果目标位置已有旧副本、普通文件或其他软连接，脚本会先将它们移动到目标目录同级的 `skills-backup/xie-symlink-migration-<时间戳-进程号>/`，再创建新链接；备份不会被当成可用 skill 枚举，重复执行也不会产生额外备份。

当前 Codex 会枚举 `~/.agents/skills`，因此不建议同时同步到 `~/.codex/skills`，避免出现重复入口。

## 校验

```bash
./scripts/validate.sh
```

校验内容包括 skill 目录完整性、`SKILL.md` frontmatter、`agents/openai.yaml` 存在性，`xie-xiaoshuo` 自带的结构测试和 `novel_tools.py` 回归测试，以及本地软连接安装、旧副本备份与重复执行测试。
