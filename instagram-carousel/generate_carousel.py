#!/usr/bin/env python3
# /usr/bin/python3 generate_carousel.py input.json [--output-dir ./out]
"""
Minimalist Instagram carousel -- Simon Sinek style.
Solid color bg + Courier New + left-aligned text.
Colors rotate per slide from a palette.

Supports inline markup:
  *text*  → accent color (gold/custom)
  _text_  → underline
  ~text~  → italic

Supports brand styles:
  "classic"  — Bold, dark palette (default)
  "minimal"  — Regular weight, softer dark palette
  "contrast" — Bold, first slide white rest dark
  "warm"     — Bold, warm dark palette

Input JSON:
{
  "slides": [
    {"text": "Primera línea.\nSegunda línea."},
    {"text": "Otra *idea* importante."}
  ],
  "brand": {
    "palette": ["#111118", "#1A2B5E", "#2A1F5E", "#0D2B1A"],
    "handle": "@yourhandle",
    "style": "classic"
  }
}
"""

import json, sys, os, argparse, re
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Install: /usr/bin/python3 -m pip install Pillow"); sys.exit(1)

SIZE = 1080
LEFT_MARGIN = 130
RIGHT_MARGIN = 120
MAX_FONT = 120
MIN_FONT = 38
BOTTOM_HANDLE_Y = SIZE - 110
ACCENT_COLOR_DEFAULT = (255, 215, 0)  # dorado

COURIER_BOLD = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
COURIER_BOLD_ITALIC = "/System/Library/Fonts/Supplemental/Courier New Bold Italic.ttf"
COURIER_REGULAR = "/System/Library/Fonts/Supplemental/Courier New.ttf"
COURIER_ITALIC = "/System/Library/Fonts/Supplemental/Courier New Italic.ttf"

