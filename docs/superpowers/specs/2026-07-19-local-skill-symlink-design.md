# 本地 Skill 软连接设计

## 目标

让 `~/.agents/skills` 与 `~/.claude/skills` 中的 7 个 `xie-*` skill 直接引用本仓库的 `skills/` 目录。以后修改仓库源码后，两端立即读取新内容，不再需要重复执行复制同步。

## 方案

`scripts/sync-to-local.sh` 保留原有调用形式，但把行为从 `rsync` 复制改为创建绝对路径软连接：

```text
目标目录/xie-write -> 仓库/skills/xie-write
```

绝对路径明确绑定当前源码仓库 `/Users/yang/project/xie-xiaoshuo-skills`。仓库移动后需要重新运行脚本以重建链接。

## 迁移与安全

- 目标不存在时直接创建软连接。
- 目标已经是指向正确源码的软连接时保持不变，保证重复执行安全。
- 目标是旧目录、普通文件或其他软连接时，先移动到目标目录同级的 `skills-backup/xie-symlink-migration-<时间戳-进程号>/`，再创建新链接，避免备份被递归枚举为可用 skill。
- 只处理脚本中明确列出的 7 个 `xie-*` skill，不触碰其他本地 skill。
- 源码 skill 缺少 `SKILL.md` 时立即失败，不迁移任何对应目标。

## 校验

新增 Shell 回归测试，使用临时目录验证：

1. 7 个目标均创建为软连接。
2. 每个链接均指向仓库对应源码目录。
3. 旧目录会在 skill 枚举根目录之外备份，独有文件不丢失。
4. 重复执行不会创建额外备份。

`scripts/validate.sh` 纳入该测试。真实迁移后再用 `readlink`、`diff` 和完整校验确认 `~/.agents`、`~/.claude` 两端均即时引用源码。
