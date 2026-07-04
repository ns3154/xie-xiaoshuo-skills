#!/usr/bin/env python3
"""通用小说工具脚本的最小回归测试。"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("novel_tools.py")
SPEC = importlib.util.spec_from_file_location("novel_tools", SCRIPT_PATH)
novel_tools = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(novel_tools)


class NovelToolsTest(unittest.TestCase):
    def make_project(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="novel-tools-test-"))
        volume = root / "正文" / "第一卷-测试"
        volume.mkdir(parents=True)
        (volume / "第001章-开端.txt").write_text(
            "第1章 开端\n雪落。\n照霜未死。\n",
            encoding="utf-8",
        )
        (volume / "第002章-税银.txt").write_text(
            "第2章 税银\n税银入院。\n旧册开封。\n",
            encoding="utf-8",
        )
        intro_dir = root / "审稿" / "引读"
        intro_dir.mkdir(parents=True)
        (intro_dir / "专业AI审稿引读.md").write_text("# 引读\n", encoding="utf-8")
        return root

    def make_truth_system(self, root: Path, pending: str = "当前待同步：无") -> None:
        truth_root = root / "资料" / "真相系统"
        truth_root.mkdir(parents=True)
        required_text = {
            "00-使用说明.md": "# 使用说明\n",
            "01-连续性门禁.md": "当前门禁：PASS\n",
            "02-待同步章节.md": f"{pending}\n",
            "05-人物状态快照.md": "# 人物状态快照\n",
            "06-物件持有表.md": "# 物件持有表\n",
            "07-伏笔承诺回收表.md": "# 伏笔承诺回收表\n",
            "08-下一章上下文包.md": "# 下一章上下文包\n",
            "09-章节结算模板.md": "# 章节结算模板\n",
            "10-因果链复盘.md": "# 因果链复盘\n",
        }
        for name, content in required_text.items():
            (truth_root / name).write_text(content, encoding="utf-8")
        records = [
            '{"chapter": 1, "title": "开端"}\n',
            '{"chapter": 2, "title": "税银"}\n',
        ]
        (truth_root / "03-事实总账.jsonl").write_text("".join(records), encoding="utf-8")
        (truth_root / "04-事件时间线.jsonl").write_text("".join(records), encoding="utf-8")

    def make_finished_truth_system(self, root: Path, body_gate: str = "PASS") -> None:
        truth_root = root / "资料" / "真相系统"
        truth_root.mkdir(parents=True)
        required_text = {
            "00-使用说明.md": "# 使用说明\n",
            "01-完本门禁.md": (
                "# 完本门禁\n\n"
                "| 层级 | 结论 | 说明 |\n"
                "|---|---|---|\n"
                f"| 正文门禁 | {body_gate} | 正文层面可交付。 |\n"
                "| 台账门禁 | 待关闭 | 台账仍有复读索引，不代表正文失败。 |\n"
            ),
            "02-待核账章节.md": "当前正文门禁：PASS\n当前台账门禁：待关闭\n",
            "05-人物终局状态.md": "# 人物终局状态\n",
            "06-物件身份归属表.md": "# 物件身份归属表\n",
            "07-伏笔承诺回收表.md": "# 伏笔承诺回收表\n",
            "08-全书问题池.md": "# 全书问题池\n",
            "09-完本自检清单.md": "# 完本自检清单\n",
            "10-修订建议.md": "# 修订建议\n",
        }
        for name, content in required_text.items():
            (truth_root / name).write_text(content, encoding="utf-8")
        records = [
            '{"chapter": 1, "title": "开端"}\n',
            '{"chapter": 2, "title": "税银"}\n',
        ]
        (truth_root / "03-事实总账.jsonl").write_text("".join(records), encoding="utf-8")
        (truth_root / "04-事件时间线.jsonl").write_text("".join(records), encoding="utf-8")

    def test_collect_stats_excludes_title_from_body_count(self) -> None:
        root = self.make_project()

        chapters = novel_tools.collect_chapters(root)

        self.assertEqual([1, 2], [chapter.number for chapter in chapters])
        expected_body = novel_tools.count_non_whitespace("雪落。\n照霜未死。")
        self.assertEqual(expected_body, chapters[0].body_chars)
        self.assertGreater(chapters[0].total_chars, chapters[0].body_chars)

    def test_validate_project_requires_title_alignment(self) -> None:
        root = self.make_project()
        bad_file = root / "正文" / "第一卷-测试" / "第003章-错位.txt"
        bad_file.write_text("第4章 错位\n章题错位。\n", encoding="utf-8")

        errors = novel_tools.validate_project(root, expected_count=3)

        self.assertTrue(
            any("文件名章号与标题章号不一致" in error for error in errors),
            errors,
        )

    def test_validate_placeholder_detection_avoids_story_usage(self) -> None:
        root = self.make_project()
        story_file = root / "正文" / "第一卷-测试" / "第003章-账目.txt"
        story_file.write_text("第3章 账目\n仓验一升，待补一升。\n", encoding="utf-8")

        self.assertEqual([], novel_tools.validate_project(root, expected_count=3))

        story_file.write_text("第3章 账目\n待补：这里以后补一段现场。\n", encoding="utf-8")
        errors = novel_tools.validate_project(root, expected_count=3)

        self.assertTrue(any("占位" in error for error in errors), errors)

    def test_create_zip_excludes_cache_and_allows_include_as(self) -> None:
        root = self.make_project()
        (root / "正文" / ".DS_Store").write_text("cache", encoding="utf-8")
        cache_dir = root / "正文" / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "bad.pyc").write_bytes(b"cache")
        out_path = root / "交付包" / "审稿包.zip"

        entries = novel_tools.create_zip(
            root,
            out_path,
            includes=["正文"],
            include_as=[("审稿/引读/专业AI审稿引读.md", "专业AI审稿引读.md")],
        )

        self.assertIn("专业AI审稿引读.md", entries)
        self.assertIn("正文/第一卷-测试/第001章-开端.txt", entries)
        self.assertFalse(any(entry.endswith(".DS_Store") for entry in entries))
        self.assertFalse(any("__pycache__" in entry or entry.endswith(".pyc") for entry in entries))
        with zipfile.ZipFile(out_path) as archive:
            self.assertEqual(sorted(entries), sorted(archive.namelist()))

    def test_truth_gate_passes_when_truth_system_is_current(self) -> None:
        root = self.make_project()
        self.make_truth_system(root)

        self.assertEqual([], novel_tools.validate_truth_system(root))

    def test_truth_gate_fails_when_pending_not_cleared(self) -> None:
        root = self.make_project()
        self.make_truth_system(root, pending="当前待同步：第3章")

        errors = novel_tools.validate_truth_system(root)

        self.assertTrue(any("待同步章节未清零" in error for error in errors), errors)

    def test_truth_gate_fails_when_jsonl_missing_existing_chapter(self) -> None:
        root = self.make_project()
        self.make_truth_system(root)
        truth_root = root / "资料" / "真相系统"
        (truth_root / "03-事实总账.jsonl").write_text(
            '{"chapter": 1, "title": "开端"}\n',
            encoding="utf-8",
        )

        errors = novel_tools.validate_truth_system(root)

        self.assertTrue(any("03-事实总账.jsonl 缺少" in error for error in errors), errors)

    def test_truth_gate_passes_finished_truth_system_with_open_ledger(self) -> None:
        root = self.make_project()
        self.make_finished_truth_system(root)

        self.assertEqual([], novel_tools.validate_truth_system(root))

    def test_truth_gate_fails_finished_truth_system_when_body_gate_fails(self) -> None:
        root = self.make_project()
        self.make_finished_truth_system(root, body_gate="FAIL")

        errors = novel_tools.validate_truth_system(root)

        self.assertTrue(any("正文门禁当前状态不是 PASS" in error for error in errors), errors)

    def test_context_pack_builds_ai_readable_window_and_memory_sources(self) -> None:
        root = self.make_project()
        (root / "正文" / "第一卷-测试" / "第003章-追问.txt").write_text(
            "第3章 追问\n岑砚追问旧册。\n灯下留下新钩子。\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("当前正文边界：三章测试。\n", encoding="utf-8")
        memory_root = root / "资料" / "写作记忆"
        memory_root.mkdir(parents=True)
        (memory_root / "00-当前写作状态.md").write_text(
            "当前落点：第3章，必须承接税银入院。\n",
            encoding="utf-8",
        )
        (memory_root / "07-章节摘要.md").write_text(
            "第1章：照霜未死。\n第2章：税银入院，旧册开封。\n",
            encoding="utf-8",
        )

        pack = novel_tools.build_context_pack(root, target_chapter=3, window=1, max_source_chars=80)

        self.assertEqual(3, pack["target"]["number"])
        self.assertEqual([2, 3], [chapter["number"] for chapter in pack["chapter_window"]])
        self.assertIn("旧册开封", pack["chapter_window"][0]["ending"])
        self.assertTrue(
            any(
                source["path"] == "资料/写作记忆/00-当前写作状态.md"
                and "第3章" in source["text"]
                for source in pack["sources"]
            ),
            pack["sources"],
        )

    def test_doctor_report_surfaces_project_gaps_for_ai_use(self) -> None:
        root = self.make_project()
        self.make_finished_truth_system(root)
        (root / "README.md").write_text("# 测试项目\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("# 协作规则\n", encoding="utf-8")

        report = novel_tools.build_doctor_report(root, expected_count=2)

        self.assertEqual(2, report["chapter_count"])
        self.assertEqual(
            {"start": 1, "end": 2, "missing": [], "duplicates": []},
            report["chapter_numbers"],
        )
        self.assertEqual("PASS", report["checks"]["chapter_format"]["status"])
        self.assertEqual("PASS", report["checks"]["truth_gate"]["status"])
        self.assertEqual("finished", report["truth_profile"]["type"])
        self.assertIn(
            "资料/写作记忆/00-当前写作状态.md",
            report["required_files"]["missing"],
        )
        self.assertTrue(
            any("写作记忆" in recommendation for recommendation in report["recommendations"]),
            report["recommendations"],
        )

    def test_query_project_finds_keyword_across_body_memory_and_truth_system(self) -> None:
        root = self.make_project()
        self.make_truth_system(root)
        (root / "正文" / "第一卷-测试" / "第002章-税银.txt").write_text(
            "第2章 税银\n税银入院。\n暂籍归岑砚保管。\n",
            encoding="utf-8",
        )
        memory_root = root / "资料" / "写作记忆"
        memory_root.mkdir(parents=True)
        (memory_root / "04-伏笔台账.md").write_text(
            "第2章：暂籍伏笔推进，不能提前揭底。\n",
            encoding="utf-8",
        )
        truth_root = root / "资料" / "真相系统"
        (truth_root / "03-事实总账.jsonl").write_text(
            '{"chapter": 1, "title": "开端"}\n'
            '{"chapter": 2, "title": "税银", "fact": "暂籍入院"}\n',
            encoding="utf-8",
        )

        results = novel_tools.query_project(root, "暂籍", chapter=2, max_results=10)

        paths = {result["path"] for result in results}
        self.assertIn("正文/第一卷-测试/第002章-税银.txt", paths)
        self.assertIn("资料/写作记忆/04-伏笔台账.md", paths)
        self.assertIn("资料/真相系统/03-事实总账.jsonl", paths)
        self.assertTrue(all(result["chapter"] == 2 for result in results), results)
        self.assertTrue(all("暂籍" in result["snippet"] for result in results), results)

    def test_scaffold_ai_layer_dry_run_then_writes_missing_templates_only(self) -> None:
        root = self.make_project()
        readme = root / "README.md"
        readme.write_text("已有入口，不可覆盖。\n", encoding="utf-8")

        dry_run = novel_tools.scaffold_ai_layer(
            root,
            profile="continuous",
            include_entry=True,
            write=False,
        )

        self.assertFalse((root / "资料" / "写作记忆" / "00-当前写作状态.md").exists())
        self.assertIn("资料/写作记忆/00-当前写作状态.md", dry_run["pending"])
        self.assertIn("README.md", dry_run["existing"])

        written = novel_tools.scaffold_ai_layer(
            root,
            profile="continuous",
            include_entry=True,
            write=True,
        )

        self.assertEqual("已有入口，不可覆盖。\n", readme.read_text(encoding="utf-8"))
        self.assertIn("资料/写作记忆/00-当前写作状态.md", written["created"])
        self.assertIn("资料/真相系统/01-连续性门禁.md", written["created"])
        status_text = (root / "资料" / "写作记忆" / "00-当前写作状态.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("待核", status_text)
        agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
        readme_template = novel_tools.SCAFFOLD_ENTRY_TEMPLATES["README.md"]
        next_context = (root / "资料" / "真相系统" / "08-下一章上下文包.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("写作前读取策略", agents_text)
        self.assertIn("固定入口", agents_text)
        self.assertIn("按章按需", agents_text)
        self.assertIn("不要把几十万字正文或整套资料一次性塞入上下文", agents_text)
        self.assertIn("开写前读取策略", readme_template)
        self.assertIn("未写的下一章以 `资料/真相系统/08-下一章上下文包.md` 为准", readme_template)
        self.assertIn("控制在 800-1500 字", next_context)
        self.assertNotIn("至少读取", agents_text)


if __name__ == "__main__":
    unittest.main()
