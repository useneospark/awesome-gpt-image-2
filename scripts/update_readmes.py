#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update all README files with web-cases collection references."""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Language-specific content
CONTENT = {
    "en": {
        "badge_old": "Prompts-280+-blue",
        "badge_new": "Prompts-743+-blue",
        "badge_alt_old": "280+ Prompts",
        "badge_alt_new": "743+ Prompts",
        "total_old": "**Total: 280+ production-ready prompts**",
        "total_new": "**Total: 743+ production-ready prompts** — 280 curated + 463 from web collection",
        "quick_links_end": "**Total: 280+ production-ready prompts**",
        "web_cases_note": (
            "\n> Looking for more? Check out the [Web Collection](prompts/web-cases/README.md) "
            "with **463 additional prompts** sourced from [gpt-image2.canghe.ai](https://gpt-image2.canghe.ai/).\n"
        ),
        "toc_insert": "- [Extended Collection](#extended-collection)\n",
        "extended_section": """
---

## Extended Collection

Looking for even more prompts? Browse the **[Web Collection](prompts/web-cases/README.md)** — **463 additional GPT Image 2 prompts** organized into 13 categories:

| Category | Prompts |
|----------|---------|
| UI & Interfaces | 73 |
| Posters & Typography | 73 |
| Photography & Realism | 59 |
| Charts & Infographics | 50 |
| Illustration & Art | 47 |
| Products & E-commerce | 35 |
| Other Use Cases | 28 |
| Brand & Logos | 23 |
| Characters & People | 21 |
| Scenes & Storytelling | 17 |
| History & Classical Themes | 16 |
| Architecture & Spaces | 11 |
| Documents & Publishing | 10 |

All prompts include full text, source attribution, and example images.

""",
    },
    "zh": {
        "badge_old": "提示词-280+-blue",
        "badge_new": "提示词-743+-blue",
        "badge_alt_old": "280+ 提示词",
        "badge_alt_new": "743+ 提示词",
        "total_old": "**总计：280+ 生产级提示词**",
        "total_new": "**总计：743+ 生产级提示词** — 280 个精选 + 463 个网络合集",
        "quick_links_end": "**总计：280+ 生产级提示词**",
        "web_cases_note": (
            "\n> 想要更多？查看 [网络合集](prompts/web-cases/README.md) "
            "，包含从 [gpt-image2.canghe.ai](https://gpt-image2.canghe.ai/) 获取的 **463 个额外提示词**。\n"
        ),
        "toc_insert": "- [扩展合集](#扩展合集)\n",
        "extended_section": """
---

## 扩展合集

想要更多提示词？浏览 **[网络合集](prompts/web-cases/README.md)** — 按 13 个分类整理的 **463 个额外 GPT Image 2 提示词**：

| 分类 | 提示词数量 |
|------|-----------|
| UI & 界面设计 | 73 |
| 海报与排版 | 73 |
| 摄影与写实 | 59 |
| 图表与信息图 | 50 |
| 插画与艺术 | 47 |
| 产品与电商 | 35 |
| 其他用例 | 28 |
| 品牌与 Logo | 23 |
| 角色与人物 | 21 |
| 场景与叙事 | 17 |
| 历史与古典主题 | 16 |
| 建筑与空间 | 11 |
| 文档与出版 | 10 |

所有提示词均包含完整文本、来源标注和示例图片。

---
""",
    },
    "ja": {
        "badge_old": "プロンプト-280+-blue",
        "badge_new": "プロンプト-743+-blue",
        "badge_alt_old": "280+ プロンプト",
        "badge_alt_new": "743+ プロンプト",
        # Japanese README doesn't have Quick Links, uses English content
        "total_old": None,
        "total_new": None,
        "quick_links_end": None,
        "web_cases_note": None,
        "toc_insert": "- [Extended Collection](#extended-collection)\n",
        "extended_section": """
---

## Extended Collection

Looking for even more prompts? Browse the **[Web Collection](prompts/web-cases/README.md)** — **463 additional GPT Image 2 prompts** organized into 13 categories:

| Category | Prompts |
|----------|---------|
| UI & Interfaces | 73 |
| Posters & Typography | 73 |
| Photography & Realism | 59 |
| Charts & Infographics | 50 |
| Illustration & Art | 47 |
| Products & E-commerce | 35 |
| Other Use Cases | 28 |
| Brand & Logos | 23 |
| Characters & People | 21 |
| Scenes & Storytelling | 17 |
| History & Classical Themes | 16 |
| Architecture & Spaces | 11 |
| Documents & Publishing | 10 |

All prompts include full text, source attribution, and example images.

""",
    },
    "ko": {
        "badge_old": "프롬프트-280+-blue",
        "badge_new": "프롬프트-743+-blue",
        "badge_alt_old": "280+ 프롬프트",
        "badge_alt_new": "743+ 프롬프트",
        "total_old": None,
        "total_new": None,
        "quick_links_end": None,
        "web_cases_note": None,
        "toc_insert": "- [Extended Collection](#extended-collection)\n",
        "extended_section": """
---

## Extended Collection

Looking for even more prompts? Browse the **[Web Collection](prompts/web-cases/README.md)** — **463 additional GPT Image 2 prompts** organized into 13 categories:

| Category | Prompts |
|----------|---------|
| UI & Interfaces | 73 |
| Posters & Typography | 73 |
| Photography & Realism | 59 |
| Charts & Infographics | 50 |
| Illustration & Art | 47 |
| Products & E-commerce | 35 |
| Other Use Cases | 28 |
| Brand & Logos | 23 |
| Characters & People | 21 |
| Scenes & Storytelling | 17 |
| History & Classical Themes | 16 |
| Architecture & Spaces | 11 |
| Documents & Publishing | 10 |

All prompts include full text, source attribution, and example images.

""",
    },
    "es": {
        "badge_old": "Prompts-280+-blue",
        "badge_new": "Prompts-743+-blue",
        "badge_alt_old": "280+ Prompts",
        "badge_alt_new": "743+ Prompts",
        "total_old": None,
        "total_new": None,
        "quick_links_end": None,
        "web_cases_note": None,
        "toc_insert": "- [Extended Collection](#extended-collection)\n",
        "extended_section": """
---

## Extended Collection

Looking for even more prompts? Browse the **[Web Collection](prompts/web-cases/README.md)** — **463 additional GPT Image 2 prompts** organized into 13 categories:

| Category | Prompts |
|----------|---------|
| UI & Interfaces | 73 |
| Posters & Typography | 73 |
| Photography & Realism | 59 |
| Charts & Infographics | 50 |
| Illustration & Art | 47 |
| Products & E-commerce | 35 |
| Other Use Cases | 28 |
| Brand & Logos | 23 |
| Characters & People | 21 |
| Scenes & Storytelling | 17 |
| History & Classical Themes | 16 |
| Architecture & Spaces | 11 |
| Documents & Publishing | 10 |

All prompts include full text, source attribution, and example images.

""",
    },
    "fr": {
        "badge_old": "Prompts-280+-blue",
        "badge_new": "Prompts-743+-blue",
        "badge_alt_old": "280+ Prompts",
        "badge_alt_new": "743+ Prompts",
        "total_old": None,
        "total_new": None,
        "quick_links_end": None,
        "web_cases_note": None,
        "toc_insert": "- [Extended Collection](#extended-collection)\n",
        "extended_section": """
---

## Extended Collection

Looking for even more prompts? Browse the **[Web Collection](prompts/web-cases/README.md)** — **463 additional GPT Image 2 prompts** organized into 13 categories:

| Category | Prompts |
|----------|---------|
| UI & Interfaces | 73 |
| Posters & Typography | 73 |
| Photography & Realism | 59 |
| Charts & Infographics | 50 |
| Illustration & Art | 47 |
| Products & E-commerce | 35 |
| Other Use Cases | 28 |
| Brand & Logos | 23 |
| Characters & People | 21 |
| Scenes & Storytelling | 17 |
| History & Classical Themes | 16 |
| Architecture & Spaces | 11 |
| Documents & Publishing | 10 |

All prompts include full text, source attribution, and example images.

""",
    },
    "de": {
        "badge_old": "Prompts-280+-blue",
        "badge_new": "Prompts-743+-blue",
        "badge_alt_old": "280+ Prompts",
        "badge_alt_new": "743+ Prompts",
        "total_old": None,
        "total_new": None,
        "quick_links_end": None,
        "web_cases_note": None,
        "toc_insert": "- [Extended Collection](#extended-collection)\n",
        "extended_section": """
---

## Extended Collection

Looking for even more prompts? Browse the **[Web Collection](prompts/web-cases/README.md)** — **463 additional GPT Image 2 prompts** organized into 13 categories:

| Category | Prompts |
|----------|---------|
| UI & Interfaces | 73 |
| Posters & Typography | 73 |
| Photography & Realism | 59 |
| Charts & Infographics | 50 |
| Illustration & Art | 47 |
| Products & E-commerce | 35 |
| Other Use Cases | 28 |
| Brand & Logos | 23 |
| Characters & People | 21 |
| Scenes & Storytelling | 17 |
| History & Classical Themes | 16 |
| Architecture & Spaces | 11 |
| Documents & Publishing | 10 |

All prompts include full text, source attribution, and example images.

""",
    },
}

