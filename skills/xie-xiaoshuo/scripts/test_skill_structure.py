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


if __name__ == "__main__":
    unittest.main()
