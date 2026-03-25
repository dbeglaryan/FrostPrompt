#!/usr/bin/env python3
"""
Multi-Model Prompt Formatter
Adapts Nano Banana prompts for different image generation models.
"""

import json
import sys
import argparse


MODEL_CONFIGS = {
    "nano-banana-pro": {
        "name": "Nano Banana Pro (Gemini 3 Pro Image)",
        "max_tokens": 65536,
        "strengths": "Complex scenes, deep reasoning, photorealism",
        "resolutions": ["1K", "2K", "4K"],
        "aspect_ratios": ["1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        "tips": [
            "Excels at multi-subject scenes with complex interactions",
            "Best for photorealistic output requiring fine detail",
            "Supports up to 14 reference images",
            "Use for text rendering with multiple fonts",
        ],
        "transform": None,  # Native format, no changes needed
    },
    "nano-banana-2": {
        "name": "Nano Banana 2 (Gemini 3.1 Flash Image)",
        "max_tokens": 131072,
        "strengths": "Speed, iteration, real-time search",
        "resolutions": ["0.5K", "1K", "2K", "4K"],
        "aspect_ratios": ["1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "1:4", "4:1", "1:8", "8:1"],
        "tips": [
            "Faster generation, better for rapid iteration",
            "Supports extra aspect ratios (1:4, 4:1, 1:8, 8:1)",
            "Includes 0.5K resolution for quick drafts",
            "Use real-time web search for current events",
        ],
        "transform": None,
    },
    "midjourney": {
        "name": "Midjourney v6",
        "strengths": "Artistic quality, aesthetic coherence",
        "tips": [
            "Prefers concise prompts over long descriptions",
            "Use :: to separate concepts with different weights",
            "Use --ar for aspect ratio, --s for stylize, --c for chaos",
            "Works best with evocative language rather than technical specs",
        ],
        "transform": "midjourney",
    },
    "dall-e-3": {
        "name": "DALL-E 3",
        "strengths": "Text rendering, instruction following",
        "tips": [
            "Excellent at following detailed instructions",
            "Good text rendering without special syntax",
            "Supports natural language descriptions",
            "Use clear, specific language for best results",
        ],
        "transform": "dalle",
    },
    "flux": {
        "name": "Flux (Black Forest Labs)",
        "strengths": "Photorealism, composition control",
        "tips": [
            "Excels at photorealistic output",
            "Prefers structured, detailed prompts",
            "Good at handling complex compositions",
            "Supports guidance scale for prompt adherence",
        ],
        "transform": "flux",
    },
    "stable-diffusion": {
        "name": "Stable Diffusion XL / SD3",
        "strengths": "Flexibility, LoRA support, fine-tuning",
        "tips": [
            "Use comma-separated tags for SD-style prompting",
            "Include quality boosters: masterpiece, best quality, highly detailed",
            "Use negative prompt for unwanted elements",
            "Weight important terms with (term:1.3) syntax",
        ],
        "transform": "sd",
    },
}


def adapt_for_midjourney(prompt):
    """Convert a Nano Banana prompt to Midjourney style."""
    # Midjourney prefers shorter, more evocative prompts
    # Remove technical camera specs and replace with MJ params
    adapted = prompt

    # Extract aspect ratio if mentioned
    ar = ""
    import re
    ar_match = re.search(r'(\d+:\d+)\s*aspect ratio', prompt)
    if ar_match:
        ar = f" --ar {ar_match.group(1)}"

    # Simplify - keep core description, remove camera specs
    lines_to_remove = [
        r'Shot on a [^.]+\.',
        r'Shot with a [^.]+\.',
        r'[Cc]olor grading [^.]+\.',
        r'reminiscent of [^.]+film[^.]*\.',
    ]
    for pattern in lines_to_remove:
        adapted = re.sub(pattern, '', adapted)

    # Clean up
    adapted = re.sub(r'\s+', ' ', adapted).strip()
    adapted = re.sub(r'\.\s*\.', '.', adapted)

    return adapted + ar + " --s 750 --v 6"


def adapt_for_dalle(prompt):
    """Convert to DALL-E 3 style - mostly keep as-is, DALL-E handles natural language well."""
    return prompt


def adapt_for_flux(prompt):
    """Convert to Flux style."""
    return prompt


def adapt_for_sd(prompt):
    """Convert a Nano Banana prompt to Stable Diffusion tag style."""
    import re

    # Extract key concepts and convert to comma-separated tags
    adapted = prompt

    # Add quality boosters at the start
    quality = "masterpiece, best quality, highly detailed, "

    # Build negative prompt from any negative language
    negative_parts = []
    neg_patterns = [
        (r'no\s+(\w+)', r'\1'),
        (r'without\s+(\w+)', r'\1'),
    ]
    for pattern, replacement in neg_patterns:
        matches = re.findall(pattern, adapted, re.IGNORECASE)
        negative_parts.extend(matches)

    negative_prompt = "lowres, bad anatomy, bad hands, text, error, missing fingers, cropped, worst quality, low quality, jpeg artifacts, blurry"
    if negative_parts:
        negative_prompt = ", ".join(negative_parts) + ", " + negative_prompt

    return {
        "prompt": quality + adapted,
        "negative_prompt": negative_prompt,
    }


def format_for_model(prompt, model):
    """Adapt a prompt for a specific model."""
    if model not in MODEL_CONFIGS:
        return {"error": f"Unknown model '{model}'. Available: {', '.join(MODEL_CONFIGS.keys())}"}

    config = MODEL_CONFIGS[model]
    result = {
        "model": config["name"],
        "strengths": config.get("strengths", ""),
        "tips": config.get("tips", []),
    }

    transform = config.get("transform")
    if transform == "midjourney":
        result["prompt"] = adapt_for_midjourney(prompt)
    elif transform == "dalle":
        result["prompt"] = adapt_for_dalle(prompt)
    elif transform == "flux":
        result["prompt"] = adapt_for_flux(prompt)
    elif transform == "sd":
        sd_result = adapt_for_sd(prompt)
        result["prompt"] = sd_result["prompt"]
        result["negative_prompt"] = sd_result["negative_prompt"]
    else:
        result["prompt"] = prompt

    if "resolutions" in config:
        result["resolutions"] = config["resolutions"]
    if "aspect_ratios" in config:
        result["aspect_ratios"] = config["aspect_ratios"]

    return result


def format_all_models(prompt):
    """Generate adapted prompts for all supported models."""
    results = {}
    for model in MODEL_CONFIGS:
        results[model] = format_for_model(prompt, model)
    return results


def main():
    parser = argparse.ArgumentParser(description="Multi-Model Prompt Formatter")
    sub = parser.add_subparsers(dest="command")

    # Format for specific model
    fp = sub.add_parser("format", help="Format prompt for a specific model")
    fp.add_argument("prompt", help="Prompt text")
    fp.add_argument("--model", "-m", required=True, choices=list(MODEL_CONFIGS.keys()))

    # Format for all models
    ap = sub.add_parser("all", help="Format prompt for all models")
    ap.add_argument("prompt", help="Prompt text")

    # List models
    sub.add_parser("models", help="List supported models")

    args = parser.parse_args()

    if args.command == "format":
        result = format_for_model(args.prompt, args.model)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "all":
        results = format_all_models(args.prompt)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "models":
        models = {k: {"name": v["name"], "strengths": v.get("strengths", "")} for k, v in MODEL_CONFIGS.items()}
        print(json.dumps(models, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
