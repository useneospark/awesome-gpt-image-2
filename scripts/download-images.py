#!/usr/bin/env python3
"""
批量下载 GPT Image 2 示例图片
"""
import os
import requests
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "public" / "images"

# 图片URL列表，按分类组织
IMAGES = {
    "illustration": [
        ("https://pub-e1dc3561f27d41a4b14b346813c0a4fc.r2.dev/2026/04/317607c84c0f.jpg", "character-design-lira.jpg"),
        ("https://cdn.evolink.ai/character_case7/output.jpg", "mecha-girl-sea-city.jpg"),
        ("https://cdn.evolink.ai/character_case9/output.jpg", "chaos-notes-face.jpg"),
        ("https://cdn.evolink.ai/poster_case31/output.jpg", "dreamy-watercolor.jpg"),
        ("https://cdn.evolink.ai/case_case93/output.jpg", "new-chinese-lotus.jpg"),
    ],
    "portraits": [
        ("https://cdn.evolink.ai/portrait_case1/output.jpg", "convenience-store-neon.jpg"),
        ("https://cdn.evolink.ai/portrait_case2/output.jpg", "cinematic-minimal.jpg"),
        ("https://cdn.evolink.ai/portrait_case11/output.jpg", "korean-idol-bedroom.jpg"),
        ("https://cdn.evolink.ai/portrait_case15/output.jpg", "fujifilm-strawberry.jpg"),
        ("https://cdn.evolink.ai/portrait_case4/output.jpg", "35mm-flash-editorial.jpg"),
        ("https://cdn.evolink.ai/portrait_case6/output.jpg", "soft-airy-35mm.jpg"),
        ("https://cdn.evolink.ai/portrait_case7/output.jpg", "luxury-glam-beauty.jpg"),
    ],
    "product": [
        ("https://cdn.notegpt.io/notegpt/static/blog/b6c2684e69e2ba652bf927e51697e52c.jpeg", "wireless-earbuds-macro.jpg"),
        ("https://cdn.evolink.ai/portrait_case79/output.jpg", "strawberry-soft-serve.jpg"),
    ],
    "ui-design": [
        ("https://cdn.notegpt.io/notegpt/static/blog/2a9a50dc0280a3a0f3dece42b97b7177.jpeg", "smart-home-dashboard.jpg"),
        ("https://cdn.evolink.ai/case_case61/output.jpg", "youtube-thumbnail.jpg"),
    ],
    "typography": [
        ("https://cdn.notegpt.io/notegpt/static/blog/d2d6c0489a8772fdf3c6a34d13f877a7.png", "mind-map-brain.jpg"),
    ],
    "cinematic": [
        ("https://v3b.fal.media/files/b/0a970066/fJ92BDR74EvGuiQ1bOqZ__yuzFTyGN.jpg", "train-reflection.jpg"),
    ],
    "marketing": [
        ("https://cdn.notegpt.io/notegpt/static/blog/4ad5987810ef8d569e069eb8abf94262.jpeg", "blog-header-books.jpg"),
        ("https://cdn.notegpt.io/notegpt/static/blog/8a25e6347b6293bc0d52d96202c12f46.jpeg", "personal-brand-lifestyle.jpg"),
    ],
    "anime": [
        ("https://cdn.evolink.ai/character_case1/output.jpg", "anime-snapshot.jpg"),
        ("https://cdn.evolink.ai/character_case3/output.jpg", "galgame-character-page.jpg"),
        ("https://cdn.evolink.ai/character_case8/output.jpg", "saint-seiya-cards.jpg"),
    ],
    "experimental": [
        ("https://cdn.notegpt.io/notegpt/static/blog/4bcd6e814562f5125c2910d69a33e4e2.jpeg", "surreal-whale.jpg"),
        ("https://cdn.notegpt.io/notegpt/static/blog/d7a2399267f3325467c08c1a31c7ea0a.jpeg", "historical-remix-astronaut.jpg"),
        ("https://cdn.evolink.ai/comparison_case23/output.jpg", "silhouette-universe.jpg"),
        ("https://cdn.evolink.ai/comparison_case29/output.jpg", "lion-camel-ridge.jpg"),
    ],
    "fantasy": [
        ("https://cdn.evolink.ai/comparison_case30/output.jpg", "cs-terraria-mashup.jpg"),
    ],
    "architecture": [
        ("https://cdn.notegpt.io/notegpt/static/blog/3803c1c50d86de395d3d27e88dd987c9.jpeg", "luxury-boutique.jpg"),
    ],
}

def download_image(url: str, dest: Path) -> bool:
    """下载单张图片"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            dest.write_bytes(resp.content)
            print(f"  [OK] {dest.name}")
            return True
        else:
            print(f"  [FAIL] {dest.name} (HTTP {resp.status_code})")
            return False
    except Exception as e:
        print(f"  [FAIL] {dest.name} ({e})")
        return False

def main():
    total = 0
    success = 0
    for category, images in IMAGES.items():
        cat_dir = IMAGES_DIR / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[{category}] -> {cat_dir}")
        for url, filename in images:
            total += 1
            dest = cat_dir / filename
            if dest.exists():
                print(f"  → {filename} (exists)")
                success += 1
                continue
            if download_image(url, dest):
                success += 1
    print(f"\n{'='*40}")
    print(f"Total: {total}, Success: {success}, Failed: {total - success}")

if __name__ == "__main__":
    main()
