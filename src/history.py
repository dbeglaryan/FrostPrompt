#!/usr/bin/env python3
"""
Nano Banana Prompt History & Favorites
Tracks generated prompts, allows favoriting, and enables re-use.
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path(__file__).parent.parent / "prompts" / ".history"
HISTORY_FILE = HISTORY_DIR / "history.json"
FAVORITES_FILE = HISTORY_DIR / "favorites.json"


def _load(filepath):
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(filepath, data):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_to_history(prompt, metadata=None):
    """Add a prompt to history."""
    history = _load(HISTORY_FILE)
    entry = {
        "id": len(history) + 1,
        "prompt": prompt,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {},
    }
    history.append(entry)
    _save(HISTORY_FILE, history)
    return entry


def get_history(limit=20):
    """Get recent history."""
    history = _load(HISTORY_FILE)
    return list(reversed(history[-limit:]))


def clear_history():
    """Clear all history."""
    _save(HISTORY_FILE, [])
    return {"cleared": True}


def add_favorite(prompt, name=None, tags=None):
    """Save a prompt as a favorite."""
    favorites = _load(FAVORITES_FILE)
    for existing in favorites:
        if existing.get("prompt", "").strip() == prompt.strip():
            return {"skipped": True, "existing_id": existing["id"]}
    entry = {
        "id": len(favorites) + 1,
        "name": name or f"Favorite #{len(favorites) + 1}",
        "prompt": prompt,
        "tags": tags or [],
        "timestamp": datetime.now().isoformat(),
    }
    favorites.append(entry)
    _save(FAVORITES_FILE, favorites)
    return entry


def get_favorites():
    """Get all favorites."""
    return _load(FAVORITES_FILE)


def remove_favorite(fav_id):
    """Remove a favorite by ID."""
    favorites = _load(FAVORITES_FILE)
    favorites = [f for f in favorites if f["id"] != fav_id]
    # Re-index
    for i, f in enumerate(favorites):
        f["id"] = i + 1
    _save(FAVORITES_FILE, favorites)
    return {"removed": fav_id}


def search_history(query):
    """Search history by keyword."""
    history = _load(HISTORY_FILE)
    query_lower = query.lower()
    results = []
    for entry in history:
        if query_lower in entry["prompt"].lower() or query_lower in json.dumps(entry.get("metadata", {})).lower():
            results.append(entry)
    return list(reversed(results[-20:]))


def main():
    parser = argparse.ArgumentParser(description="Prompt History & Favorites")
    sub = parser.add_subparsers(dest="command")

    # Add to history
    ap = sub.add_parser("add", help="Add prompt to history")
    ap.add_argument("prompt", help="Prompt text")
    ap.add_argument("--model", help="Model used")
    ap.add_argument("--ratio", help="Aspect ratio")
    ap.add_argument("--resolution", help="Resolution")

    # View history
    hp = sub.add_parser("list", help="View recent history")
    hp.add_argument("--limit", "-n", type=int, default=20)

    # Search history
    sp = sub.add_parser("search", help="Search history")
    sp.add_argument("query", help="Search query")

    # Clear history
    sub.add_parser("clear", help="Clear all history")

    # Add favorite
    fp = sub.add_parser("fav", help="Add a favorite")
    fp.add_argument("prompt", help="Prompt text")
    fp.add_argument("--name", help="Favorite name")
    fp.add_argument("--tags", nargs="+", help="Tags")

    # List favorites
    sub.add_parser("favs", help="List all favorites")

    # Remove favorite
    rp = sub.add_parser("unfav", help="Remove a favorite")
    rp.add_argument("id", type=int, help="Favorite ID")

    args = parser.parse_args()

    if args.command == "add":
        metadata = {}
        if hasattr(args, "model") and args.model:
            metadata["model"] = args.model
        if hasattr(args, "ratio") and args.ratio:
            metadata["aspect_ratio"] = args.ratio
        if hasattr(args, "resolution") and args.resolution:
            metadata["resolution"] = args.resolution
        result = add_to_history(args.prompt, metadata)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "list":
        print(json.dumps(get_history(args.limit), indent=2, ensure_ascii=False))

    elif args.command == "search":
        print(json.dumps(search_history(args.query), indent=2, ensure_ascii=False))

    elif args.command == "clear":
        print(json.dumps(clear_history()))

    elif args.command == "fav":
        result = add_favorite(args.prompt, args.name, args.tags)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "favs":
        print(json.dumps(get_favorites(), indent=2, ensure_ascii=False))

    elif args.command == "unfav":
        print(json.dumps(remove_favorite(args.id)))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
