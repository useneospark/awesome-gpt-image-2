#!/usr/bin/env python3
"""
Batch generate images for ALL prompts in the repository.

Usage:
    export NEOSPARK_API_KEY="np_xxxxx"
    python scripts/generate-all-images.py

Options:
    --category CATEGORY   Generate only one category (e.g. cinematic)
    --resume              Skip already-generated images
    --quality {standard,high}
    --limit N             Stop after N images (for testing)
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://api.useneospark.com/api/v1"
ROOT = Path(__file__).parent.parent
OUTPUT_ROOT = ROOT / "public" / "images"
PROGRESS_FILE = ROOT / ".generation-progress.json"

# Map category folder/name to aspect ratio
CATEGORY_ASPECT_RATIOS = {
    "featured": "1:1",
    "cinematic": "16:9",
    "portraits": "3:4",
    "product": "1:1",
    "ui-design": "9:16",
    "fantasy": "16:9",
    "nature": "16:9",
    "marketing": "1:1",
    "typography": "3:4",
    "architecture": "16:9",
    "experimental": "1:1",
    # additional sub-categories
    "text-rendering": "1:1",
    "cinematic-scenes": "16:9",
    "character-design": "3:4",
    "posters-illustration": "3:4",
    "portraits-extended": "3:4",
    "ui-social-extended": "9:16",
    "product-extended": "1:1",
    "community-creative": "1:1",
}


def slugify(text: str) -> str:
    """Convert title to URL-safe slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")[:60]


def extract_prompts_from_markdown(file_path: Path) -> list[dict]:
    """Parse a markdown file and extract all prompt blocks."""
    content = file_path.read_text(encoding="utf-8")
    prompts = []
    # Match ### Title followed by > prompt text
    pattern = r"#{3,4}\s+(.+?)\n\n>\s+(.+?)(?=\n\n|\n#{2,4}\s|\n---|\Z)"
    for match in re.finditer(pattern, content, re.DOTALL):
        title = match.group(1).strip()
        prompt_text = match.group(2).strip().replace("\n", " ")
        # Remove markdown bold/italic
        prompt_text = re.sub(r"\*\*|__|\*|_", "", prompt_text)
        prompts.append({"title": title, "prompt": prompt_text})
    return prompts


def discover_all_prompts() -> list[dict]:
    """Scan all prompt files and return flat list with category info."""
    all_items = []

    # Main categories
    main_dirs = [
        "prompts/featured",
        "prompts/cinematic",
        "prompts/portraits",
        "prompts/product",
        "prompts/ui-design",
        "prompts/fantasy",
        "prompts/nature",
        "prompts/marketing",
        "prompts/typography",
        "prompts/architecture",
        "prompts/experimental",
    ]
    for dir_path in main_dirs:
        readme = ROOT / dir_path / "README.md"
        if readme.exists():
            category = Path(dir_path).name
            for p in extract_prompts_from_markdown(readme):
                all_items.append({
                    "category": category,
                    "slug": slugify(p["title"]),
                    "title": p["title"],
                    "prompt": p["prompt"],
                    "aspect_ratio": CATEGORY_ASPECT_RATIOS.get(category, "1:1"),
                })

    # Additional prompts
    additional_dir = ROOT / "prompts" / "additional"
    if additional_dir.exists():
        for md_file in sorted(additional_dir.glob("*.md")):
            if md_file.name == "README.md":
                continue
            category = md_file.stem
            for p in extract_prompts_from_markdown(md_file):
                all_items.append({
                    "category": f"additional-{category}",
                    "slug": slugify(p["title"]),
                    "title": p["title"],
                    "prompt": p["prompt"],
                    "aspect_ratio": CATEGORY_ASPECT_RATIOS.get(category, "1:1"),
                })

    return all_items


def get_headers(api_key: str) -> dict:
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }


def create_session(api_key: str, title: str) -> str:
    url = f"{BASE_URL}/drawing/sessions"
    resp = requests.post(url, headers=get_headers(api_key), json={"title": title})
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Failed to create session: {data}")
    return data["data"]["session_id"]


def submit_generation(api_key: str, session_id: str, prompt: str, aspect_ratio: str,
                      model: str = "gpt-image-2", provider: str = "tengda",
                      resolution: str = "1K", quality: str = "standard") -> str:
    url = f"{BASE_URL}/drawing/sessions/{session_id}/generate"
    payload = {
        "prompt": prompt,
        "model": model,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "negative_prompt": "blurry, low quality, distorted, deformed",
        "num_images": 1,
        "provider": provider,
        "quality": quality,
        "optimize_prompt": True,
    }
    resp = requests.post(url, headers=get_headers(api_key), json=payload)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Failed to submit generation: {data}")
    return data["data"]["message_id"]


