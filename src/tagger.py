#!/usr/bin/env python3
"""
Auto-Tagger for Nano Banana Prompts
Scans all prompts and assigns structured tags for style, use-case, subject, and mood.
Outputs a tagged JSON index for fast filtering.
"""

import csv
import json
import sys
import re
import argparse
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "prompts" / "database.csv"
TAGS_CACHE = Path(__file__).parent.parent / "prompts" / ".cache" / "tags.json"

STYLE_RULES = {
    "photography": ["photo", "photograph", "camera", "lens", "f/", "dslr", "shot on", "canon", "nikon", "fujifilm", "sony", "hasselblad"],
    "cinematic": ["cinematic", "film still", "movie scene", "anamorphic", "widescreen", "film grain"],
    "anime": ["anime", "manga", "japanese animation", "cel-shaded", "studio ghibli", "shonen", "shoujo"],
    "illustration": ["illustration", "illustrated", "digital art", "concept art", "hand-drawn", "digital painting"],
    "3d-render": ["3d render", "3d model", "blender", "octane", "unreal engine", "c4d", "cinema 4d", "ray tracing"],
    "pixel-art": ["pixel art", "pixelated", "8-bit", "16-bit", "retro game", "sprite"],
    "watercolor": ["watercolor", "watercolour", "aquarelle", "wet media", "watercolor painting"],
    "oil-painting": ["oil painting", "oil on canvas", "impasto", "brushstroke", "classical painting"],
    "minimalist": ["minimalist", "minimal", "clean design", "simple", "negative space", "flat design"],
    "cyberpunk": ["cyberpunk", "neon", "dystopian", "holographic", "futuristic city"],
    "retro": ["retro", "vintage", "nostalgia", "old-school", "analog", "70s", "80s", "90s"],
    "sketch": ["sketch", "line art", "pencil", "charcoal", "drawing", "ink drawing"],
    "isometric": ["isometric", "diorama", "tilt-shift", "miniature"],
    "chibi": ["chibi", "kawaii", "q-style", "cute character", "super deformed"],
    "surreal": ["surreal", "surrealism", "dreamlike", "impossible", "dali", "escher"],
    "pop-art": ["pop art", "andy warhol", "comic book", "halftone", "bold colors"],
    "gothic": ["gothic", "dark fantasy", "macabre", "dark aesthetic"],
    "steampunk": ["steampunk", "clockwork", "victorian", "brass", "gears"],
    "vaporwave": ["vaporwave", "synthwave", "retrowave", "neon grid", "aesthetic"],
    "art-nouveau": ["art nouveau", "art deco", "mucha", "ornamental"],
}

USECASE_RULES = {
    "product-marketing": ["product", "commercial", "advertisement", "brand", "packaging", "marketing", "mockup"],
    "social-media": ["social media", "instagram", "twitter", "tiktok", "post", "story", "feed", "reel"],
    "youtube-thumbnail": ["youtube", "thumbnail", "video cover", "clickbait"],
    "profile-avatar": ["profile", "avatar", "headshot", "pfp", "profile picture"],
    "poster-flyer": ["poster", "flyer", "banner", "billboard", "signage", "placard"],
    "infographic": ["infographic", "diagram", "chart", "educational", "data viz", "flowchart", "timeline"],
    "ecommerce": ["ecommerce", "e-commerce", "product listing", "shop", "store", "amazon", "listing"],
    "game-asset": ["game", "game asset", "sprite", "character design", "weapon design", "rpg"],
    "storyboard": ["storyboard", "comic", "panel", "sequence", "narrative", "comic strip"],
    "app-design": ["app", "ui design", "ux", "interface", "web design", "wireframe", "dashboard"],
    "logo": ["logo", "brand mark", "emblem", "icon design", "wordmark", "monogram"],
    "fashion": ["fashion", "outfit", "clothing", "apparel", "runway", "editorial fashion"],
    "food": ["food", "drink", "beverage", "recipe", "culinary", "restaurant", "cafe"],
    "architecture": ["architecture", "interior", "building", "room design", "house", "office space"],
    "landscape": ["landscape", "nature", "scenery", "mountain", "ocean", "forest", "sunset"],
    "typography": ["typography", "text design", "lettering", "font", "calligraphy", "type"],
    "quote-card": ["quote", "motivational", "inspirational", "verse", "saying"],
    "meme": ["meme", "funny", "humor", "reaction", "viral"],
    "wallpaper": ["wallpaper", "desktop", "phone wallpaper", "background"],
}

SUBJECT_RULES = {
    "portrait": ["portrait", "face", "headshot", "selfie", "close-up face"],
    "character": ["character", "oc", "original character", "fictional", "fantasy character"],
    "product": ["product", "item", "object", "device", "gadget", "bottle", "jar", "package"],
    "animal": ["animal", "creature", "pet", "dog", "cat", "bird", "wildlife", "dragon"],
    "vehicle": ["vehicle", "car", "motorcycle", "spaceship", "aircraft", "boat", "truck"],
    "architecture": ["building", "house", "interior", "room", "skyscraper", "castle", "temple"],
    "landscape": ["landscape", "mountain", "ocean", "forest", "desert", "sky", "field"],
    "food": ["food", "meal", "dish", "drink", "coffee", "cake", "sushi", "cocktail"],
    "fashion": ["dress", "suit", "outfit", "shoes", "jewelry", "handbag", "watch"],
    "text": ["text", "typography", "lettering", "sign", "poster text", "quote"],
    "group": ["group", "couple", "family", "crowd", "team"],
    "abstract": ["abstract", "pattern", "geometric", "fractal", "texture"],
}

