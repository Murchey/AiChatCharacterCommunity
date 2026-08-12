#!/usr/bin/env bash
#
# 打包脚本：将 Characters/ 下的角色内容打包为 zip
#   - dist/game/   按游戏分类，每个游戏目录一个 zip（如 ArknightsEndfield.zip）
#   - dist/single/ 每个角色目录一个 zip（重名角色以 "游戏_角色" 命名避免覆盖）
#
# 用法: bash scripts/build-packs.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHARACTERS="$ROOT/Characters"
DIST="$ROOT/dist"
GAME_DIR="$DIST/game"
SINGLE_DIR="$DIST/single"

rm -rf "$DIST"
mkdir -p "$GAME_DIR" "$SINGLE_DIR"

# ---------- 1. 游戏分类打包 ----------
while IFS= read -r game_dir; do
  game="$(basename "$game_dir")"
  echo "[game] $game"
  (cd "$CHARACTERS" && zip -qr "$GAME_DIR/$game.zip" "$game")
done < <(find "$CHARACTERS" -mindepth 1 -maxdepth 1 -type d | sort)

# ---------- 2. 角色分类打包 ----------
while IFS= read -r char_dir; do
  char="$(basename "$char_dir")"
  game="$(basename "$(dirname "$char_dir")")"
  name="$char"
  if [[ -e "$SINGLE_DIR/$char.zip" ]]; then
    name="${game}_${char}"
    echo "[single] 重名角色，已重命名: $name"
  fi
  echo "[single] $name"
  (cd "$char_dir/.." && zip -qr "$SINGLE_DIR/$name.zip" "$char")
done < <(find "$CHARACTERS" -mindepth 2 -maxdepth 2 -type d | sort)

echo ""
echo "===== 游戏包 ($(ls -1 "$GAME_DIR" | wc -l) 个) ====="
ls -1 "$GAME_DIR"
echo ""
echo "===== 角色包 ($(ls -1 "$SINGLE_DIR" | wc -l) 个) ====="
ls -1 "$SINGLE_DIR"