def poll_message(api_key: str, message_id: str, poll_interval: int = 5, max_retries: int = 60) -> dict:
    url = f"{BASE_URL}/drawing/messages/{message_id}"
    for attempt in range(max_retries):
        resp = requests.get(url, headers={"X-API-Key": api_key})
        resp.raise_for_status()
        data = resp.json()
        result = data.get("data", {})
        status = result.get("status")
        if status == "completed":
            return result
        if status == "failed":
            raise RuntimeError(f"Generation failed: {result.get('error_msg', 'Unknown error')}")
        time.sleep(poll_interval)
    raise RuntimeError(f"Polling timed out after {max_retries} attempts")


def download_image(image_url: str, output_path: Path) -> None:
    if image_url.startswith("/"):
        image_url = f"https://api.useneospark.com{image_url}"
    resp = requests.get(image_url, stream=True)
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def load_progress() -> set[str]:
    if PROGRESS_FILE.exists():
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return set(data.get("completed", []))
    return set()


def save_progress(completed: set[str]) -> None:
    PROGRESS_FILE.write_text(json.dumps({"completed": sorted(completed)}, indent=2), encoding="utf-8")


def generate_for_item(api_key: str, item: dict, session_id: str, quality: str) -> Path | None:
    category = item["category"]
    slug = item["slug"]
    output_dir = OUTPUT_ROOT / category.replace("additional-", "")
    output_path = output_dir / f"{slug}.png"

    if output_path.exists():
        print(f"  [SKIP] Already exists: {output_path}")
        return output_path

    try:
        message_id = submit_generation(
            api_key=api_key,
            session_id=session_id,
            prompt=item["prompt"],
            aspect_ratio=item["aspect_ratio"],
            quality=quality,
        )
        result = poll_message(api_key, message_id)
        images = result.get("images", [])
        if not images:
            print(f"  [WARN] No images for: {item['title']}")
            return None

        download_image(images[0]["url"], output_path)
        cost = result.get("actual_cost", "?")
        print(f"  [OK] Saved ({cost}pt): {output_path.name}")
        return output_path

    except Exception as e:
        print(f"  [ERR] {item['title']}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Batch generate all prompt images")
    parser.add_argument("--api-key", default=os.environ.get("NEOSPARK_API_KEY"))
    parser.add_argument("--quality", default="standard", choices=["standard", "high"])
    parser.add_argument("--category", help="Only generate this category (e.g. cinematic, portraits)")
    parser.add_argument("--resume", action="store_true", help="Skip already generated images")
    parser.add_argument("--limit", type=int, help="Stop after N images (for testing)")
    args = parser.parse_args()

    if not args.api_key:
        print("Error: API key required. Use --api-key or set NEOSPARK_API_KEY env var.")
        sys.exit(1)

    all_items = discover_all_prompts()
    print(f"Discovered {len(all_items)} total prompts")

    # Filter by category if specified
    if args.category:
        all_items = [i for i in all_items if args.category in i["category"]]
        print(f"Filtered to {len(all_items)} prompts in category '{args.category}'")

    # Load progress
    completed = load_progress() if args.resume else set()
    if completed:
        print(f"Resuming: {len(completed)} already completed")

    # Group by category for session reuse
    by_category: dict[str, list[dict]] = {}
    for item in all_items:
        by_category.setdefault(item["category"], []).append(item)

    total = len(all_items)
    success_count = 0
    fail_count = 0
    skipped = 0

    try:
        for category, items in by_category.items():
            print(f"\n{'=' * 60}")
            print(f"Category: {category} ({len(items)} prompts)")

            # Create one session per category
            try:
                session_id = create_session(args.api_key, f"Batch: {category}")
                print(f"Session: {session_id}")
            except Exception as e:
                print(f"Failed to create session for {category}: {e}")
                fail_count += len(items)
                continue

            for item in items:
                key = f"{item['category']}/{item['slug']}"
                if key in completed:
                    skipped += 1
                    continue

                if args.limit and (success_count + fail_count + skipped) >= args.limit:
                    print(f"\nReached limit of {args.limit} images. Stopping.")
                    raise KeyboardInterrupt

                img_path = generate_for_item(args.api_key, item, session_id, args.quality)
                if img_path:
                    completed.add(key)
                    success_count += 1
                else:
                    fail_count += 1

                save_progress(completed)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    print(f"\n{'=' * 60}")
    print(f"Done: {success_count} success, {fail_count} failed, {skipped} skipped")
    print(f"Total generated: {success_count + skipped}/{total}")
    print(f"Estimated cost: {(success_count * (4 if args.quality == 'standard' else 7))} points")


if __name__ == "__main__":
    main()
