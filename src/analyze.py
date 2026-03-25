#!/usr/bin/env python3
"""
Nano Banana Prompt Analyzer
Analyzes prompts against best practices and suggests improvements.
"""

import sys
import json
import re
import argparse

# Elements to check for in a well-structured prompt
CHECKLIST = {
    "subject": {
        "description": "Clear subject with specific materials/textures",
        "keywords": [],  # Checked via length heuristic
        "weight": 10,
    },
    "lighting": {
        "description": "Explicit lighting design",
        "keywords": [
            "light", "lighting", "lit", "shadow", "glow", "backlight",
            "softbox", "rim light", "golden hour", "chiaroscuro", "ambient",
            "sun", "neon", "fluorescent", "candlelight", "spotlight",
            "dramatic light", "natural light", "studio light", "volumetric",
        ],
        "weight": 15,
    },
    "camera": {
        "description": "Camera angle or lens specified",
        "keywords": [
            "camera", "lens", "f/", "focal", "angle", "shot", "aperture",
            "wide-angle", "macro", "telephoto", "fisheye", "35mm", "50mm",
            "85mm", "low angle", "high angle", "aerial", "bird's eye",
            "eye level", "dutch angle", "overhead", "close-up", "medium shot",
            "full shot", "gopro", "dslr", "fujifilm", "canon", "nikon",
            "depth of field", "bokeh", "tilt-shift",
        ],
        "weight": 12,
    },
    "composition": {
        "description": "Composition and framing defined",
        "keywords": [
            "composition", "framing", "center", "centered", "rule of thirds",
            "symmetr", "asymmetr", "foreground", "background", "midground",
            "leading lines", "negative space", "fill the frame", "panoramic",
            "portrait orientation", "landscape orientation", "cropped",
            "full body", "half body", "headshot", "wide shot",
        ],
        "weight": 10,
    },
    "style": {
        "description": "Visual style clearly stated",
        "keywords": [
            "style", "aesthetic", "realistic", "photorealistic", "illustration",
            "watercolor", "oil painting", "digital art", "anime", "manga",
            "minimalist", "retro", "vintage", "cyberpunk", "fantasy",
            "surreal", "abstract", "impressionist", "pop art", "art deco",
            "art nouveau", "baroque", "gothic", "steampunk", "vaporwave",
            "pixel art", "3d render", "isometric", "flat design",
            "editorial", "commercial", "cinematic", "film still",
        ],
        "weight": 10,
    },
    "color_grading": {
        "description": "Color grading or mood defined",
        "keywords": [
            "color", "colour", "tone", "grading", "palette", "warm",
            "cool", "muted", "vibrant", "saturated", "desaturated",
            "monochrome", "sepia", "teal", "orange", "pastel",
            "earth tones", "kodak", "fuji", "portra", "velvia",
            "film stock", "grain", "moody", "bright", "dark",
        ],
        "weight": 8,
    },
    "materiality": {
        "description": "Physical materials and textures described",
        "keywords": [
            "texture", "material", "fabric", "leather", "wood", "metal",
            "glass", "ceramic", "stone", "marble", "concrete", "silk",
            "velvet", "denim", "linen", "wool", "chrome", "matte",
            "glossy", "rough", "smooth", "polished", "weathered",
            "rusted", "brushed", "anodized", "carbon fiber", "crystal",
        ],
        "weight": 8,
    },
    "text_quotes": {
        "description": "Rendered text enclosed in quotes with font specified",
        "keywords": [],  # Checked with special logic
        "weight": 5,
    },
    "positive_framing": {
        "description": "Uses positive framing (no negatives)",
        "keywords": [],  # Checked with special logic
        "weight": 10,
    },
    "narrative": {
        "description": "Prompt is narrative, not a keyword list",
        "keywords": [],  # Checked via comma density
        "weight": 8,
    },
}

NEGATIVE_WORDS = [
    "no ", "not ", "without ", "don't ", "doesn't ", "isn't ", "aren't ",
    "never ", "none ", "nothing ", "neither ", "nor ", "nobody ",
    "avoid ", "exclude ", "remove ",
]


def analyze_prompt(prompt_text):
    """Analyze a prompt and return scores and suggestions."""
    text_lower = prompt_text.lower()
    words = text_lower.split()
    total_words = len(words)

    results = {}
    total_score = 0
    max_score = 0
    suggestions = []

    for key, check in CHECKLIST.items():
        max_score += check["weight"]
        found = False

        if key == "subject":
            # Subject is present if prompt has reasonable length
            found = total_words >= 10
            if not found:
                suggestions.append("Add more detail to your subject. Describe specific materials, colors, and textures.")

        elif key == "text_quotes":
            # Check if any rendered text is in quotes
            has_text_intent = any(w in text_lower for w in ["text", "word", "letter", "title", "headline", "sign", "label", "caption"])
            if has_text_intent:
                has_quotes = '"' in prompt_text or "'" in prompt_text
                has_font = any(w in text_lower for w in ["font", "typeface", "serif", "sans", "bold", "italic", "typography"])
                if has_quotes and has_font:
                    found = True
                elif has_quotes:
                    found = True
                    suggestions.append("You have text in quotes (good!), but also specify a font style (e.g., 'bold sans-serif font', 'Century Gothic').")
                else:
                    suggestions.append("Enclose any rendered text in quotes and specify a font style for best results.")
            else:
                found = True  # No text rendering needed, not applicable

        elif key == "positive_framing":
            negatives_found = [nw.strip() for nw in NEGATIVE_WORDS if nw in text_lower]
            if not negatives_found:
                found = True
            else:
                suggestions.append(f"Rephrase negative terms ({', '.join(negatives_found[:3])}) to positive framing. E.g., 'no cars' -> 'empty street'.")

        elif key == "narrative":
            # Check comma density - keyword lists have lots of commas
            comma_count = prompt_text.count(",")
            if total_words > 0:
                comma_ratio = comma_count / total_words
                if comma_ratio < 0.15:  # Less than 15% comma-to-word ratio
                    found = True
                else:
                    suggestions.append("Your prompt reads like a keyword list. Try writing it as a narrative description instead.")
            else:
                found = False

        else:
            # Standard keyword check
            for kw in check["keywords"]:
                if kw in text_lower:
                    found = True
                    break
            if not found:
                suggestions.append(f"Missing: {check['description']}. Add specific {key.replace('_', ' ')} details.")

        score = check["weight"] if found else 0
        total_score += score
        results[key] = {
            "present": found,
            "score": score,
            "max": check["weight"],
            "description": check["description"],
        }

    percentage = round((total_score / max_score) * 100) if max_score > 0 else 0

    # Determine grade
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "grade": grade,
        "word_count": total_words,
        "checks": results,
        "suggestions": suggestions,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze a Nano Banana prompt")
    parser.add_argument("prompt", nargs="?", help="The prompt text to analyze (or pipe via stdin)")
    args = parser.parse_args()

    if args.prompt:
        text = args.prompt
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    result = analyze_prompt(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
