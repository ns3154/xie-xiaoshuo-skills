#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT/skills"
TARGET_DIR="${1:-$HOME/.agents/skills}"

SKILLS=(
  xie-xiaoshuo
  xie-write
  xie-review
  xie-deslop
  xie-learn
  xie-import
  xie-cover
)

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "找不到 skills 目录：$SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

for skill in "${SKILLS[@]}"; do
  if [[ ! -f "$SOURCE_DIR/$skill/SKILL.md" ]]; then
    echo "缺少 skill：$skill" >&2
    exit 1
  fi

  rsync -a --delete \
    --exclude '.DS_Store' \
    --exclude '__pycache__' \
    "$SOURCE_DIR/$skill/" "$TARGET_DIR/$skill/"
done

echo "已同步 ${#SKILLS[@]} 个 skill 到：$TARGET_DIR"

