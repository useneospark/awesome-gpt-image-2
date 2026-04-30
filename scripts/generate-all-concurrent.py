#!/usr/bin/env python3
"""
Concurrent batch image generation for ALL prompts.
Submits multiple generation requests in parallel within one session,
then polls all message IDs concurrently.

Usage:
    export NEOSPARK_API_KEY="np_xxxxx"
    python scripts/generate-all-concurrent.py

Options:
    --workers N       Concurrent generate submissions (default: 5)
    --quality {standard,high}
    --category CAT    Only one category
    --resume          Skip already generated
"""

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

BASE_URL = "https://api.useneospark.com/api/v1"
ROOT = Path(__file__).parent.parent
OUTPUT_ROOT = ROOT / "public" / "images"
PROGRESS_FILE = ROOT / ".generation-progress.json"

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
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")[:60]


def extract_prompts_from_markdown(file_path: Path) -> list[dict]:
    content = file_path.read_text(encoding="utf-8")
    prompts = []
    pattern = r"#{3,4}\s+(.+?)\n\n>\s+(.+?)(?=\n\n|\n#{2,4}\s|\n---|\Z)"
    for match in re.finditer(pattern, content, re.DOTALL):
        title = match.group(1).strip()
        prompt_text = match.group(2).strip().replace("\n", " ")
        prompt_text = re.sub(r"\*\*|__|\*|_", "", prompt_text)
        prompts.append({"title": title, "prompt": prompt_text})
    return prompts


def discover_all_prompts() -> list[dict]:
    all_items = []
    main_dirs = [
        "prompts/featured", "prompts/cinematic", "prompts/portraits",
        "prompts/product", "prompts/ui-design", "prompts/fantasy",
        "prompts/nature", "prompts/marketing", "prompts/typography",
        "prompts/architecture", "prompts/experimental",
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
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


def create_session(api_key: str, title: str) -> str:
    url = f"{BASE_URL}/drawing/sessions"
    resp = requests.post(url, headers=get_headers(api_key), json={"title": title})
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Failed to create session: {data}")
    return data["data"]["session_id"]


def submit_generation(api_key: str, session_id: str, prompt: str, aspect_ratio: str,
                      quality: str = "standard") -> str:
    url = f"{BASE_URL}/drawing/sessions/{session_id}/generate"
    payload = {
        "prompt": prompt,
        "model": "gpt-image-2",
        "resolution": "1K",
        "aspect_ratio": aspect_ratio,
        "negative_prompt": "blurry, low quality, distorted, deformed",
        "num_images": 1,
        "provider": "tengda",
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


def generate_one(api_key: str, session_id: str, item: dict, quality: str) -> tuple[str, Path | None]:
    """Worker: submit + poll + download one image. Returns (key, path or None)."""
    key = f"{item['category']}/{item['slug']}"
    category = item["category"]
    slug = item["slug"]
    output_dir = OUTPUT_ROOT / category.replace("additional-", "")
    output_path = output_dir / f"{slug}.png"

    if output_path.exists():
        return key, output_path

    try:
        message_id = submit_generation(
            api_key, session_id, item["prompt"], item["aspect_ratio"], quality
        )
        result = poll_message(api_key, message_id)
        images = result.get("images", [])
        if not images:
            return key, None
        download_image(images[0]["url"], output_path)
        cost = result.get("actual_cost", "?")
        print(f"  [OK] {category}/{slug} ({cost}pt)")
        return key, output_path
    except Exception as e:
        print(f"  [ERR] {category}/{slug}: {e}")
        return key, None


def process_batch(api_key: str, session_id: str, items: list[dict], quality: str, workers: int) -> dict[str, Path | None]:
    """Process a batch of items concurrently."""
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(generate_one, api_key, session_id, item, quality): item
            for item in items
        }
        for future in as_completed(futures):
            item = futures[future]
            try:
                key, path = future.result()
                results[key] = path
            except Exception as e:
                print(f"  [ERR] {item['category']}/{item['slug']}: {e}")
                results[f"{item['category']}/{item['slug']}"] = None
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=os.environ.get("NEOSPARK_API_KEY"))
    parser.add_argument("--quality", default="standard", choices=["standard", "high"])
    parser.add_argument("--category")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent submissions")
    args = parser.parse_args()

    if not args.api_key:
        print("Error: API key required")
        sys.exit(1)

    all_items = discover_all_prompts()
    print(f"Discovered {len(all_items)} total prompts")

    if args.category:
        all_items = [i for i in all_items if args.category in i["category"]]
        print(f"Filtered to {len(all_items)} prompts in '{args.category}'")

    completed = load_progress() if args.resume else set()
    if completed:
        print(f"Resuming: {len(completed)} already done")

    # Filter out completed
    pending = [i for i in all_items if f"{i['category']}/{i['slug']}" not in completed]
    print(f"Pending: {len(pending)} images to generate")
    print(f"Workers: {args.workers} concurrent")
    print(f"Estimated time: ~{len(pending) * 50 // args.workers // 60} minutes")

    if not pending:
        print("Nothing to generate!")
        return

    # Group by category, process category by category
    by_category: dict[str, list[dict]] = {}
    for item in pending:
        by_category.setdefault(item["category"], []).append(item)

    total_success = 0
    total_fail = 0

    try:
        for category, items in by_category.items():
            print(f"\n{'=' * 60}")
            print(f"Category: {category} ({len(items)} prompts)")

            try:
                session_id = create_session(args.api_key, f"Batch: {category}")
                print(f"Session: {session_id}")
            except Exception as e:
                print(f"Failed to create session: {e}")
                total_fail += len(items)
                continue

            # Split into batches of 'workers' size
            batch_size = args.workers
            for batch_idx in range(0, len(items), batch_size):
                batch = items[batch_idx:batch_idx + batch_size]
                print(f"  Batch {batch_idx // batch_size + 1}/{(len(items) + batch_size - 1) // batch_size} ({len(batch)} items)")

                results = process_batch(args.api_key, session_id, batch, args.quality, args.workers)

                for key, path in results.items():
                    if path:
                        completed.add(key)
                        total_success += 1
                    else:
                        total_fail += 1

                save_progress(completed)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    print(f"\n{'=' * 60}")
    print(f"Done: {total_success} success, {total_fail} failed")
    print(f"Total: {len(completed)}/{len(all_items)}")
    pts = 4 if args.quality == "standard" else 7
    print(f"Estimated cost this run: {total_success * pts} points")


if __name__ == "__main__":
    main()
