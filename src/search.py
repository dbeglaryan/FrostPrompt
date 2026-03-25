#!/usr/bin/env python3
"""
Nano Banana Prompt Search Engine
Searches 11,000+ curated prompts by keyword, category, style, or use case.
Supports fuzzy matching, category filtering, and ranked results.
"""

import csv
import sys
import json
import re
import argparse
from pathlib import Path
from collections import defaultdict

DATABASE_PATH = Path(__file__).parent.parent / "prompts" / "database.csv"

# Category taxonomy for intelligent matching
STYLE_KEYWORDS = {
    "photography": ["photo", "photograph", "camera", "lens", "f/", "iso", "shutter", "dslr", "mirrorless", "35mm", "50mm", "85mm"],
    "cinematic": ["cinematic", "film still", "movie", "scene", "dramatic", "widescreen", "anamorphic"],
    "anime": ["anime", "manga", "japanese animation", "cel-shaded", "studio ghibli"],
    "illustration": ["illustration", "illustrated", "digital art", "concept art", "hand-drawn"],
    "3d-render": ["3d render", "3d model", "blender", "octane", "unreal engine", "c4d", "cinema 4d"],
    "pixel-art": ["pixel art", "pixelated", "8-bit", "16-bit", "retro game"],
    "watercolor": ["watercolor", "watercolour", "aquarelle", "wet media"],
    "oil-painting": ["oil painting", "oil on canvas", "impasto", "brushstroke"],
    "minimalist": ["minimalist", "minimal", "clean", "simple", "negative space"],
    "cyberpunk": ["cyberpunk", "sci-fi", "futuristic", "neon", "dystopian"],
    "retro": ["retro", "vintage", "nostalgia", "old-school", "analog"],
    "sketch": ["sketch", "line art", "pencil", "charcoal", "drawing"],
    "isometric": ["isometric", "isometric view", "diorama", "tilt-shift"],
    "chibi": ["chibi", "cute", "kawaii", "q-style", "chibi style"],
}

USECASE_KEYWORDS = {
    "product-marketing": ["product", "marketing", "commercial", "advertisement", "ad", "brand", "packaging"],
    "social-media": ["social media", "instagram", "twitter", "tiktok", "post", "story", "reel"],
    "youtube-thumbnail": ["youtube", "thumbnail", "clickbait", "video cover"],
    "profile-avatar": ["profile", "avatar", "headshot", "portrait", "pfp"],
    "poster-flyer": ["poster", "flyer", "banner", "billboard", "signage"],
    "infographic": ["infographic", "diagram", "chart", "educational", "data visualization"],
    "ecommerce": ["ecommerce", "e-commerce", "product listing", "shop", "store", "amazon"],
    "game-asset": ["game", "game asset", "sprite", "character design", "weapon", "item"],
    "storyboard": ["storyboard", "comic", "panel", "sequence", "narrative"],
    "app-design": ["app", "ui", "ux", "interface", "web design", "mockup", "wireframe"],
    "logo": ["logo", "brand mark", "emblem", "icon design", "wordmark"],
    "fashion": ["fashion", "outfit", "clothing", "apparel", "style", "runway"],
    "food": ["food", "drink", "beverage", "recipe", "culinary", "restaurant"],
    "architecture": ["architecture", "interior", "building", "room", "house", "office"],
    "landscape": ["landscape", "nature", "scenery", "mountain", "ocean", "forest"],
    "typography": ["typography", "text", "lettering", "font", "calligraphy", "type design"],
}


def load_database():
    """Load and parse the prompt database CSV."""
    prompts = []
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append(row)
    return prompts


def tokenize(text):
    """Simple tokenizer for matching."""
    return set(re.findall(r'\w+', text.lower()))


def score_prompt(prompt, query_tokens, query_lower, category=None, style=None):
    """Score a prompt against search criteria. Higher = better match."""
    score = 0
    title = (prompt.get("title") or "").lower()
    description = (prompt.get("description") or "").lower()
    content = (prompt.get("content") or "").lower()

    title_tokens = tokenize(title)
    desc_tokens = tokenize(description)
    content_tokens = tokenize(content)

    # Exact phrase match in title (highest signal)
    if query_lower in title:
        score += 100

    # Exact phrase match in description
    if query_lower in description:
        score += 50

    # Exact phrase match in content
    if query_lower in content:
        score += 30

    # Token overlap scoring
    title_overlap = len(query_tokens & title_tokens)
    desc_overlap = len(query_tokens & desc_tokens)
    content_overlap = len(query_tokens & content_tokens)

    score += title_overlap * 20
    score += desc_overlap * 10
    score += content_overlap * 5

    # Category matching
    if category:
        cat_lower = category.lower()
        cat_keywords = USECASE_KEYWORDS.get(cat_lower, []) or STYLE_KEYWORDS.get(cat_lower, [])
        if cat_keywords:
            for kw in cat_keywords:
                if kw in title or kw in description or kw in content:
                    score += 15
        else:
            # Direct keyword match
            if cat_lower in title or cat_lower in description:
                score += 15

    # Style matching
    if style:
        style_lower = style.lower()
        style_keywords = STYLE_KEYWORDS.get(style_lower, [style_lower])
        for kw in style_keywords:
            if kw in title or kw in description or kw in content:
                score += 15

    return score