COURIER_FALLBACKS = [
    COURIER_BOLD, COURIER_REGULAR,
    "/System/Library/Fonts/Courier.ttc",
    "/Library/Fonts/Courier New.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

# -- Styles ------------------------------------------------------------------

STYLES = {
    "classic": {
        "font_base": COURIER_BOLD,
        "font_italic": COURIER_BOLD_ITALIC,
        "palette": ["#0a0a12", "#0d1a40", "#1a0a0d", "#081820", "#0d0d08"],
        "accent": (255, 215, 0),
    },
    "minimal": {
        "font_base": COURIER_REGULAR,
        "font_italic": COURIER_ITALIC,
        "palette": ["#1a1a2e", "#16213e", "#0f3460", "#1a1a2e", "#16213e"],
        "accent": (100, 200, 255),
    },
    "contrast": {
        "font_base": COURIER_BOLD,
        "font_italic": COURIER_BOLD_ITALIC,
        "palette": ["#f0f0f0", "#0d1a40", "#1a0a0d", "#081820", "#0d0d08"],
        "accent": (255, 180, 0),
    },
    "warm": {
        "font_base": COURIER_BOLD,
        "font_italic": COURIER_BOLD_ITALIC,
        "palette": ["#1a0a00", "#2d1b00", "#0d1a0d", "#1a0d0d", "#1a1200"],
        "accent": (255, 160, 60),
    },
}

# -- Font cache ---------------------------------------------------------------

_FONT_CACHE = {}

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def load_font(path, size):
    key = (path, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    font = None
    if os.path.exists(path):
        try:
            font = ImageFont.truetype(path, size)
        except Exception:
            pass
    if font is None:
        for fallback in COURIER_FALLBACKS:
            if os.path.exists(fallback):
                try:
                    font = ImageFont.truetype(fallback, size)
                    break
                except Exception:
                    continue
    _FONT_CACHE[key] = font or ImageFont.load_default()
    return _FONT_CACHE[key]

def text_w(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]

# -- Markup parser ------------------------------------------------------------

def parse_markup(line):
    """Parse *accent*, _underline_, ~italic~ markup.
    Returns list of (text, style) tuples.
    Style: 'normal', 'accent', 'underline', 'italic'
    """
    segments = []
    pattern = re.compile(r'(\*([^*]+)\*|_([^_]+)_|~([^~]+)~)')
    last = 0
    for m in pattern.finditer(line):
        if m.start() > last:
            segments.append((line[last:m.start()], 'normal'))
        if m.group(2) is not None:
            segments.append((m.group(2), 'accent'))
        elif m.group(3) is not None:
            segments.append((m.group(3), 'underline'))
        elif m.group(4) is not None:
            segments.append((m.group(4), 'italic'))
        last = m.end()
    if last < len(line):
        segments.append((line[last:], 'normal'))
    if not segments:
        segments.append((line, 'normal'))
    return segments

def plain_text(line):
    """Strip markup for length calculation."""
    return re.sub(r'[*_~]', '', line)

# -- Font sizing --------------------------------------------------------------

def auto_font_size(lines):
    available_w = SIZE - LEFT_MARGIN - RIGHT_MARGIN
    available_h = 680
    longest = max((len(plain_text(l)) for l in lines), default=1)
    n = len(lines)
    size_w = int(available_w / (longest * 0.601))
    size_h = int(available_h / (n * 1.42))
    return max(MIN_FONT, min(MAX_FONT, min(size_w, size_h)))

def auto_font_size_global(max_lines, max_chars):
    available_w = SIZE - LEFT_MARGIN - RIGHT_MARGIN
    available_h = 680
    size_w = int(available_w / (max_chars * 0.601))
    size_h = int(available_h / (max_lines * 1.42))
    return max(MIN_FONT, min(MAX_FONT, min(size_w, size_h)))

# -- Drawing ------------------------------------------------------------------

def draw_styled_line(draw, x, y, line, font_base, font_italic, font_size,
                     text_color, accent_color):
    """Draw a single line with markup effects."""
    segments = parse_markup(line)
    cursor_x = x
    for text, style in segments:
        if style == 'italic':
            font = font_italic
            color = text_color
        elif style == 'accent':
            font = font_base
            color = accent_color
        else:
            font = font_base
            color = text_color

        draw.text((cursor_x, y), text, font=font, fill=color)
        w = text_w(draw, text, font)

        if style == 'underline':
            line_y = y + font_size + 2
            draw.line([(cursor_x, line_y), (cursor_x + w, line_y)],
                      fill=text_color, width=max(2, font_size // 20))

        cursor_x += w

def generate_slide(slide, bg_color_hex, handle, num, total, out,
                   uniform_font_size=None, style_config=None):
    style_config = style_config or STYLES["classic"]
    bg = hex_to_rgb(bg_color_hex)
    text = slide.get("text", "").rstrip()

    brightness = sum(bg) / 3
    text_color = (20, 20, 20) if brightness > 160 else (255, 255, 255)
    accent_color = style_config.get("accent", ACCENT_COLOR_DEFAULT)

    img = Image.new("RGB", (SIZE, SIZE), bg)
    draw = ImageDraw.Draw(img)

    lines = text.split("\n")
    font_size = uniform_font_size if uniform_font_size else auto_font_size(lines)
    font_base = load_font(style_config["font_base"], font_size)
    font_italic = load_font(style_config["font_italic"], font_size)
    line_height = int(font_size * 1.42)

    # Calcular altura total incluyendo subtítulo
    subtitle = slide.get("subtitle", "")
    sub_size = max(32, int(font_size * 0.6))
    sub_height = int(sub_size * 1.42) + line_height // 2 if subtitle else 0
    total_text_h = len(lines) * line_height + sub_height

    # Centrar verticalmente
    usable_top = 80
    usable_bottom = BOTTOM_HANDLE_Y - 40
    usable_h = usable_bottom - usable_top
    y = usable_top + (usable_h - total_text_h) // 2

    for line in lines:
        draw_styled_line(draw, LEFT_MARGIN, y, line,
                         font_base, font_italic, font_size,
                         text_color, accent_color)
        y += line_height

    # Subtítulo en fuente más pequeña (opcional)
    if subtitle:
        sub_font = load_font(style_config["font_base"], sub_size)
        sub_color = (tuple(min(255, c + 160) for c in bg) if brightness < 160
                     else tuple(max(0, c - 160) for c in bg))
        y += line_height // 2
        draw.text((LEFT_MARGIN, y), subtitle, font=sub_font, fill=sub_color)

    if handle:
        fh = load_font(style_config["font_base"], 30)
        hw = text_w(draw, handle, fh)
        draw.text(((SIZE - hw) // 2, BOTTOM_HANDLE_Y), handle, font=fh, fill=text_color)

    img.save(out, "PNG")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("--output-dir", default="./carousel_output")
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    slides = data.get("slides", [])
    brand = data.get("brand", {})
    handle = brand.get("handle", "")

    # Style
    style_name = brand.get("style", "classic")
    style_config = STYLES.get(style_name, STYLES["classic"])

    # Palette: use brand palette if provided, else style default
    palette = brand.get("palette", style_config["palette"])
    if not palette:
        palette = style_config["palette"]

    if not slides:
        print("No slides."); sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = len(slides)

    # Calcular tamaño de fuente UNIFORME basado en la slide más larga
    all_max_lines = 0
    all_max_chars = 0
    for slide in slides:
        lines = slide.get("text", "").split("\n")
        all_max_lines = max(all_max_lines, len(lines))
        all_max_chars = max(all_max_chars, max((len(plain_text(l)) for l in lines), default=1))
    uniform_font_size = auto_font_size_global(all_max_lines, all_max_chars)

    for i, slide in enumerate(slides, 1):
        bg = palette[(i - 1) % len(palette)]
        out = str(out_dir / f"slide_{i:02d}.png")
        generate_slide(slide, bg, handle, i, total, out,
                       uniform_font_size, style_config)
        preview = plain_text(slide.get("text", ""))[:38].replace("\n", " / ")
        print(f"  slide_{i:02d}.png  [{bg}]  {preview}")

    print(f"\nDone. {total} slides -> {out_dir.resolve()}")

if __name__ == "__main__":
    main()
