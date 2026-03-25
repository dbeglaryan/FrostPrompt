#!/usr/bin/env python3
"""
Nano Banana Prompt Template Engine
Reusable prompt templates with variable substitution.
"""

import json
import re
import sys
import argparse
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Built-in templates
BUILTIN_TEMPLATES = {
    "quote-card": {
        "name": "Quote Card",
        "description": "Inspirational quote card for social media",
        "variables": {
            "quote_text": {"description": "The quote text", "default": "Stay hungry, stay foolish."},
            "attribution": {"description": "Quote attribution", "default": "Steve Jobs"},
            "font_style": {"description": "Typography style", "default": "elegant calligraphy"},
            "background": {"description": "Background scene", "default": "soft gradient from deep navy to warm amber"},
            "aspect_ratio": {"description": "Aspect ratio", "default": "9:16"},
            "mood": {"description": "Overall mood", "default": "inspirational and warm"},
        },
        "template": """A vertical social media story image with a {aspect_ratio} aspect ratio. {background}. In the upper third of the frame, {font_style} typography in warm ivory white reads: "{quote_text}" Below the quote in a smaller, thin sans-serif font: "— {attribution}". The text has a subtle warm drop shadow for legibility. Cinematic color grading with rich golden tones, a {mood} atmosphere. Shot with soft, diffused lighting creating gentle depth.""",
    },
    "product-shot": {
        "name": "Product Photography",
        "description": "Professional product photography for marketing",
        "variables": {
            "product": {"description": "Product description", "default": "minimalist ceramic coffee mug with matte sage glaze"},
            "surface": {"description": "Surface/table the product sits on", "default": "raw concrete countertop"},
            "props": {"description": "Surrounding props", "default": "a single eucalyptus sprig and scattered coffee beans"},
            "lighting": {"description": "Lighting setup", "default": "soft diffused overhead lighting from a large softbox"},
            "camera": {"description": "Camera and lens", "default": "Canon EOS R5 with a 90mm macro lens at f/2.8"},
            "style": {"description": "Photography style", "default": "clean Scandinavian-inspired commercial photography"},
        },
        "template": """A {product}, placed on a {surface} beside {props}. {lighting}, creating gentle shadows with subtle highlights on the product surface. Close-up shot at a 30-degree angle, shallow depth of field. {style}. Shot on a {camera}. Ultra-sharp detail, natural textures visible, professional color grading with clean, neutral tones.""",
    },
    "portrait": {
        "name": "Portrait Photography",
        "description": "Professional portrait with controlled lighting and style",
        "variables": {
            "subject": {"description": "Subject description", "default": "a confident young woman with auburn hair"},
            "clothing": {"description": "What they're wearing", "default": "a tailored charcoal blazer over a cream silk blouse"},
            "setting": {"description": "Background/setting", "default": "a sunlit architectural corridor with marble columns"},
            "lighting": {"description": "Lighting design", "default": "natural window light from the left with subtle fill bounce"},
            "camera": {"description": "Camera specs", "default": "Fujifilm X-T5 with an 85mm f/1.4 lens"},
            "mood": {"description": "Color grading/mood", "default": "warm, editorial color grading with soft skin tones"},
        },
        "template": """{subject} wearing {clothing}. Standing in {setting}. {lighting}, creating soft catchlights in the eyes and gentle shadows defining facial structure. Medium shot, slightly off-center composition with negative space. Shot on a {camera}, shallow depth of field with creamy bokeh. {mood}, reminiscent of magazine editorial photography.""",
    },
    "landscape": {
        "name": "Landscape Photography",
        "description": "Breathtaking landscape or nature scene",
        "variables": {
            "scene": {"description": "Main landscape", "default": "rolling Tuscan hills with cypress tree rows"},
            "sky": {"description": "Sky conditions", "default": "golden hour sky with dramatic cumulus clouds lit from below"},
            "foreground": {"description": "Foreground elements", "default": "a weathered stone path lined with wild poppies"},
            "camera": {"description": "Camera and lens", "default": "Nikon Z9 with a 24mm f/2.8 wide-angle lens"},
            "film": {"description": "Film stock or color grade", "default": "Kodak Ektar 100 with rich saturated earth tones"},
        },
        "template": """{scene} stretching toward the horizon under a {sky}. In the foreground, {foreground} leads the eye into the scene. Volumetric light rays pierce through the clouds, casting long warm shadows across the terrain. Shot on a {camera}, deep depth of field capturing sharp detail from foreground to infinity. Color grading reminiscent of {film}. Photorealistic, ultra-sharp, cinematic composition with rule-of-thirds framing.""",
    },
    "social-post": {
        "name": "Social Media Post",
        "description": "Eye-catching social media content",
        "variables": {
            "subject": {"description": "Main visual subject", "default": "a flat-lay of artisan coffee tools"},
            "background": {"description": "Background", "default": "warm walnut wood surface with natural grain"},
            "text_overlay": {"description": "Text to render on image", "default": "BREW BETTER"},
            "font": {"description": "Font style for text", "default": "bold condensed sans-serif in matte white"},
            "palette": {"description": "Color palette", "default": "warm earth tones with cream and espresso brown"},
            "aspect_ratio": {"description": "Aspect ratio", "default": "1:1"},
        },
        "template": """A {aspect_ratio} social media post image. {subject} arranged on a {background}. Bold {font} typography reads "{text_overlay}" positioned to complement the composition. {palette} color palette throughout. Soft overhead studio lighting with minimal shadows. Clean, modern aesthetic with professional art direction. High contrast, crisp focus, styled for maximum engagement.""",
    },
    "anime-character": {
        "name": "Anime Character",
        "description": "Anime/manga style character illustration",
        "variables": {
            "character": {"description": "Character description", "default": "a silver-haired elf mage with emerald eyes"},
            "outfit": {"description": "Outfit details", "default": "flowing midnight blue robes with golden runic embroidery"},
            "pose": {"description": "Pose and action", "default": "casting a spell, hands glowing with arcane energy"},
            "background": {"description": "Background scene", "default": "an ancient library filled with floating books and candlelight"},
            "style": {"description": "Anime sub-style", "default": "detailed anime illustration, Studio Ufotable quality"},
        },
        "template": """{character} wearing {outfit}. {pose}. Set against {background}. {style} with vibrant colors, detailed cel shading, dynamic lighting with rim light highlighting the character's silhouette. Detailed eyes with light reflections, flowing hair with individual strand detail. Clean line art with rich color fills, atmospheric particle effects.""",
    },
    "youtube-thumbnail": {
        "name": "YouTube Thumbnail",
        "description": "High-CTR YouTube thumbnail design",
        "variables": {
            "subject": {"description": "Main subject/person", "default": "a surprised tech reviewer holding a glowing device"},
            "headline": {"description": "Bold text overlay", "default": "YOU NEED THIS"},
            "background": {"description": "Background", "default": "vibrant gradient from electric blue to deep purple"},
            "accent_color": {"description": "Accent/highlight color", "default": "bright yellow"},
        },
        "template": """A 16:9 YouTube thumbnail. {subject} on the left side of frame, looking toward camera with an exaggerated expression. {background} behind them with {accent_color} accent elements and a subtle radial burst. Bold Impact font in {accent_color} with thick black outline reads "{headline}" on the right side. High saturation, punchy contrast, slightly over-lit face for visibility at small sizes. Professional studio lighting with strong key light. Designed for maximum click-through at thumbnail scale.""",
    },
}


