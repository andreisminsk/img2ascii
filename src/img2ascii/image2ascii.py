#!/usr/bin/env python3
"""Convert .png/.jpg images into printable ASCII art.

Usage:
    image2ascii input.png
    image2ascii input.jpg -w 100 -o art.txt
    image2ascii photo.png --invert --charset "detailed"
"""

import argparse
import sys
import os

from PIL import Image
from .charsets import CHARSETS

# Terminal glyphs are typically ~twice as tall as they are wide,
# so we squash the vertical resolution to keep the aspect correct.
CHAR_ASPECT = 0.55


def convert(image, width, charset, invert=False,
            char_aspect=CHAR_ASPECT, height=None):
    """Map a PIL image to an ASCII string preserving aspect ratio."""
    orig_w, orig_h = image.size
    if height is None or height <= 0:
        if width <= 0:
            width = orig_w
        height = max(1, int(round(orig_h / orig_w * width * char_aspect)))
    else:
        if width <= 0:
            width = max(1, int(round(orig_w / orig_h * height / char_aspect)))
    width = min(width, max(1, orig_w))
    height = min(height, max(1, orig_h))

    img = image.convert("L").resize((width, height), Image.LANCZOS)
    pixels = list(img.tobytes())

    if invert:
        pixels = [255 - p for p in pixels]

    lo, hi = min(pixels), max(pixels)
    n = len(charset) - 1
    if hi == lo:
        hi = lo + 1

    art = []
    for row in range(height):
        line_chars = []
        for col in range(width):
            v = pixels[row * width + col]
            idx = int((v - lo) / (hi - lo) * n + 0.5)
            line_chars.append(charset[idx])
        art.append("".join(line_chars))
    return "\n".join(art)


def main():
    p = argparse.ArgumentParser(
        description="Convert .png/.jpg images into printable ASCII art.")
    p.add_argument("input", help="Path to the source image (.png or .jpg).")
    p.add_argument("-w", "--width", type=int, default=120,
                   help="Output width in characters (default: 120).")
    p.add_argument("-H", "--height", type=int, default=None,
                   help="Output height in characters (overrides aspect calc; "
                        "raise this for more detail).")
    p.add_argument("-o", "--output", default=None,
                   help="Write result to this text file (default: print to stdout).")
    p.add_argument("--charset", default="default", choices=sorted(CHARSETS),
                   help="Character set to use (default: %(default)s).")
    p.add_argument("--invert", action="store_true",
                   help="Invert the tonal mapping (dark bg -> light bg).")
    p.add_argument("--char-aspect", type=float, default=CHAR_ASPECT,
                   help="Terminal char height/width ratio (default: %(default)s).")
    args = p.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"File not found: {args.input}")
    ext = os.path.splitext(args.input)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg"):
        sys.exit(f"Unsupported format: {ext} (use .png or .jpg).")

    image = Image.open(args.input)
    ascii_art = convert(image, args.width, CHARSETS[args.charset],
                        args.invert, args.char_aspect, args.height)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(ascii_art + "\n")
        print(f"ASCII art written to {args.output}", file=sys.stderr)
    else:
        print(ascii_art)


if __name__ == "__main__":
    main()
