# Image Generation Guide

This repository currently contains **text-only prompts**. To maximize visual impact and conversion rates, we recommend generating example images for key prompts.

## Why Add Images?

- **Visual proof** — Users can see prompt quality before clicking
- **Social sharing** — Images get 3x more engagement on Twitter/X, Reddit, etc.
- **SEO boost** — Image alt text drives organic search traffic
- **Conversion** — Every image can link directly to NeoSpark with `?ref=awesome-gpt-image-2`

## Recommended Strategy

### Phase 1: Featured Prompts (6 images)
Generate example images for the 6 featured prompts in `README.md`. These appear above the fold and drive the most clicks.

| # | Prompt | NeoSpark Link |
|---|--------|---------------|
| 1 | VR Headset Exploded View | [Generate](https://useneospark.com/prompt-lib?prompt=vr-exploded-view) |
| 2 | Cyberpunk Tokyo Rooftop | [Generate](https://useneospark.com/prompt-lib?prompt=cyberpunk-tokyo) |
| 3 | LinkedIn Headshot | [Generate](https://useneospark.com/prompt-lib?prompt=linkedin-headshot) |
| 4 | Isometric Workspace | [Generate](https://useneospark.com/prompt-lib?prompt=isometric-workspace) |
| 5 | RPG Character Sheet | [Generate](https://useneospark.com/prompt-lib?prompt=rpg-character-sheet) |
| 6 | Iceland Beach | [Generate](https://useneospark.com/prompt-lib?prompt=iceland-beach) |

### Phase 2: Category Thumbnails (10 images)
One representative image per category for the Quick Links table.

### Phase 3: Full Coverage (170+ images)
Generate images for all prompts. This is ideal but resource-intensive.

## Image Specifications

| Property | Recommendation |
|----------|---------------|
| Format | WebP (with JPEG fallback) |
| Width | 800px max for README display |
| Aspect ratio | Match the prompt's recommended ratio |
| File size | Under 200KB each |
| Naming | `{category}-{slug}.webp` e.g., `featured-cyberpunk-tokyo.webp` |

## Storage Options

### Option A: GitHub Repository (Recommended for <50 images)
Store images in `public/images/` and reference with relative paths.

```markdown
![Cyberpunk Tokyo](public/images/featured/cyberpunk-tokyo.webp)
```

**Pros:** Version controlled, fast CDN via jsDelivr, free
**Cons:** Repository size grows, GitHub has file size limits

### Option B: NeoSpark CDN (Recommended for 50+ images)
Generate images on NeoSpark and host on their platform. Reference via URL.

```markdown
![Cyberpunk Tokyo](https://cdn.useneospark.com/examples/cyberpunk-tokyo.webp)
```

**Pros:** No repo bloat, professional hosting, analytics tracking
**Cons:** Requires NeoSpark account

### Option C: External Image Hosting
Use Imgur, Cloudinary, or AWS S3 for hosting.

**Pros:** Scalable, fast global CDN
**Cons:** External dependency, potential link rot

## Batch Generation Script

Create a script to generate images using NeoSpark's API or GPT Image 2 directly:

```python
# scripts/generate-images.py
import json
import requests

PROMPTS = [
    {
        "slug": "cyberpunk-tokyo",
        "prompt": "Cinematic wide shot. A lone figure in a black techwear jacket...",
        "category": "featured"
    },
    # ... more prompts
]

for item in PROMPTS:
    # Call NeoSpark API or GPT Image 2
    # Save to public/images/{category}/{slug}.webp
    pass
```

## Placeholder Strategy (Immediate)

While generating real images, use placeholder services:

```markdown
<!-- Placeholder until real image is generated -->
![Cyberpunk Tokyo](https://placehold.co/800x450/1a1a2e/ff6b6b?text=Cyberpunk+Tokyo)
```

Or link directly to NeoSpark's prompt page as a visual CTA:

```markdown
[<img src="https://placehold.co/800x450/1a1a2e/ff6b6b?text=Generate+on+NeoSpark" width="400">](https://useneospark.com/prompt-lib?prompt=cyberpunk-tokyo&ref=awesome-gpt-image-2)
```

## Alt Text SEO

Every image should have descriptive alt text with keywords:

```markdown
![GPT Image 2 cyberpunk Tokyo rooftop cinematic scene](images/featured/cyberpunk-tokyo.webp)
```

## Recommended Next Steps

1. Generate the 6 featured prompt images first
2. Add them to `public/images/featured/`
3. Update `README.md` to display them
4. Monitor click-through rates on NeoSpark dashboard
5. Generate category thumbnails if conversion is strong