def fill_template(template_name, variables=None):
    """Fill a template with provided variables, using defaults for missing ones."""
    if template_name not in BUILTIN_TEMPLATES:
        # Check custom templates
        custom_path = TEMPLATES_DIR / f"{template_name}.json"
        if custom_path.exists():
            with open(custom_path, "r", encoding="utf-8") as f:
                template_data = json.load(f)
        else:
            return {"error": f"Template '{template_name}' not found. Available: {', '.join(list_templates())}"}
    else:
        template_data = BUILTIN_TEMPLATES[template_name]

    variables = variables or {}
    template_str = template_data["template"]

    # Fill with provided values or defaults
    for var_name, var_info in template_data["variables"].items():
        value = variables.get(var_name, var_info["default"])
        template_str = template_str.replace(f"{{{var_name}}}", value)

    return {
        "template": template_name,
        "prompt": template_str,
        "variables_used": {k: variables.get(k, v["default"]) for k, v in template_data["variables"].items()},
    }


def list_templates():
    """List all available templates."""
    templates = {}
    for name, data in BUILTIN_TEMPLATES.items():
        templates[name] = {
            "name": data["name"],
            "description": data["description"],
            "variables": {k: v["description"] for k, v in data["variables"].items()},
        }

    # Add custom templates
    if TEMPLATES_DIR.exists():
        for f in TEMPLATES_DIR.glob("*.json"):
            with open(f, "r", encoding="utf-8") as fh:
                custom = json.load(fh)
                templates[f.stem] = {
                    "name": custom.get("name", f.stem),
                    "description": custom.get("description", ""),
                    "variables": {k: v["description"] for k, v in custom.get("variables", {}).items()},
                }

    return templates


def save_custom_template(name, template_data):
    """Save a custom template."""
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    path = TEMPLATES_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    return {"saved": str(path)}


def main():
    parser = argparse.ArgumentParser(description="Nano Banana Prompt Templates")
    sub = parser.add_subparsers(dest="command")

    # List templates
    sub.add_parser("list", help="List available templates")

    # Fill template
    fp = sub.add_parser("fill", help="Fill a template with variables")
    fp.add_argument("template", help="Template name")
    fp.add_argument("--var", "-v", action="append", nargs=2, metavar=("KEY", "VALUE"), help="Variable key=value pairs")

    # Show template details
    sp = sub.add_parser("show", help="Show template details and defaults")
    sp.add_argument("template", help="Template name")

    args = parser.parse_args()

    if args.command == "list":
        print(json.dumps(list_templates(), indent=2, ensure_ascii=False))

    elif args.command == "fill":
        variables = {}
        if args.var:
            for key, value in args.var:
                variables[key] = value
        result = fill_template(args.template, variables)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "show":
        templates = list_templates()
        if args.template in templates:
            detail = templates[args.template]
            if args.template in BUILTIN_TEMPLATES:
                detail["template_text"] = BUILTIN_TEMPLATES[args.template]["template"]
                detail["defaults"] = {k: v["default"] for k, v in BUILTIN_TEMPLATES[args.template]["variables"].items()}
            print(json.dumps(detail, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"error": f"Template '{args.template}' not found"}))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
