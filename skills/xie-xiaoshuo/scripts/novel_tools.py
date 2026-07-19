#!/usr/bin/env python3
"""中文长篇小说项目通用统计、校验和打包工具。"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import NamedTuple


DEFAULT_BODY_DIR = "正文"
TRUTH_SYSTEM_DIR = Path("资料") / "真相系统"
TRUTH_REQUIRED_FILES = (
    "00-使用说明.md",
    "01-连续性门禁.md",
    "02-待同步章节.md",
    "03-事实总账.jsonl",
    "04-事件时间线.jsonl",
    "05-人物状态快照.md",
    "06-物件持有表.md",
    "07-伏笔承诺回收表.md",
    "08-下一章上下文包.md",
    "09-章节结算模板.md",
    "10-因果链复盘.md",
)
FINISHED_TRUTH_REQUIRED_FILES = (
    "00-使用说明.md",
    "01-完本门禁.md",
    "02-待核账章节.md",
    "03-事实总账.jsonl",
    "04-事件时间线.jsonl",
    "05-人物终局状态.md",
    "06-物件身份归属表.md",
    "07-伏笔承诺回收表.md",
    "08-全书问题池.md",
    "09-完本自检清单.md",
    "10-修订建议.md",
)
CONTEXT_SOURCE_FILES = (
    "README.md",
    "AGENTS.md",
    "资料/写作记忆/00-当前写作状态.md",
    "资料/写作记忆/02-人物状态表.md",
    "资料/写作记忆/03-时间线.md",
    "资料/写作记忆/04-伏笔台账.md",
    "资料/写作记忆/05-设定规则.md",
    "资料/写作记忆/07-章节摘要.md",
    "资料/写作记忆/08-风格与禁忌.md",
    "资料/写作记忆/10-章节规格卡.md",
    "资料/写作记忆/11-失败与避坑.md",
    "资料/真相系统/00-使用说明.md",
    "资料/真相系统/01-连续性门禁.md",
    "资料/真相系统/01-完本门禁.md",
    "资料/真相系统/02-待同步章节.md",
    "资料/真相系统/02-待核账章节.md",
    "资料/真相系统/05-人物状态快照.md",
    "资料/真相系统/05-人物终局状态.md",
    "资料/真相系统/06-物件持有表.md",
    "资料/真相系统/06-物件身份归属表.md",
    "资料/真相系统/07-伏笔承诺回收表.md",
    "资料/真相系统/08-下一章上下文包.md",
    "资料/真相系统/08-全书问题池.md",
    "资料/真相系统/10-因果链复盘.md",
)
ENTRY_REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
)
MEMORY_REQUIRED_FILES = (
    "00-当前写作状态.md",
    "01-故事圣经.md",
    "02-人物状态表.md",
    "03-时间线.md",
    "04-伏笔台账.md",
    "05-设定规则.md",
    "07-章节摘要.md",
    "08-风格与禁忌.md",
    "10-章节规格卡.md",
    "11-失败与避坑.md",
)
QUERY_TEXT_SUFFIXES = {".md", ".txt", ".json"}
SCAFFOLD_ENTRY_TEMPLATES = {
    "README.md": """# 小说项目入口

## 当前状态

- 项目阶段：待核
- 正文目录：`正文/`
- 当前可写落点：待核
- 最近处理：待核

## 开写前读取策略

### 固定入口

每次写正文、续写、改正文前，先读以下短入口，确认当前落点、门禁状态和下一章承接：

1. `AGENTS.md`
2. `资料/写作记忆/00-当前写作状态.md`
3. `资料/写作记忆/08-风格与禁忌.md`
4. `资料/真相系统/01-连续性门禁.md`
5. `资料/真相系统/02-待同步章节.md`
6. `资料/真相系统/08-下一章上下文包.md`

### 按章按需

- 大纲、人物表、声口表、伏笔总表：只读本章相关卷段、人物、伏笔和声口卡。
- 章节摘要、人物状态、时间线、伏笔台账、设定规则：按章号、人物、物件、地点和关键词定位读取。
- 相邻正文：读取上一章结尾、本章相关前文和下一章必须承接的后果，不做无差别全文通读。

### 长篇后期规则

- 未写的下一章以 `资料/真相系统/08-下一章上下文包.md` 为准。
- 追查旧事实优先用 `novel_tools.py query`；回查已写章节周边上下文时再用 `novel_tools.py context-pack`。
- 正文事实优先于大纲；若冲突，以正文和真相系统结算后的事实为准，再更新资料。

## 目录说明

- `正文/`：正式章节 `.txt`，唯一正文事实源。
- `资料/写作记忆/`：当前状态、章节摘要、人物、时间线、伏笔、设定、风格和规格卡。
- `资料/真相系统/`：长篇连续性门禁、事实总账、事件时间、人物/物件状态、伏笔承诺和下一章上下文包。

## 清理边界

- 不得在清理任务中移动、删除或归档 `正文/`、`资料/写作记忆/`、`资料/真相系统/`、当前有效大纲、`README.md` 和 `AGENTS.md`，除非用户当次点名。
- 外部评审原文、投递包、压缩包和过程稿不作为后续写正文的优先依据；有效结论应落到账或大纲。
""",
    "AGENTS.md": """# 协作规则

## 1. 语言和事实源

- 所有对话、文档和报告默认使用中文。
- `正文/` 是唯一正式正文和最高事实源。
- 大纲是计划，正文已经写出的内容才是事实。
- 无法从正文、写作记忆或真相系统确认的内容标 `待核`。
- 未获授权前不得修改正文。

## 2. 写作前读取策略

写正文、续写、改正文前，先读固定入口，确认当前落点、门禁状态、风格硬禁和下一章承接：

- `资料/写作记忆/00-当前写作状态.md`
- `资料/写作记忆/08-风格与禁忌.md`
- `资料/真相系统/01-连续性门禁.md`
- `资料/真相系统/02-待同步章节.md`
- `资料/真相系统/08-下一章上下文包.md`

以下资料按章按需读取，不要求每次全文通读：

- 大纲：只读当前卷、当前关卡链、下一处承接和与本章冲突的计划项。
- 人物表/声口表：只读本章出场、被审、被牵动或影响决策的人物；写对话前抽取本章出场人物声口卡。
- 伏笔总表/伏笔台账：只读本章会触发、推进、暂缓或回收的伏笔。
- 章节摘要、人物状态、时间线、设定规则：按人物、章号、物件、地点和伏笔关键词定位读取。
- 相邻正文：读取上一章结尾、本章相关前文和下一章必须承接的后果。

