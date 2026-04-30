#!/usr/bin/env python3
"""
Generate example images for featured prompts using NeoSpark Image Generation API.

Usage:
    export NEOSPARK_API_KEY="np_xxxxx"
    python scripts/generate-images.py

Or:
    python scripts/generate-images.py --api-key np_xxxxx
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://api.useneospark.com/api/v1"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "images" / "featured"

FEATURED_PROMPTS = [
    {
        "slug": "vr-exploded-view",
        "title": "VR Headset Exploded View",
        "prompt": "A premium product poster, vertical 3:4 layout. Center: an exploded view of a futuristic VR headset with each component floating in perfect alignment — lenses, display panel, circuit board, battery pack, head strap. Clean white background with subtle gradient. Each component labeled with thin lines and minimal sans-serif text. Soft studio lighting from above, slight shadow beneath each piece. Professional product photography style, ultra-sharp detail, Apple-level presentation quality.",
        "aspect_ratio": "3:4",
        "width": 450,
        "height": 600,
    },
    {
        "slug": "cyberpunk-tokyo",
        "title": "Cyberpunk Tokyo Rooftop",
        "prompt": "Cinematic wide shot. A lone figure in a black techwear jacket stands on a rain-slicked Tokyo rooftop at midnight. Neon signs in Japanese and English reflect in puddles — pink, cyan, electric blue. Distant holographic advertisements float between skyscrapers. Light rain falling, captured as streaks. Shot on anamorphic lens, 2.39:1 widescreen, film grain, teal shadows and magenta highlights. Blade Runner 2049 aesthetic.",
        "aspect_ratio": "16:9",
        "width": 600,
        "height": 338,
    },
    {
        "slug": "linkedin-headshot",
        "title": "Professional LinkedIn Headshot",
        "prompt": "Professional medium-shot portrait of a confident woman in her early 30s wearing a tailored navy blue blazer over a cream silk blouse. Neutral grey studio background. Soft three-point lighting: key light from camera-left at 45 degrees, fill at -2 stops, hair light from behind. Shot on 85mm lens at f/2.8, sharp focus on eyes with shallow depth of field. Natural skin texture with visible pores, no beauty filter. Warm color temperature at 3200K. Corporate yet approachable expression.",
        "aspect_ratio": "3:4",
        "width": 450,
        "height": 600,
    },
    {
        "slug": "isometric-workspace",
        "title": "Isometric 3D Workspace",
        "prompt": "A 45-degree isometric miniature 3D scene of a modern designer's workspace diorama on a light wood display base. A sleek iMac, wireless keyboard, potted monstera plant, coffee cup, and design books arranged neatly. Soft PBR textures, realistic materials, clean unified composition. Pastel color palette dominated by sage green and warm cream. Studio softbox lighting, subtle ambient occlusion. Square 1:1 frame, centered subject, plenty of negative space. Clay-render aesthetic.",
        "aspect_ratio": "1:1",
        "width": 500,
        "height": 500,
    },
    {
        "slug": "rpg-character-sheet",
        "title": "Fantasy RPG Character Sheet",
        "prompt": "A professional character reference sheet for an original fantasy RPG character: a young female mage with silver-white hair and violet eyes, wearing an ornate dark cloak with glowing teal rune patterns. On a clean white background: three-view turnaround showing front, side, and back; facial expression variations (neutral, smiling, angry, surprised); detailed costume breakdown; color palette swatches; brief world-building notes in clean typography. Organized grid layout, concept art style, high resolution. Aspect ratio 16:9.",
        "aspect_ratio": "16:9",
        "width": 600,
        "height": 338,
    },
    {
        "slug": "iceland-beach",
        "title": "Iceland Black Sand Beach",
        "prompt": "Dramatic wide landscape of Iceland's Reynisfjara black sand beach at dawn. Massive basalt sea stacks rise from the churning North Atlantic. Low fog drifts across the black volcanic sand. A single figure in a bright red rain jacket walks along the shoreline for scale. Moody desaturated color grade — almost monochrome with just the red jacket as accent. 24mm wide lens, f/11 for deep focus. Ultra-detailed 4K, National Geographic quality.",
        "aspect_ratio": "16:9",
        "width": 600,
        "height": 338,
    },
]


def get_headers(api_key: str) -> dict:
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }


def create_session(api_key: str, title: str) -> str:
    """Create a drawing session and return session_id."""
    url = f"{BASE_URL}/drawing/sessions"
    resp = requests.post(url, headers=get_headers(api_key), json={"title": title})
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Failed to create session: {data}")
    return data["data"]["session_id"]


def submit_generation(
    api_key: str,
    session_id: str,
    prompt: str,
    aspect_ratio: str,
    model: str = "gpt-image-2",
    provider: str = "tengda",
    resolution: str = "1K",
    quality: str = "standard",
    num_images: int = 1,
) -> str:
    """Submit generation task and return message_id."""
    url = f"{BASE_URL}/drawing/sessions/{session_id}/generate"
    payload = {
        "prompt": prompt,
        "model": model,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "negative_prompt": "blurry, low quality, distorted, deformed",
        "num_images": num_images,
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
    """Poll message status until completed or failed."""
    url = f"{BASE_URL}/drawing/messages/{message_id}"
    for attempt in range(max_retries):
        resp = requests.get(url, headers={"X-API-Key": api_key})
        resp.raise_for_status()
        data = resp.json()
        result = data.get("data", {})
        status = result.get("status")
        print(f"  Poll {attempt + 1}/{max_retries}: status={status}")
        if status == "completed":
            return result
        if status == "failed":
            raise RuntimeError(f"Generation failed: {result.get('error_msg', 'Unknown error')}")
        time.sleep(poll_interval)
    raise RuntimeError(f"Polling timed out after {max_retries} attempts")


def download_image(image_url: str, output_path: Path) -> None:
    """Download image from URL to local path."""
    if image_url.startswith("/"):
        image_url = f"https://api.useneospark.com{image_url}"
    resp = requests.get(image_url, stream=True)
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  Saved to {output_path}")


def generate_single_image(
    api_key: str,
    item: dict,
    quality: str = "standard",
) -> Path | None:
    """Generate one featured image. Returns the saved image path or None on failure."""
    print(f"\n{'=' * 60}")
    print(f"Generating: {item['title']}")
    print(f"Aspect ratio: {item['aspect_ratio']}")
    print(f"Quality: {quality}")

    try:
        session_id = create_session(api_key, item["title"])
        print(f"  Session created: {session_id}")

        message_id = submit_generation(
            api_key=api_key,
            session_id=session_id,
            prompt=item["prompt"],
            aspect_ratio=item["aspect_ratio"],
            quality=quality,
        )
        print(f"  Message ID: {message_id}")

        result = poll_message(api_key, message_id)
        images = result.get("images", [])
        if not images:
            print(f"  WARNING: No images returned for {item['title']}")
            return None

        image_url = images[0]["url"]
        ext = Path(image_url).suffix or ".png"
        output_path = OUTPUT_DIR / f"featured-{item['slug']}{ext}"
        download_image(image_url, output_path)

        actual_cost = result.get("actual_cost", "N/A")
        print(f"  Cost: {actual_cost} points")
        return output_path

    except Exception as e:
        print(f"  ERROR generating {item['title']}: {e}")
        return None


def update_readme(image_map: dict[str, Path]) -> None:
    """Update README.md to reference local generated images instead of placehold.co."""
    readme_path = Path(__file__).parent.parent / "README.md"
    if not readme_path.exists():
        print(f"README.md not found at {readme_path}, skipping update")
        return

    content = readme_path.read_text(encoding="utf-8")
    original = content

    for slug, img_path in image_map.items():
        rel_path = img_path.relative_to(img_path.parent.parent.parent).as_posix()
        # Replace placehold.co image for this slug
        old_pattern = f"https://placehold.co/600x400/[^\"']+?{slug.replace('-', '+')}[^\"']*?"
        # Use a more robust replacement: find the <img> tag containing this slug in its href context
        # We look for the <a> block wrapping the <img> for this slug
        import re
        # Match the <a> tag with href containing the slug, and replace the img src inside it
        pattern = (
            rf'(<a href="https://useneospark\.com/prompt-lib\?prompt={slug}[^"]*">\s*<img src=")'
            rf'https://placehold\.co/[^"]+'
            rf'(" alt="[^"]+" width="\d+">\s*</a>)'
        )
        replacement = rf'\g<1>{rel_path}\g<2>'
        content, count = re.subn(pattern, replacement, content, count=1)
        if count:
            print(f"  Updated README.md: {slug} -> {rel_path}")
        else:
            print(f"  WARNING: Could not find placeholder to replace for {slug}")

    if content != original:
        readme_path.write_text(content, encoding="utf-8")
        print("\nREADME.md updated successfully.")
    else:
        print("\nNo changes made to README.md.")


def main():
    parser = argparse.ArgumentParser(description="Generate featured prompt images via NeoSpark API")
    parser.add_argument("--api-key", default=os.environ.get("NEOSPARK_API_KEY"), help="NeoSpark API key (or set NEOSPARK_API_KEY env var)")
    parser.add_argument("--quality", default="standard", choices=["standard", "high"], help="Image quality (standard=4pts, high=7pts)")
    parser.add_argument("--slug", help="Generate only a single prompt by slug (e.g. cyberpunk-tokyo)")
    parser.add_argument("--skip-readme", action="store_true", help="Do not update README.md after generation")
    args = parser.parse_args()

    if not args.api_key:
        print("Error: API key required. Use --api-key or set NEOSPARK_API_KEY environment variable.")
        sys.exit(1)

    if args.api_key.startswith("np_"):
        masked = args.api_key[:7] + "****" + args.api_key[-4:]
    else:
        masked = args.api_key[:4] + "****"
    print(f"Using API key: {masked}")

    prompts_to_generate = FEATURED_PROMPTS
    if args.slug:
        prompts_to_generate = [p for p in FEATURED_PROMPTS if p["slug"] == args.slug]
        if not prompts_to_generate:
            print(f"Error: No prompt found with slug '{args.slug}'")
            sys.exit(1)

    print(f"\nGenerating {len(prompts_to_generate)} featured image(s)...")
    print(f"Output directory: {OUTPUT_DIR}")

    image_map: dict[str, Path] = {}
    for item in prompts_to_generate:
        img_path = generate_single_image(args.api_key, item, quality=args.quality)
        if img_path:
            image_map[item["slug"]] = img_path

    print(f"\n{'=' * 60}")
    print(f"Generation complete. {len(image_map)}/{len(prompts_to_generate)} images saved.")

    if image_map and not args.skip_readme:
        print("\nUpdating README.md...")
        update_readme(image_map)

    if len(image_map) < len(prompts_to_generate):
        sys.exit(1)


if __name__ == "__main__":
    main()