FILES = {
    "README.md": "en",
    "README_zh.md": "zh",
    "README_ja.md": "ja",
    "README_ko.md": "ko",
    "README_es.md": "es",
    "README_fr.md": "fr",
    "README_de.md": "de",
}


def update_readme(filename: str, lang: str):
    """Update a single README file."""
    filepath = BASE_DIR / filename
    content = filepath.read_text(encoding="utf-8")
    c = CONTENT[lang]

    # 1. Update badge
    content = content.replace(c["badge_old"], c["badge_new"])
    content = content.replace(c["badge_alt_old"], c["badge_alt_new"])

    # 2. Add web cases note after Quick Links (before updating total count)
    if c["web_cases_note"] and c["quick_links_end"]:
        lines = content.split("\n")
        new_lines = []
        added_note = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if not added_note and c["quick_links_end"] in line:
                # Add the web cases note after this line
                new_lines.append("")
                new_lines.append(c["web_cases_note"].strip())
                added_note = True
        content = "\n".join(new_lines)

    # 3. Update total count line
    if c["total_old"] and c["total_old"] in content:
        content = content.replace(c["total_old"], c["total_new"])

    # 4. Add to Table of Contents
    # Insert before Prompt Engineering Tips / How to Contribute / License
    toc_insert = c["toc_insert"]
    if toc_insert.strip() not in content:
        # Find "- [Prompt Engineering Tips" or "- [How to Contribute" or "- [License"
        for marker in ["- [Prompt Engineering Tips", "- [How to Contribute", "- [License", "- [提示工程技巧", "- [如何贡献", "- [许可证"]:
            if marker in content:
                content = content.replace(marker, toc_insert + marker)
                break

    # 5. Add Extended Collection section before Prompt Engineering Tips / Powered by / License
    extended = c["extended_section"].strip()
    # Remove trailing --- from extended section since the target already has one
    if extended.endswith("---"):
        extended = extended[:-3].rstrip()
    if "## Extended Collection" not in content and "## 扩展合集" not in content:
        # Find a good place to insert - before Prompt Engineering Tips or License
        markers = [
            "\n---\n\n## Prompt Engineering Tips",
            "\n---\n\n## 提示工程技巧",
            "\n---\n\n## Powered by NeoSpark",
            "\n---\n\n## License",
            "\n---\n\n## 许可证",
        ]
        for marker in markers:
            if marker in content:
                content = content.replace(marker, "\n" + extended + "\n" + marker)
                break
        else:
            # If no marker found, append at the end before the final div
            if "</div>" in content and "## License" in content:
                # Find last "---" before License
                pass
            else:
                content = content.rstrip() + "\n" + extended + "\n"

    filepath.write_text(content, encoding="utf-8")
    print(f"  Updated {filename}")


def main():
    print("Updating README files...")
    for filename, lang in FILES.items():
        update_readme(filename, lang)
    print("Done!")


if __name__ == "__main__":
    main()
