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

默认同步到 `~/.agents/skills`：

```bash
./scripts/sync-to-local.sh
```

指定目标目录：

```bash
./scripts/sync-to-local.sh ~/.claude/skills
```

当前 Codex 会枚举 `~/.agents/skills`，因此不建议同时同步到 `~/.codex/skills`，避免出现重复入口。

## 校验

```bash
./scripts/validate.sh
```

校验内容包括 skill 目录完整性、`SKILL.md` frontmatter、`agents/openai.yaml` 存在性，以及 `xie-xiaoshuo` 自带的结构测试和 `novel_tools.py` 回归测试。

