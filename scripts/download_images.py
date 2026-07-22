#!/usr/bin/env python3
"""从 Pexels + Unsplash 下载景区图片

需要 API Key:
  - Pexels: https://www.pexels.com/api/ → 免费注册 → 200次/小时
  - Unsplash: https://unsplash.com/developers → 注册App → 50次/小时

配置方式:
  export PEXELS_API_KEY=xxx
  export UNSPLASH_ACCESS_KEY=xxx

用法:
  python scripts/download_images.py
"""

import os
import re
import sys
import time
import json
import urllib.request
import urllib.parse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PICTURE_DIR = PROJECT_ROOT / "picture"

UA = "Mozilla/5.0 (compatible; TravelPlatform/1.0)"
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

# 景点 → 搜索关键词 → 目标张数 (洪崖洞已有4张Unsplash)
TARGETS = [
    ("长江索道", ["chongqing cableway", "yangtze river cableway"], 3),
    ("磁器口", ["ciqikou chongqing", "chongqing old street"], 4),
    ("武隆天生三桥", ["wulong china", "three natural bridges"], 5),
    ("大足石刻", ["dazu rock carvings", "buddhist cliff carvings"], 4),
    ("白帝城", ["white emperor city", "three gorges china"], 3),
    ("巫山小三峡", ["wushan china", "three gorges river"], 3),
    ("金佛山", ["jinfo mountain", "golden buddha mountain"], 4),
    ("酉阳桃花源", ["peach blossom spring chongqing", "youyang china"], 4),
    ("四面山", ["simian mountain waterfall", "chongqing waterfall"], 3),
    ("川剧变脸", ["sichuan opera", "chinese opera face"], 3),
    ("火锅文化", ["chongqing hotpot", "chinese hotpot feast"], 3),
    ("铜梁火龙", ["chinese fire dragon", "dragon dance fire"], 3),
]


def api_get(url, headers=None):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def search_pexels(query, per_page=10):
    """Pexels API search — 免费 200次/h"""
    if not PEXELS_KEY:
        return []
    encoded = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={encoded}&per_page={per_page}&size=large&orientation=landscape"
    try:
        data = api_get(url, {"Authorization": PEXELS_KEY})
        return [p["src"]["large"] for p in data.get("photos", [])]
    except Exception as e:
        print(f"    Pexels 失败 '{query}': {e}")
        return []


def search_unsplash(query, per_page=10):
    """Unsplash API search — 免费 50次/h"""
    if not UNSPLASH_KEY:
        return []
    encoded = urllib.parse.quote(query)
    url = f"https://api.unsplash.com/search/photos?query={encoded}&per_page={per_page}&orientation=landscape"
    try:
        data = api_get(url, {"Authorization": f"Client-ID {UNSPLASH_KEY}"})
        return [p["urls"]["regular"] for p in data.get("results", [])]
    except Exception as e:
        print(f"    Unsplash 失败 '{query}': {e}")
        return []


def download(url, filepath):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            with open(filepath, "wb") as f:
                f.write(r.read())
            return True
    except Exception as e:
        print(f"    下载失败: {e}")
        return False


def download_for(name, keywords, target):
    """为一个景点下载图片"""
    loc_dir = PICTURE_DIR / name
    existing = len(list(loc_dir.glob("*.jpg"))) if loc_dir.exists() else 0
    needed = target - existing

    if needed <= 0:
        print(f"  ✅ {name}: 已有 {existing} 张")
        return target, target

    print(f"  📥 {name}: 需 {needed} 张 (已有 {existing})")
    downloaded = 0
    seen = set()

    # Round 1: Pexels
    for kw in keywords:
        if downloaded >= needed:
            break
        urls = search_pexels(kw)
        for u in urls:
            if downloaded >= needed:
                break
            if u in seen:
                continue
            seen.add(u)
            fname = f"pexels_{downloaded+1}.jpg"
            fpath = loc_dir / fname
            os.makedirs(loc_dir, exist_ok=True)
            time.sleep(0.2)
            if download(u, fpath):
                downloaded += 1
                print(f"    ✅ [{downloaded}/{target}] {fname}")

    # Round 2: Unsplash
    for kw in keywords:
        if downloaded >= needed:
            break
        urls = search_unsplash(kw)
        for u in urls:
            if downloaded >= needed:
                break
            if u in seen:
                continue
            seen.add(u)
            fname = f"unsplash_{downloaded+1}.jpg"
            fpath = loc_dir / fname
            os.makedirs(loc_dir, exist_ok=True)
            time.sleep(0.5)
            if download(u, fpath):
                downloaded += 1
                print(f"    ✅ [{downloaded}/{target}] {fname}")

    return target, downloaded


def main():
    print("=" * 60)
    print("🎯 Pexels + Unsplash 景区图片下载")
    if not PEXELS_KEY and not UNSPLASH_KEY:
        print("\n❌ 未设置 API Key!")
        print("   请先注册获取 Key:")
        print("   · Pexels: https://www.pexels.com/api/  → 免费")
        print("   · Unsplash: https://unsplash.com/developers  → 免费")
        print("\n   然后设置环境变量:")
        print("   export PEXELS_API_KEY=你的key")
        print("   export UNSPLASH_ACCESS_KEY=你的key\n")
        sys.exit(1)

    total = 0
    found = 0
    missing = []

    for name, keywords, target in TARGETS:
        t, f = download_for(name, keywords, target)
        total += t
        found += f
        if f < t:
            missing.append((name, t - f))
        print()

    print("=" * 60)
    print(f"📊 总计: {len(TARGETS)} 个景点, {found}/{total} 张")
    if missing:
        print("\n❓ 仍需手动查找:")
        for m, cnt in missing:
            print(f"  · {m}: 缺 {cnt} 张")
    print("=" * 60)


if __name__ == "__main__":
    main()