MOOD_RULES = {
    "dramatic": ["dramatic", "intense", "powerful", "bold", "striking", "epic"],
    "peaceful": ["peaceful", "serene", "calm", "tranquil", "gentle", "quiet"],
    "dark": ["dark", "moody", "gloomy", "noir", "shadowy", "mysterious"],
    "bright": ["bright", "vibrant", "colorful", "cheerful", "sunny", "vivid"],
    "nostalgic": ["nostalgic", "vintage", "retro", "old", "memory", "classic"],
    "luxurious": ["luxury", "elegant", "premium", "high-end", "opulent", "sophisticated"],
    "playful": ["playful", "fun", "whimsical", "cute", "quirky", "lighthearted"],
    "eerie": ["eerie", "creepy", "haunting", "unsettling", "spooky", "horror"],
    "romantic": ["romantic", "love", "intimate", "tender", "passion", "warmth"],
    "futuristic": ["futuristic", "sci-fi", "tech", "cyber", "neon", "holographic"],
}


def tag_prompt(prompt):
    """Assign tags to a single prompt."""
    text = f"{prompt.get('title', '')} {prompt.get('description', '')} {prompt.get('content', '')}".lower()

    tags = {"styles": [], "use_cases": [], "subjects": [], "moods": []}

    for tag, keywords in STYLE_RULES.items():
        if any(kw in text for kw in keywords):
            tags["styles"].append(tag)

    for tag, keywords in USECASE_RULES.items():
        if any(kw in text for kw in keywords):
            tags["use_cases"].append(tag)

    for tag, keywords in SUBJECT_RULES.items():
        if any(kw in text for kw in keywords):
            tags["subjects"].append(tag)

    for tag, keywords in MOOD_RULES.items():
        if any(kw in text for kw in keywords):
            tags["moods"].append(tag)

    return tags


def build_tag_index(force=False):
    """Tag all prompts and save the index."""
    if TAGS_CACHE.exists() and not force:
        with open(TAGS_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Tagging all prompts...", file=sys.stderr)
    prompts = []
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append(row)

    index = {}
    tag_counts = {"styles": {}, "use_cases": {}, "subjects": {}, "moods": {}}

    for p in prompts:
        pid = p.get("id", "")
        tags = tag_prompt(p)
        index[pid] = {
            "title": p.get("title", ""),
            "tags": tags,
        }
        for category, tag_list in tags.items():
            for t in tag_list:
                tag_counts[category][t] = tag_counts[category].get(t, 0) + 1

    result = {"index": index, "tag_counts": tag_counts, "total": len(prompts)}

    TAGS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(TAGS_CACHE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(f"Tagged {len(prompts)} prompts.", file=sys.stderr)
    return result


def filter_by_tags(styles=None, use_cases=None, subjects=None, moods=None, limit=20):
    """Filter prompts by tag combinations."""
    data = build_tag_index()
    index = data["index"]

    results = []
    for pid, info in index.items():
        tags = info["tags"]
        match = True
        if styles:
            if not any(s in tags["styles"] for s in styles):
                match = False
        if use_cases:
            if not any(u in tags["use_cases"] for u in use_cases):
                match = False
        if subjects:
            if not any(s in tags["subjects"] for s in subjects):
                match = False
        if moods:
            if not any(m in tags["moods"] for m in moods):
                match = False
        if match:
            results.append({"id": pid, "title": info["title"], "tags": tags})
            if len(results) >= limit:
                break

    return results


def main():
    parser = argparse.ArgumentParser(description="Auto-tag Nano Banana prompts")
    sub = parser.add_subparsers(dest="command")

    # Build
    bp = sub.add_parser("build", help="Build tag index")
    bp.add_argument("--force", "-f", action="store_true")

    # Stats
    sub.add_parser("stats", help="Show tag distribution")

    # Filter
    fp = sub.add_parser("filter", help="Filter prompts by tags")
    fp.add_argument("--style", "-s", action="append", help="Style tags")
    fp.add_argument("--use-case", "-u", action="append", help="Use-case tags")
    fp.add_argument("--subject", "-j", action="append", help="Subject tags")
    fp.add_argument("--mood", "-m", action="append", help="Mood tags")
    fp.add_argument("--limit", "-n", type=int, default=20)

    # Tag single prompt
    tp = sub.add_parser("tag", help="Tag a single prompt by ID")
    tp.add_argument("id", help="Prompt ID")

    args = parser.parse_args()

    if args.command == "build":
        data = build_tag_index(force=args.force)
        print(json.dumps({"total": data["total"], "tag_counts": data["tag_counts"]}, indent=2, ensure_ascii=False))

    elif args.command == "stats":
        data = build_tag_index()
        # Sort each category by count
        stats = {}
        for cat, counts in data["tag_counts"].items():
            sorted_tags = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            stats[cat] = [{"tag": t, "count": c} for t, c in sorted_tags]
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.command == "filter":
        results = filter_by_tags(args.style, args.use_case, args.subject, args.mood, args.limit)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "tag":
        prompts = []
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row.get("id", "")) == args.id:
                    tags = tag_prompt(row)
                    print(json.dumps({"id": args.id, "title": row.get("title", ""), "tags": tags}, indent=2, ensure_ascii=False))
                    return
        print(json.dumps({"error": f"Prompt {args.id} not found"}))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
