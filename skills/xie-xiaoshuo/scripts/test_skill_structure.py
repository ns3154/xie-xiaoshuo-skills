#!/usr/bin/env python3
"""校验写小说 skill 拆分后的结构。"""

from __future__ import annotations

import unittest
from pathlib import Path


ROUTER_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROUTER_ROOT.parent
ROUTER_MD = ROUTER_ROOT / "SKILL.md"


class XieSplitStructureTest(unittest.TestCase):
    def test_router_is_light_and_agents_only(self) -> None:
        content = ROUTER_MD.read_text(encoding="utf-8")
        lines = content.splitlines()

        self.assertLessEqual(len(lines), 120)
        self.assertIn("~/.agents/skills/", content)
        self.assertIn("不要再同步或维护 `~/.codex/skills/xie-xiaoshuo`", content)
        self.assertIn("路由表", content)

    def test_expected_subskills_exist(self) -> None:
        expected = {
            "xie-write": "写正文",
            "xie-review": "审稿",
            "xie-deslop": "去 AI 味",
            "xie-learn": "扫榜",
            "xie-import": "导入",
            "xie-cover": "封面",
        }

        router = ROUTER_MD.read_text(encoding="utf-8")
        for skill_name, trigger in expected.items():
            with self.subTest(skill_name=skill_name):
                skill_md = SKILLS_ROOT / skill_name / "SKILL.md"
                openai_yaml = SKILLS_ROOT / skill_name / "agents" / "openai.yaml"
                self.assertTrue(skill_md.exists(), skill_name)
                self.assertTrue(openai_yaml.exists(), skill_name)
                self.assertIn(skill_name, router)
                self.assertIn(trigger, skill_md.read_text(encoding="utf-8"))

    def test_shared_tools_remain_available(self) -> None:
        tool = ROUTER_ROOT / "scripts" / "novel_tools.py"
        self.assertTrue(tool.exists())
        content = ROUTER_MD.read_text(encoding="utf-8")
        self.assertIn("novel_tools.py", content)
        self.assertIn("context-pack", content)
        self.assertIn("doctor", content)
        self.assertIn("query", content)
        self.assertIn("scaffold", content)

    def test_review_and_cover_references_are_copied(self) -> None:
        review_ref = SKILLS_ROOT / "xie-review" / "references" / "review-and-packaging.md"
        cover_ref = SKILLS_ROOT / "xie-cover" / "references" / "cover-generation.md"
        write_ref = SKILLS_ROOT / "xie-write" / "references" / "input-governance.md"

        for path in (review_ref, cover_ref, write_ref):
            self.assertTrue(path.exists(), str(path))
            self.assertIn("## 目录", path.read_text(encoding="utf-8"))

    def test_xie_write_uses_layered_context_governance(self) -> None:
        content = (SKILLS_ROOT / "xie-write" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("写前读取策略", content)
        self.assertIn("固定入口", content)
        self.assertIn("按章按需", content)
        self.assertIn("不要把整套资料或全部正文一次性塞进上下文", content)
        self.assertNotIn("长篇写作和正文修订至少读取", content)

    def test_xie_write_locks_genre_engine_contract(self) -> None:
        content = (SKILLS_ROOT / "xie-write" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("题材主引擎", content)
        self.assertIn("推进章或回报章", content)
        self.assertIn("非悬疑题材", content)
        self.assertIn("悬疑是主引擎或共同主引擎", content)
        self.assertIn("获得新信息", content)
        self.assertIn("无脸新谜面", content)
        self.assertIn("已完成的主类型推进或回报", content)
        self.assertIn("未兑现的悬念债务", content)

    def test_xie_write_requires_chinese_fullwidth_quotes(self) -> None:
        content = (SKILLS_ROOT / "xie-write" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("外层使用 `“”`，嵌套引语使用 `‘’`", content)
        self.assertIn("英文半角引号", content)

    def test_xie_write_templates_separate_payoff_from_suspense(self) -> None:
        templates = (SKILLS_ROOT / "xie-write" / "references" / "templates.md").read_text(
            encoding="utf-8"
        )
        governance = (
            SKILLS_ROOT / "xie-write" / "references" / "input-governance.md"
        ).read_text(encoding="utf-8")

        for field in (
            "题材主引擎",
            "本章阶段：推进 / 回报",
            "本章主类型推进或回报",
            "悬念职责",
            "是否新增谜面及回收期限",
            "结尾钩子类型",
        ):
            self.assertIn(field, templates)
        self.assertNotIn("本章爽点或悬念：", templates)
        self.assertIn("本章必须完成的主类型推进或回报", governance)
        self.assertIn("可暂缓的伏笔债务", governance)
        self.assertIn("不能仅因仍是 `open`", governance)


if __name__ == "__main__":
    unittest.main()