后期正文和资料体量变大后，未写下一章优先读 `资料/真相系统/08-下一章上下文包.md`；追查旧事实用关键词查询、章节号定位和 `novel_tools.py query`；回查已写章节周边上下文时再用 `novel_tools.py context-pack`。不要把几十万字正文或整套资料一次性塞入上下文。

## 3. 正文硬规则

- 正文目录默认是 `正文/`，文件使用 `.txt`。
- 每章第一行只写 `第x章 章节名`，标题行以外不得出现规格卡、任务说明、伏笔说明、读者提示、AI 自述或创作脚手架。
- 章末最后一段就是钩子，钩子后不追加总结、升华、作者解释或后文预告。
- 章节排序按数值章号，不按字符串排序。

## 4. 写后回写

每完成一章或一次正文修订，回写写作记忆和真相系统；新增或修改正文后，先把相关章节列入 `资料/真相系统/02-待同步章节.md`，完成事实、事件、人物、物件、伏笔和下一章承接结算后，才能清为“当前待同步：无”。

## 5. 交付门禁

- 交付前必须确认 `资料/真相系统/01-连续性门禁.md` 为 PASS，`02-待同步章节.md` 已清零。
- 交付前必须跑：

```bash
python3 ~/.agents/skills/xie-xiaoshuo/scripts/novel_tools.py truth-gate .
```

