#!/usr/bin/env python3
"""
Semantic Search Engine for Nano Banana Prompts
Uses sentence-transformers to embed prompts and find semantically similar matches.
Pre-computes and caches embeddings for fast subsequent searches.
"""

import csv
import json
import sys
import os
import argparse
import pickle
import numpy as np
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "prompts" / "database.csv"
CACHE_DIR = Path(__file__).parent.parent / "prompts" / ".cache"
EMBEDDINGS_CACHE = CACHE_DIR / "embeddings.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast, good quality, 384 dimensions


def load_database():
    """Load and parse the prompt database CSV."""
    prompts = []
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append(row)
    return prompts


def get_searchable_text(prompt):
    """Combine title + description + first 500 chars of content for embedding."""
    title = prompt.get("title", "")
    desc = prompt.get("description", "")
    content = prompt.get("content", "")[:500]
    return f"{title}. {desc}. {content}".strip()


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


def build_embeddings(force=False):
    """Build and cache embeddings for all prompts."""
    if EMBEDDINGS_CACHE.exists() and not force:
        print("Loading cached embeddings...", file=sys.stderr)
        with open(EMBEDDINGS_CACHE, "rb") as f:
            data = pickle.load(f)
        print(f"Loaded {len(data['embeddings'])} cached embeddings.", file=sys.stderr)
        return data

    print("Building embeddings for all prompts (first time only)...", file=sys.stderr)
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: sentence-transformers not installed. Run: pip install sentence-transformers", file=sys.stderr)
        sys.exit(1)

    model = SentenceTransformer(MODEL_NAME)
    prompts = load_database()
    texts = [get_searchable_text(p) for p in prompts]

    print(f"Encoding {len(texts)} prompts...", file=sys.stderr)
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=256)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "embeddings": embeddings,
        "prompts": prompts,
        "model_name": MODEL_NAME,
    }
    with open(EMBEDDINGS_CACHE, "wb") as f:
        pickle.dump(data, f)

    print(f"Cached {len(embeddings)} embeddings to {EMBEDDINGS_CACHE}", file=sys.stderr)
    return data


def semantic_search(query, limit=10, category=None, style=None, threshold=0.1):
    """Search prompts by semantic similarity."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: sentence-transformers not installed. Run: pip install sentence-transformers", file=sys.stderr)
        sys.exit(1)

    data = build_embeddings()
    embeddings = data["embeddings"]
    prompts = data["prompts"]

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([query])

    # Cosine similarity
    similarities = np.dot(embeddings, query_embedding.T).flatten()
    norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    norms[norms == 0] = 1e-10
    cosine_scores = similarities / norms

    # Optional category/style filtering
    if category or style:
        for i, p in enumerate(prompts):
            text = f"{p.get('title', '')} {p.get('description', '')} {p.get('content', '')}".lower()
            if category and category.lower() not in text:
                cosine_scores[i] *= 0.3  # Penalize non-matching, don't exclude
            if style and style.lower() not in text:
                cosine_scores[i] *= 0.3

    top_indices = np.argsort(cosine_scores)[::-1][:limit]

    results = []
    for idx in top_indices:
        score = float(cosine_scores[idx])
        if score < threshold:
            continue
        p = prompts[idx]
        results.append({
            "id": p.get("id", ""),
            "title": p.get("title", ""),
            "similarity": round(score, 4),
            "description": p.get("description", "")[:200],
            "author": parse_author(p.get("author", "")),
        })

    return results


def semantic_search_verbose(query, limit=10, category=None, style=None, threshold=0.1):
    """Search with full prompt content included."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: sentence-transformers not installed. Run: pip install sentence-transformers", file=sys.stderr)
        sys.exit(1)

    data = build_embeddings()
    embeddings = data["embeddings"]
    prompts = data["prompts"]

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([query])

    similarities = np.dot(embeddings, query_embedding.T).flatten()
    norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    norms[norms == 0] = 1e-10
    cosine_scores = similarities / norms

    if category or style:
        for i, p in enumerate(prompts):
            text = f"{p.get('title', '')} {p.get('description', '')} {p.get('content', '')}".lower()
            if category and category.lower() not in text:
                cosine_scores[i] *= 0.3
            if style and style.lower() not in text:
                cosine_scores[i] *= 0.3

    top_indices = np.argsort(cosine_scores)[::-1][:limit]

    results = []
    for idx in top_indices:
        score = float(cosine_scores[idx])
        if score < threshold:
            continue
        p = prompts[idx]
        results.append({
            "id": p.get("id", ""),
            "title": p.get("title", ""),
            "similarity": round(score, 4),
            "description": p.get("description", "")[:200],
            "author": parse_author(p.get("author", "")),
            "content": p.get("content", ""),
            "sourceLink": p.get("sourceLink", ""),
        })

    return results


def find_similar(prompt_id, limit=10):
    """Find prompts similar to a given prompt by ID."""
    data = build_embeddings()
    embeddings = data["embeddings"]
    prompts = data["prompts"]

    # Find the target prompt index
    target_idx = None
    for i, p in enumerate(prompts):
        if str(p.get("id", "")) == str(prompt_id):
            target_idx = i
            break

    if target_idx is None:
        return {"error": f"Prompt {prompt_id} not found"}

    target_embedding = embeddings[target_idx].reshape(1, -1)
    similarities = np.dot(embeddings, target_embedding.T).flatten()
    norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(target_embedding)
    norms[norms == 0] = 1e-10
    cosine_scores = similarities / norms

    # Exclude self
    cosine_scores[target_idx] = -1

    top_indices = np.argsort(cosine_scores)[::-1][:limit]

    results = []
    for idx in top_indices:
        p = prompts[idx]
        results.append({
            "id": p.get("id", ""),
            "title": p.get("title", ""),
            "similarity": round(float(cosine_scores[idx]), 4),
            "description": p.get("description", "")[:200],
            "author": parse_author(p.get("author", "")),
        })

    return {
        "source": prompts[target_idx].get("title", ""),
        "similar": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Semantic Search for Nano Banana Prompts")
    sub = parser.add_subparsers(dest="command")

    # Semantic search
    sp = sub.add_parser("search", help="Semantic search for prompts")
    sp.add_argument("query", help="Natural language search query")
    sp.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    sp.add_argument("--category", "-c", help="Filter by category")
    sp.add_argument("--style", "-s", help="Filter by style")
    sp.add_argument("--verbose", "-v", action="store_true", help="Include full prompt content")
    sp.add_argument("--threshold", "-t", type=float, default=0.1, help="Min similarity to include (default: 0.1)")

    # Find similar
    fp = sub.add_parser("similar", help="Find prompts similar to a given prompt")
    fp.add_argument("id", help="Source prompt ID")
    fp.add_argument("--limit", "-n", type=int, default=10, help="Max results")

    # Build cache
    bp = sub.add_parser("build", help="Pre-build the embeddings cache")
    bp.add_argument("--force", "-f", action="store_true", help="Force rebuild even if cache exists")

    args = parser.parse_args()

    if args.command == "search":
        if args.verbose:
            results = semantic_search_verbose(args.query, args.limit, args.category, args.style, args.threshold)
        else:
            results = semantic_search(args.query, args.limit, args.category, args.style, args.threshold)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "similar":
        results = find_similar(args.id, args.limit)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "build":
        build_embeddings(force=args.force)
        print("Embeddings cache built successfully.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
