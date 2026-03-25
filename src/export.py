#!/usr/bin/env python3
"""
Nano Banana Prompt Export
Export prompts in multiple formats: JSON, Markdown, plain text, clipboard-ready.
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

EXPORT_DIR = Path(__file__).parent.parent / "exports"


def export_json(prompt, metadata=None):
    """Export as structured JSON."""
    data = {
        "prompt": prompt,
        "metadata": metadata or {},
        "exported_at": datetime.now().isoformat(),
        "format": "json",
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_markdown(prompt, metadata=None):
    """Export as formatted Markdown."""
    meta = metadata or {}
    lines = ["# Nano Banana Prompt", ""]
    lines.append("## Prompt")
    lines.append("```")
    lines.append(prompt)
    lines.append("```")
    lines.append("")

    if meta:
        lines.append("## Settings")
        if "model" in meta:
            lines.append(f"- **Model**: {meta['model']}")
        if "aspect_ratio" in meta:
            lines.append(f"- **Aspect Ratio**: {meta['aspect_ratio']}")
        if "resolution" in meta:
            lines.append(f"- **Resolution**: {meta['resolution']}")
        lines.append("")

    if "tips" in meta:
        lines.append("## Tips")
        for tip in meta["tips"]:
            lines.append(f"- {tip}")
        lines.append("")

    if "variations" in meta:
        lines.append("## Variations")
        for i, var in enumerate(meta["variations"], 1):
            lines.append(f"### Variation {i}")
            lines.append("```")
            lines.append(var)
            lines.append("```")
            lines.append("")

    lines.append(f"*Generated with FrostPrompt — {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)


def export_plain(prompt):
    """Export as plain text, ready to paste."""
    return prompt


def export_api_payload(prompt, metadata=None):
    """Export as a ready-to-use Gemini API JSON payload."""
    meta = metadata or {}
    model = meta.get("model", "gemini-2.0-flash-preview-image-generation")
    aspect_ratio = meta.get("aspect_ratio", "1:1")
    resolution = meta.get("resolution", "1024")

    # Map resolution strings to pixel values
    res_map = {"0.5K": "512", "1K": "1024", "2K": "2048", "4K": "4096"}
    if resolution in res_map:
        resolution = res_map[resolution]

    payload = {
        "model": model,
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageGenerationConfig": {
                "aspectRatio": aspect_ratio,
            }
        }
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def export_batch(prompts, format_type="json", metadata=None):
    """Export multiple prompts at once."""
    meta = metadata or {}

    if format_type == "json":
        data = {
            "prompts": [{"index": i + 1, "prompt": p} for i, p in enumerate(prompts)],
            "count": len(prompts),
            "metadata": meta,
            "exported_at": datetime.now().isoformat(),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    elif format_type == "markdown":
        lines = [f"# Nano Banana Prompt Batch ({len(prompts)} prompts)", ""]
        for i, p in enumerate(prompts, 1):
            lines.append(f"## Prompt {i}")
            lines.append("```")
            lines.append(p)
            lines.append("```")
            lines.append("")
        lines.append(f"*Generated with FrostPrompt — {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        return "\n".join(lines)

    elif format_type == "plain":
        separator = "\n" + "=" * 60 + "\n"
        return separator.join(prompts)

    return json.dumps({"error": "Unknown format"})


def save_export(content, filename=None, format_type="md"):
    """Save exported content to a file."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prompt_{timestamp}.{format_type}"
    path = EXPORT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(path)


def main():
    parser = argparse.ArgumentParser(description="Export Nano Banana Prompts")
    sub = parser.add_subparsers(dest="command")

    # Single prompt export
    ep = sub.add_parser("single", help="Export a single prompt")
    ep.add_argument("prompt", help="Prompt text")
    ep.add_argument("--format", "-f", choices=["json", "markdown", "plain", "api"], default="plain")
    ep.add_argument("--model", help="Model name")
    ep.add_argument("--ratio", help="Aspect ratio")
    ep.add_argument("--resolution", help="Resolution")
    ep.add_argument("--save", "-s", action="store_true", help="Save to file")

    # Batch export
    bp = sub.add_parser("batch", help="Export multiple prompts from JSON stdin")
    bp.add_argument("--format", "-f", choices=["json", "markdown", "plain"], default="json")
    bp.add_argument("--save", "-s", action="store_true", help="Save to file")

    args = parser.parse_args()

    if args.command == "single":
        metadata = {}
        if args.model:
            metadata["model"] = args.model
        if args.ratio:
            metadata["aspect_ratio"] = args.ratio
        if args.resolution:
            metadata["resolution"] = args.resolution

        if args.format == "json":
            output = export_json(args.prompt, metadata)
        elif args.format == "markdown":
            output = export_markdown(args.prompt, metadata)
        elif args.format == "api":
            output = export_api_payload(args.prompt, metadata)
        else:
            output = export_plain(args.prompt)

        if args.save:
            ext = {"json": "json", "markdown": "md", "plain": "txt", "api": "json"}[args.format]
            path = save_export(output, format_type=ext)
            print(json.dumps({"saved": path, "format": args.format}))
        else:
            print(output)

    elif args.command == "batch":
        prompts_data = json.loads(sys.stdin.read())
        if isinstance(prompts_data, list):
            prompts = prompts_data
        else:
            prompts = [p.get("prompt", p) if isinstance(p, dict) else p for p in prompts_data.get("prompts", [])]

        output = export_batch(prompts, args.format)

        if args.save:
            ext = {"json": "json", "markdown": "md", "plain": "txt"}[args.format]
            path = save_export(output, format_type=ext)
            print(json.dumps({"saved": path, "format": args.format, "count": len(prompts)}))
        else:
            print(output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
