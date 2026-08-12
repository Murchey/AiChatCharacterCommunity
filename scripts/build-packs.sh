#!/usr/bin/env bash
#
# 打包脚本：将 Characters/ 下的角色内容打包为 zip
#   - dist/game/   按游戏分类，每个游戏目录一个 zip（如 ArknightsEndfield.zip）
#   - dist/single/ 每个角色目录一个 zip（重名角色以 "游戏_角色" 命名避免覆盖）
#
# 说明：GitHub Release 的资产文件名不支持非 ASCII 字符（中文会被改名为
# default.zip），因此 zip 文件名统一转为驼峰拼音（如 佩丽卡 -> PeiLiKa），
# zip 包内的目录名仍保留中文原名。
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

# 确保 pypinyin 可用（中文名转驼峰拼音用）
if ! python3 -c "import pypinyin" >/dev/null 2>&1; then
  pip install --quiet pypinyin
fi

# 中文名转驼峰拼音：ASCII 段原样保留，中文段转驼峰拼音
#   佩丽卡 -> PeiLiKa
#   银狼（SilverWolfLv999） -> YinLang_SilverWolfLv999
#   ArknightsEndfield -> ArknightsEndfield
to_camel() {
  python3 -c '
import re, sys
from pypinyin import pinyin, Style

def convert(name):
    parts = []
    for seg in re.split(r"([\x00-\x7f]+)", name):
        if not seg:
            continue
        if seg.isascii():
            cleaned = re.sub(r"[^A-Za-z0-9._-]", "", seg)
            if cleaned:
                parts.append(cleaned)
        else:
            camel = "".join(
                s[0].capitalize()
                for s in pinyin(seg, style=Style.NORMAL)
                if s[0] and all(ord(c) < 128 and c.isalnum() for c in s[0])
            )
            if camel:
                parts.append(camel)
    return "_".join(parts)

print(convert(sys.argv[1]))
' "$1"
}

# ---------- 1. 游戏分类打包 ----------
while IFS= read -r game_dir; do
  game="$(basename "$game_dir")"
  zip_name="$(to_camel "$game")"
  echo "[game] $game -> $zip_name.zip"
  (cd "$CHARACTERS" && zip -qr "$GAME_DIR/$zip_name.zip" "$game")
done < <(find "$CHARACTERS" -mindepth 1 -maxdepth 1 -type d | sort)

# ---------- 2. 角色分类打包 ----------
while IFS= read -r char_dir; do
  char="$(basename "$char_dir")"
  game="$(basename "$(dirname "$char_dir")")"
  zip_name="$(to_camel "$char")"
  if [[ -e "$SINGLE_DIR/$zip_name.zip" ]]; then
    zip_name="$(to_camel "${game}_${char}")"
    echo "[single] 重名角色，已重命名: $zip_name"
  fi
  echo "[single] $zip_name"
  (cd "$char_dir/.." && zip -qr "$SINGLE_DIR/$zip_name.zip" "$char")
done < <(find "$CHARACTERS" -mindepth 2 -maxdepth 2 -type d | sort)

echo ""
echo "===== 游戏包 ($(ls -1 "$GAME_DIR" | wc -l) 个) ====="
ls -1 "$GAME_DIR"
echo ""
echo "===== 角色包 ($(ls -1 "$SINGLE_DIR" | wc -l) 个) ====="
ls -1 "$SINGLE_DIR"
