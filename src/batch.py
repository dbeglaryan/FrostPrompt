#!/usr/bin/env python3
"""
Nano Banana Batch Prompt Generator
Generates multiple variations of a base prompt with controlled modifications.
"""

import json
import sys
import re
import random
import argparse
from pathlib import Path

# Variation dimensions
LIGHTING_VARIATIONS = [
    "golden hour backlighting creating long warm shadows",
    "dramatic Chiaroscuro lighting with harsh high contrast and a single hard light from the upper left",
    "soft diffused overcast lighting with even, shadowless illumination",
    "neon-lit nighttime scene with vibrant cyan and magenta reflections",
    "three-point softbox studio setup with clean, even lighting",
    "candlelit scene with warm flickering orange glow and deep shadows",
    "moonlit scene with cool blue tones and soft ethereal highlights",
    "harsh midday sun casting sharp defined shadows directly below",
    "volumetric god-rays piercing through fog or mist",
    "ring light portrait lighting with catchlights in the eyes",
]

CAMERA_VARIATIONS = [
    "Shot on a Canon EOS R5 with an 85mm f/1.4 lens, shallow depth of field with creamy bokeh",
    "Shot on a Fujifilm X-T5 with a 35mm f/1.4 lens, natural color science and subtle grain",
    "Shot on a Hasselblad medium format with an 80mm lens, incredible detail and dynamic range",
    "Shot on a vintage Leica M6 with a 50mm Summilux, classic rangefinder rendering",
    "Shot on a GoPro at ultra-wide angle, immersive distorted perspective",
    "Shot on a Sony A7IV with a 24-70mm f/2.8 at 50mm, versatile documentary feel",
    "Shot on a disposable camera with flash, raw unpolished aesthetic with muted colors",
    "Shot on a Nikon Z9 with a 200mm f/2 telephoto, compressed background with extreme bokeh",
    "Shot on a drone from aerial perspective, DJI Mavic wide-angle overhead view",
    "Shot with a tilt-shift lens creating miniature diorama effect",
]

COLOR_VARIATIONS = [
    "Warm color grading with rich golden tones, reminiscent of Kodak Portra 400",
    "Cool cinematic color grading with muted teal-and-orange split toning",
    "High contrast black and white with deep blacks and bright highlights",
    "Desaturated muted earth tones with lifted blacks, indie film aesthetic",
    "Vibrant oversaturated colors with punchy primaries, pop art energy",
    "Nostalgic sepia-tinted warm tones, reminiscent of 1970s Ektachrome",
    "Pastel color palette with soft pinks, lavenders, and mint greens",
    "Dark moody color grading with deep shadows and selective warm highlights",
    "Cross-processed film look with unexpected color shifts and high grain",
    "Clean neutral color grading with true-to-life white balance and minimal stylization",
]

STYLE_VARIATIONS = [
    "Photorealistic photography with ultra-sharp detail",
    "Cinematic film still with anamorphic lens characteristics",
    "Watercolor illustration with visible brushstrokes and soft edges",
    "Oil painting style with rich impasto texture and visible canvas",
    "Anime illustration with vibrant cel shading and clean line art",
    "3D render with subsurface scattering and ray-traced reflections",
    "Minimalist flat design with bold shapes and limited color palette",
    "Vintage magazine illustration from the 1960s with halftone dots",
    "Pencil sketch with detailed crosshatching and paper texture",
    "Isometric pixel art with clean edges and limited palette",
]

COMPOSITION_VARIATIONS = [
    "centered composition with symmetrical framing",
    "rule-of-thirds composition with the subject placed at the left intersection",
    "dramatic low-angle shot looking upward",
    "aerial bird's-eye view looking straight down",
    "over-the-shoulder perspective creating depth and context",
    "extreme close-up filling the frame with texture detail",
    "wide establishing shot showing the full environment",
    "Dutch angle tilted at 15 degrees for dynamic tension",
    "framed through an archway or doorway creating natural vignette",
    "split composition with the subject reflected in water or a mirror",
]


