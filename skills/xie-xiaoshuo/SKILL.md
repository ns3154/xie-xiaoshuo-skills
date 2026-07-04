---
name: xie-xiaoshuo
description: "Use when 用户需要中文网文协作总入口：写正文、续写、改稿、审稿、去 AI 味、拆文扫榜、导入旧稿、封面、送审包装或长篇项目维护；优先路由到 xie-* 子技能，用户不需要记住所有子技能名。"
---

# 写小说总入口

## 1. 总原则

这是个人中文网文工具箱的主入口，只负责判断意图、守住硬边界、把任务交给更小的 `xie-*` 技能执行。不要把低频长流程继续塞回本文件。

- 当前维护源只放在 `~/.agents/skills/`；不要再同步或维护 `~/.codex/skills/xie-xiaoshuo`。
- 用户只要说 `/xie`、`写小说`、`帮我写书`、`续写`、`审稿`、`去 AI 味` 等，都可以先进入本入口，再由本入口路由。
- 所有对话、文档、正文、写作说明默认使用中文。
- 项目资料和正文事实优先于模型记忆、旧项目经验、远端工具或外部审稿结论。
- 旧项目只能复用方法层，不能带入人物、卷名、章号、文风、声口、审稿分数和结局判断。
- 能执行就执行；只有缺少答案会破坏主线、人物关系、文件安全或用户授权边界时，才停下来问。

## 2. 路由表

| 用户意图 | 路由技能 | 处理范围 |
|---|---|---|
| 写正文、续写、补章、重写、改稿、修大纲、长链写作计划、回写记忆 | `xie-write` | 正文生产、章节规格、声口、伏笔、时间线、写后回写 |
| 审稿、终审、卷末检查、完稿审读、专业 AI 审稿包、二轮复审、送审包装、项目清理 | `xie-review` | review-only、问题分级、最小修补、审稿数据包、送审材料、保守归档 |
| 去 AI 味、降模板感、清理机械句式、模型退化检查 | `xie-deslop` | 保留原意的文本降噪、确定性表层检查、最小改写 |
| 扫榜、拆文、对标、学习爆款、市场趋势、题材判断 | `xie-learn` | 榜单采集、拆文库、节奏/情绪/文风方法层沉淀 |
| 导入已有小说、反向解析旧稿、把半成品变成项目结构 | `xie-import` | 章节拆分、资料初始化、摘要/人物/伏笔/时间线反推 |
| 封面、封面图、上架封面、封面迭代 | `xie-cover` | 书名笔名确认、封面提示词、出图、尺寸和质量检查 |

如果目标技能不可用，按对应流程在本轮直接执行，并说明 fallback；不要因为缺少子技能就中止任务。

## 3. 通用读取边界

写作、改稿、审稿、导入或清理前，先确认当前工作区和书名。若项目有 `AGENTS.md`、`CLAUDE.md`、`README.md`、`资料/写作记忆/`、正文相邻章节、审稿报告或项目脚本，优先读取这些本地状态源。

最低共同边界：

- `正文/` 默认只放正式章节 `.txt`，标题行格式为 `第x章 章节名`。
- 大纲是计划，正文才是事实；计划不能覆盖已经写出的内容。
- 修改正文前先看相关文件的现状和用户授权范围，不借机改主线、人设、结局。
- 写完或修完正文后必须回写项目记忆；没有记忆文件时创建简版。
- 审稿任务先声明覆盖范围，不能把抽检、旧报告或目录名当全文结论。
- 清理任务默认保守移动到 `bak/`，不直接永久删除；不得归档或删除 `正文/`、`资料/写作记忆/`、`资料/真相系统/`、当前有效大纲、`AGENTS.md`、`README.md` 和项目脚本，除非用户当次点名。

## 4. 工具与兼容

通用统计、章节检查、打包脚本仍保留在本入口目录，供各子技能复用：

```bash
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py stats <项目根目录> --details
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py check <项目根目录> --expected-count <章节数>
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py doctor <项目根目录> --expected-count <章节数>
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py scaffold <项目根目录> --include-entry --write
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py truth-gate <项目根目录>
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py query <项目根目录> <关键词> --chapter <章号>
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py context-pack <项目根目录> --target-chapter <章号>
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py zip <项目根目录> <输出zip> --include 正文 --include 审稿数据包
```

旧 reference 文件暂时保留在本目录作为兼容资产；新增工作优先读对应 `xie-*` 技能自己的说明。
