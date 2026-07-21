#!/usr/bin/env python3
"""笔记 Markdown → JS 数据转换器

用法:
    # 预览（不修改 index.html）
    python scripts/build_notes.py --dry-run

    # 正式生成并注入 index.html
    python scripts/build_notes.py

目录结构:
    content/notes/*.md  →  解析  →  index.html 中的 const N = [...]
"""

import re
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
NOTES_DIR = PROJECT_ROOT / "content" / "notes"
INDEX_FILE = PROJECT_ROOT / "frontend" / "public" / "index.html"

# Frontmatter 键 → JS 字段映射
FIELD_MAP = {
    "id": "id",
    "category": "d",
    "badge": "bc",
    "cols": "c",
    "rows": "r",
    "image": "img",
    "summary": "s",
    "pois": "rp",        # 逗号分隔，如: p_wulong,p_hongya
    "feat": "feat",      # true/false
}


def parse_note(filepath: Path) -> dict:
    """解析单个 Markdown 文件，返回 JS 对象字典"""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # 第一行是标题
    title = lines[0].lstrip("#").strip() if lines else filepath.stem

    # 解析 frontmatter
    meta = {}
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        if line == "---":
            break
        if ":" in line and not line.startswith("---"):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            meta[key] = val
        i += 1

    # 正文：--- 之后的所有内容
    content_start = i + 1
    content = "\n".join(lines[content_start:]).strip()

    # 构建 JS 对象字段
    js = {"n": title, "content": content}

    for md_key, js_key in FIELD_MAP.items():
        if md_key in meta:
            val = meta[md_key]
            if js_key == "rp":
                # POI ID 用逗号分隔
                val = [p.strip() for p in val.split(",") if p.strip()]
            elif js_key in ("c", "r"):
                val = int(val)
            elif js_key == "feat":
                val = val.lower() == "true"
            elif js_key == "id":
                val = val  # 保持字符串
            js[js_key] = val

    return js


def js_object(entry: dict) -> str:
    """将字典转为紧凑的 JS 对象字符串"""
    parts = []
    # 固定字段顺序
    for key in ["id", "n", "d", "bc", "c", "r"]:
        if key in entry:
            v = entry[key]
            parts.append(f"{key}:{json_dumps(v)}")

    # feat（可选）
    if entry.get("feat"):
        parts.append("feat:true")

    # img, s
    for key in ["img", "s"]:
        if key in entry:
            parts.append(f"{key}:{json_dumps(entry[key])}")

    # content（正文，放到最后但要换行好看）
    content = entry.get("content", "")

    # rp（关联景点）
    if "rp" in entry and entry["rp"]:
        parts.append(f"rp:{json_dumps(entry['rp'])}")

    line1 = "  {" + ",".join(parts) + ","
    line2 = f"   {json_dumps(content)}"
    line3 = "  }"

    return line1 + "\n" + line2 + "\n" + line3


def json_dumps(val):
    """安全地转为 JS 值"""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, list):
        return "[" + ",".join(json_dumps(v) for v in val) + "]"
    if isinstance(val, str):
        # 转义单引号和反斜杠
        escaped = val.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    return str(val)


def build_notes(dry_run: bool = False):
    """主流程：读取所有 MD 文件 → 生成 JS → 注入 index.html"""
    if not NOTES_DIR.exists():
        print(f"[ERROR] 笔记目录不存在: {NOTES_DIR}")
        sys.exit(1)

    md_files = sorted(NOTES_DIR.glob("*.md"))
    if not md_files:
        print("[INFO] 没有找到 .md 文件")
        return

    print(f"[INFO] 发现 {len(md_files)} 篇笔记")
    entries = []
    for f in md_files:
        try:
            entry = parse_note(f)
            entries.append(entry)
            print(f"  ✅ {f.name} → {entry.get('id', '?')}")
        except Exception as e:
            print(f"  ❌ {f.name}: {e}")

    # 生成 JS 数组
    js_lines = ["const N=["]
    for i, entry in enumerate(entries):
        js_block = js_object(entry)
        if i < len(entries) - 1:
            js_block += ","
        js_lines.append(js_block)
    js_lines.append("];")

    new_n_array = "\n".join(js_lines)

    if dry_run:
        print("\n[DRY RUN] 生成的 JS 代码（前 500 字符）:")
        print(new_n_array[:500])
        print("...")
        return

    # 注入到 index.html
    html = INDEX_FILE.read_text(encoding="utf-8")
    # 找到 const N=[ 到 ]; 的区间并替换
    pattern = r"(const N=\[).*?(\n\];)"
    if not re.search(pattern, html, re.DOTALL):
        print("[ERROR] 在 index.html 中找不到 const N=[...] 区间")
        sys.exit(1)

    new_html = re.sub(pattern, new_n_array + r"\2", html, count=1, flags=re.DOTALL)
    INDEX_FILE.write_text(new_html, encoding="utf-8")
    print(f"\n✅ 已更新 {INDEX_FILE} ({len(entries)} 篇笔记)")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    build_notes(dry_run=dry)
