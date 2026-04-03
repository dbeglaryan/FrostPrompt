#!/usr/bin/env python3
"""
Generate one image at a time from a job file.
Waits for you to press Enter between each generation.

Usage:
  python src/generate_one.py prompts/jobs/starprep-sonography-diagrams.json
  python src/generate_one.py prompts/jobs/starprep-sonography-diagrams.json --start 5
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: pip install google-genai")
    sys.exit(1)

MODELS = {
    "pro": "nano-banana-pro-preview",
    "flash": "gemini-3.1-flash-image-preview",
    "gemini-3-pro": "gemini-3-pro-image-preview",
    "imagen": "imagen-4.0-generate-001",
}


def load_key():
    for p in [Path.cwd() / ".env", Path(__file__).parent.parent / ".env"]:
        if p.exists():
            for line in open(p):
                if line.startswith("GEMINI_API_KEY="):
                    return line.strip().split("=", 1)[1].strip().strip('"')
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    print("No API key found. Set GEMINI_API_KEY or create .env")
    sys.exit(1)


def generate(client, prompt, model_key, output_path, max_retries=3):
    model = MODELS.get(model_key, MODELS["pro"])
    config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])

    for attempt in range(1, max_retries + 1):
        try:
            print(f"  Attempt {attempt}/{max_retries}...")
            r = client.models.generate_content(
                model=model,
                contents=[types.Part.from_text(text=prompt)],
                config=config,
            )
            if r.candidates:
                for part in r.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        data = part.inline_data.data
                        if isinstance(data, str):
                            data = base64.b64decode(data)
                        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(data)
                        print(f"  Saved: {output_path} ({len(data):,} bytes)")
                        return True
                    elif part.text:
                        print(f"  Model returned text: {part.text[:150]}")

            if attempt < max_retries:
                delay = 10 * attempt
                print(f"  No image. Retrying in {delay}s...")
                time.sleep(delay)

        except Exception as e:
            err = str(e)
            if "429" in err:
                delay = 30 * attempt
                print(f"  Rate limited. Waiting {delay}s...")
                time.sleep(delay)
            else:
                print(f"  Error: {err[:200]}")
                if attempt < max_retries:
                    time.sleep(10)
                else:
                    return False
    return False


def main():
    parser = argparse.ArgumentParser(description="Generate one image at a time")
    parser.add_argument("job_file", help="Path to job JSON file")
    parser.add_argument("--start", type=int, default=1, help="Start from prompt number (1-indexed)")
    args = parser.parse_args()

    with open(args.job_file, "r", encoding="utf-8") as f:
        job = json.load(f)

    defaults = job.get("defaults", {})
    prompts = job["prompts"]
    output_dir = Path(job.get("output_dir", "output"))
    total = len(prompts)

    client = genai.Client(api_key=load_key())

    print(f"\nJob: {job['name']}")
    print(f"Total prompts: {total}")
    print(f"Starting from: #{args.start}")
    print(f"Output: {output_dir}/")
    print("=" * 50)

    for i, p in enumerate(prompts, 1):
        if i < args.start:
            continue

        pid = p.get("id", f"prompt_{i}")
        model = p.get("model", defaults.get("model", "pro"))
        filename = p.get("filename", f"{pid}.png")
        out_path = output_dir / filename

        if out_path.exists():
            print(f"\n[{i}/{total}] {pid} — already exists, skipping")
            continue

        print(f"\n[{i}/{total}] {pid}")
        print(f"  Model: {model}")
        print(f"  Prompt: {p['prompt'][:100]}...")

        try:
            input("  Press Enter to generate (Ctrl+C to quit)... ")
        except KeyboardInterrupt:
            print("\n\nStopped. Resume with: --start", i)
            sys.exit(0)

        ok = generate(client, p["prompt"], model, out_path)
        if ok:
            print(f"  Done!")
        else:
            print(f"  FAILED — try again later with: --start {i}")


if __name__ == "__main__":
    main()
