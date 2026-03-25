#!/usr/bin/env python3
"""
Nano Banana Prompt Chaining
Generates sequences of follow-up editing prompts for iterative refinement.
"""

import json
import sys
import argparse


# Common editing operations with prompt templates
EDIT_OPERATIONS = {
    "change-background": {
        "description": "Change the background/setting",
        "template": "Keep the subject exactly the same — same pose, lighting on the subject, and all details. Change only the background to {value}.",
    },
    "change-lighting": {
        "description": "Change the lighting",
        "template": "Keep everything the same but change the lighting to {value}. Maintain the same subject, composition, and setting.",
    },
    "change-style": {
        "description": "Change the visual style",
        "template": "Recreate this exact scene with the same composition and subjects, but render it in {value} style.",
    },
    "change-colors": {
        "description": "Change the color grading",
        "template": "Keep the scene identical but apply {value} color grading. Maintain all subjects, composition, and lighting.",
    },
    "add-element": {
        "description": "Add an element to the scene",
        "template": "Add {value} to the scene. Keep everything else exactly the same — same subject, background, lighting, and composition.",
    },
    "remove-element": {
        "description": "Remove an element from the scene",
        "template": "Remove {value} from the image. Fill the space naturally with the surrounding background. Keep everything else identical.",
    },
    "change-text": {
        "description": "Change rendered text",
        "template": "Keep the entire image identical but change the text to read \"{value}\". Maintain the same font style, size, color, and position.",
    },
    "change-outfit": {
        "description": "Change what the subject is wearing",
        "template": "Keep the same person, pose, background, and lighting. Change only their outfit to {value}.",
    },
    "change-time": {
        "description": "Change time of day",
        "template": "Transform this scene to {value}. Adjust lighting, sky, shadows, and ambient color accordingly while keeping all subjects and composition the same.",
    },
    "change-season": {
        "description": "Change the season",
        "template": "Transform this scene to {value}. Adjust vegetation, sky, lighting warmth, and atmospheric conditions accordingly while keeping subjects and composition the same.",
    },
    "upscale": {
        "description": "Request higher detail/resolution",
        "template": "Regenerate this exact image with more detail. Add finer textures, sharper edges, and more intricate details throughout. Maintain the exact same composition, subjects, and style.",
    },
    "change-angle": {
        "description": "Change the camera angle",
        "template": "Show this same scene from {value}. Keep all subjects, lighting, and style the same but change the camera perspective.",
    },
    "change-mood": {
        "description": "Change the emotional mood",
        "template": "Keep the same scene and subjects but shift the mood to {value}. Adjust lighting, color grading, and atmospheric effects to match.",
    },
}


def generate_chain(base_prompt, edits):
    """Generate a chain of editing prompts.

    edits: list of dicts with 'operation' and 'value' keys
    """
    chain = [{"step": 0, "type": "generate", "prompt": base_prompt}]

    for i, edit in enumerate(edits):
        op = edit.get("operation", "")
        value = edit.get("value", "")

        if op in EDIT_OPERATIONS:
            template = EDIT_OPERATIONS[op]["template"]
            edit_prompt = template.replace("{value}", value)
        else:
            edit_prompt = f"{op}: {value}"

        chain.append({
            "step": i + 1,
            "type": "edit",
            "operation": op,
            "prompt": edit_prompt,
        })

    return chain


def suggest_edits(base_prompt):
    """Suggest possible editing chains based on the prompt content."""
    text_lower = base_prompt.lower()
    suggestions = []

    # Always suggest these
    suggestions.append({
        "operation": "change-lighting",
        "examples": ["golden hour backlighting", "dramatic noir lighting", "soft overcast diffused light", "neon-lit nighttime"]
    })
    suggestions.append({
        "operation": "change-style",
        "examples": ["watercolor illustration", "oil painting", "anime", "vintage film photograph"]
    })
    suggestions.append({
        "operation": "change-colors",
        "examples": ["warm sepia tones", "cool blue cinematic", "high contrast black and white", "pastel palette"]
    })

    # Context-specific suggestions
    if any(w in text_lower for w in ["outdoor", "landscape", "sky", "sun", "field", "mountain", "street"]):
        suggestions.append({
            "operation": "change-time",
            "examples": ["sunset golden hour", "blue hour twilight", "midnight with starry sky", "overcast rainy day"]
        })
        suggestions.append({
            "operation": "change-season",
            "examples": ["autumn with golden foliage", "winter with fresh snow", "spring with cherry blossoms", "summer with lush green"]
        })

    if any(w in text_lower for w in ["person", "model", "man", "woman", "character", "portrait"]):
        suggestions.append({
            "operation": "change-outfit",
            "examples": ["formal black tuxedo", "casual streetwear", "traditional cultural attire", "futuristic sci-fi armor"]
        })

    if any(w in text_lower for w in ["text", "quote", "title", "headline", '"']):
        suggestions.append({
            "operation": "change-text",
            "examples": ["Your custom text here"]
        })

    suggestions.append({
        "operation": "change-background",
        "examples": ["a neon-lit Tokyo alley at night", "a sun-drenched Mediterranean coast", "a cozy coffee shop interior", "deep space with nebula"]
    })

    suggestions.append({
        "operation": "change-angle",
        "examples": ["a low angle looking up", "an aerial bird's eye view", "an extreme close-up", "a wide establishing shot"]
    })

    return suggestions


def list_operations():
    """List all available editing operations."""
    return {k: v["description"] for k, v in EDIT_OPERATIONS.items()}


def main():
    parser = argparse.ArgumentParser(description="Prompt Chaining for Iterative Editing")
    sub = parser.add_subparsers(dest="command")

    # Generate chain
    cp = sub.add_parser("chain", help="Generate an editing chain")
    cp.add_argument("prompt", help="Base prompt")
    cp.add_argument("--edits", "-e", required=True, help="JSON array of edits: [{\"operation\": \"...\", \"value\": \"...\"}]")

    # Suggest edits
    sp = sub.add_parser("suggest", help="Suggest possible edits for a prompt")
    sp.add_argument("prompt", help="Base prompt to analyze")

    # List operations
    sub.add_parser("operations", help="List available editing operations")

    args = parser.parse_args()

    if args.command == "chain":
        edits = json.loads(args.edits)
        chain = generate_chain(args.prompt, edits)
        print(json.dumps(chain, indent=2, ensure_ascii=False))

    elif args.command == "suggest":
        suggestions = suggest_edits(args.prompt)
        print(json.dumps(suggestions, indent=2, ensure_ascii=False))

    elif args.command == "operations":
        print(json.dumps(list_operations(), indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
