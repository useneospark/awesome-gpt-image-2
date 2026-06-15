#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dynamically update all README files with current web-cases collection counts.

Reads cases.json as the source of truth and refreshes badge totals, summary
lines, and Extended Collection tables across all supported languages.
"""

import json
import re
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CASES_JSON = BASE_DIR / "cases.json"
WEB_CASES_README = BASE_DIR / "prompts" / "web-cases" / "README.md"

# Legacy/marketing count for the originally curated prompt collection.
CURATED_COUNT = 280

README_FILES = {
    "README.md": "en",
    "README_zh.md": "zh",
    "README_ja.md": "ja",
    "README_ko.md": "ko",
    "README_es.md": "es",
    "README_fr.md": "fr",
    "README_de.md": "de",
}

# Category order used in the original READMEs (kept stable for consistency).
CATEGORY_ORDER = [
    "UI & Interfaces",
    "Posters & Typography",
    "Photography & Realism",
    "Charts & Infographics",
    "Illustration & Art",
    "Products & E-commerce",
    "Other Use Cases",
    "Brand & Logos",
    "Characters & People",
    "Scenes & Storytelling",
    "History & Classical Themes",
    "Architecture & Spaces",
    "Documents & Publishing",
]

CATEGORY_TRANSLATIONS = {
    "UI & Interfaces": "UI & 界面设计",
    "Posters & Typography": "海报与排版",
    "Photography & Realism": "摄影与写实",
    "Charts & Infographics": "图表与信息图",
    "Illustration & Art": "插画与艺术",
    "Products & E-commerce": "产品与电商",
    "Other Use Cases": "其他用例",
    "Brand & Logos": "品牌与 Logo",
    "Characters & People": "角色与人物",
    "Scenes & Storytelling": "场景与叙事",
    "History & Classical Themes": "历史与古典主题",
    "Architecture & Spaces": "建筑与空间",
    "Documents & Publishing": "文档与出版",
}

# Filenames for each category's markdown file in prompts/web-cases/.
CATEGORY_FILES = {
    "UI & Interfaces": "ui-interfaces.md",
    "Posters & Typography": "posters-typography.md",
    "Photography & Realism": "photography-realism.md",
    "Charts & Infographics": "charts-infographics.md",
    "Illustration & Art": "illustration-art.md",
    "Products & E-commerce": "products-ecommerce.md",
    "Other Use Cases": "other.md",
    "Brand & Logos": "brand-logos.md",
    "Characters & People": "characters-people.md",
    "Scenes & Storytelling": "scenes-storytelling.md",
    "History & Classical Themes": "history-classical.md",
    "Architecture & Spaces": "architecture.md",
    "Documents & Publishing": "documents-publishing.md",
}

LANG_LABELS = {
    "en": ("Prompts", "Prompts"),
    "zh": ("提示词", "提示词"),
    "ja": ("プロンプト", "プロンプト"),
    "ko": ("프롬프트", "프롬프트"),
    "es": ("Prompts", "Prompts"),
    "fr": ("Prompts", "Prompts"),
    "de": ("Prompts", "Prompts"),
}


def load_counts():
    """Load total and per-category counts from cases.json."""
    with open(CASES_JSON, encoding="utf-8") as f:
        data = json.load(f)

    web_count = data["totalCases"]
    category_counts = Counter(case["category"] for case in data["cases"])
    return {
        "curated": CURATED_COUNT,
        "web": web_count,
        "total": CURATED_COUNT + web_count,
        "categories": {cat: category_counts.get(cat, 0) for cat in CATEGORY_ORDER},
    }


def build_extended_section(lang: str, counts: dict) -> str:
    """Build the Extended Collection markdown section for a language."""
    web = counts["web"]
    rows = []
    for cat in CATEGORY_ORDER:
        count = counts["categories"][cat]
        display_cat = CATEGORY_TRANSLATIONS[cat] if lang == "zh" else cat
        rows.append(f"| {display_cat} | {count} |")

    if lang == "zh":
        return (
            "---\n\n"
            "## 扩展合集\n\n"
            "想要更多提示词？浏览 **[网络合集](prompts/web-cases/README.md)** — "
            f"按 13 个分类整理的 **{web} 个额外 GPT Image 2 提示词**：\n\n"
            "| 分类 | 提示词数量 |\n"
            "|------|-----------|\n"
            + "\n".join(rows)
            + "\n\n"
            "所有提示词均包含完整文本、来源标注和示例图片。\n"
        )

    return (
        "---\n\n"
        "## Extended Collection\n\n"
        "Looking for even more prompts? Browse the **[Web Collection](prompts/web-cases/README.md)** — "
        f"**{web} additional GPT Image 2 prompts** organized into 13 categories:\n\n"
        "| Category | Prompts |\n"
        "|----------|---------|\n"
        + "\n".join(rows)
        + "\n\n"
        "All prompts include full text, source attribution, and example images.\n"
    )


def replace_extended_section(content: str, lang: str, counts: dict) -> str:
    """Replace the Extended Collection section, preserving surrounding structure."""
    section = build_extended_section(lang, counts)

    # Match from the section header (with its leading '---') up to the next
    # leading '---' followed by another '##' heading, or end of file.
    if lang == "zh":
        header = r"## 扩展合集"
    else:
        header = r"## Extended Collection"

    pattern = re.compile(
        rf"---\n\n{header}.*?(?=\n---\n\n## |$)",
        re.DOTALL,
    )

    new_content, n = pattern.subn(section, content)
    if n == 0:
        print(f"  Warning: Extended Collection section not found")
    return new_content


def update_badge(content: str, lang: str, total: int) -> str:
    """Update the shield badge image URL and alt text."""
    badge_label, alt_word = LANG_LABELS[lang]

    # Image URL: e.g. Prompts-783+-blue -> Prompts-{total}+-blue
    content = re.sub(
        rf"https://img\.shields\.io/badge/{re.escape(badge_label)}-\d+\+-blue\.svg",
        f"https://img.shields.io/badge/{badge_label}-{total}+-blue.svg",
        content,
    )

    # Alt text: e.g. alt="783+ Prompts" -> alt="{total}+ Prompts"
    content = re.sub(
        rf'alt="\d+\+ {re.escape(alt_word)}"',
        f'alt="{total}+ {alt_word}"',
        content,
    )
    return content


def update_en_summary(content: str, counts: dict) -> str:
    """Update English Quick Links total summary and web collection note."""
    total = counts["total"]
    web = counts["web"]

    # Total summary line
    content = re.sub(
        r"\*\*Total: \d+\+ production-ready prompts\*\* — \d+ curated \+ \d+ from web collection",
        f"**Total: {total}+ production-ready prompts** — {counts['curated']} curated + {web} from web collection",
        content,
    )

    # Web collection note
    content = re.sub(
        r"with \*\*\d+ additional prompts\*\* sourced from",
        f"with **{web} additional prompts** sourced from",
        content,
    )
    return content


def update_zh_summary(content: str, counts: dict) -> str:
    """Update Chinese Quick Links total summary and web collection note."""
    total = counts["total"]
    web = counts["web"]

    # Total summary line
    content = re.sub(
        r"\*\*总计：\d+\+ 生产级提示词\*\* — \d+ 个精选 \+ \d+ 个网络合集",
        f"**总计：{total}+ 生产级提示词** — {counts['curated']} 个精选 + {web} 个网络合集",
        content,
    )

    # Web collection note
    content = re.sub(
        r"包含从 (\[gpt-image2\.canghe\.ai\]\(https://gpt-image2\.canghe\.ai/\)) 获取的 \*\*\d+ 个额外提示词\*\*",
        rf"包含从 \1 获取的 **{web} 个额外提示词**",
        content,
    )
    return content


def update_readme(filename: str, lang: str, counts: dict):
    """Update a single README file."""
    filepath = BASE_DIR / filename
    content = filepath.read_text(encoding="utf-8")

    content = update_badge(content, lang, counts["total"])
    content = replace_extended_section(content, lang, counts)

    if lang == "en":
        content = update_en_summary(content, counts)
    elif lang == "zh":
        content = update_zh_summary(content, counts)

    filepath.write_text(content, encoding="utf-8")
    print(f"  Updated {filename}")


def update_web_cases_readme(counts: dict):
    """Update prompts/web-cases/README.md with current counts."""
    web = counts["web"]
    rows = []
    for cat in CATEGORY_ORDER:
        count = counts["categories"][cat]
        filename = CATEGORY_FILES[cat]
        rows.append(f"| {cat} | {count} | [{filename}]({filename}) |")

    content = WEB_CASES_README.read_text(encoding="utf-8")

    # Update intro line
    content = re.sub(
        r"A comprehensive collection of \*\*\d+ GPT Image 2 prompts\*\*",
        f"A comprehensive collection of **{web} GPT Image 2 prompts**",
        content,
    )

    # Replace category table
    table_pattern = re.compile(
        r"(\| Category \| Prompts \| File \|\n"
        r"\|----------\|---------\|------\|\n)"
        r"(?:\| .*? \| \d+ \| \[.*?\]\(.*?\.md\) \|\n)+",
    )
    new_table = "| Category | Prompts | File |\n|----------|---------|------|\n" + "\n".join(rows) + "\n"
    content, n = table_pattern.subn(new_table, content)
    if n == 0:
        print("  Warning: web-cases category table not found")

    # Update total line
    content = re.sub(
        r"\*\*Total: \d+ prompts\*\*",
        f"**Total: {web} prompts**",
        content,
    )

    WEB_CASES_README.write_text(content, encoding="utf-8")
    print(f"  Updated {WEB_CASES_README.relative_to(BASE_DIR)}")


def main():
    counts = load_counts()
    print(
        f"Loaded counts: {counts['curated']} curated + "
        f"{counts['web']} web = {counts['total']} total"
    )

    print("\nUpdating README files...")
    for filename, lang in README_FILES.items():
        update_readme(filename, lang, counts)

    print("\nUpdating web-cases README...")
    update_web_cases_readme(counts)

    print("\nDone!")


if __name__ == "__main__":
    main()
