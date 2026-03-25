# Nano Banana Prompting Frameworks - Detailed Examples

## Framework 1: Image Generation

### Text-to-Image (No References)

**Formula:** `[Subject] + [Action] + [Location/Context] + [Composition] + [Style]`

**Example 1 - Fashion Editorial:**
```
A striking fashion model wearing a tailored brown dress, sleek boots, and holding a structured handbag. Posing with a confident, statuesque stance, slightly turned. A seamless, deep cherry red studio backdrop. Medium-full shot, center-framed. Fashion magazine style editorial, shot on medium-format analog film, pronounced grain, high saturation, cinematic lighting effect.
```

**Example 2 - Product Shot:**
```
A minimalist ceramic coffee mug with a matte sage green glaze, steam rising gently from fresh black coffee. Placed on a raw concrete countertop beside a single eucalyptus sprig. Soft, diffused overhead lighting from a large softbox, creating gentle shadows. Close-up shot at a 30-degree angle, shallow depth of field. Clean, Scandinavian-inspired commercial photography style.
```

**Example 3 - Fantasy Scene:**
```
An ancient elven library carved into a living tree, shelves of leather-bound tomes glowing with soft bioluminescent light. A cloaked scholar sits reading at a massive oak desk, their face illuminated by a floating crystal orb. Volumetric light rays pierce through gaps in the bark canopy above. Wide-angle establishing shot showing the full vertical scale of the space. Painterly fantasy illustration style with rich, saturated jewel tones.
```

### Multimodal (With Reference Images)

**Formula:** `[Reference images] + [Relationship instruction] + [New scenario]`

**Example:**
```
Using the attached napkin sketch as the structure and the attached fabric sample as the texture, transform this into a high-fidelity 3D armchair render. Place it in a sun-drenched, minimalist living room with floor-to-ceiling windows and warm oak flooring.
```

## Framework 2: Image Editing

### Conversational Editing (Inpainting)
```
Remove the man from the photo. Keep the background, lighting, and perspective exactly the same.
```

### Style Transfer
```
Recreate the exact content of this photograph — same composition, same subjects, same layout — but render it in the style of a Van Gogh painting with visible brushstrokes and swirling sky.
```

### Adding Elements
```
Place the product from image 1 onto the table in image 2. Match the lighting, shadows, and perspective of the target scene. The product should look like it was photographed there originally.
```

## Framework 3: Real-Time Information

**Formula:** `[Source/Search request] + [Analytical task] + [Visual translation]`

**Example 1:**
```
Search for the current weather and date in San Francisco. If it's raining, create a scene of the Golden Gate Bridge under grey, rainy skies. Visualize this as a miniature city-in-a-cup concept embedded within a realistic, modern smartphone UI.
```

**Example 2:**
```
Look up the current top 5 programming languages by popularity. Create a clean, modern infographic bar chart comparing them, using each language's brand color. Style it as a polished LinkedIn post with the title "Top Programming Languages 2026" in a bold sans-serif font.
```

## Framework 4: Text Rendering & Localization

**Example 1 - Product Mockup with Multi-line Text:**
```
A high-end, glossy commercial beauty shot of a sleek, minimalist nude-colored face moisturizer jar resting on a warm studio background. The lighting is soft and radiant. Next to the product, render three lines of text: the word "GLOW" in a flowing, elegant Brush Script font at the top, "10% OFF" in a heavy, blocky Impact font in the middle, and "Your First Order" in a thin, minimalist Century Gothic font at the bottom.
```

**Example 2 - Typographic Poster:**
```
A typographic poster with a solid black background. Bold letters spell "New York", filling the center of the frame. The text acts as a cut-out window. A photograph of the New York skyline is visible only inside the letterforms. The surrounding area remains solid black.
```

**Example 3 - Localized Marketing:**
```
Create a travel poster for Tokyo with the headline "EXPLORE" in English and its Japanese translation "探検する" below it. Use a clean, modern sans-serif font for English and a complementary brush-style font for Japanese. Cherry blossom petals frame the edges.
```

## Framework 5: Creative Director Mode

### Lighting Design Examples

**Studio Setup:**
```
...lit with a classic three-point softbox setup: key light at 45 degrees camera-left, fill light at half intensity camera-right, and a hair light from behind creating a subtle rim glow on the subject's shoulders.
```

**Dramatic:**
```
...Chiaroscuro lighting with harsh, high contrast. A single hard light source from the upper left casting deep, defined shadows. The rest of the scene falls into near-darkness.
```

**Golden Hour:**
```
...golden hour backlighting creating long shadows stretching toward the camera. The sun is just above the horizon, wrapping everything in warm amber light with gentle lens flare.
```

### Camera & Lens Examples

**Immersive Action:**
```
...shot on a GoPro mounted at ground level, capturing the intense distorted wide-angle perspective of a skateboarder mid-trick.
```

**Portrait:**
```
...shot on a Fujifilm X-T5 with an 85mm f/1.4 lens, shallow depth of field creating silky smooth bokeh in the background.
```

**Documentary:**
```
...shot on a cheap disposable camera, slightly overexposed, with that raw, unpolished flash aesthetic and muted plastic-lens color rendition.
```

### Color Grading Examples

**Nostalgic:**
```
...rendered as if on 1980s Kodak Ektachrome film, slightly grainy, with warm yellows and softened highlights.
```

**Modern Cinematic:**
```
...cinematic color grading with muted teal-and-orange split toning, lifted blacks, and desaturated midtones.
```

**High Fashion:**
```
...crisp, high-contrast color grading with punchy saturated primaries against clean white backgrounds.
```

### Materiality Examples

Instead of generic descriptions, use specific materials:

| Generic | Specific |
|---------|----------|
| suit jacket | navy blue tweed with herringbone pattern |
| armor | ornate elven plate armor, etched with silver leaf patterns |
| mug | minimalist ceramic coffee mug with a matte sage glaze |
| table | weathered oak farmhouse table with visible grain |
| dress | flowing champagne silk charmeuse gown |
| wall | exposed red brick with crumbling mortar joints |
| floor | polished Carrara marble with grey veining |

## Combining Frameworks

The most powerful prompts combine multiple frameworks:

```
[Framework 1: Generation] A master perfumer in her atelier, examining a crystal flacon of amber-colored perfume against the light.
[Framework 5: Lighting] Warm, diffused window light from the left, casting a golden glow through the liquid.
[Framework 5: Camera] Shot on a Hasselblad with an 80mm lens at f/2.8, creating a dreamy shallow depth of field.
[Framework 5: Color] Color graded like a Wes Anderson film — warm pastels, symmetrical framing, with a hint of pink.
[Framework 5: Materials] The atelier features dark mahogany shelving, hundreds of tiny glass vials, brass fixtures, and a worn leather-topped desk.
```

**Combined prompt:**
```
A master perfumer in her atelier, examining a crystal flacon of amber-colored perfume against the light. Warm, diffused window light from the left, casting a golden glow through the liquid. The atelier features dark mahogany shelving, hundreds of tiny glass vials, brass fixtures, and a worn leather-topped desk. Shot on a Hasselblad with an 80mm lens at f/2.8, creating a dreamy shallow depth of field. Color graded like a Wes Anderson film — warm pastels, symmetrical framing, with a hint of pink.
```
