#!/usr/bin/env python3
"""Render an ASCII-art .txt file back into a PNG image.

Two modes:
  --mode text   Draw each character as a monospace glyph on a solid background.
  --mode blocks Fill each cell with a gray rectangle (default).

Usage:
    ascii2png art.txt
    ascii2png art.txt --mode blocks --cell-size 8 -o art.png
    ascii2png art.txt --mode blocks --charset fine --cell-aspect 0.5
"""

import argparse
import sys
import os

from PIL import Image, ImageDraw, ImageFont, ImageColor

from .charsets import CHARSETS

# Common monospace fonts across platforms (first existing one wins).
FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
    "/Library/Fonts/Courier New.ttf",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
]


def load_font(path, size):
    if path:
        return ImageFont.truetype(path, size)
    for cand in FONT_CANDIDATES:
        if os.path.isfile(cand):
            return ImageFont.truetype(cand, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def parse_color(value, mode="RGB"):
    try:
        return ImageColor.getcolor(value, mode)
    except ValueError:
        sys.exit(f"Could not parse color: {value!r}")


def render_text(lines, font_size=16, fg="#ffffff", bg="#000000",
                font_path=None, pad=10, line_spacing=1.0):
    """Render lines as monospace glyphs (terminal look)."""
    if not lines or all(not ln for ln in lines):
        sys.exit("No text to render.")
    fg, bg = parse_color(fg), parse_color(bg)
    font = load_font(font_path, font_size)

    width = max(len(ln) for ln in lines)
    ascent, descent = font.getmetrics()
    cell_w = max(1, int(round(font.getlength("M"))))
    cell_h = max(1, int(round((ascent + descent) * line_spacing)))

    img = Image.new("RGB", (pad * 2 + cell_w * width,
                            pad * 2 + cell_h * len(lines)), bg)
    draw = ImageDraw.Draw(img)
    for row, line in enumerate(lines):
        y = pad + row * cell_h
        for col, ch in enumerate(line):
            if ch == " ":
                continue
            draw.text((pad + col * cell_w, y), ch, font=font, fill=fg)
    return img


def render_blocks(lines, charset="default", cell_size=8, cell_aspect=1.0,
                  invert=False, pad=10):
    """Render lines as gray rectangles (gray gradation from the character).

    Dark character -> dark gray, light character -> light gray.
    """
    if not lines or all(not ln for ln in lines):
        sys.exit("No text to render.")
    cs = CHARSETS.get(charset, CHARSETS["default"])
    n = len(cs)
    lookup = {ch: i for i, ch in enumerate(cs)}

    width = max(len(ln) for ln in lines)
    height = len(lines)

    small = Image.new("L", (width, height))
    px = small.load()
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == " ":
                i = n - 1
            elif ch in lookup:
                i = lookup[ch]
            else:
                i = n // 2
            b = i / (n - 1)
            if invert:
                b = 1.0 - b
            px[c, r] = round(255 * b)

    cw = max(1, int(cell_size))
    ch = max(1, int(round(cell_size * cell_aspect)))
    big = small.resize((width * cw, height * ch), Image.NEAREST).convert("RGB")

    if pad:
        out = Image.new("RGB", (big.width + 2 * pad, big.height + 2 * pad),
                        (255, 255, 255))
        out.paste(big, (pad, pad))
        return out
    return big


def main():
    p = argparse.ArgumentParser(
        description="Render an ASCII-art .txt file into a PNG image.")
    p.add_argument("input", help="Path to the ASCII art text file.")
    p.add_argument("-o", "--output", default=None,
                   help="Output PNG path (default: <input>.png).")
    p.add_argument("--mode", choices=["text", "blocks"], default="blocks",
                   help="text = monospace glyphs, blocks = gray rectangles "
                        "(default: blocks).")
    p.add_argument("--font-size", type=int, default=16,
                   help="[text] glyph cell height in px (default: 16).")
    p.add_argument("--fg", default="#ffffff",
                   help="[text] character color (default: white).")
    p.add_argument("--bg", default="#000000",
                   help="[text] background color (default: black).")
    p.add_argument("--font", default=None,
                   help="[text] path to a monospace TTF/OTF font.")
    p.add_argument("--line-spacing", type=float, default=1.0,
                   help="[text] vertical spacing multiplier (default: 1.0).")
    p.add_argument("--charset", default="default", choices=sorted(CHARSETS),
                   help="[blocks] charset the source art was made with "
                        "(must match image2ascii, default: default).")
    p.add_argument("--cell-size", type=int, default=8,
                   help="[blocks] cell size in px (default: 8).")
    p.add_argument("--cell-aspect", type=float, default=1.0,
                   help="[blocks] cell height/width ratio. 1.0 = square cells "
                        "(default). For a round trip that matches the original "
                        "image proportions, create the art with "
                        "'image2ascii --char-aspect 1.0' and keep 1.0.")
    p.add_argument("--invert", action="store_true",
                   help="[blocks] flip the gray mapping.")
    p.add_argument("--pad", type=int, default=10,
                   help="Outer padding in px (default: 10).")
    args = p.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"File not found: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    if args.mode == "blocks":
        img = render_blocks(lines, args.charset, args.cell_size,
                            args.cell_aspect, args.invert, args.pad)
    else:
        img = render_text(lines, args.font_size, args.fg, args.bg,
                          args.font, args.pad, args.line_spacing)

    out = args.output or os.path.splitext(args.input)[0] + ".png"
    img.save(out)
    print(f"Saved {out}  ({img.width}x{img.height}px, mode={args.mode})")


if __name__ == "__main__":
    main()
