# FrostPrompt

An intelligent prompt engineering toolkit for Google's Nano Banana Pro and Nano Banana 2 image generation models. Not a static prompt collection — this is an **active prompt engineering system** with semantic search, quality scoring, batch generation, multi-model support, and iterative editing chains.

## What Makes This Different

| Feature | Static Collections | This Project |
|---------|-------------------|--------------|
| Search | Ctrl+F keywords | AI semantic search (understands meaning) |
| Prompt Creation | Copy-paste | 7 reusable templates + 5 Google frameworks |
| Quality Control | None | A+ to F grading against 10 criteria |
| Variations | Manual | Batch generator with 5 variation dimensions |
| Editing | Start over | Prompt chaining with 13 edit operations |
| Models | Single model | 6 models (Nano Banana, MJ, DALL-E, Flux, SD) |
| Export | None | JSON, Markdown, plain text, Gemini API payloads |
| Organization | None | Auto-tagging, history, favorites |
| Integration | None | Extensible skill system, CLI tools |

## Features

### 1. Searchable Database — 11,795 Prompts

**Keyword search** for exact matches:
```bash
python src/search.py search "product photography" --style photography --limit 5
```

**Semantic search** for conceptual matches:
```bash
python src/semantic.py search "peaceful spiritual scene with divine light" --limit 5
python src/semantic.py similar 12710 --limit 5  # Find prompts similar to ID 12710
```

**Tag-based filtering** across 4 dimensions:
```bash
python src/tagger.py filter --style photography --mood dramatic --limit 10
python src/tagger.py stats  # See full tag distribution
```

### 2. Prompt Quality Analyzer

Instant quality scoring with actionable improvement suggestions:
```bash
python src/analyze.py "A photo of a coffee cup"
# Grade F (24%) — missing 7 of 10 criteria

python src/analyze.py "A handcrafted ceramic mug with warm caramel glaze..."
# Grade A+ (90%) — all key elements present
```

10 criteria based on Google's official guidelines: subject specificity, lighting design, camera/lens, composition, visual style, color grading, materiality, text rendering, positive framing, narrative structure.

### 3. Reusable Templates

7 built-in templates for common use cases:
```bash
python src/templates.py list
python src/templates.py fill quote-card -v quote_text "Your quote here" -v font_style "calligraphy"
python src/templates.py fill product-shot -v product "leather watch" -v lighting "dramatic rim light"
```

Templates: `quote-card`, `product-shot`, `portrait`, `landscape`, `social-post`, `anime-character`, `youtube-thumbnail`

### 4. Batch Prompt Generation

Generate multiple variations at once:
```bash
# 5 variations with different lighting and color
python src/batch.py vary "A sunset over mountains" --count 5 --dimensions lighting color

# Same template, multiple subjects
python src/batch.py subjects --template "Professional headshot of {subject}" --subjects "a CEO" "an artist" "an athlete"

# Adapt for multiple aspect ratios
python src/batch.py ratios "A landscape scene" --ratios 1:1 9:16 16:9
```

### 5. Prompt Chaining (Iterative Editing)

Generate sequences of follow-up prompts for refining images:
```bash
# Get suggestions for what to edit
python src/chain.py suggest "A golden hour landscape with text quote"

# Generate an editing chain
python src/chain.py chain "base prompt" --edits '[{"operation": "change-lighting", "value": "neon nighttime"}]'
```

13 edit operations: change-background, change-lighting, change-style, change-colors, add-element, remove-element, change-text, change-outfit, change-time, change-season, upscale, change-angle, change-mood

### 6. Multi-Model Support

Adapt prompts for 6 different image generation models:
```bash
python src/multimodel.py format "your prompt" --model midjourney
python src/multimodel.py format "your prompt" --model stable-diffusion
python src/multimodel.py all "your prompt"  # All models at once
```

Models: `nano-banana-pro`, `nano-banana-2`, `midjourney`, `dall-e-3`, `flux`, `stable-diffusion`

### 7. Export Formats

```bash
python src/export.py single "prompt" --format json --save
python src/export.py single "prompt" --format markdown --save
python src/export.py single "prompt" --format api --model gemini-2.0-flash --ratio 9:16
```

### 8. History & Favorites

```bash
python src/history.py add "prompt" --model "Nano Banana Pro" --ratio "9:16"
python src/history.py list
python src/history.py fav "prompt" --name "My Best Prompt" --tags landscape golden-hour
python src/history.py favs
```

### 9. Extensible Skill System

Includes a skill definition file that can be integrated with LLM-powered workflows to orchestrate all tools above automatically.

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/nano-banana-prompt-engineer.git
cd nano-banana-prompt-engineer

# Core tools (no dependencies)
python src/search.py search "sunset landscape" --limit 5
python src/analyze.py "your prompt here"
python src/templates.py fill quote-card -v quote_text "Hello World"
python src/batch.py vary "a mountain scene" --count 3

# Semantic search (requires sentence-transformers)
pip install sentence-transformers
python src/semantic.py build    # One-time: builds embeddings cache (~4 min)
python src/semantic.py search "peaceful nature scene" --limit 5
```

### As an LLM Skill
Copy `.claude/skills/nano-banana.md`, `src/`, and `prompts/` to your project. The skill file contains the complete knowledge base and tool orchestration instructions, compatible with any LLM workflow.

## Model Quick Reference

| Spec | Nano Banana 2 | Nano Banana Pro |
|------|---------------|-----------------|
| Base Model | Gemini 3.1 Flash Image | Gemini 3 Pro Image |
| Input Tokens | 131,072 | 65,536 |
| Output Tokens | 32,768 | 32,768 |
| Resolutions | 0.5K, 1K, 2K, 4K | 1K, 2K, 4K |
| Aspect Ratios | 14 options | 10 options |
| Ref Images | Up to 14 | Up to 14 |
| Best For | Speed, iteration | Complex scenes |

## Project Structure

```
nano-banana-prompt-engineer/
├── .claude/skills/
│   └── nano-banana.md          # LLM skill definition
├── src/
│   ├── search.py               # Keyword search engine
│   ├── semantic.py             # AI semantic search (sentence-transformers)
│   ├── analyze.py              # Prompt quality analyzer (A+ to F)
│   ├── tagger.py               # Auto-tagging system (style/use-case/subject/mood)
│   ├── templates.py            # Reusable prompt templates
│   ├── batch.py                # Batch variation generator
│   ├── chain.py                # Iterative editing chains
│   ├── multimodel.py           # Multi-model prompt formatter
│   ├── history.py              # History & favorites
│   └── export.py               # Multi-format export
├── prompts/
│   └── database.csv            # 11,795 curated prompts
├── templates/                  # Custom user templates
├── examples/
│   └── frameworks.md           # Detailed framework examples
├── exports/                    # Saved exports
├── README.md
└── LICENSE
```

## Requirements

- **Core tools**: Python 3.8+ (no external dependencies)
- **Semantic search**: `pip install sentence-transformers` (downloads ~90MB model on first use)

## Contributing

Contributions welcome! Add prompts, improve search scoring, add templates, submit framework examples, or report bugs.

## License

MIT License. Prompt database is community-sourced for educational purposes with original authors credited.

Built by [Daniel Beglaryan](https://github.com/dbeglaryan) | [CipherForces](https://cipherforces.com)
