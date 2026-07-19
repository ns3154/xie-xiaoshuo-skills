#!/usr/bin/env python3
"""校验改稿、审稿与去 AI 味流程不会机械削弱有效情绪。"""

from __future__ import annotations

import unittest
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]


class EmotionPreservationGateTest(unittest.TestCase):
    def read_skill(self, name: str) -> str:
        return (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")

    def test_write_has_emotion_preservation_gate(self) -> None:
        content = self.read_skill("xie-write")

        for rule in (
            "情绪保护门",
            "前后两三句",
            "修改前后情绪强度",
            "可改可不改",
            "不同对象、不同动作",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, content)

    def test_review_separates_hard_problems_from_emotional_choices(self) -> None:
        content = self.read_skill("xie-review")

        for rule in (
            "情绪保护门",
            "事实错误、逻辑矛盾或明显阅读障碍",
            "情绪载体",
            "可保留选择",
            "不同对象、不同动作",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, content)

    def test_deslop_judges_function_instead_of_surface_words(self) -> None:
        content = self.read_skill("xie-deslop")

        for rule in (
            "情绪保护门",
            "不按词面",
            "铺垫—兑现",
            "情绪烈度",
            "不同对象、不同动作",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, content)


if __name__ == "__main__":
    unittest.main()