- `truth-gate` 未通过时按 P0 处理，不得用“文风已修好”“机械检查通过”覆盖。
""",
}
MEMORY_TEMPLATE_TITLES = {
    "00-当前写作状态.md": "当前写作状态",
    "01-故事圣经.md": "故事圣经",
    "02-人物状态表.md": "人物状态表",
    "03-时间线.md": "时间线",
    "04-伏笔台账.md": "伏笔台账",
    "05-设定规则.md": "设定规则",
    "07-章节摘要.md": "章节摘要",
    "08-风格与禁忌.md": "风格与禁忌",
    "10-章节规格卡.md": "章节规格卡",
    "11-失败与避坑.md": "失败与避坑",
}
CONTINUOUS_TRUTH_TEMPLATES = {
    "00-使用说明.md": "# 使用说明\n\n待核：本目录由 scaffold 初始化，所有条目必须按正文回填。\n",
    "01-连续性门禁.md": "# 连续性门禁\n\n当前门禁：FAIL\n\n待核：补齐事实总账、事件时间线和待同步章节后再改为 PASS。\n",
    "02-待同步章节.md": "# 待同步章节\n\n当前待同步：待核\n",
    "03-事实总账.jsonl": "",
    "04-事件时间线.jsonl": "",
    "05-人物状态快照.md": "# 人物状态快照\n\n待核：按正文最后已知状态回填。\n",
    "06-物件持有表.md": "# 物件持有表\n\n待核：按正文确认物件、文书、印信和账册归属。\n",
    "07-伏笔承诺回收表.md": "# 伏笔承诺回收表\n\n待核：按 open/advance/resolve/abandon 记录。\n",
    "08-下一章上下文包.md": (
        "# 下一章上下文包\n\n"
        "待核：写作前由正文与台账生成。\n\n"
        "## 使用规则\n\n"
        "- 本文件只服务未写的下一章，建议控制在 800-1500 字。\n"
        "- 只写上一章尾、当前人物/物件/信息差、必须承接的果、禁止重复的动作和章末钩子方向。\n"
        "- 不复制整章正文、大段大纲或完整人物表；旧事实用 `novel_tools.py query` 定位。\n"
    ),
    "09-章节结算模板.md": "# 章节结算模板\n\n待核：记录新增事实、事件、人物状态、物件归属和伏笔变化。\n",
    "10-因果链复盘.md": "# 因果链复盘\n\n待核：复盘相邻章节因果承接。\n",
}
FINISHED_TRUTH_TEMPLATES = {
    "00-使用说明.md": "# 使用说明\n\n待核：本目录由 scaffold 初始化，所有条目必须按正文回填。\n",
    "01-完本门禁.md": "# 完本门禁\n\n| 层级 | 结论 | 说明 |\n|---|---|---|\n| 正文门禁 | FAIL | 待核：全文复读完成后再改为 PASS。 |\n| 台账门禁 | 待核 | 待核：台账补齐后关闭。 |\n",
    "02-待核账章节.md": "# 待核账章节\n\n当前正文门禁：FAIL\n当前台账门禁：待核\n",
    "03-事实总账.jsonl": "",
    "04-事件时间线.jsonl": "",
    "05-人物终局状态.md": "# 人物终局状态\n\n待核：按正文终局状态回填。\n",
    "06-物件身份归属表.md": "# 物件身份归属表\n\n待核：按正文确认物件、文书、身份和归属。\n",
    "07-伏笔承诺回收表.md": "# 伏笔承诺回收表\n\n待核：按 open/advance/resolve/abandon 记录。\n",
    "08-全书问题池.md": "# 全书问题池\n\n待核：只登记可回溯正文的问题。\n",
    "09-完本自检清单.md": "# 完本自检清单\n\n待核：全文复读后勾核。\n",
    "10-修订建议.md": "# 修订建议\n\n待核：门禁未 PASS 前只记录核账项，不提出正文修订方案。\n",
}
CHAPTER_FILE_RE = re.compile(r"第\s*0*(\d+)\s*章")
TITLE_LINE_RE = re.compile(r"^第\s*0*(\d+)\s*章(?:[：:\s　-]+(.+))?$")
PLACEHOLDER_RE = re.compile(
    r"(?im)^\s*(?:[#>*-]\s*)?(?:TODO|TBD|FIXME|待补|占位)(?:\s*[:：]|\s|$)"
    r"|[\[【(<（]\s*(?:TODO|TBD|FIXME|待补|占位)\s*[\]】)>）]"
)
HALFWIDTH_CJK_QUOTE_RE = re.compile(
    r'"[^"\n]*[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff][^"\n]*"'
    r"|'[^'\n]*[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff][^'\n]*'"
)
EXCLUDED_NAMES = {".DS_Store", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc"}


class Chapter(NamedTuple):
    path: Path
    rel_path: str
    volume: str
    number: int
    file_number: int | None
    title_number: int | None
    title: str
    first_line: str
    body_chars: int
    total_chars: int
    text: str


class VolumeSummary(NamedTuple):
    volume: str
    start: int
    end: int
    chapter_count: int
    body_chars: int
    total_chars: int


def count_non_whitespace(text: str) -> int:
    return sum(1 for char in text if not char.isspace())


def is_excluded(path: Path) -> bool:
    return (
        path.name in EXCLUDED_NAMES
        or path.suffix in EXCLUDED_SUFFIXES
        or any(part in EXCLUDED_NAMES for part in path.parts)
    )


def resolve_body_root(project_root: Path, body_dir: str = DEFAULT_BODY_DIR) -> Path:
    root = project_root.resolve()
    candidate = root / body_dir
    return candidate if candidate.is_dir() else root


def parse_number(pattern: re.Pattern[str], text: str) -> int | None:
    match = pattern.search(text)
    return int(match.group(1)) if match else None


def parse_chapter(path: Path, project_root: Path, body_root: Path) -> Chapter:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    first_line = lines[0].strip() if lines else ""
    title_match = TITLE_LINE_RE.match(first_line)
    file_number = parse_number(CHAPTER_FILE_RE, path.name)
    title_number = int(title_match.group(1)) if title_match else None
    number = file_number or title_number or 10**9
    title = title_match.group(2).strip() if title_match and title_match.group(2) else path.stem
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""

    try:
        volume = path.parent.relative_to(body_root).as_posix()
    except ValueError:
        volume = path.parent.name

    return Chapter(
        path=path,
        rel_path=path.relative_to(project_root).as_posix(),
        volume=volume or ".",
        number=number,
        file_number=file_number,
        title_number=title_number,
        title=title,
        first_line=first_line,
        body_chars=count_non_whitespace(body),
        total_chars=count_non_whitespace(text),
        text=text,
    )


def collect_chapters(project_root: str | Path, body_dir: str = DEFAULT_BODY_DIR) -> list[Chapter]:
    root = Path(project_root).resolve()
    body_root = resolve_body_root(root, body_dir)
    txt_files = sorted(
        path for path in body_root.rglob("*.txt") if path.is_file() and not is_excluded(path)
    )
    chapters = [parse_chapter(path, root, body_root) for path in txt_files]
    return sorted(chapters, key=lambda chapter: (chapter.number, chapter.rel_path))


def summarize_by_volume(chapters: list[Chapter]) -> list[VolumeSummary]:
    grouped: dict[str, list[Chapter]] = defaultdict(list)
    for chapter in chapters:
        grouped[chapter.volume].append(chapter)

    summaries: list[VolumeSummary] = []
    for volume, volume_chapters in grouped.items():
        ordered = sorted(volume_chapters, key=lambda chapter: chapter.number)
        summaries.append(
            VolumeSummary(
                volume=volume,
                start=ordered[0].number,
                end=ordered[-1].number,
                chapter_count=len(ordered),
                body_chars=sum(chapter.body_chars for chapter in ordered),
                total_chars=sum(chapter.total_chars for chapter in ordered),
            )
        )
    return sorted(summaries, key=lambda summary: summary.start)


def validate_project(
    project_root: str | Path,
    body_dir: str = DEFAULT_BODY_DIR,
    expected_count: int | None = None,
) -> list[str]:
    chapters = collect_chapters(project_root, body_dir)
    errors: list[str] = []
    if not chapters:
        return [f"未找到正文 .txt 文件：{Path(project_root) / body_dir}"]

    for chapter in chapters:
        if chapter.file_number is None:
            errors.append(f"{chapter.rel_path}：章节文件名无法解析章号")
        if chapter.title_number is None:
            errors.append(f"{chapter.rel_path}：首行章题格式错误，应为“第x章 章节名”")
        if (
            chapter.file_number is not None
            and chapter.title_number is not None
            and chapter.file_number != chapter.title_number
        ):
            errors.append(
                f"{chapter.rel_path}：文件名章号与标题章号不一致"
                f"（文件名第{chapter.file_number}章，标题第{chapter.title_number}章）"
            )
        if PLACEHOLDER_RE.search(chapter.text):
            errors.append(f"{chapter.rel_path}：正文含 TODO/TBD/FIXME/待补/占位 残留")
        halfwidth_quote_lines = [
            str(line_no)
            for line_no, line in enumerate(chapter.text.splitlines(), start=1)
            if HALFWIDTH_CJK_QUOTE_RE.search(line)
        ]
        if halfwidth_quote_lines:
            errors.append(
                f"{chapter.rel_path}：正文用英文半角引号包裹中文"
                f"（第{'、'.join(halfwidth_quote_lines)}行）；"
                "外层应使用“”，嵌套引语应使用‘’"
            )

    numbers = [chapter.file_number for chapter in chapters if chapter.file_number is not None]
    duplicates = sorted(number for number, count in Counter(numbers).items() if count > 1)
    if duplicates:
        errors.append("存在重复章号：" + "、".join(f"第{number}章" for number in duplicates))

    unique_numbers = sorted(set(numbers))
    if unique_numbers:
        missing = sorted(set(range(unique_numbers[0], unique_numbers[-1] + 1)) - set(unique_numbers))
        if missing:
            preview = "、".join(f"第{number}章" for number in missing[:20])
            suffix = "..." if len(missing) > 20 else ""
            errors.append(f"章节不连续，缺章：{preview}{suffix}")

    if expected_count is not None and len(chapters) != expected_count:
        errors.append(f"章节数不符：实际 {len(chapters)}，预期 {expected_count}")

    return errors


def read_jsonl_records(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    records: list[dict[str, object]] = []
    errors: list[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as error:
            errors.append(f"{path.name} 第 {line_no} 行不是合法 JSON：{error.msg}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path.name} 第 {line_no} 行必须是 JSON object")
            continue
        records.append(record)
    return records, errors


def chapter_numbers_from_records(
    records: list[dict[str, object]],
    path_name: str,
) -> tuple[set[int], list[str]]:
    numbers: set[int] = set()
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        value = record.get("chapter")
        if isinstance(value, int):
            numbers.add(value)
        elif isinstance(value, str) and value.isdigit():
            numbers.add(int(value))
        else:
            errors.append(f"{path_name} 第 {index} 条缺少整数 chapter 字段")
    return numbers, errors


def validate_truth_jsonl_coverage(truth_root: Path, chapter_numbers: set[int]) -> list[str]:
    errors: list[str] = []
    for rel_path in ("03-事实总账.jsonl", "04-事件时间线.jsonl"):
        path = truth_root / rel_path
        if not path.is_file():
            continue
        records, json_errors = read_jsonl_records(path)
        errors.extend(json_errors)
        numbers, number_errors = chapter_numbers_from_records(records, rel_path)
        errors.extend(number_errors)
        missing = sorted(chapter_numbers - numbers)
        if missing:
            preview = "、".join(f"第{number}章" for number in missing[:20])
            suffix = "..." if len(missing) > 20 else ""
            errors.append(f"{rel_path} 缺少正文已存在章节记录：{preview}{suffix}")
    return errors


def parse_finished_body_gate(gate_text: str) -> str | None:
    table_match = re.search(r"\|\s*正文门禁\s*\|\s*([^|\s]+)\s*\|", gate_text)
    if table_match:
        return table_match.group(1).strip()
    line_match = re.search(r"(?m)^当前正文门禁：\s*(\S+)\s*$", gate_text)
    return line_match.group(1).strip() if line_match else None


def validate_continuous_truth_system(
    root: Path,
    truth_root: Path,
    body_dir: str = DEFAULT_BODY_DIR,
) -> list[str]:
    errors: list[str] = []

    for rel_path in TRUTH_REQUIRED_FILES:
        if not (truth_root / rel_path).is_file():
            errors.append(f"真相系统缺文件：{TRUTH_SYSTEM_DIR.as_posix()}/{rel_path}")

    gate_path = truth_root / "01-连续性门禁.md"
    if gate_path.is_file():
        gate_text = gate_path.read_text(encoding="utf-8")
        gate_match = re.search(r"(?m)^当前门禁：\s*(\S+)\s*$", gate_text)
        if gate_match is None:
            errors.append("连续性门禁必须有独立状态行“当前门禁：PASS”")
        elif gate_match.group(1) != "PASS":
            errors.append(f"连续性门禁当前状态不是 PASS：{gate_match.group(1)}")

    pending_path = truth_root / "02-待同步章节.md"
    if pending_path.is_file():
        pending_text = pending_path.read_text(encoding="utf-8")
        pending_match = re.search(r"(?m)^当前待同步：\s*(.+?)\s*$", pending_text)
        if pending_match is None:
            errors.append("待同步章节必须有独立状态行“当前待同步：无”")
        elif pending_match.group(1) != "无":
            errors.append(f"待同步章节未清零：{pending_match.group(1)}")
        if re.search(r"(?im)^\s*-\s*\[\s*\]", pending_text):
            errors.append("待同步章节仍有未勾选事项")

    chapters = collect_chapters(root, body_dir)
    chapter_numbers = {chapter.number for chapter in chapters if chapter.number != 10**9}
    errors.extend(validate_truth_jsonl_coverage(truth_root, chapter_numbers))
    return errors


def validate_finished_truth_system(
    root: Path,
    truth_root: Path,
    body_dir: str = DEFAULT_BODY_DIR,
) -> list[str]:
    errors: list[str] = []

    for rel_path in FINISHED_TRUTH_REQUIRED_FILES:
        if not (truth_root / rel_path).is_file():
            errors.append(f"真相系统缺文件：{TRUTH_SYSTEM_DIR.as_posix()}/{rel_path}")

    gate_path = truth_root / "01-完本门禁.md"
    if gate_path.is_file():
        body_gate = parse_finished_body_gate(gate_path.read_text(encoding="utf-8"))
        if body_gate is None:
            errors.append("完本门禁必须包含“正文门禁 | PASS”或“当前正文门禁：PASS”")
        elif body_gate != "PASS":
            errors.append(f"正文门禁当前状态不是 PASS：{body_gate}")

    chapters = collect_chapters(root, body_dir)
    chapter_numbers = {chapter.number for chapter in chapters if chapter.number != 10**9}
    errors.extend(validate_truth_jsonl_coverage(truth_root, chapter_numbers))
    return errors


def validate_truth_system(
    project_root: str | Path,
    body_dir: str = DEFAULT_BODY_DIR,
) -> list[str]:
    root = Path(project_root).resolve()
    truth_root = root / TRUTH_SYSTEM_DIR
    errors: list[str] = []

    if not truth_root.is_dir():
        return [f"未找到真相系统目录：{TRUTH_SYSTEM_DIR.as_posix()}"]

    if (truth_root / "01-完本门禁.md").is_file():
        errors.extend(validate_finished_truth_system(root, truth_root, body_dir))
    else:
        errors.extend(validate_continuous_truth_system(root, truth_root, body_dir))
    return errors


def chapter_number_summary(chapters: list[Chapter]) -> dict[str, object]:
    numbers = sorted(chapter.number for chapter in chapters if chapter.number != 10**9)
    duplicates = sorted(number for number, count in Counter(numbers).items() if count > 1)
    if not numbers:
        return {"start": None, "end": None, "missing": [], "duplicates": duplicates}

    missing = sorted(set(range(numbers[0], numbers[-1] + 1)) - set(numbers))
    return {
        "start": numbers[0],
        "end": numbers[-1],
        "missing": missing,
        "duplicates": duplicates,
    }


def detect_truth_profile(truth_root: Path) -> dict[str, object]:
    if not truth_root.is_dir():
        return {
            "type": "missing",
            "label": "未找到真相系统",
            "root": TRUTH_SYSTEM_DIR.as_posix(),
            "required_files": [],
            "missing": [],
        }
    if (truth_root / "01-完本门禁.md").is_file():
        required = FINISHED_TRUTH_REQUIRED_FILES
        profile_type = "finished"
        label = "完本门禁"
    elif (truth_root / "01-连续性门禁.md").is_file():
        required = TRUTH_REQUIRED_FILES
        profile_type = "continuous"
        label = "连续性门禁"
    else:
        required = ()
        profile_type = "unknown"
        label = "未知真相系统"

    missing = [name for name in required if not (truth_root / name).is_file()]
    return {
        "type": profile_type,
        "label": label,
        "root": TRUTH_SYSTEM_DIR.as_posix(),
        "required_files": list(required),
        "missing": missing,
    }


def build_required_file_report(root: Path, truth_profile: dict[str, object]) -> dict[str, object]:
    required: list[str] = list(ENTRY_REQUIRED_FILES)
    required.extend((Path("资料") / "写作记忆" / name).as_posix() for name in MEMORY_REQUIRED_FILES)

    truth_type = truth_profile.get("type")
    if truth_type == "finished":
        required.extend((TRUTH_SYSTEM_DIR / name).as_posix() for name in FINISHED_TRUTH_REQUIRED_FILES)
    elif truth_type == "continuous":
        required.extend((TRUTH_SYSTEM_DIR / name).as_posix() for name in TRUTH_REQUIRED_FILES)
    else:
        required.append(TRUTH_SYSTEM_DIR.as_posix())

    missing = [rel_path for rel_path in required if not (root / rel_path).is_file()]
    return {
        "checked": required,
        "missing": missing,
    }


def check_result(errors: list[str]) -> dict[str, object]:
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def build_doctor_recommendations(
    checks: dict[str, dict[str, object]],
    required_files: dict[str, object],
    truth_profile: dict[str, object],
) -> list[str]:
    recommendations: list[str] = []
    missing_files = [str(path) for path in required_files.get("missing", [])]

    if checks["chapter_format"]["status"] != "PASS":
        recommendations.append("先修复章节格式、章号连续性或占位残留，再进入写作/审稿。")
    if truth_profile.get("type") == "missing":
        recommendations.append("补建资料/真相系统，至少建立门禁、事实总账和事件时间线。")
    elif checks["truth_gate"]["status"] != "PASS":
        recommendations.append("先结算真相系统门禁，避免 AI 基于过期事实续写或审稿。")
    if any(path.startswith("资料/写作记忆/") for path in missing_files):
        recommendations.append("补齐资料/写作记忆的当前状态、人物、时间线、伏笔、设定和章节摘要。")
    if any(path in ENTRY_REQUIRED_FILES for path in missing_files):
        recommendations.append("补齐 README.md/AGENTS.md，明确项目入口、事实源和协作边界。")
    if not recommendations:
        recommendations.append("工具体检未发现阻断项，可以进入上下文打包、补账或审稿。")
    return recommendations


def build_doctor_report(
    project_root: str | Path,
    body_dir: str = DEFAULT_BODY_DIR,
    expected_count: int | None = None,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    chapters = collect_chapters(root, body_dir)
    truth_profile = detect_truth_profile(root / TRUTH_SYSTEM_DIR)
    chapter_errors = validate_project(root, body_dir, expected_count)
    truth_errors = validate_truth_system(root, body_dir)
    checks = {
        "chapter_format": check_result(chapter_errors),
        "truth_gate": check_result(truth_errors),
    }
    required_files = build_required_file_report(root, truth_profile)

    return {
        "project_root": str(root),
        "body_dir": body_dir,
        "chapter_count": len(chapters),
        "expected_count": expected_count,
        "chapter_numbers": chapter_number_summary(chapters),
        "truth_profile": truth_profile,
        "required_files": required_files,
        "checks": checks,
        "recommendations": build_doctor_recommendations(checks, required_files, truth_profile),
    }


def format_doctor_markdown(report: dict[str, object]) -> str:
    chapter_numbers = report["chapter_numbers"]
    truth_profile = report["truth_profile"]
    required_files = report["required_files"]
    checks = report["checks"]
    assert isinstance(chapter_numbers, dict)
    assert isinstance(truth_profile, dict)
    assert isinstance(required_files, dict)
    assert isinstance(checks, dict)

    lines = [
        "# 小说项目工具体检",
        "",
        f"- 项目根：`{report['project_root']}`",
        f"- 正文目录：`{report['body_dir']}`",
        f"- 章节数：{report['chapter_count']}",
        f"- 预期章节数：{report['expected_count'] if report['expected_count'] is not None else '未指定'}",
        (
            f"- 章号范围：{chapter_numbers['start']} - {chapter_numbers['end']}，"
            f"缺章 {len(chapter_numbers['missing'])}，重复 {len(chapter_numbers['duplicates'])}"
        ),
        f"- 真相系统：{truth_profile['label']}（{truth_profile['type']}）",
        "",
        "## 检查结果",
    ]

    for name, result in checks.items():
        assert isinstance(result, dict)
        lines.append(f"- {name}：{result['status']}")
        for error in result["errors"]:
            lines.append(f"  - {error}")

    lines.extend(["", "## 缺失文件"])
    missing = required_files["missing"]
    assert isinstance(missing, list)
    if missing:
        lines.extend(f"- {path}" for path in missing)
    else:
        lines.append("无。")

    lines.extend(["", "## 建议"])
    recommendations = report["recommendations"]
    assert isinstance(recommendations, list)
    lines.extend(f"- {item}" for item in recommendations)
    return "\n".join(lines).rstrip() + "\n"


def memory_template(name: str) -> str:
    title = MEMORY_TEMPLATE_TITLES[name]
    return f"# {title}\n\n待核：本文件由 scaffold 初始化，必须以正文为准逐项回填。\n"


def resolve_scaffold_profile(root: Path, profile: str) -> str:
    if profile in {"continuous", "finished"}:
        return profile
    truth_type = detect_truth_profile(root / TRUTH_SYSTEM_DIR).get("type")
    if truth_type == "finished":
        return "finished"
    return "continuous"


def scaffold_templates(profile: str, include_entry: bool) -> dict[str, str]:
    templates: dict[str, str] = {}
    if include_entry:
        templates.update(SCAFFOLD_ENTRY_TEMPLATES)

    for name in MEMORY_REQUIRED_FILES:
        templates[(Path("资料") / "写作记忆" / name).as_posix()] = memory_template(name)

    truth_templates = (
        FINISHED_TRUTH_TEMPLATES if profile == "finished" else CONTINUOUS_TRUTH_TEMPLATES
    )
    for name, content in truth_templates.items():
        templates[(TRUTH_SYSTEM_DIR / name).as_posix()] = content
    return templates


def scaffold_ai_layer(
    project_root: str | Path,
    profile: str = "auto",
    include_entry: bool = False,
    write: bool = False,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    resolved_profile = resolve_scaffold_profile(root, profile)
    templates = scaffold_templates(resolved_profile, include_entry)
    pending: list[str] = []
    existing: list[str] = []
    created: list[str] = []

    for rel_path, content in templates.items():
        path = root / rel_path
        if path.exists():
            existing.append(rel_path)
            continue
        pending.append(rel_path)
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created.append(rel_path)

    return {
        "project_root": str(root),
        "profile": resolved_profile,
        "write": write,
        "pending": pending,
        "existing": existing,
        "created": created,
    }


def format_scaffold_markdown(result: dict[str, object]) -> str:
    lines = [
        "# AI 协作层初始化",
        "",
        f"- 项目根：`{result['project_root']}`",
        f"- 模式：{result['profile']}",
        f"- 写入：{'是' if result['write'] else '否，dry-run'}",
        "",
        "## 待创建" if not result["write"] else "## 已创建",
    ]
    key = "created" if result["write"] else "pending"
    paths = result[key]
    assert isinstance(paths, list)
    if paths:
        lines.extend(f"- {path}" for path in paths)
    else:
        lines.append("无。")

    existing = result["existing"]
    assert isinstance(existing, list)
    lines.extend(["", "## 已存在且未覆盖"])
    if existing:
        lines.extend(f"- {path}" for path in existing)
    else:
        lines.append("无。")
    return "\n".join(lines).rstrip() + "\n"


def trim_text(text: str, max_chars: int) -> str:
    stripped = text.strip()
    if len(stripped) <= max_chars:
        return stripped
    return stripped[:max_chars].rstrip() + "\n...（已截断）"


def trim_text_from_end(text: str, max_chars: int) -> str:
    stripped = text.strip()
    if len(stripped) <= max_chars:
        return stripped
    return "（前文已截断）...\n" + stripped[-max_chars:].lstrip()


def chapter_body(chapter: Chapter) -> str:
    return "\n".join(chapter.text.splitlines()[1:]).strip()


def chapter_context(chapter: Chapter, max_chars: int) -> dict[str, object]:
    body = chapter_body(chapter)
    return {
        "number": chapter.number,
        "title": chapter.title,
        "volume": chapter.volume,
        "path": chapter.rel_path,
        "opening": trim_text(body, max_chars),
        "ending": trim_text_from_end(body, max_chars),
        "body_chars": chapter.body_chars,
    }


def collect_context_sources(root: Path, max_source_chars: int) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for rel_path in CONTEXT_SOURCE_FILES:
        path = root / rel_path
        if not path.is_file():
            continue
        sources.append(
            {
                "path": rel_path,
                "text": trim_text(path.read_text(encoding="utf-8"), max_source_chars),
            }
        )
    return sources


def relative_project_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def infer_chapter_number(text: str) -> int | None:
    title_number = parse_number(TITLE_LINE_RE, text.strip())
    if title_number is not None:
        return title_number
    return parse_number(CHAPTER_FILE_RE, text)


def record_chapter_number(record: dict[str, object]) -> int | None:
    value = record.get("chapter")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def source_label(path: Path, root: Path, body_root: Path) -> str:
    try:
        path.relative_to(body_root)
        return "正文"
    except ValueError:
        pass

    rel_parts = relative_project_path(path, root).split("/")
    if "写作记忆" in rel_parts:
        return "写作记忆"
    if "真相系统" in rel_parts:
        return "真相系统"
    if rel_parts and rel_parts[0] == "资料":
        return "资料"
    return "项目入口"


def make_snippet(text: str, keyword: str, max_chars: int = 120) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    index = normalized.lower().find(keyword.lower())
    if index < 0:
        return trim_text(normalized, max_chars)
    start = max(0, index - max_chars // 2)
    end = min(len(normalized), index + len(keyword) + max_chars // 2)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(normalized) else ""
    return prefix + normalized[start:end].strip() + suffix


def query_match(
    source: str,
    path: str,
    chapter: int | None,
    line: int | None,
    record: int | None,
    snippet: str,
) -> dict[str, object]:
    return {
        "source": source,
        "path": path,
        "chapter": chapter,
        "line": line,
        "record": record,
        "snippet": snippet,
    }


def iter_query_files(root: Path, body_root: Path) -> list[Path]:
    files: list[Path] = []
    for rel_path in ENTRY_REQUIRED_FILES:
        path = root / rel_path
        if path.is_file():
            files.append(path)

    data_root = root / "资料"
    if data_root.is_dir():
        for path in sorted(data_root.rglob("*")):
            if path.is_file() and not is_excluded(path):
                if path.suffix in QUERY_TEXT_SUFFIXES or path.suffix == ".jsonl":
                    files.append(path)

    body_files = {chapter.path for chapter in collect_chapters(root)}
    return [path for path in files if path not in body_files and not path.is_relative_to(body_root)]


def query_jsonl_file(
    path: Path,
    root: Path,
    keyword: str,
    chapter_filter: int | None,
) -> list[dict[str, object]]:
    records, errors = read_jsonl_records(path)
    if errors:
        raw_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        matches: list[dict[str, object]] = []
        for line_no, line in enumerate(raw_lines, start=1):
            if keyword not in line:
                continue
            chapter = infer_chapter_number(line)
            if chapter_filter is not None and chapter != chapter_filter:
                continue
            matches.append(
                query_match(
                    source_label(path, root, root / DEFAULT_BODY_DIR),
                    relative_project_path(path, root),
                    chapter,
                    line_no,
                    None,
                    make_snippet(line, keyword),
                )
            )
        return matches

    matches = []
    for index, record in enumerate(records, start=1):
        record_text = json.dumps(record, ensure_ascii=False, sort_keys=True)
        if keyword not in record_text:
            continue
        chapter = record_chapter_number(record) or infer_chapter_number(record_text)
        if chapter_filter is not None and chapter != chapter_filter:
            continue
        matches.append(
            query_match(
                source_label(path, root, root / DEFAULT_BODY_DIR),
                relative_project_path(path, root),
                chapter,
                None,
                index,
                make_snippet(record_text, keyword),
            )
        )
    return matches


def query_text_file(
    path: Path,
    root: Path,
    body_root: Path,
    keyword: str,
    chapter_filter: int | None,
) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")

    for line_no, line in enumerate(text.splitlines(), start=1):
        if keyword not in line:
            continue
        chapter = infer_chapter_number(line)
        if chapter_filter is not None and chapter != chapter_filter:
            continue
        matches.append(
            query_match(
                source_label(path, root, body_root),
                relative_project_path(path, root),
                chapter,
                line_no,
                None,
                make_snippet(line, keyword),
            )
        )
    return matches


def query_project(
    project_root: str | Path,
    keyword: str,
    chapter: int | None = None,
    body_dir: str = DEFAULT_BODY_DIR,
    max_results: int = 20,
) -> list[dict[str, object]]:
    root = Path(project_root).resolve()
    body_root = resolve_body_root(root, body_dir)
    matches: list[dict[str, object]] = []

    for item in collect_chapters(root, body_dir):
        if chapter is not None and item.number != chapter:
            continue
        for line_no, line in enumerate(item.text.splitlines(), start=1):
            if keyword not in line:
                continue
            matches.append(
                query_match(
                    "正文",
                    item.rel_path,
                    item.number,
                    line_no,
                    None,
                    make_snippet(line, keyword),
                )
            )
            if len(matches) >= max_results:
                return matches

    for path in iter_query_files(root, body_root):
        if path.suffix == ".jsonl":
            file_matches = query_jsonl_file(path, root, keyword, chapter)
        else:
            file_matches = query_text_file(path, root, body_root, keyword, chapter)
        matches.extend(file_matches)
        if len(matches) >= max_results:
            return matches[:max_results]
    return matches


def format_query_markdown(
    results: list[dict[str, object]],
    keyword: str,
    chapter: int | None = None,
) -> str:
    lines = [
        "# 小说项目查询",
        "",
        f"- 关键词：`{keyword}`",
        f"- 章号限定：{f'第{chapter}章' if chapter is not None else '无'}",
        f"- 命中数：{len(results)}",
        "",
        "## 命中",
    ]
    if not results:
        lines.append("未命中。")
    for result in results:
        position = []
        if result["chapter"] is not None:
            position.append(f"第{result['chapter']}章")
        if result["line"] is not None:
            position.append(f"第{result['line']}行")
        if result["record"] is not None:
            position.append(f"第{result['record']}条")
        where = "，".join(position) if position else "未标章节"
        lines.append(f"- [{result['source']}] `{result['path']}`（{where}）：{result['snippet']}")
    return "\n".join(lines).rstrip() + "\n"


def build_context_pack(
    project_root: str | Path,
    target_chapter: int,
    body_dir: str = DEFAULT_BODY_DIR,
    window: int = 1,
    max_source_chars: int = 2400,
    max_chapter_chars: int = 1200,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    chapters = collect_chapters(root, body_dir)
    target = next((chapter for chapter in chapters if chapter.number == target_chapter), None)
    if target is None:
        raise ValueError(f"未找到目标章节：第{target_chapter}章")

    start = target_chapter - window
    end = target_chapter + window
    chapter_window = [
        chapter_context(chapter, max_chapter_chars)
        for chapter in chapters
        if start <= chapter.number <= end
    ]

    return {
        "project_root": str(root),
        "body_dir": body_dir,
        "target": chapter_context(target, max_chapter_chars),
        "chapter_window": chapter_window,
        "sources": collect_context_sources(root, max_source_chars),
    }


def format_context_pack_markdown(pack: dict[str, object]) -> str:
    target = pack["target"]
    assert isinstance(target, dict)
    lines = [
        "# AI 上下文包",
        "",
        f"- 项目根：`{pack['project_root']}`",
        f"- 正文目录：`{pack['body_dir']}`",
        f"- 目标章节：第{target['number']}章 {target['title']}",
        "- 使用口径：正文是唯一事实源；资料摘录只作导航和核账辅助。",
        "",
        "## 章节窗口",
    ]

    for chapter in pack["chapter_window"]:
        assert isinstance(chapter, dict)
        lines.extend(
            [
                "",
                f"### 第{chapter['number']}章 {chapter['title']}",
                f"- 文件：`{chapter['path']}`",
                f"- 卷：{chapter['volume']}",
                f"- 正文非空白字符：{chapter['body_chars']}",
                "",
                "#### 开头摘录",
                "```text",
                str(chapter["opening"]),
                "```",
                "",
                "#### 结尾摘录",
                "```text",
                str(chapter["ending"]),
                "```",
            ]
        )

    lines.extend(["", "## 资料摘录"])
    sources = pack["sources"]
    assert isinstance(sources, list)
    if not sources:
        lines.append("未找到可摘录的项目资料。")
    for source in sources:
        assert isinstance(source, dict)
        lines.extend(
            [
                "",
                f"### {source['path']}",
                "```markdown",
                str(source["text"]),
                "```",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def iter_included_files(project_root: Path, rel_path: str) -> list[tuple[Path, str]]:
    source = (project_root / rel_path).resolve()
    if not source.exists():
        raise FileNotFoundError(f"打包路径不存在：{rel_path}")
    if source.is_file():
        return [] if is_excluded(source) else [(source, source.relative_to(project_root).as_posix())]

    files: list[tuple[Path, str]] = []
    for path in sorted(source.rglob("*")):
        if path.is_file() and not is_excluded(path):
            files.append((path, path.relative_to(project_root).as_posix()))
    return files


def parse_include_as(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--include-as 格式应为 源路径=压缩包内路径")
    source, arcname = value.split("=", 1)
    source = source.strip()
    arcname = arcname.strip()
    if not source or not arcname:
        raise argparse.ArgumentTypeError("--include-as 的源路径和压缩包内路径不能为空")
    return source, arcname


def create_zip(
    project_root: str | Path,
    zip_path: str | Path,
    includes: list[str],
    include_as: list[tuple[str, str]] | None = None,
) -> list[str]:
    root = Path(project_root).resolve()
    out_path = Path(zip_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    entries: list[tuple[Path, str]] = []
    for rel_path in includes:
        entries.extend(iter_included_files(root, rel_path))

    for source_text, arcname in include_as or []:
        source = (root / source_text).resolve()
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"打包映射源文件不存在：{source_text}")
        if not is_excluded(source):
            entries.append((source, arcname))

    seen: set[str] = set()
    written: list[str] = []
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source, arcname in sorted(entries, key=lambda item: item[1]):
            if source == out_path or arcname in seen:
                continue
            archive.write(source, arcname)
            seen.add(arcname)
            written.append(arcname)
    return written


def print_stats(chapters: list[Chapter], details: bool = False) -> None:
    summaries = summarize_by_volume(chapters)
    print("字数口径：正文非空白字符不含首行章题；全文非空白字符含首行章题。")
    print("范围\t章节数\t正文非空白字符\t全文非空白字符")
    for summary in summaries:
        print(
            f"{summary.volume}\t{summary.chapter_count}\t"
            f"{summary.body_chars:,}\t{summary.total_chars:,}"
        )
    print(
        f"合计\t{len(chapters)}\t"
        f"{sum(chapter.body_chars for chapter in chapters):,}\t"
        f"{sum(chapter.total_chars for chapter in chapters):,}"
    )

    if details:
        print()
        print("章节\t正文非空白字符\t全文非空白字符")
        for chapter in chapters:
            print(f"{chapter.rel_path}\t{chapter.body_chars:,}\t{chapter.total_chars:,}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="中文长篇小说项目通用工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stats_parser = subparsers.add_parser("stats", help="统计正文非空白字符")
    stats_parser.add_argument("project_root", type=Path, help="小说项目根目录")
    stats_parser.add_argument("--body-dir", default=DEFAULT_BODY_DIR, help="正文目录名，默认“正文”")
    stats_parser.add_argument("--details", action="store_true", help="输出逐章明细")
    stats_parser.add_argument("--json", action="store_true", help="输出 JSON")

    check_parser = subparsers.add_parser("check", help="校验章节格式、章号连续性和占位残留")
    check_parser.add_argument("project_root", type=Path, help="小说项目根目录")
    check_parser.add_argument("--body-dir", default=DEFAULT_BODY_DIR, help="正文目录名，默认“正文”")
    check_parser.add_argument("--expected-count", type=int, help="预期章节数")

    doctor_parser = subparsers.add_parser("doctor", help="只读体检老项目的 AI 协作资料缺口")
    doctor_parser.add_argument("project_root", type=Path, help="小说项目根目录")
    doctor_parser.add_argument("--body-dir", default=DEFAULT_BODY_DIR, help="正文目录名，默认“正文”")
    doctor_parser.add_argument("--expected-count", type=int, help="预期章节数")
    doctor_parser.add_argument("--json", action="store_true", help="输出 JSON")

    scaffold_parser = subparsers.add_parser("scaffold", help="安全初始化 AI 协作层模板")
    scaffold_parser.add_argument("project_root", type=Path, help="小说项目根目录")
    scaffold_parser.add_argument(
        "--profile",
        choices=("auto", "continuous", "finished"),
        default="auto",
        help="真相系统模板类型，默认自动识别；无法识别时按连载项目",
    )
    scaffold_parser.add_argument(
        "--include-entry",
        action="store_true",
        help="同时创建缺失的 README.md 和 AGENTS.md",
    )
    scaffold_parser.add_argument(
        "--write",
        action="store_true",
        help="实际写入缺失模板；不加则只 dry-run",
    )
    scaffold_parser.add_argument("--json", action="store_true", help="输出 JSON")

    truth_parser = subparsers.add_parser("truth-gate", help="校验长篇真相系统门禁")
    truth_parser.add_argument("project_root", type=Path, help="小说项目根目录")
    truth_parser.add_argument("--body-dir", default=DEFAULT_BODY_DIR, help="正文目录名，默认“正文”")

    query_parser = subparsers.add_parser("query", help="按关键词查询正文、写作记忆和真相系统")
    query_parser.add_argument("project_root", type=Path, help="小说项目根目录")
    query_parser.add_argument("keyword", help="查询关键词")
    query_parser.add_argument("--chapter", type=int, help="限定章号")
    query_parser.add_argument("--body-dir", default=DEFAULT_BODY_DIR, help="正文目录名，默认“正文”")
    query_parser.add_argument("--max-results", type=int, default=20, help="最多输出命中数，默认 20")
    query_parser.add_argument("--json", action="store_true", help="输出 JSON")

    context_parser = subparsers.add_parser("context-pack", help="生成 AI 写作/审稿上下文包")
    context_parser.add_argument("project_root", type=Path, help="小说项目根目录")
    context_parser.add_argument("--target-chapter", type=int, required=True, help="目标章号")
    context_parser.add_argument("--body-dir", default=DEFAULT_BODY_DIR, help="正文目录名，默认“正文”")
    context_parser.add_argument("--window", type=int, default=1, help="目标章前后章节窗口，默认 1")
    context_parser.add_argument(
        "--max-source-chars",
        type=int,
        default=2400,
        help="每个资料文件最多摘录字符数，默认 2400",
    )
    context_parser.add_argument(
        "--max-chapter-chars",
        type=int,
        default=1200,
        help="每章开头/结尾最多摘录字符数，默认 1200",
    )
    context_parser.add_argument("--json", action="store_true", help="输出 JSON")

    zip_parser = subparsers.add_parser("zip", help="生成排除缓存的通用 zip 包")
    zip_parser.add_argument("project_root", type=Path, help="小说项目根目录")
    zip_parser.add_argument("zip_path", type=Path, help="输出 zip 路径")
    zip_parser.add_argument("--include", action="append", required=True, help="加入压缩包的项目相对路径")
    zip_parser.add_argument(
        "--include-as",
        action="append",
        default=[],
        type=parse_include_as,
        help="把单个文件按指定包内路径加入，格式：源路径=包内路径",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "stats":
            chapters = collect_chapters(args.project_root, args.body_dir)
            if args.json:
                print(
                    json.dumps(
                        [chapter._asdict() | {"path": str(chapter.path)} for chapter in chapters],
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                print_stats(chapters, args.details)
            return 0

        if args.command == "check":
            errors = validate_project(args.project_root, args.body_dir, args.expected_count)
            if errors:
                print("检查未通过：")
                for error in errors:
                    print(f"- {error}")
                return 1
            print("检查通过。")
            return 0

        if args.command == "doctor":
            report = build_doctor_report(
                args.project_root,
                body_dir=args.body_dir,
                expected_count=args.expected_count,
            )
            if args.json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                print(format_doctor_markdown(report), end="")
            checks = report["checks"]
            assert isinstance(checks, dict)
            return 0 if all(result["status"] == "PASS" for result in checks.values()) else 1

        if args.command == "scaffold":
            result = scaffold_ai_layer(
                args.project_root,
                profile=args.profile,
                include_entry=args.include_entry,
                write=args.write,
            )
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(format_scaffold_markdown(result), end="")
            return 0

        if args.command == "truth-gate":
            errors = validate_truth_system(args.project_root, args.body_dir)
            if errors:
                print("真相系统门禁未通过：")
                for error in errors:
                    print(f"- {error}")
                return 1
            print("真相系统门禁通过。")
            return 0

        if args.command == "query":
            results = query_project(
                args.project_root,
                args.keyword,
                chapter=args.chapter,
                body_dir=args.body_dir,
                max_results=args.max_results,
            )
            if args.json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                print(format_query_markdown(results, args.keyword, args.chapter), end="")
            return 0

        if args.command == "context-pack":
            pack = build_context_pack(
                args.project_root,
                target_chapter=args.target_chapter,
                body_dir=args.body_dir,
                window=args.window,
                max_source_chars=args.max_source_chars,
                max_chapter_chars=args.max_chapter_chars,
            )
            if args.json:
                print(json.dumps(pack, ensure_ascii=False, indent=2))
            else:
                print(format_context_pack_markdown(pack), end="")
            return 0

        if args.command == "zip":
            entries = create_zip(args.project_root, args.zip_path, args.include, args.include_as)
            print(f"已生成：{args.zip_path}")
            print(f"文件数：{len(entries)}")
            return 0
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