def generate_variations(base_prompt, count=5, vary=None):
    """Generate variations of a base prompt.

    vary: list of dimensions to vary. Options: lighting, camera, color, style, composition, all
    If None, varies all dimensions.
    """
    if vary is None or "all" in vary:
        vary = ["lighting", "camera", "color", "style", "composition"]

    dimension_pools = {
        "lighting": LIGHTING_VARIATIONS,
        "camera": CAMERA_VARIATIONS,
        "color": COLOR_VARIATIONS,
        "style": STYLE_VARIATIONS,
        "composition": COMPOSITION_VARIATIONS,
    }

    variations = []
    for i in range(count):
        modified = base_prompt
        changes = {}

        for dim in vary:
            pool = dimension_pools.get(dim, [])
            if not pool:
                continue
            replacement = random.choice(pool)
            changes[dim] = replacement

        # Build the variation by appending modifications
        suffix_parts = []
        for dim, value in changes.items():
            suffix_parts.append(value)

        # If the base prompt is long enough, append. Otherwise build from scratch.
        variation_prompt = base_prompt.rstrip(".")
        if suffix_parts:
            variation_prompt += ". " + ". ".join(suffix_parts) + "."

        variations.append({
            "variation": i + 1,
            "prompt": variation_prompt,
            "changes": changes,
        })

    return variations


def batch_from_subjects(subjects, template, count_per_subject=1):
    """Generate prompts for multiple subjects using a template pattern.

    template: a string with {subject} placeholder
    subjects: list of subject descriptions
    """
    results = []
    for subject in subjects:
        for i in range(count_per_subject):
            prompt = template.replace("{subject}", subject)
            if count_per_subject > 1:
                # Add random variation
                lighting = random.choice(LIGHTING_VARIATIONS)
                camera = random.choice(CAMERA_VARIATIONS)
                prompt = prompt.rstrip(".") + f". {lighting}. {camera}."
            results.append({
                "subject": subject,
                "variation": i + 1,
                "prompt": prompt,
            })
    return results


def batch_aspect_ratios(base_prompt, ratios=None):
    """Generate the same prompt adapted for different aspect ratios."""
    if ratios is None:
        ratios = ["1:1", "9:16", "16:9", "4:3", "3:2"]

    ratio_hints = {
        "1:1": "square composition, centered subject with balanced framing",
        "9:16": "vertical composition for mobile story format, tall framing with subject in upper or lower third",
        "16:9": "widescreen cinematic composition with horizontal depth",
        "4:3": "classic photo composition with comfortable framing",
        "3:2": "standard DSLR composition with natural proportions",
        "4:5": "slightly vertical portrait composition for Instagram feed",
        "21:9": "ultra-wide cinematic panorama composition",
    }

    results = []
    for ratio in ratios:
        hint = ratio_hints.get(ratio, f"{ratio} aspect ratio composition")
        adapted = f"A {ratio} aspect ratio image with {hint}. {base_prompt}"
        results.append({
            "aspect_ratio": ratio,
            "prompt": adapted,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Batch Nano Banana Prompt Generator")
    sub = parser.add_subparsers(dest="command")

    # Variations
    vp = sub.add_parser("vary", help="Generate variations of a base prompt")
    vp.add_argument("prompt", help="Base prompt text")
    vp.add_argument("--count", "-n", type=int, default=5, help="Number of variations")
    vp.add_argument("--dimensions", "-d", nargs="+",
                     choices=["lighting", "camera", "color", "style", "composition", "all"],
                     default=["all"], help="Which dimensions to vary")

    # Multi-subject
    mp = sub.add_parser("subjects", help="Generate prompts for multiple subjects")
    mp.add_argument("--template", "-t", required=True, help="Template with {subject} placeholder")
    mp.add_argument("--subjects", "-s", nargs="+", required=True, help="List of subjects")
    mp.add_argument("--variations", "-v", type=int, default=1, help="Variations per subject")

    # Aspect ratio batch
    ap = sub.add_parser("ratios", help="Adapt prompt for multiple aspect ratios")
    ap.add_argument("prompt", help="Base prompt text")
    ap.add_argument("--ratios", "-r", nargs="+", help="Aspect ratios to generate")

    args = parser.parse_args()

    if args.command == "vary":
        results = generate_variations(args.prompt, args.count, args.dimensions)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "subjects":
        results = batch_from_subjects(args.subjects, args.template, args.variations)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "ratios":
        results = batch_aspect_ratios(args.prompt, args.ratios)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
