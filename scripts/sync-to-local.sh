#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT/skills"
TARGET_DIR="${1:-$HOME/.agents/skills}"
BACKUP_ROOT="$(dirname "$TARGET_DIR")/$(basename "$TARGET_DIR")-backup"
BACKUP_DIR=""

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

for skill in "${SKILLS[@]}"; do
  if [[ ! -f "$SOURCE_DIR/$skill/SKILL.md" ]]; then
    echo "缺少 skill：$skill" >&2
    exit 1
  fi
done

mkdir -p "$TARGET_DIR"

for skill in "${SKILLS[@]}"; do
  source="$SOURCE_DIR/$skill"
  target="$TARGET_DIR/$skill"

  if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
    continue
  fi

  if [[ -e "$target" || -L "$target" ]]; then
    if [[ -z "$BACKUP_DIR" ]]; then
      BACKUP_DIR="$BACKUP_ROOT/xie-symlink-migration-$(date +%Y%m%d-%H%M%S)-$$"
      mkdir -p "$BACKUP_DIR"
    fi
    mv "$target" "$BACKUP_DIR/$skill"
  fi

  ln -s "$source" "$target"
done

echo "已链接 ${#SKILLS[@]} 个 skill 到：$TARGET_DIR"
if [[ -n "$BACKUP_DIR" ]]; then
  echo "旧副本已备份到：$BACKUP_DIR"
fi
