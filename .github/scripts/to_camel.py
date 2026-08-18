#!/usr/bin/env python3
"""
将中文角色名转换为驼峰拼音（用于 GitHub Release 文件名）
用法: python3 to_camel.py "中文名"
"""
import re
import sys
from pypinyin import pinyin, Style

def to_camel(name):
    """将中文名转换为驼峰拼音"""
    parts = []
    for seg in re.split(r'([\x00-\x7f]+)', name):
        if not seg:
            continue
        if seg.isascii():
            # ASCII 部分，清理非法字符
            cleaned = re.sub(r'[^A-Za-z0-9._-]', '', seg)
            if cleaned:
                parts.append(cleaned)
        else:
            # 中文部分，转换为驼峰拼音
            camel = ''.join(
                s[0].capitalize()
                for s in pinyin(seg, style=Style.NORMAL)
                if s[0] and all(ord(c) < 128 and c.isalnum() for c in s[0])
            )
            if camel:
                parts.append(camel)
    return '_'.join(parts)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 to_camel.py '中文名'", file=sys.stderr)
        sys.exit(1)
    
    name = sys.argv[1]
    print(to_camel(name))
