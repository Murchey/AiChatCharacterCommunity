#!/usr/bin/env python3
"""本地打包脚本：按 Characters / Stickers 生成全量包与增量更新包。

用法:
  python package.py                 # dist 不存在 → 全量；已有 dist → 本轮变更输出到 dist/update/
  python package.py characters      # 只处理角色包
  python package.py game stickers   # 多种模式
  python package.py --full          # 强制全量重打 dist/（不生成 update/）
  python package.py --list          # 只预览将要处理的内容，不实际写入
  python package.py --clean         # 删除 dist/ 后再全量打包

输出目录:
  dist/game/        每个 Characters/<游戏>/ 一个当前完整 zip
  dist/characters/  每个含 Profile.json 的角色一个当前完整 zip
  dist/stickers/    每个 Stickers/<表情包>/ 一个当前完整 zip（仅图片）
  dist/.package_manifest.json  本地内容哈希与元数据缓存
  dist/update/     本次新增或变更的 zip；下一次运行前自动归档到对应主分类

增量说明:
  - 脚本先比较目录内容签名，不再只根据 zip 是否存在判断。
  - 每个文件缓存 size、mtime_ns 与 BLAKE2b 摘要；元数据未变时不重新读取文件内容。
  - 只有变更文件才以 4 MiB 分块流式重算摘要，避免大量图片反复哈希造成卡顿。
  - 已有 dist 时，本轮变更只写入 dist/update/；下一次打包开始时，上一轮 update 会自动归档进对应的主分类目录。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHARACTERS_DIR = ROOT / "Characters"
STICKERS_DIR = ROOT / "Stickers"
DIST_DIR = ROOT / "dist"
_MANIFEST_FILENAME = ".package_manifest.json"

# 兼容旧 mode 名 single → characters
_MODE_ALIASES = {"single": "characters"}
_STICKER_IMAGE_EXTS = {".gif", ".webp", ".png", ".jpg", ".jpeg"}
_HASH_CHUNK_SIZE = 4 * 1024 * 1024  # 4 MiB：减少大量小文件读取的循环开销


def _hash_file(path: Path) -> str:
    """以固定大块流式读取文件，避免把图片等大文件一次性载入内存。"""
    digest = hashlib.blake2b(digest_size=20)
    with path.open("rb") as source:
        while chunk := source.read(_HASH_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint_file(path: Path, cached: dict[str, object] | None) -> dict[str, object]:
    """返回文件指纹；大小与 mtime_ns 未变时复用上次 digest。"""
    stat = path.stat()
    if (
        cached
        and cached.get("size") == stat.st_size
        and cached.get("mtime_ns") == stat.st_mtime_ns
        and isinstance(cached.get("digest"), str)
    ):
        digest = cached["digest"]
    else:
        digest = _hash_file(path)
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns, "digest": digest}


def _cache_key(path: Path) -> str:
    """优先写仓库相对路径，临时目录测试时回退绝对路径。"""
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _directory_signature(
    src_dir: Path,
    file_cache: dict[str, dict[str, object]],
    include_exts: set[str] | None,
) -> tuple[str, dict[str, dict[str, object]]]:
    """生成目录内容签名，并只重哈希元数据发生变化的文件。"""
    updated_cache = dict(file_cache)
    digest = hashlib.blake2b(digest_size=20)
    for path in sorted(src_dir.rglob("*")):
        if not path.is_file() or (include_exts is not None and path.suffix.lower() not in include_exts):
            continue
        key = _cache_key(path)
        fingerprint = _fingerprint_file(path, updated_cache.get(key))
        updated_cache[key] = fingerprint
        rel = path.relative_to(src_dir).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(fingerprint["digest"]).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest(), updated_cache


def _manifest_path() -> Path:
    return DIST_DIR / _MANIFEST_FILENAME


def _update_dir() -> Path:
    return DIST_DIR / "update"


def _load_manifest() -> dict[str, dict[str, object]]:
    path = _manifest_path()
    if not path.is_file():
        return {"files": {}, "packages": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("哈希清单无法读取，将按首次增量生成更新包。")
        return {"files": {}, "packages": {}}
    if not isinstance(value, dict):
        return {"files": {}, "packages": {}}
    files = value.get("files")
    packages = value.get("packages")
    return {
        "files": files if isinstance(files, dict) else {},
        "packages": packages if isinstance(packages, dict) else {},
    }


def _save_manifest(manifest: dict[str, dict[str, object]]) -> None:
    path = _manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


def _package_changed(
    package_key: str,
    source_dir: Path,
    include_exts: set[str] | None,
    manifest: dict[str, dict[str, object]],
    full: bool,
) -> bool:
    raw_files = manifest["files"]
    file_cache = {
        key: value
        for key, value in raw_files.items()
        if isinstance(key, str) and isinstance(value, dict)
    }
    signature, updated_cache = _directory_signature(source_dir, file_cache, include_exts)
    manifest["files"] = updated_cache
    old_signature = manifest["packages"].get(package_key)
    manifest["packages"][package_key] = signature
    return full or old_signature != signature


def _archive_previous_update() -> int:
    """将上一轮 dist/update 的包归档为新的主分类包。"""
    update_dir = _update_dir()
    archived = 0
    for category in ("game", "characters", "stickers"):
        pending_dir = update_dir / category
        if not pending_dir.is_dir():
            continue
        destination_dir = DIST_DIR / category
        for zip_path in sorted(pending_dir.glob("*.zip")):
            destination_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(zip_path), str(destination_dir / zip_path.name))
            archived += 1
        shutil.rmtree(pending_dir)
    if update_dir.is_dir() and not any(update_dir.iterdir()):
        update_dir.rmdir()
    if archived:
        print(f"已归档上一轮更新包：{archived} 个 zip")
    return archived


def _prepare_update() -> None:
    """创建空的本轮 update 目录；旧 update 必须先由归档流程处理。"""
    _update_dir().mkdir(parents=True, exist_ok=True)


def _zip_dir(src_dir: Path, zip_path: Path, include_exts: set[str] | None = None) -> int:
    """将目录打包为 zip，zip 内保留目录本身作为最外层目录名。"""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    root_name = src_dir.name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src_dir.rglob("*")):
            if not path.is_file():
                continue
            if include_exts is not None and path.suffix.lower() not in include_exts:
                continue
            rel = path.relative_to(src_dir)
            zf.write(path, f"{root_name}/{rel.as_posix()}")
            count += 1
    return count


def _iter_game_dirs() -> list[Path]:
    if not CHARACTERS_DIR.is_dir():
        return []
    return sorted(
        p for p in CHARACTERS_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")
    )


def _iter_character_dirs() -> list[tuple[str, Path]]:
    results: list[tuple[str, Path]] = []
    for game_dir in _iter_game_dirs():
        for char_dir in sorted(game_dir.iterdir()):
            if char_dir.is_dir() and (char_dir / "Profile.json").is_file():
                results.append((game_dir.name, char_dir))
    return results


def _iter_sticker_dirs() -> list[Path]:
    if not STICKERS_DIR.is_dir():
        return []
    return sorted(
        p for p in STICKERS_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")
    )


def _sticker_has_images(sticker_dir: Path) -> bool:
    return any(
        p.is_file() and p.suffix.lower() in _STICKER_IMAGE_EXTS
        for p in sticker_dir.rglob("*")
    )


def package_games(*, full: bool, list_only: bool, manifest: dict[str, dict[str, object]]) -> list[Path]:
    """按游戏打包；全量写 dist，增量写 dist/update/game。"""
    games = _iter_game_dirs()
    if not games:
        print("未找到 Characters/ 下的游戏目录。")
        return []

    out_dir = DIST_DIR / "game"
    created: list[Path] = []
    for game_dir in games:
        dist_zip_path = out_dir / f"{game_dir.name}.zip"
        zip_path = dist_zip_path if full else _update_dir() / "game" / dist_zip_path.name
        changed = _package_changed(f"game/{game_dir.name}", game_dir, None, manifest, full)
        if not changed:
            print(f"[game] 跳过 {game_dir.name}（内容未变化）")
            continue
        if list_only:
            target = f"dist/update/game/{zip_path.name}" if not full else f"game/{zip_path.name}"
            print(f"[game] {game_dir.name}  ->  {target}")
            created.append(zip_path)
            continue
        count = _zip_dir(game_dir, zip_path)
        print(f"[game] 已写入 {zip_path.relative_to(ROOT)}  ({count} 个文件)")
        created.append(zip_path)
    return created


def package_characters(*, full: bool, list_only: bool, manifest: dict[str, dict[str, object]]) -> list[Path]:
    """按角色打包；全量写 dist，增量写 dist/update/characters。"""
    chars = _iter_character_dirs()
    if not chars:
        print("未找到含 Profile.json 的角色目录。")
        return []

    out_dir = DIST_DIR / "characters"
    created: list[Path] = []
    for game_name, char_dir in chars:
        dist_zip_path = out_dir / f"{char_dir.name}.zip"
        zip_path = dist_zip_path if full else _update_dir() / "characters" / dist_zip_path.name
        package_key = f"characters/{game_name}/{char_dir.name}"
        changed = _package_changed(package_key, char_dir, None, manifest, full)
        if not changed:
            print(f"[characters] 跳过 {char_dir.name}（内容未变化）")
            continue
        if list_only:
            target = f"dist/update/characters/{zip_path.name}" if not full else f"characters/{zip_path.name}"
            print(f"[characters] {game_name}/{char_dir.name}  ->  {target}")
            created.append(zip_path)
            continue
        count = _zip_dir(char_dir, zip_path)
        print(f"[characters] 已写入 {zip_path.relative_to(ROOT)}  ({count} 个文件)")
        created.append(zip_path)
    return created


def package_stickers(*, full: bool, list_only: bool, manifest: dict[str, dict[str, object]]) -> list[Path]:
    """表情包打包；全量写 dist，增量写 dist/update/stickers。"""
    stickers = _iter_sticker_dirs()
    if not stickers:
        print("未找到 Stickers/ 下的表情包目录。")
        return []

    out_dir = DIST_DIR / "stickers"
    created: list[Path] = []
    attempted_valid = 0
    for sticker_dir in stickers:
        if not _sticker_has_images(sticker_dir):
            print(f"[stickers] 跳过 {sticker_dir.name}：无支持图片")
            continue
        attempted_valid += 1
        dist_zip_path = out_dir / f"{sticker_dir.name}.zip"
        zip_path = dist_zip_path if full else _update_dir() / "stickers" / dist_zip_path.name
        changed = _package_changed(
            f"stickers/{sticker_dir.name}", sticker_dir, _STICKER_IMAGE_EXTS, manifest, full
        )
        if not changed:
            print(f"[stickers] 跳过 {sticker_dir.name}（内容未变化）")
            continue
        if list_only:
            target = f"dist/update/stickers/{zip_path.name}" if not full else f"stickers/{zip_path.name}"
            print(f"[stickers] {sticker_dir.name}  ->  {target}")
            created.append(zip_path)
            continue
        count = _zip_dir(sticker_dir, zip_path, include_exts=_STICKER_IMAGE_EXTS)
        print(f"[stickers] 已写入 {zip_path.relative_to(ROOT)}  ({count} 个文件)")
        created.append(zip_path)

    if attempted_valid == 0 and not list_only:
        print("Stickers/ 下没有有效表情包（至少需要一张 gif/webp/png/jpg/jpeg）。")
    return created


def _migrate_legacy_layout() -> None:
    """旧 dist/single → dist/characters；忽略并提示旧 name_mapping。"""
    legacy_single = DIST_DIR / "single"
    target = DIST_DIR / "characters"
    if legacy_single.is_dir() and not target.exists():
        legacy_single.rename(target)
        print("已将 dist/single 重命名为 dist/characters")
    legacy_map = DIST_DIR / "name_mapping"
    if legacy_map.exists():
        print("发现旧目录 dist/name_mapping（Windows 不再使用拼音索引），可手动删除。")


def clean_dist() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print(f"已清空 {DIST_DIR.relative_to(ROOT)}/")
    else:
        print("dist/ 不存在，无需清理。")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="本地打包角色/表情包（Windows 中文文件名；支持增量）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "模式:\n"
            "  game        dist/game/\n"
            "  characters  dist/characters/（旧名 single 亦可）\n"
            "  stickers    dist/stickers/\n"
            "\n"
            "示例:\n"
            "  python package.py\n"
            "  python package.py characters\n"
            "  python package.py --full\n"
            "  python package.py --clean\n"
        ),
    )
    parser.add_argument(
        "modes",
        nargs="*",
        help="game / characters(/single) / stickers；省略则全部",
    )
    parser.add_argument("--list", action="store_true", help="只预览，不写 zip")
    parser.add_argument("--full", action="store_true", help="强制重打全部（不删除已有其他文件）")
    parser.add_argument("--clean", action="store_true", help="打包前删除 dist/（随后全量）")
    args = parser.parse_args(argv)

    modes_raw = [_MODE_ALIASES.get(m, m) for m in (args.modes or ["game", "characters", "stickers"])]
    valid = {"game", "characters", "stickers"}
    unknown = [m for m in modes_raw if m not in valid]
    if unknown:
        raise SystemExit(f"未知模式: {', '.join(unknown)}（可用: game, characters, stickers）")

    # 去重且保持顺序
    modes: list[str] = []
    for m in modes_raw:
        if m not in modes:
            modes.append(m)

    dist_existed = DIST_DIR.exists()
    full = args.full or args.clean or not dist_existed

    if args.clean and not args.list:
        clean_dist()
        full = True
    elif dist_existed:
        _migrate_legacy_layout()
        if not args.list:
            _archive_previous_update()

    manifest = _load_manifest()
    if not full and not args.list:
        _prepare_update()

    print(f"工作目录: {ROOT}")
    print(f"模式: {', '.join(modes)}")
    print(f"策略: {'全量' if full else '增量（内容变化 → dist/update/）'}")
    if args.list:
        print("（--list 预览，不写 zip）")
    print("-" * 50)

    total = 0
    if "game" in modes:
        total += len(package_games(full=full, list_only=args.list, manifest=manifest))
    if "characters" in modes:
        total += len(package_characters(full=full, list_only=args.list, manifest=manifest))
    if "stickers" in modes:
        total += len(package_stickers(full=full, list_only=args.list, manifest=manifest))

    if not args.list:
        _save_manifest(manifest)

    print("-" * 50)
    if args.list:
        print(f"预览完成：将处理 {total} 个包")
    else:
        print(f"完成：共写入 {total} 个 zip")
        print(f"输出: {DIST_DIR / 'game'}, {DIST_DIR / 'characters'}, {DIST_DIR / 'stickers'}")
        if not full:
            print(f"本次增量更新: {_update_dir()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
