#!/usr/bin/env python3
"""校验 xie-deslop 的分层诊断与误判边界。"""

from __future__ import annotations

import unittest
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]
DESLOP_MD = SKILLS_ROOT / "xie-deslop" / "SKILL.md"
DESLOP_OPENAI_YAML = SKILLS_ROOT / "xie-deslop" / "agents" / "openai.yaml"


class XieDeslopSkillTest(unittest.TestCase):
    def test_uses_six_diagnostic_gates(self) -> None:
        content = DESLOP_MD.read_text(encoding="utf-8")

        for gate in (
            "场面连续性",
            "人物行为比例",
            "专业拟真",
            "动作模板",
            "模型退化",
            "解释与声口",
        ):
            with self.subTest(gate=gate):
                self.assertIn(gate, content)

    def test_preserves_existing_style_checks(self) -> None:
        content = DESLOP_MD.read_text(encoding="utf-8")

        for symptom in (
            "模板转折",
            "抽象总结",
            "同长段落",
            "列表句式",
            "情绪空泛",
            "人物同声",
            "章末升华",
        ):
            with self.subTest(symptom=symptom):
                self.assertIn(symptom, content)

    def test_blocks_context_free_overdiagnosis(self) -> None:
        content = DESLOP_MD.read_text(encoding="utf-8")

        self.assertIn("不能据此反推作者身份", content)
        self.assertIn("省略过渡或表达含混", content)
        self.assertIn("单次出现不判 AI 味", content)
        self.assertIn("不猜测具体生成机制", content)

    def test_batch_review_tracks_scene_state(self) -> None:
        content = DESLOP_MD.read_text(encoding="utf-8")

        for state in ("姿态", "双手占用", "物件位置", "知情范围", "时间顺序"):
            with self.subTest(state=state):
                self.assertIn(state, content)

    def test_interface_mentions_continuity_review(self) -> None:
        content = DESLOP_OPENAI_YAML.read_text(encoding="utf-8")

        self.assertIn("连续性", content)
        self.assertIn("模型退化", content)


if __name__ == "__main__":
    unittest.main()
