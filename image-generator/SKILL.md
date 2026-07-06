---
name: image-generator
description: Generates images from text descriptions using the Pollinations AI service (no API key required) and displays them directly in the conversation. Use this skill whenever the user asks to create, generate, draw, make, render, or show an image, picture, illustration, artwork, photo, avatar, icon, or any other visual of something — including casual phrasing like "can I get a pic of X", "draw me X", "I need an image for Y", or "what would X look like". Always trigger this even if the user doesn't say the word "image" explicitly but is clearly asking for a picture of something. Do not just describe what an image would look like in words — actually generate and display it with this skill.
---

# Image Generator (Pollinations AI)

Turns a user's request into a rendered image using Pollinations AI's free, keyless image
endpoint. The core idea: users rarely write great image-generation prompts on the first try,
so this skill's job is to translate their intent into a prompt that actually produces a good
image, then show the result — not just hand back a URL.

## Workflow

1. **Understand the request.** Figure out the subject, whether the user already specified a
   style, mood, or composition, and whether they hint at a particular shape/use for the image
   (portrait, landscape, icon, wallpaper, etc.) — see the sizing guide below.
2. **Enhance the prompt** (see rules below).
3. **Generate the image** with `scripts/generate_image.py`, which builds the URL and tries to
   download the image to a local file in the same step (see Building the image below).
4. **Show the result two ways**, since Markdown image embeds of external URLs don't reliably
   render in every Claude interface:
   - Embed it inline with Markdown image syntax so it shows up immediately if the interface
     supports it: `![description](https://image.pollinations.ai/prompt/...)`
   - If the download succeeded, also save the file locally and present it
     as a file (e.g. via `present_files`) so the user has a reliable way to view/download it
     even if the inline embed doesn't render for them.
   - If the download failed (e.g. no network access to `image.pollinations.ai` in this
     environment), fall back to the Markdown embed alone and don't block on the file step.
5. Optionally follow up with the original and enhanced prompt (see Response Format).

## Prompt enhancement rules

Good image prompts are specific and sensory. When enhancing a prompt, look for opportunities to
add (without changing what the user actually asked for):

- **Style** — realistic photo, anime, digital painting, watercolor, 3D render, pixel art, etc.
- **Lighting** — cinematic lighting, golden hour, volumetric light, soft studio light, neon glow
- **Composition / camera angle** — wide shot, close-up, low angle, aerial view, rule of thirds
- **Environment / setting** — where the scene takes place and what's around the subject
- **Color palette** — vibrant, muted, monochrome, pastel, high contrast
- **Quality descriptors** — highly detailed, ultra detailed, masterpiece, 8k, sharp focus
- **Artistic extras** — mood, atmosphere, texture, small storytelling details

**How much to change:**
- If the request is short and vague ("cat astronaut", "dragon over tokyo"), do a full rewrite
  into a rich, vivid prompt across most of the categories above.
- If the user already wrote a detailed prompt, only lightly polish it — add a missing category
  or two (e.g. they described the scene but not the lighting), don't restructure what they wrote.
- If the user specifies a style (anime, oil painting, photorealistic, pixel art, etc.), keep that
  style — don't override it with a different one.
- If no style is specified, infer one that fits the subject naturally.
- Never change the subject, characters, or core intent of the request. Enhancement adds detail,
  it doesn't redirect the idea.
- If the user explicitly asks to use their exact raw prompt (e.g. "use exactly this prompt",
  "don't change my wording"), skip enhancement and encode their text as-is.

### Examples

**User:** `cat astronaut`
**Enhanced:** `Cute orange cat astronaut standing on the moon wearing a futuristic spacesuit, Earth visible in the background, cinematic lighting, ultra detailed digital art, masterpiece, vibrant colors, 8k.`

**User:** `dragon over tokyo`
**Enhanced:** `Epic fantasy artwork of a gigantic glowing dragon flying above futuristic Tokyo at night, neon signs illuminating the city, dramatic clouds, volumetric lighting, cinematic composition, highly detailed digital painting, masterpiece, 8k.`

**User:** `a golden retriever sitting in a sunlit meadow, photorealistic` (already detailed + styled)
**Enhanced:** `A golden retriever sitting in a sunlit meadow, photorealistic, soft golden-hour lighting, shallow depth of field, tall grass swaying gently, warm color palette, sharp focus, high detail.` (style kept, only lighting/composition lightly added)

## Building the image

`scripts/generate_image.py` builds the Pollinations URL (handling URL-encoding of the prompt,
since spaces, punctuation, and special characters all need proper percent-encoding) and then
tries to download the resulting image to a local file in one step:

```bash
python3 scripts/generate_image.py "Cute orange cat astronaut standing on the moon..." \
  --width 1024 --height 1024 --out cat-astronaut.png
```

It prints a `URL:` line (always) and, if the download succeeded, a `FILE:` line with the saved
path. Use the `FILE:` path with your file-presenting tool; use the `URL:` line for the Markdown
embed. If only `URL:` appears, the download failed (e.g. this environment can't reach
`image.pollinations.ai`) — that's fine, just use the embed on its own.

**Seed — default to random.** Each run picks a random seed automatically unless you pass
`--seed <n>`. This matters because the same prompt + same seed always produces the exact same
image — good when the user wants to iterate on one image (keep the seed fixed while you tweak
the prompt) or reproduce a result, but wrong as a default since most requests expect a fresh
image each time. Only pass an explicit seed when the user is refining/regenerating the same
concept and you want continuity, or when they ask for a specific result to be reproducible.

**Width/height — adapt to the request, don't default blindly to square.** Read what the image
is *for* and pick dimensions that fit:

| Use case / hint from the user | width x height |
|---|---|
| Default / unspecified, general picture | 1024 x 1024 |
| Portrait, phone wallpaper, character art | 768 x 1024 |
| Landscape, scenery, desktop wallpaper | 1024 x 768 |
| Widescreen wallpaper, banner | 1920 x 1080 |
| Icon, avatar, small square asset | 512 x 512 |

These are starting points, not a rigid table — if the user gives an explicit size or ratio,
use that instead.

## Response format

Whenever a user requests an image:

1. Build the enhanced prompt, then run `generate_image.py` to get the URL (and, if possible,
   a downloaded file).
2. Render the image inline with Markdown image syntax — never paste the raw URL as plain text.
3. If a file was downloaded, save it locally and present it as a file
   too, so there's a reliable way to view it regardless of interface.
4. Optionally, underneath the image, briefly show the prompts so the user can see what was generated and tweak it if they want:

```
🎨 Prompt: <original prompt>

✨ Enhanced Prompt:
<enhanced prompt>
```

Skip this breakdown for trivial/casual requests where it would feel like clutter — use judgment.

## Important rules

- Never send the user's raw, unenhanced prompt to Pollinations unless they explicitly ask for
  their exact wording to be used.
- Preserve the user's intent — enhancement adds sensory/technical detail, it never changes who
  or what is in the image.
- The final deliverable is the rendered image (and, when possible, a downloadable file) — not
  just a link or a URL string.
- Default to a random seed per image; only fix the seed when the user is iterating on one image
  or explicitly wants a reproducible result.
- Pick width/height to fit the request (see sizing guide) instead of always using 1024x1024.
- If the user asks for multiple images or variations, generate each with its own enhanced prompt
  and let the seed vary naturally (don't reuse the same seed across different variations) and
  render each one inline.
