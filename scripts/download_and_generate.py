#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download case images and generate Markdown files from cases.json"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent.parent
CASES_JSON = BASE_DIR / "cases.json"
IMAGES_DIR = BASE_DIR / "public" / "images" / "cases"
PROMPTS_DIR = BASE_DIR / "prompts" / "web-cases"
BASE_URL = "https://gpt-image2.canghe.ai"

# Category mapping: cases.json category -> directory name
CATEGORY_SLUGS = {
    "Architecture & Spaces": "architecture",
    "Brand & Logos": "brand-logos",
    "Characters & People": "characters-people",
    "Charts & Infographics": "charts-infographics",
    "Documents & Publishing": "documents-publishing",
    "History & Classical Themes": "history-classical",
    "Illustration & Art": "illustration-art",
    "Other Use Cases": "other",
    "Photography & Realism": "photography-realism",
    "Posters & Typography": "posters-typography",
    "Products & E-commerce": "products-ecommerce",
    "Scenes & Storytelling": "scenes-storytelling",
    "UI & Interfaces": "ui-interfaces",
}


def download_image(case_id: int) -> bool:
    """Download a single case image."""
    image_name = f"case{case_id}.jpg"
    image_path = IMAGES_DIR / image_name

    if image_path.exists():
        return True  # Already downloaded

    url = f"{BASE_URL}/images/{image_name}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"  Failed to download case{case_id}.jpg (status {response.status_code})")
            return False
    except Exception as e:
        print(f"  Error downloading case{case_id}.jpg: {e}")
        return False


def download_all_images(cases: list, max_workers: int = 10) -> dict:
    """Download all case images concurrently."""
    print(f"Downloading {len(cases)} images to {IMAGES_DIR}...")
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    results = {"success": 0, "failed": 0, "skipped": 0}
    case_ids = [c["id"] for c in cases]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(download_image, cid): cid for cid in case_ids}
        for i, future in enumerate(as_completed(future_to_id)):
            cid = future_to_id[future]
            success = future.result()
            image_path = IMAGES_DIR / f"case{cid}.jpg"
            if success and image_path.exists():
                if image_path.stat().st_size > 0:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            elif image_path.exists():
                results["skipped"] += 1
            else:
                results["failed"] += 1

            if (i + 1) % 50 == 0:
                print(f"  Progress: {i + 1}/{len(case_ids)} done")

    print(f"Download complete: {results['success']} success, {results['failed']} failed, {results['skipped']} skipped")
    return results


def generate_markdown_files(cases: list):
    """Generate Markdown files organized by category."""
    print("\nGenerating Markdown files...")
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

    # Group cases by category
    by_category = {}
    for case in cases:
        cat = case["category"]
        by_category.setdefault(cat, []).append(case)

    for cat, cat_cases in by_category.items():
        slug = CATEGORY_SLUGS.get(cat, cat.lower().replace(" ", "-").replace("&", "and"))
        md_path = PROMPTS_DIR / f"{slug}.md"

        lines = [
            f"# {cat} Prompts",
            "",
            f"A collection of {len(cat_cases)} GPT Image 2 prompts for {cat.lower()}.",
            "",
            "| # | Title | Image |",
            "|---|-------|-------|",
        ]

        for case in cat_cases:
            case_id = case["id"]
            title = case["title"].replace("|", "\\|")
            image_ext = case["image"].split(".")[-1]
            image_path = f"/public/images/cases/case{case_id}.{image_ext}"
            lines.append(f"| {case_id} | {title} | ![{title}]({image_path}) |")

        lines.extend([
            "",
            "## Prompts",
            "",
        ])

        for case in cat_cases:
            case_id = case["id"]
            title = case["title"]
            prompt = case["prompt"]
            image_ext = case["image"].split(".")[-1]
            image_path = f"/public/images/cases/case{case_id}.{image_ext}"

            lines.extend([
                f"### {title}",
                "",
                f"**Source:** {case.get('sourceLabel', 'Unknown')} - [{case.get('sourceUrl', '#')}]({case.get('sourceUrl', '#')})",
                "",
                f"![{title}]({image_path})",
                "",
                "> " + prompt.replace("\n", "\n> "),
                "",
            ])

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"  Written {md_path} ({len(cat_cases)} prompts)")

    print(f"Generated {len(by_category)} Markdown files in {PROMPTS_DIR}")


def main():
    if not CASES_JSON.exists():
        print(f"Error: {CASES_JSON} not found")
        sys.exit(1)

    with open(CASES_JSON, encoding="utf-8") as f:
        data = json.load(f)

    cases = data["cases"]
    print(f"Loaded {len(cases)} cases from {CASES_JSON}")
    print(f"Categories: {data['categories']}")

    # Download images
    download_all_images(cases, max_workers=15)

    # Generate Markdown files
    generate_markdown_files(cases)

    print("\nDone!")


if __name__ == "__main__":
    main()