def search(query, category=None, style=None, limit=10):
    """Search prompts by query with optional category/style filters."""
    prompts = load_database()
    query_lower = query.lower().strip()
    query_tokens = tokenize(query_lower)

    scored = []
    for p in prompts:
        s = score_prompt(p, query_tokens, query_lower, category, style)
        if s > 0:
            scored.append((s, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:limit]


def parse_author(raw):
    """Parse author field which may be JSON."""
    if not raw:
        return "Unknown"
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data.get("name", raw)
    except (json.JSONDecodeError, TypeError):
        pass
    return raw


def format_result(score, prompt, verbose=False):
    """Format a single search result."""
    result = {
        "id": prompt.get("id", ""),
        "title": prompt.get("title", ""),
        "score": score,
        "description": prompt.get("description", "")[:200],
        "author": parse_author(prompt.get("author", "")),
    }
    if verbose:
        result["content"] = prompt.get("content", "")
        result["sourceLink"] = prompt.get("sourceLink", "")
    return result


def list_categories():
    """List all available categories."""
    cats = {"styles": sorted(STYLE_KEYWORDS.keys()), "use_cases": sorted(USECASE_KEYWORDS.keys())}
    return cats


def get_prompt_by_id(prompt_id):
    """Retrieve a specific prompt by ID."""
    prompts = load_database()
    for p in prompts:
        if str(p.get("id", "")) == str(prompt_id):
            return p
    return None


def random_prompts(count=5, category=None, style=None):
    """Get random prompts, optionally filtered."""
    import random
    prompts = load_database()

    if category or style:
        filtered = []
        for p in prompts:
            text = f"{p.get('title', '')} {p.get('description', '')} {p.get('content', '')}".lower()
            match = True
            if category:
                cat_kws = USECASE_KEYWORDS.get(category.lower(), [category.lower()])
                if not any(kw in text for kw in cat_kws):
                    match = False
            if style:
                style_kws = STYLE_KEYWORDS.get(style.lower(), [style.lower()])
                if not any(kw in text for kw in style_kws):
                    match = False
            if match:
                filtered.append(p)
        prompts = filtered

    return random.sample(prompts, min(count, len(prompts)))


def stats():
    """Get database statistics."""
    prompts = load_database()
    authors = defaultdict(int)
    for p in prompts:
        a = p.get("author", "Unknown")
        if a:
            authors[a] += 1
    top_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "total_prompts": len(prompts),
        "unique_authors": len(authors),
        "top_authors": [{"name": a, "count": c} for a, c in top_authors],
    }


def main():
    parser = argparse.ArgumentParser(description="Nano Banana Prompt Search Engine")
    sub = parser.add_subparsers(dest="command")

    # Search
    sp = sub.add_parser("search", help="Search prompts")
    sp.add_argument("query", help="Search query")
    sp.add_argument("--category", "-c", help="Filter by use-case category")
    sp.add_argument("--style", "-s", help="Filter by visual style")
    sp.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    sp.add_argument("--verbose", "-v", action="store_true", help="Include full prompt content")

    # Get by ID
    gp = sub.add_parser("get", help="Get prompt by ID")
    gp.add_argument("id", help="Prompt ID")

    # Random
    rp = sub.add_parser("random", help="Get random prompts")
    rp.add_argument("--count", "-n", type=int, default=5)
    rp.add_argument("--category", "-c", help="Filter by category")
    rp.add_argument("--style", "-s", help="Filter by style")

    # Categories
    sub.add_parser("categories", help="List all categories")

    # Stats
    sub.add_parser("stats", help="Database statistics")

    args = parser.parse_args()

    if args.command == "search":
        results = search(args.query, args.category, args.style, args.limit)
        output = [format_result(s, p, args.verbose) for s, p in results]
        print(json.dumps(output, indent=2, ensure_ascii=False))

    elif args.command == "get":
        p = get_prompt_by_id(args.id)
        if p:
            print(json.dumps(p, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"error": f"Prompt {args.id} not found"}))

    elif args.command == "random":
        results = random_prompts(args.count, args.category, args.style)
        output = [{"id": p.get("id"), "title": p.get("title"), "description": p.get("description", "")[:200]} for p in results]
        print(json.dumps(output, indent=2, ensure_ascii=False))

    elif args.command == "categories":
        print(json.dumps(list_categories(), indent=2))

    elif args.command == "stats":
        print(json.dumps(stats(), indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
