#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYNC_SCRIPT="$ROOT/scripts/sync-to-local.sh"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/xie-skill-sync-test.XXXXXX")"
TARGET_DIR="$TEST_ROOT/skills"

SKILLS=(
  xie-xiaoshuo
  xie-write
  xie-review
  xie-deslop
  xie-learn
  xie-import
  xie-cover
)

cleanup() {
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

fail() {
  echo "软连接同步测试失败：$*" >&2
  exit 1
}

mkdir -p "$TARGET_DIR/xie-write"
echo "需要保留的本地内容" > "$TARGET_DIR/xie-write/独有文件.txt"

"$SYNC_SCRIPT" "$TARGET_DIR" >/dev/null

for skill in "${SKILLS[@]}"; do
  target="$TARGET_DIR/$skill"
  expected="$ROOT/skills/$skill"

  [[ -L "$target" ]] || fail "$skill 不是软连接"
  [[ "$(readlink "$target")" == "$expected" ]] \
    || fail "$skill 指向了错误路径：$(readlink "$target")"
done

backup_root="$TEST_ROOT/skills-backup"
[[ -d "$backup_root" ]] || fail "备份目录没有移出 skill 枚举根目录"
backup_file="$(find "$backup_root" -type f -path '*/xie-write/独有文件.txt' -print -quit)"
[[ -n "$backup_file" ]] || fail "没有备份旧的 xie-write 独有文件"

backup_count_before="$(
  find "$backup_root" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' '
)"

"$SYNC_SCRIPT" "$TARGET_DIR" >/dev/null

backup_count_after="$(
  find "$backup_root" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' '
)"
[[ "$backup_count_after" == "$backup_count_before" ]] \
  || fail "重复执行创建了额外备份"

echo "软连接同步测试通过：${#SKILLS[@]} 个 skill"
