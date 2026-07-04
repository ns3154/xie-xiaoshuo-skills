#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"

python3 - "$SKILLS_DIR" <<'PY'
import re
import sys
from pathlib import Path

skills_dir = Path(sys.argv[1])
expected = [
    "xie-xiaoshuo",
    "xie-write",
    "xie-review",
    "xie-deslop",
    "xie-learn",
    "xie-import",
    "xie-cover",
]

errors = []
for name in expected:
    root = skills_dir / name
    skill_md = root / "SKILL.md"
    openai_yaml = root / "agents" / "openai.yaml"

    if not skill_md.exists():
        errors.append(f"{name}: 缺少 SKILL.md")
        continue
    if not openai_yaml.exists():
        errors.append(f"{name}: 缺少 agents/openai.yaml")

    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", content, re.S)
    if not match:
        errors.append(f"{name}: SKILL.md 缺少 YAML frontmatter")
        continue

    frontmatter = match.group(1)
    if not re.search(rf"^name:\s*['\"]?{re.escape(name)}['\"]?\s*$", frontmatter, re.M):
        errors.append(f"{name}: frontmatter name 不匹配")
    if not re.search(r"^description:\s*.+", frontmatter, re.M):
        errors.append(f"{name}: frontmatter 缺少 description")

if errors:
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)

print(f"结构校验通过：{len(expected)} 个 skill")
PY

python3 -m unittest discover -s "$SKILLS_DIR/xie-xiaoshuo/scripts" -p 'test_*.py'

